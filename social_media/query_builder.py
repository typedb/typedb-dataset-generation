from enum import Enum
from random import Random
from typing import Any
from uuid import UUID
from yaml import safe_load


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


class QueryBuilder:
    _username_suffix_digits = 3
    _group_id_prefix = "grp"
    _post_id_prefix = "pst"
    _comment_id_prefix = "cmt"
    _place_id_prefix = "plc"
    _media_id_prefix = "med"
    _start_year = 2020
    _end_year = 2024

    def __init__(self, seed=0):
        self._random = Random(seed)
        self._usernames: list[str] = list()
        self._group_ids: list[str] = list()
        self._post_ids: list[str] = list()
        self._comment_ids: list[str] = list()
        self._place_ids: list[str] = list()

        with open("resources/female_names.yml", "r") as file:
            self._female_names: list[dict[str, Any]] = safe_load(file)

        with open("resources/male_names.yml", "r") as file:
            self._male_names: list[dict[str, Any]] = safe_load(file)

        with open("resources/last_names.yml", "r") as file:
            self._last_names: list[dict[str, Any]] = safe_load(file)

    def _get_new_uuid(self) -> str:
        return UUID(version=4, int=self._random.getrandbits(128)).hex

    def _get_new_group_id(self) -> str:
        return f"{self._group_id_prefix}-{self._get_new_uuid()}"

    def _get_new_post_id(self) -> str:
        return f"{self._post_id_prefix}-{self._get_new_uuid()}"

    def _get_new_comment_id(self) -> str:
        return f"{self._comment_id_prefix}-{self._get_new_uuid()}"

    def _get_new_place_id(self) -> str:
        return f"{self._place_id_prefix}-{self._get_new_uuid()}"

    def _get_new_media_id(self) -> str:
        return f"{self._media_id_prefix}-{self._get_new_uuid()}"

    def _choose_random_name(self, name_list: list[dict[str, Any]]):
        percentile = self._random.uniform(0.0, name_list[-1]["percentile"])

        for name in name_list:
            if name["percentile"] >= percentile:
                return name["value"]

    def _get_random_name(self, name_type: NameType, gender: Gender) -> str:
        match name_type:
            case NameType.FIRST:
                match gender:
                    case Gender.FEMALE:
                        return self._choose_random_name(self._female_names)
                    case Gender.MALE:
                        return self._choose_random_name(self._male_names)
                    case Gender.OTHER:
                        gender = self._random.choice((Gender.FEMALE, Gender.MALE))
                        return self._get_random_name(NameType.FIRST, gender)
                    case _:
                        raise RuntimeError()
            case NameType.LAST:
                return self._choose_random_name(self._last_names)
            case NameType.FULL:
                return f"{self._get_random_name(NameType.FIRST, gender)} {self._get_random_name(NameType.LAST, gender)}"
            case _:
                raise RuntimeError()

    def _get_random_gender(self) -> Gender:
        percentile = self._random.uniform(0.0, 100.0)

        if 0.0 <= percentile < 5.0:
            return Gender.OTHER
        if 5.0 <= percentile < 50.0:
            return Gender.MALE
        else:
            return Gender.FEMALE

    def _get_random_username(self, name: str) -> str:
        name_part = "".join(name.split())
        number_part = "".join(str(self._random.randint(0, 9)) for _ in range(self._username_suffix_digits))
        return name_part + number_part

    def _get_random_email(self, username: str) -> str:
        domain = self._random.choice([domain.value for domain in EmailDomain])
        return f"{username}@{domain}"

    def _get_random_relationship_status(self) -> RelationshipStatus:
        return self._random.choice([status for status in RelationshipStatus])

    def _get_random_timestamp(self, timestamp_format: TimestampFormat, start: str = None, end: str = None) -> str:
        if start is None:
            start = datetime(year=self._start_year, month=1, day=1)
        else:
            start = timestamp_format.parse_string(start)

        if end is None:
            end = datetime(year=self._end_year + 1, month=1, day=1)
        else:
            end = timestamp_format.parse_string(end)

        timestamp = start + (end - start) * self._random.random()
        return timestamp_format.to_string(timestamp)
