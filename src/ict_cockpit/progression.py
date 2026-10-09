from enum import Enum


class ProgressionBoundary(str, Enum):
    """Canonical upward learning/progression boundaries."""

    STUDY_TO_REHEARSAL = "Study -> Rehearsal"
    REHEARSAL_TO_VALIDATION = "Rehearsal -> Validation"
    VALIDATION_TO_EXECUTION = "Validation -> Execution"
