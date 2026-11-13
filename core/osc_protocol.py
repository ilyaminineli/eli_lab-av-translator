from __future__ import annotations

import ipaddress
import logging
import re
import threading
import time
from collections import OrderedDict, deque
from collections.abc import Callable

from core.performance_control import ControlEvent

_LOG = logging.getLogger(__name__)
_NAMESPACE = "/eli_lab/v1"
_IDENTIFIER = re.compile(r"^[A-Za-z0-9_.:-]{1,64}$")
_MACROS = frozenset({
    "energy", "cutoff", "chaos", "density", "depth", "decay", "pressure", "fragment"
})
_SCENES = frozenset({
    "in", "exp", "tm_a", "trns", "dev", "fr", "ssp", "rtrns",
    "rc", "rc_w", "peak", "intd", "s_s", "rls", "c", "end",
})


def _identifier(value: object, field: str) -> str:
    if not isinstance(value, str) or not _IDENTIFIER.fullmatch(value):
        raise ValueError(f"{field} must be a short OSC identifier.")
    return value


def _integer(value: object, field: str, minimum: int, maximum: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{field} must be an OSC integer.")
    if not minimum <= value <= maximum:
        raise ValueError(f"{field} is outside its permitted range.")
    return value


def _number(value: object, field: str, minimum: float, maximum: float) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field} must be an OSC number.")
    result = float(value)
    if not minimum <= result <= maximum:
        raise ValueError(f"{field} is outside its permitted range.")
    return result


class OSCProtocolAdapter:
    """Strict /eli_lab/v1 decoder with restart-safe session and sequence checks."""

    def __init__(self, source: str = "sonic_pi", session_history: int = 64) -> None:
        self.source = source
        self.session_history = max(4, int(session_history))
        self._sessions: OrderedDict[str, int] = OrderedDict()
        self._active_session = ""
        self._lock = threading.Lock()

    @property
    def active_session(self) -> str:
        with self._lock:
            return self._active_session

    def decode(self, address: str, args: tuple[object, ...] | list[object]) -> ControlEvent:
        """Translate one OSC message into a validated, renderer-independent event."""
        if not isinstance(address, str) or not address.startswith(f"{_NAMESPACE}/"):
            raise ValueError("Unsupported OSC address or protocol namespace.")
        parts = address[len(_NAMESPACE):].strip("/").split("/")
        route = "/".join(parts)
        values = tuple(args)
        if len(values) < 2:
            raise ValueError("Every protocol message requires session ID and sequence.")

        session_id = _identifier(values[0], "session_id")
        sequence = _integer(values[1], "sequence", 1, 2_147_483_647)
        payload_args = values[2:]

        if route == "transport/start":
            if len(payload_args) != 2:
                raise ValueError("transport/start expects BPM and beats_per_bar.")
            payload = {
                "bpm": _number(payload_args[0], "bpm", 20.0, 300.0),
                "beats_per_bar": _integer(payload_args[1], "beats_per_bar", 1, 16),
            }
            kind = "transport.start"
        elif route == "transport/stop":
            if payload_args:
                raise ValueError("transport/stop takes no additional arguments.")
            payload = {}
            kind = "transport.stop"
        elif route == "transport/tempo":
            if len(payload_args) != 1:
                raise ValueError("transport/tempo expects one BPM value.")
            payload = {"bpm": _number(payload_args[0], "bpm", 20.0, 300.0)}
            kind = "transport.tempo"
        elif route == "clock/bar":
            if len(payload_args) != 3:
                raise ValueError("clock/bar expects bar index, BPM and beats_per_bar.")
            payload = {
                "bar_index": _integer(payload_args[0], "bar_index", 1, 10_000_000),
                "bpm": _number(payload_args[1], "bpm", 20.0, 300.0),
                "beats_per_bar": _integer(payload_args[2], "beats_per_bar", 1, 16),
            }
            kind = "clock.bar"
        elif route == "scene/select":
            if len(payload_args) != 3:
                raise ValueError("scene/select expects scene ID, intensity and bar index.")
            scene_id = _identifier(payload_args[0], "scene_id")
            if scene_id not in _SCENES:
                raise ValueError(f"Unknown SONATA scene ID: {scene_id!r}.")
            payload = {
                "scene_id": scene_id,
                "intensity": _number(payload_args[1], "intensity", 0.0, 1.0),
                "bar_index": _integer(payload_args[2], "bar_index", 0, 10_000_000),
            }
            kind = "scene.select"
        elif route == "scene/intensity":
            if len(payload_args) != 1:
                raise ValueError("scene/intensity expects one normalized value.")
            payload = {"intensity": _number(payload_args[0], "intensity", 0.0, 1.0)}
            kind = "scene.intensity"
        elif route == "macro/set":
            if len(payload_args) != 2:
                raise ValueError("macro/set expects a name and normalized value.")
            macro = _identifier(payload_args[0], "macro name")
            if macro not in _MACROS:
                raise ValueError(f"Unsupported Sonic Pi macro: {macro!r}.")
            payload = {
                "name": macro,
                "value": _number(payload_args[1], "macro value", 0.0, 1.0),
            }
            kind = "macro.set"
        elif route == "cue/trigger":
            if len(payload_args) != 1:
                raise ValueError("cue/trigger expects one cue name.")
            payload = {"name": _identifier(payload_args[0], "cue name")}
            kind = "cue.trigger"
        elif route == "source/heartbeat":
            if payload_args:
                raise ValueError("source/heartbeat takes no additional arguments.")
            payload = {}
            kind = "source.heartbeat"
        else:
            raise ValueError(f"Unknown /eli_lab/v1 route: {route!r}.")

        with self._lock:
            previous = self._sessions.get(session_id)
            if kind == "transport.start":
                if previous is not None:
                    raise ValueError("A session ID cannot be reused; restart with a new ID.")
            else:
                if session_id != self._active_session:
                    raise ValueError("Message does not belong to the active session.")
                if previous is None or sequence <= previous:
                    raise ValueError("Duplicate or stale OSC sequence number.")

            event = ControlEvent(
                kind=kind,
                source=self.source,
                payload=payload,
                sequence=sequence,
                session_id=session_id,
            )
            self._sessions[session_id] = sequence
            self._sessions.move_to_end(session_id)
            self._active_session = session_id
            while len(self._sessions) > self.session_history:
                oldest = next(iter(self._sessions))
                if oldest == self._active_session:
                    self._sessions.move_to_end(oldest)
                    continue
                self._sessions.popitem(last=False)
            return event


