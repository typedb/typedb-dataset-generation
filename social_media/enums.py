from datetime import datetime
from enum import Enum


class NameType(Enum):
    FIRST = "first"
    LAST = "last"
    FULL = "full"


class Gender(Enum):
    FEMALE = "female"
    MALE = "male"
    OTHER = "other"


class EmailDomain(Enum):
    GOOGLE = "gmail.com"
    MICROSOFT = "outlook.com"
    PROTON = "proton.me"
    AOL = "aol.com"
    YAHOO = "yahoo.com"


class RelationshipStatus(Enum):
    SINGLE = "single"
    RELATIONSHIP = "relationship"
    ENGAGED = "engaged"
    MARRIED = "married"
    COMPLICATED = "complicated"

    @property
    def relationship_type(self) -> str:
        match self:
            case RelationshipStatus.SINGLE:
                raise ValueError()
            case RelationshipStatus.RELATIONSHIP:
                return "relationship"
            case RelationshipStatus.ENGAGED:
                return "engagement"
            case RelationshipStatus.MARRIED:
                return "marriage"
            case RelationshipStatus.COMPLICATED:
                raise ValueError()
            case _:
                raise RuntimeError()

    @property
    def partner_role(self) -> str:
        match self:
            case RelationshipStatus.SINGLE:
                raise ValueError()
            case RelationshipStatus.RELATIONSHIP:
                return "partner"
            case RelationshipStatus.ENGAGED:
                return "fiance"
            case RelationshipStatus.MARRIED:
                return "spouse"
            case RelationshipStatus.COMPLICATED:
                raise ValueError()
            case _:
                raise RuntimeError()

    @property
    def date_type(self) -> str:
        match self:
            case RelationshipStatus.SINGLE:
                raise ValueError()
            case RelationshipStatus.RELATIONSHIP:
                return "start-date"
            case RelationshipStatus.ENGAGED:
                return "engagement-date"
            case RelationshipStatus.MARRIED:
                return "marriage-date"
            case RelationshipStatus.COMPLICATED:
                raise ValueError()
            case _:
                raise RuntimeError()


class TimestampFormat(Enum):
    DATE = "YYYY-MM-DD"
    DATETIME = "YYYY-MM-DDTHH:MM:SS"
    PRECISE_DATETIME = "YYYY-MM-DDTHH:MM:SS.FFF"

    @property
    def _format(self) -> str:
        match self:
            case TimestampFormat.DATE:
                return "%Y-%m-%d"
            case TimestampFormat.DATETIME:
                return "%Y-%m-%dT%H:%M:%S"
            case TimestampFormat.PRECISE_DATETIME:
                return "%Y-%m-$dT%H:%M:%S.%f"
            case _:
                raise RuntimeError()

    def parse_string(self, timestamp: str) -> datetime:
        if self is TimestampFormat.PRECISE_DATETIME:
            timestamp += "000"

        return datetime.strptime(timestamp, self._format)

    def to_string(self, timestamp: datetime) -> str:
        string = timestamp.strftime(self._format)

        if self is TimestampFormat.PRECISE_DATETIME:
            string = string[:-3]

        return string


class GroupMemberRank(Enum):
    MEMBER = "member"
    MODERATOR = "moderator"
    ADMIN = "admin"
    OWNER = "owner"


class Emoji(Enum):
    LIKE = "like"
    LOVE = "love"
    FUNNY = "funny"
    SURPRISE = "surprise"
    SAD = "sad"
    ANGRY = "angry"


class PageVisibility(Enum):
    PUBLIC = "public"
    PRIVATE = "private"


class PostVisibility(Enum):
    DEFAULT = "default"
    PUBLIC = "public"
    PRIVATE = "private"


class PostType(Enum):
    TEXT = "text-post"
    SHARE = "share-post"
    IMAGE = "image-post"
    VIDEO = "video-post"
    LIVE = "live-video-post"
    POLL = "poll-post"


class PlaceType(Enum):
    REGION = "region"
    COUNTRY = "country"
    STATE = "state"
    CITY = "city"
    LANDMARK = "landmark"

    @property
    def location_type(self) -> str:
        match self:
            case PlaceType.REGION:
                return "region-location"
            case PlaceType.COUNTRY:
                return "country-location"
            case PlaceType.STATE:
                return "state-location"
            case PlaceType.CITY:
                return "city-location"
            case PlaceType.LANDMARK:
                return "landmark-location"

    @property
    def place_role(self) -> str:
        match self:
            case PlaceType.REGION:
                return "parent-region"
            case PlaceType.COUNTRY:
                return "region"
            case PlaceType.STATE:
                return "country"
            case PlaceType.CITY:
                return "parent"
            case PlaceType.LANDMARK:
                return "parent"

    @property
    def located_role(self) -> str:
        match self:
            case PlaceType.REGION:
                return "child-region"
            case PlaceType.COUNTRY:
                return "country"
            case PlaceType.STATE:
                return "state"
            case PlaceType.CITY:
                return "city"
            case PlaceType.LANDMARK:
                return "landmark"


class OrganisationType(Enum):
    COMPANY = "company"
    CHARITY = "charity"
    INSTITUTE = "educational-institute"
    SCHOOL = "school"
    COLLEGE = "college"
    UNIVERSITY = "university"
