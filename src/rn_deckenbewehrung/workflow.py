"""Preview confirmation and duplicate prevention for a single session.

Persistent Allplan ownership and transactional writing are not implemented.
Consequently this gate does NOT expose a production write method.
"""
from dataclasses import dataclass
from hashlib import sha256
import json
from .model import ValidationError


@dataclass
class PreviewGate:
    fingerprint: str | None = None
    confirmed: bool = False

    def preview(self, inputs):
        self.fingerprint = sha256(json.dumps(inputs, sort_keys=True, allow_nan=False).encode()).hexdigest()
        self.confirmed = False
        return self.fingerprint

    def confirm(self, fingerprint):
        if self.fingerprint is None or self.fingerprint != fingerprint:
            raise ValidationError("Vorschau fehlt oder wurde geändert; erneut prüfen")
        self.confirmed = True

    def require_ready(self, fingerprint, existing_run_ids):
        if not self.confirmed or fingerprint != self.fingerprint:
            raise ValidationError("Aktuelle Vorschau ausdrücklich bestätigen")
        if existing_run_ids:
            raise ValidationError("Vorhandene Erzeugung: mögliche Doppelverlegung zuerst klären")


def delete_owned_elements(*args, **kwargs):
    raise NotImplementedError("Keine Löschung ohne verifizierte persistente Allplan-Elementzuordnung")