class OSCReceiver:
    """Single-worker UDP OSC receiver that only submits ControlEvents to a bounded queue."""

    def __init__(
            self,
            submit_event: Callable[[ControlEvent], bool],
            *,
            max_messages_per_second: int = 60,
            freshness_seconds: float = 5.0,
    ) -> None:
        self._submit_event = submit_event
        self.adapter = OSCProtocolAdapter()
        self.max_messages_per_second = max(1, int(max_messages_per_second))
        self.freshness_seconds = max(1.0, float(freshness_seconds))
        self._lock = threading.RLock()
        self._server = None
        self._thread: threading.Thread | None = None
        self._stop_event = threading.Event()
        self._running = False
        self._bind_address = "127.0.0.1"
        self._port = 57121
        self._last_message_at = 0.0
        self._last_valid_message_at = 0.0
        self._last_address = ""
        self._last_error = ""
        self._received = 0
        self._accepted = 0
        self._rejected = 0
        self._rate_limited = 0
        self._dropped = 0
        self._message_times: deque[float] = deque()

    def start(self, bind_address: str = "127.0.0.1", port: int = 57121) -> int:
        """Bind and start the receiver; return the actual bound UDP port."""
        try:
            parsed = ipaddress.ip_address(str(bind_address).strip())
            if parsed.version != 4:
                raise ValueError("The current OSC bridge accepts IPv4 bind addresses only.")
            port = int(port)
            if not 0 <= port <= 65535:
                raise ValueError("OSC port must be between 0 and 65535.")
            from pythonosc.dispatcher import Dispatcher
            from pythonosc.osc_server import BlockingOSCUDPServer
        except ImportError as exc:
            with self._lock:
                self._last_error = str(exc)
            raise RuntimeError(
                "python-osc is not installed. Install the runtime requirements."
            ) from exc
        except (TypeError, ValueError) as exc:
            with self._lock:
                self._last_error = str(exc)
            raise

        with self._lock:
            if self._running:
                raise RuntimeError("The OSC receiver is already running.")
            dispatcher = Dispatcher()
            dispatcher.set_default_handler(self._handle_message)

            receiver = self

            class RecoverableServer(BlockingOSCUDPServer):
                def verify_request(self, request, client_address):
                    valid = super().verify_request(request, client_address)
                    if not valid:
                        receiver._record_invalid()
                        return False
                    return receiver._rate_allowed(time.monotonic())

                def handle_error(self, request, client_address):
                    receiver._record_invalid()
                    _LOG.debug("Discarded malformed OSC datagram from %s", client_address)

            try:
                server = RecoverableServer((str(parsed), port), dispatcher)
            except OSError as exc:
                self._last_error = str(exc)
                raise
            self._server = server
            self._bind_address = str(parsed)
            self._port = int(server.server_address[1])
            self._last_error = ""
            self._stop_event.clear()
            self._running = True
            self._thread = threading.Thread(
                target=self._serve,
                name="eli-lab-osc-receiver",
                daemon=True,
            )
            self._thread.start()
            return self._port

    def _serve(self) -> None:
        with self._lock:
            server = self._server
        try:
            if server is not None:
                server.timeout = 0.1
                while not self._stop_event.is_set():
                    try:
                        server.handle_request()
                    except OSError:
                        if self._stop_event.is_set():
                            break
                        raise
        except Exception as exc:  # keep network faults away from the render/UI thread
            with self._lock:
                self._last_error = str(exc)
            _LOG.exception("OSC receiver worker failed")
        finally:
            with self._lock:
                self._running = False

    def stop(self) -> bool:
        with self._lock:
            server = self._server
            thread = self._thread
            if server is None:
                self._running = False
                return False
        self._stop_event.set()
        server.server_close()
        if thread is not None and thread is not threading.current_thread():
            thread.join(timeout=1.0)
        with self._lock:
            self._server = None
            self._thread = None
            self._running = False
        return True

    def _rate_allowed(self, now: float) -> bool:
        with self._lock:
            while self._message_times and now - self._message_times[0] >= 1.0:
                self._message_times.popleft()
            if len(self._message_times) >= self.max_messages_per_second:
                self._rate_limited += 1
                return False
            self._message_times.append(now)
            return True

    def _record_invalid(self) -> None:
        with self._lock:
            self._rejected += 1

    def _handle_message(self, address: str, *args: object) -> None:
        now = time.monotonic()
        with self._lock:
            self._received += 1
            self._last_message_at = now
            self._last_address = str(address)
        try:
            event = self.adapter.decode(address, args)
        except (TypeError, ValueError, OverflowError) as exc:
            self._record_invalid()
            _LOG.debug("Rejected OSC message %s: %s", address, exc)
            return
        with self._lock:
            self._last_valid_message_at = now
        try:
            accepted = bool(self._submit_event(event))
        except Exception:
            accepted = False
            _LOG.exception("Control event queue rejected OSC message %s", address)
        with self._lock:
            if accepted:
                self._accepted += 1
            else:
                self._dropped += 1

    def snapshot(self) -> dict[str, object]:
        now = time.monotonic()
        with self._lock:
            age = (
                max(0.0, now - self._last_valid_message_at)
                if self._last_valid_message_at else None
            )
            if not self._running:
                status = "ERROR" if self._last_error else "STOPPED"
            elif age is None:
                status = "LISTENING"
            elif age <= self.freshness_seconds:
                status = "LIVE"
            else:
                status = "STALE"
            return {
                "status": status,
                "running": self._running,
                "bind_address": self._bind_address,
                "port": self._port,
                "active_session": self.adapter.active_session,
                "last_message_age": age,
                "last_address": self._last_address,
                "last_error": self._last_error,
                "received": self._received,
                "accepted": self._accepted,
                "rejected": self._rejected,
                "rate_limited": self._rate_limited,
                "dropped": self._dropped,
            }
