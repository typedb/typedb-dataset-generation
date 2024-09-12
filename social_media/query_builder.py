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

    def _get_random_timestamp(self, timestamp_format: TimestampFormat, start_year: int = None, end_year: int = None) -> str:
        if start_year is None:
            start_year = self._start_year

        if end_year is None:
            end_year = self._end_year

        year = self._random.randint(start_year, end_year)
        month = self._random.randint(1, 12)

        if month == 2:
            if year % 4:
                if year % 100:
                    if year % 400:
                        max_day = 29
                    else:
                        max_day = 28
                else:
                    max_day = 29
            else:
                max_day = 28
        elif month in (4, 6, 9, 11):
            max_day = 30
        else:
            max_day = 31

        day = self._random.randint(1, max_day)
        hour = self._random.randint(0, 23)
        minute = self._random.randint(0, 59)
        second = self._random.randint(0, 59)
        milliseconds = self._random.randint(0, 999)
        date = f"{str(year).zfill(4)}-{str(month).zfill(2)}-{str(day).zfill(2)}"
        time = f"{str(hour).zfill(2)}:{str(minute).zfill(2)}:{str(second).zfill(2)}"

        match timestamp_format:
            case TimestampFormat.DATE:
                return date
            case TimestampFormat.DATETIME:
                return f"{date}T{time}"
            case TimestampFormat.PRECISE_DATETIME:
                return f"{date}T{time}.{str(milliseconds).zfill(3)}"



