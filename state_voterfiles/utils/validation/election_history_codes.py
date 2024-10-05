from enum import Enum


class VoteMethodCodes(Enum):
    IN_PERSON = "IP"
    MAIL_IN = "MI"
    EARLY_VOTING = "EV"
    PROVISIONAL = "PV"
    ABSENTEE = "AB"


class PoliticalPartyCodes(Enum):
    DEMOCRATIC = "DEM"
    REPUBLICAN = "REP"
    LIBERTARIAN = "LIB"
    GREEN = "GRN"
    CONSTITUTION = "CON"
    AMERICAN_SOLIDARITY = "AMS"
    ALLIANCE = "ALL"

    # Additional parties based on various mentions and contexts:
    INDEPENDENT = "Independent"
    PROGRESSIVE = "Progressive"
    CENTRIST = "Centrist"
    MAGA = "MAGA"
    NO_LABELS = "No Labels"
    LABOUR = "Labour"


class ElectionTypeCodes(Enum):
    GENERAL = "GE"
    PRESIDENTIAL = "PE"
    MUNICIPAL = "ME"
    SPECIAL = "SE"
    RECALL = "RE"
    PRIMARY = "PR"
    OPEN_PRIMARY = "OP"
    CLOSED_PRIMARY = "CP"
    NONPARTISAN_PRIMARY = "NP"
    SCHOOL_BOARD = "SB"
    JUDICIAL = "JE"
    LOCAL = "LE"
    CONGRESSIONAL = "CE"
    MIDTERM = "ME"
    REFERENDUM = "RF"
    PRESIDENTIAL_PRIMARY = "PP"
    PRESIDENTIAL_PREFERENCE = "PPR"
    PRESIDENTIAL_CAUCUS = "PC"
