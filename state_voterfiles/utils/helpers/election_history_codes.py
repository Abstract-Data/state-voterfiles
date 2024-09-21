from enum import Enum, StrEnum


class VoteMethodCodes(StrEnum):
    IN_PERSON = "IP"
    MAIL_IN = "MI"
    EARLY_VOTING = "EV"
    PROVISIONAL = "PV"
    ABSENTEE = "AB"


class PoliticalPartyCodes(StrEnum):
    DEMOCRATIC = "Democratic"
    REPUBLICAN = "Republican"
    LIBERTARIAN = "Libertarian"
    GREEN = "Green"
    CONSTITUTION = "Constitution"
    AMERICAN_SOLIDARITY = "American Solidarity"
    ALLIANCE = "Alliance"

    # Additional parties based on various mentions and contexts:
    INDEPENDENT = "Independent"
    PROGRESSIVE = "Progressive"
    CENTRIST = "Centrist"
    MAGA = "MAGA"
    NO_LABELS = "No Labels"
    LABOUR = "Labour"
    OTHER = "Other"


class ElectionTypeCodes(StrEnum):
    GENERAL = "GE"
    GENERAL_RUNOFF = "GR"
    GOVERNMENTAL_AUTHORITY = "GA"
    GOVERNMENT_LEGISLATIVE = "GL"
    MUNICIPAL = "ME"
    SPECIAL = "SE"
    RECALL = "RE"
    PRIMARY = "PR"
    PRIMARY_RUNOFF = "PRR"
    OPEN_PRIMARY = "OP"
    CLOSED_PRIMARY = "CP"
    NONPARTISAN_PRIMARY = "NP"
    SCHOOL_BOARD = "SB"
    JUDICIAL = "JE"
    LOCAL = "LE"
    LOCAL_RUNOFF = "LR"
    CONGRESSIONAL = "CE"
    MIDTERM = "ME"
    REFERENDUM = "RF"
    PRESIDENTIAL = "PE"
    PRESIDENTIAL_PRIMARY = "PP"
    PRESIDENTIAL_PREFERENCE = "PPR"
    PRESIDENTIAL_CAUCUS = "PC"
