from __future__ import annotations

import logging
from collections.abc import Callable, Mapping
from copy import deepcopy
from dataclasses import fields
from core.composition import Layer
from core.layer_manager import LayerManager

_LOG = logging.getLogger(__name__)

type LayerMutator = Callable[[Layer], bool | None]
type MutationCommitHook = Callable[[Layer, frozenset[str], str], None]
MAX_MUTATION_FIELDS = 32


class VisualMutationAdapter:
    """Shared synchronous transaction boundary for automated layer mutations.

    Mutation callbacks receive a detached Layer candidate. The adapter computes
    the top-level field diff and delegates the commit to LayerManager, so
    contract validation, identity preservation, locking and rollback have one
    authoritative implementation.
    """

    def __init__(
        self,
        layer_manager: LayerManager,
        on_commit: MutationCommitHook | None = None,
    ) -> None:
        self.layer_manager = layer_manager
        self.on_commit = on_commit

    @property
    def composition(self):
        return self.layer_manager.composition

    def set_layer_manager(self, layer_manager: LayerManager) -> None:
        """Rebind after project/session restore replaces the Composition."""
        self.layer_manager = layer_manager

    def apply_changes(
        self,
        layer_id: str,
        changes: Mapping[str, object],
        *,
        source: str,
        respect_lock: bool = True,
    ) -> Layer:
        """Apply a small multi-field mutation as one LayerManager transaction."""
        staged = dict(changes)
        if not staged:
            layer = self.composition.get_layer(layer_id)
            if layer is None:
                raise KeyError(f"Unknown layer: {layer_id}")
            return layer
        if len(staged) > MAX_MUTATION_FIELDS:
            raise ValueError(
                f"A visual mutation may change at most {MAX_MUTATION_FIELDS} fields."
            )
        updated = self.layer_manager.update_layer(
            layer_id,
            operation=source,
            respect_lock=respect_lock,
            **staged,
        )
        self._notify_commit(updated, frozenset(staged), source)
        return updated

    def mutate_layer(
        self,
        layer_id: str,
        mutator: LayerMutator,
        *,
        source: str,
        respect_lock: bool = True,
    ) -> Layer | None:
        """Run a mutation against a detached candidate and atomically commit it.

        Returning False from the callback rejects the draft without writing.
        Exceptions also leave the live layer and identity registry untouched.
        """
        current = self.composition.get_layer(layer_id)
        if current is None:
            return None
        if respect_lock and current.locked:
            raise PermissionError(f"Layer {layer_id!r} is locked.")

        candidate = deepcopy(current)
        accepted = mutator(candidate)
        if accepted is False:
            return None
        candidate.__post_init__()

        changes: dict[str, object] = {}
        for item in fields(Layer):
            name = item.name
            if name in {"id", "visual_object_id"}:
                continue
            candidate_value = getattr(candidate, name)
            if candidate_value != getattr(current, name):
                changes[name] = deepcopy(candidate_value)
        if not changes:
            return current
        if len(changes) > MAX_MUTATION_FIELDS:
            raise ValueError(
                f"A visual mutation may change at most {MAX_MUTATION_FIELDS} fields."
            )
        return self.apply_changes(
            layer_id,
            changes,
            source=source,
            respect_lock=respect_lock,
        )

    def _notify_commit(
        self,
        layer: Layer,
        changed_fields: frozenset[str],
        source: str,
    ) -> None:
        if self.on_commit is None:
            return
        try:
            self.on_commit(layer, changed_fields, source)
        except Exception:
            # A cache/render notification must not roll back an already valid
            # composition transaction or leave the identity registry half-written.
            _LOG.exception(
                "Post-mutation notification failed for layer %s (%s)",
                layer.id,
                source,
            )
