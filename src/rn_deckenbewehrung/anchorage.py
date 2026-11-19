"""No inferred EC2/NA formula: reviewed project values are mandatory in v0.1."""
from dataclasses import dataclass
from .model import ValidationError, number


@dataclass(frozen=True)
class ReviewedLengths:
    anchorage: float
    lap: float
    standard: str
    national_annex: str
    evidence: str

    def __post_init__(self):
        number(self.anchorage, "Verankerung", strict=True)
        number(self.lap, "Übergreifung", strict=True)
        if not all(s.strip() for s in (self.standard,self.national_annex,self.evidence)):
            raise ValidationError("Norm, Nationaler Anhang und Prüfbeleg erforderlich")


def automatic_lengths(*args, **kwargs):
    raise NotImplementedError("Automatische Normbemessung noch nicht verifiziert; projektspezifischen Nachweis hinterlegen")
