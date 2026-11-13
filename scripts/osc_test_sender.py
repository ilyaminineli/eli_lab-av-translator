from __future__ import annotations

import argparse
import time
import uuid

from pythonosc.udp_client import SimpleUDPClient


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Send a deterministic /eli_lab/v1 Sonic Pi test performance."
    )
    parser.add_argument(
        "--host", default="127.0.0.1", help="AV Translator bind address"
    )
    parser.add_argument(
        "--port", type=int, default=57121, help="AV Translator OSC port"
    )
    parser.add_argument("--session-id", default="", help="Optional unique session ID")
    parser.add_argument(
        "--no-stop", action="store_true", help="Leave transport running"
    )
    args = parser.parse_args()

    session_id = args.session_id or f"test-{uuid.uuid4().hex[:12]}"
    client = SimpleUDPClient(args.host, args.port)
    sequence = 0

    def send(route: str, *payload: str | int | float) -> None:
        nonlocal sequence
        sequence += 1
        client.send_message(
            f"/eli_lab/v1/{route}",
            [session_id, sequence, *payload],
        )

    send("transport/start", 92.0, 4)
    send("transport/tempo", 92.0)
    time.sleep(0.1)
    send("clock/bar", 1, 92.0, 4)
    send("scene/select", "in", 0.12, 1)
    send("macro/set", "energy", 0.28)
    send("macro/set", "cutoff", 0.42)
    send("source/heartbeat")
    time.sleep(0.25)
    send("clock/bar", 2, 92.0, 4)
    send("scene/select", "dev", 0.62, 2)
    send("macro/set", "energy", 0.68)
    send("macro/set", "cutoff", 0.83)
    send("cue/trigger", "phrase_1")
    send("source/heartbeat")
    time.sleep(0.25)
    if not args.no_stop:
        send("cue/trigger", "end")
        send("transport/stop")

    print(
        f"Sent {sequence} /eli_lab/v1 messages to {args.host}:{args.port} "
        f"(session {session_id})."
    )


if __name__ == "__main__":
    main()
