from abc import ABC, abstractmethod
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


class SocialRelation(ABC):
    @property
    @abstractmethod
    def role_first(self) -> str:
        ...

    @property
    @abstractmethod
    def role_second(self) -> str:
        ...


class FamilyType(Enum, SocialRelation):
    FAMILY = "family"
    PARENT = "parentship"
    SIBLING = "siblingship"

    @property
    def role_first(self) -> str:
        match self:
            case FamilyType.FAMILY:
                return "relative"
            case FamilyType.PARENT:
                return "parent"
            case FamilyType.SIBLING:
                return "sibling"
            case _:
                raise RuntimeError()

    @property
    def role_second(self) -> str:
        match self:
            case FamilyType.FAMILY:
                return self.role_first
            case FamilyType.PARENT:
                return "child"
            case FamilyType.SIBLING:
                return self.role_first
            case _:
                raise RuntimeError()


class RelationshipType(Enum, SocialRelation):
    RELATIONSHIP = "relationship"
    ENGAGEMENT = "engagement"
    MARRIAGE = "marriage"

    @property
    def role_first(self) -> str:
        match self:
            case RelationshipType.RELATIONSHIP:
                return "partner"
            case RelationshipType.ENGAGEMENT:
                return "fiance"
            case RelationshipType.MARRIAGE:
                return "spouse"
            case _:
                raise RuntimeError()

    @property
    def role_second(self) -> str:
        return self.role_first

    @property
    def date_type(self) -> str:
        match self:
            case RelationshipType.RELATIONSHIP:
                return "start-date"
            case RelationshipType.ENGAGEMENT:
                return "engagement-date"
            case RelationshipType.MARRIAGE:
                return "marriage-date"
            case _:
                raise RuntimeError()

    @property
    def has_location(self) -> bool:
        return self in [RelationshipType.ENGAGEMENT, RelationshipType.MARRIAGE]

    @property
    def status(self) -> RelationshipStatus:
        match self:
            case RelationshipType.RELATIONSHIP:
                return RelationshipStatus.RELATIONSHIP
            case RelationshipType.ENGAGEMENT:
                return RelationshipStatus.ENGAGED
            case RelationshipType.MARRIAGE:
                return RelationshipStatus.MARRIED
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
            case _:
                raise RuntimeError()

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
            case _:
                raise RuntimeError()

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
            case _:
                raise RuntimeError()


class OrganisationType(Enum):
    COMPANY = "company"
    CHARITY = "charity"
    INSTITUTE = "educational-institute"
    SCHOOL = "school"
    COLLEGE = "college"
    UNIVERSITY = "university"
