from dataclasses import dataclass


@dataclass(frozen=True)
class Severity:
    key: str
    label: str


CRITICAL = Severity("critical", "Critical")
WARNING = Severity("warning", "Warning")
INFO = Severity("info", "Info")
