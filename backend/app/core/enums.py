from enum import Enum


class OpportunityType(str, Enum):
    JOB = "job"
    PROJECT = "project"
    HELP = "help"
    COLLAB = "collab"
    DATE = "date"


class OpenToCategory(str, Enum):
    JOB = "job"
    PROJECT = "project"
    HELP = "help"
    COLLAB = "collab"
    DATE = "date"


class ConnectionSource(str, Enum):
    SEED = "seed"
    MATCH = "match"
    MANUAL = "manual"
