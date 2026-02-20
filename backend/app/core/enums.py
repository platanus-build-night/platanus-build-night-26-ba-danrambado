from enum import Enum


class OpportunityType(str, Enum):
    JOB = "job"
    PROJECT = "project"
    HELP = "help"
    COLLAB = "collab"
    DATE = "date"
    FUN = "fun"


class OpenToCategory(str, Enum):
    JOB = "job"
    PROJECT = "project"
    HELP = "help"
    COLLAB = "collab"
    DATE = "date"
    FUN = "fun"


class ConnectionSource(str, Enum):
    SEED = "seed"
    MATCH = "match"
    MANUAL = "manual"
