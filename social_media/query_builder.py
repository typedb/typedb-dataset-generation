from datetime import datetime
from random import Random
from typing import Any
from uuid import UUID
from warnings import warn
from yaml import safe_load

from social_media.enums import (
    NameType,
    Gender,
    EmailDomain,
    RelationshipStatus,
    TimestampFormat,
    PageVisibility,
    PostVisibility,
    PostType,
    PlaceType,
    OrganisationType,
    SocialRelationType,
)


class SocialRelation:
    def __init__(self, type: SocialRelationType, usernames: tuple[str, str]):
        self.type = type
        self.usernames = usernames


class QueryBuilder:
    _username_suffix_digits = 3
    _group_id_prefix = "grp"
    _post_id_prefix = "pst"
    _comment_id_prefix = "cmt"
    _place_id_prefix = "plc"
    _media_id_prefix = "med"
    _birth_range = ("1970-01-01", "1980-01-01")
    _relationship_range = ("2010-01-01", "2025-01-01")
    _start_year = 2020
    _end_year = 2024
    _username_warning_threshold = 10 ** _username_suffix_digits

    def __init__(self, seed=0):
        self._random = Random(seed)
        self._person_usernames: list[str] = list()
        self._organisation_usernames: list[str] = list()
        self._group_ids: list[str] = list()
        self._post_ids: list[str] = list()
        self._comment_ids: list[str] = list()
        self._place_ids: list[str] = list()
        self._social_relations: list[SocialRelation] = list()

        with open("resources/female_names.yml", "r") as file:
            self._female_names: list[dict[str, Any]] = safe_load(file)

        with open("resources/male_names.yml", "r") as file:
            self._male_names: list[dict[str, Any]] = safe_load(file)

        with open("resources/last_names.yml", "r") as file:
            self._last_names: list[dict[str, Any]] = safe_load(file)

    @property
    def _usernames(self) -> list[str]:
        return self._person_usernames + self._organisation_usernames

    def _get_social_relation_type(self, usernames: tuple[str, str]) -> SocialRelationType | None:
        for relation in self._social_relations:
            if usernames[0] in relation.usernames and usernames[1] in relation.usernames:
                return relation.type

        return None

    def _relationship_count(self, username: str) -> int:
        return len([relation for relation in self._social_relations if relation.type.is_relationship and username in relation.usernames])

    def _parent_count(self, username: str) -> int:
        return len([relation for relation in self._social_relations if relation.type is SocialRelationType.PARENTSHIP and relation.usernames[1] == username])

    def _get_new_uuid(self) -> str:
        return UUID(version=4, int=self._random.getrandbits(128)).hex

    def _get_new_group_id(self) -> str:
        group_id = f"{self._group_id_prefix}-{self._get_new_uuid()}"
        self._group_ids.append(group_id)
        return group_id

    def _get_new_post_id(self) -> str:
        post_id = f"{self._post_id_prefix}-{self._get_new_uuid()}"
        self._post_ids.append(post_id)
        return post_id

    def _get_new_comment_id(self) -> str:
        comment_id = f"{self._comment_id_prefix}-{self._get_new_uuid()}"
        self._comment_ids.append(comment_id)
        return comment_id

    def _get_new_place_id(self) -> str:
        place_id = f"{self._place_id_prefix}-{self._get_new_uuid()}"
        self._place_ids.append(place_id)
        return place_id

    def _get_random_place_id(self) -> str:
        return self._random.choice(self._place_ids)

    def _add_new_place_id(self, place_id) -> None:
        self._place_ids.append(place_id)

    def _get_new_media_id(self) -> str:
        media_id = f"{self._media_id_prefix}-{self._get_new_uuid()}"
        return media_id

    def _choose_random_name(self, name_list: list[dict[str, Any]]):
        percentile = self._random.uniform(0.0, name_list[-1]["percentile"])

        for name in name_list:
            if name["percentile"] >= percentile:
                return name["value"]

    def _get_new_name(self, name_type: NameType, gender: Gender) -> str:
        match name_type:
            case NameType.FIRST:
                match gender:
                    case Gender.FEMALE:
                        return self._choose_random_name(self._female_names)
                    case Gender.MALE:
                        return self._choose_random_name(self._male_names)
                    case Gender.OTHER:
                        gender = self._random.choice((Gender.FEMALE, Gender.MALE))
                        return self._get_new_name(NameType.FIRST, gender)
                    case _:
                        raise RuntimeError()
            case NameType.LAST:
                return self._choose_random_name(self._last_names)
            case NameType.FULL:
                return f"{self._get_new_name(NameType.FIRST, gender)} {self._get_new_name(NameType.LAST, gender)}"
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

    def _get_new_person_username(self, name: str) -> str:
        if len(self._person_usernames) >= self._username_warning_threshold:
            message = " ".join((
                f"The number of usernames generated has exceeded {self._username_warning_threshold}.",
                f"This has a small chance to deadlock the query builder if generation continues significantly.",
                f"Consider raising the username suffix digit count (class attribute) to prevent deadlock.",
            ))

            warn(message, RuntimeWarning)

        while True:
            name_part = "".join(name.split())
            number_part = "".join(str(self._random.randint(0, 9)) for _ in range(self._username_suffix_digits))
            username = name_part + number_part

            if username not in self._person_usernames:
                self._person_usernames.append(username)
                return username

    def _get_random_person_username(self) -> str:
        return self._random.choice(self._person_usernames)

    def _add_new_organisation_username(self, username: str) -> None:
        self._organisation_usernames.append(username)

    def _get_new_email(self, username: str) -> str:
        domain = self._random.choice([domain.value for domain in EmailDomain])
        return f"{username}@{domain}"

    def _get_random_social_relation_type(self) -> SocialRelationType:
        return self._random.choice([type for type in SocialRelationType])

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

    def person(
            self,
            bio: str,
            location_id: str,
            birth_location_id: str,
            languages: list[str] = ["English"],
            is_active: bool = True,
            is_visible: bool = True,
            can_publish: bool = True,
            page_visibility: PageVisibility = PageVisibility.PUBLIC,
            post_visibility: PageVisibility = PostVisibility.PUBLIC,
    ) -> str:
        gender = self._get_random_gender()
        name = self._get_new_name(NameType.FULL, gender)
        username = self._get_new_person_username(name)
        email = self._get_new_email(username)
        profile_picture = self._get_new_media_id()
        birth_date = self._get_random_timestamp(TimestampFormat.DATE, start=self._birth_range[0], end=self._birth_range[1])

        queries = "# person\n" + " ".join((
            f"""match""",
            f"""$place isa place;""",
            f"""$place has id "{location_id}";""",
            f"""$birth-place isa place;""",
            f"""$birth-place has id "{birth_location_id}";""",
            f"""insert""",
            f"""$person isa person;""",
            f"""$person has username "{username}";""",
            f"""$person has name "{name}";""",
            f"""$person has bio "{bio}";""",
            f"""$person has profile-picture "{profile_picture}";""",
            f"""$person has gender "{gender.value}";""",
            f"""$person has email "{email}";""",
            f"""$person has is-active "{str(is_active).lower()}";""",
            f"""$person has is-visible "{str(is_visible).lower()}";""",
            f"""$person has can-publish "{str(can_publish).lower()}";""",
            f"""$person has page-visibility "{page_visibility.value}";""",
            f"""$person has post-visibility "{post_visibility.value}";""",
            f"""$birth (born: $person) isa birth;""",
            f"""$birth has birth-date {birth_date};""",
            f"""$location (place: $place, located: $person) isa location;""",
            f"""$birth-location (place: $birth-place, located: $birth) isa location;""",
        ))

        for language in languages:
            queries += f""" $person has language "{language}";"""

        return queries

    def organisation(
            self,
            organisation_type: OrganisationType,
            name: str,
            bio: str,
            location_id: str,
            tags: list[str],
            is_active: bool = True,
            is_visible: bool = True,
            can_publish: bool = True,
    ) -> str:
        username = "".join(name.split())
        self._add_new_organisation_username(username)
        profile_picture = self._get_new_media_id()

        queries = "# organisation\n" + " ".join((
            f"""match""",
            f"""$place isa place;""",
            f"""$place has id "{location_id}";""",
            f"""insert""",
            f"""$organisation isa {organisation_type.value};""",
            f"""$organisation has username "{username}";""",
            f"""$organisation has name "{name}";""",
            f"""$organisation has bio "{bio}";""",
            f"""$organisation has profile-picture"{profile_picture}";""",
            f"""$person has is-active "{str(is_active).lower()}";""",
            f"""$person has is-visible "{str(is_visible).lower()}";""",
            f"""$person has can-publish "{str(can_publish).lower()}";""",
            f"""$location (place: $place, located: $organisation) isa location;""",
        ))

        for tag in tags:
            queries += f""" $organisation has tag "{tag}";"""

        return queries

    def group(
            self,
            name: str,
            bio: str,
            tags: list[str],
            is_active: bool = True,
            is_visible: bool = True,
            can_publish: bool = True,
            page_visibility: PageVisibility = PageVisibility.PUBLIC,
            post_visibility: PageVisibility = PostVisibility.PUBLIC,
    ) -> str:
        group_id = self._get_new_group_id()
        profile_picture = self._get_new_media_id()

        queries = "# group\n" + " ".join((
            f"""insert""",
            f"""$group isa group;""",
            f"""$group has group-id "{group_id}";""",
            f"""$group has name "{name}";""",
            f"""$group has bio "{bio}";""",
            f"""$group has profile-picture "{profile_picture}";""",
            f"""$group has is-active "{str(is_active).lower()}";""",
            f"""$group has is-visible "{str(is_visible).lower()}";""",
            f"""$group has can-publish "{str(can_publish).lower()}";""",
            f"""$group has page-visibility "{page_visibility.value}";""",
            f"""$group has post-visibility "{post_visibility.value}";""",
        ))

        for tag in tags:
            queries += f""" $group has tag "{tag}";"""

        return queries

    def _post(
            self,
            post_type: PostType,
            post_text: str,
            tags: list[str],
            creation_timestamp: str = None,
            language: str = "English",
            is_visible: bool = True,
            post_visibility: PostVisibility = PostVisibility.DEFAULT,
    ) -> str:
        post_id = self._get_new_post_id()

        if creation_timestamp is None:
            creation_timestamp = self._get_random_timestamp(TimestampFormat.PRECISE_DATETIME)

        queries = "# post\n" + " ".join((
            f"""insert""",
            f"""$post isa {post_type.value};""",
            f"""$post has post-id "{post_id}";""",
            f"""$post has post-text "{post_text}";""",
            f"""$post has creation-timestamp {creation_timestamp};""",
            f"""$post has language "{language}";""",
            f"""$post has is-visible "{str(is_visible).lower()}";""",
            f"""$post has post-visibility "{post_visibility}";""",
        ))

        for tag in tags:
            queries += f""" $post has tag {tag};"""

        return queries

    def text_post(
            self,
            post_text: str,
            tags: list[str],
            creation_timestamp: str = None,
            language: str = "English",
            is_visible: bool = True,
            post_visibility: PostVisibility = PostVisibility.DEFAULT,
    ) -> str:
        return self._post(
            PostType.TEXT,
            post_text,
            tags,
            creation_timestamp,
            language,
            is_visible,
            post_visibility,
        )

    def share_post(
            self,
            post_text: str,
            original_post_id: str,
            tags: list[str],
            creation_timestamp: str = None,
            language: str = "English",
            is_visible: bool = True,
            post_visibility: PostVisibility = PostVisibility.DEFAULT,
    ) -> str:
        queries = self._post(
            PostType.SHARE,
            post_text,
            tags,
            creation_timestamp,
            language,
            is_visible,
            post_visibility,
        )

        raise NotImplementedError()

    def image_post(
            self,
            post_text: str,
            tags: list[str],
            creation_timestamp: str = None,
            language: str = "English",
            is_visible: bool = True,
            post_visibility: PostVisibility = PostVisibility.DEFAULT,
    ) -> str:
        post_image = self._get_new_media_id()

        queries = self._post(
            PostType.IMAGE,
            post_text,
            tags,
            creation_timestamp,
            language,
            is_visible,
            post_visibility,
        )

        queries += f""" $post has post-image "{post_image}";"""
        return queries

    def video_post(
            self,
            post_text: str,
            tags: list[str],
            creation_timestamp: str = None,
            language: str = "English",
            is_visible: bool = True,
            post_visibility: PostVisibility = PostVisibility.DEFAULT,
    ) -> str:
        post_video = self._get_new_media_id()

        queries = self._post(
            PostType.VIDEO,
            post_text,
            tags,
            creation_timestamp,
            language,
            is_visible,
            post_visibility,
        )

        queries += f""" $post has post-video "{post_video}";"""
        return queries

    def live_video_post(
            self,
            post_text: str,
            tags: list[str],
            creation_timestamp: str = None,
            language: str = "English",
            is_visible: bool = True,
            post_visibility: PostVisibility = PostVisibility.DEFAULT,
    ) -> str:
        post_video = self._get_new_media_id()

        queries = self._post(
            PostType.LIVE,
            post_text,
            tags,
            creation_timestamp,
            language,
            is_visible,
            post_visibility,
        )

        queries += f""" $post has post-video "{post_video}";"""
        return queries

    def poll_post(
            self,
            post_text: str,
            tags: list[str],
            question: str,
            answers: list[str],
            creation_timestamp: str = None,
            language: str = "English",
            is_visible: bool = True,
            post_visibility: PostVisibility = PostVisibility.DEFAULT,
    ) -> str:
        queries = self._post(
            PostType.POLL,
            post_text,
            tags,
            creation_timestamp,
            language,
            is_visible,
            post_visibility,
        )

        queries += f""" $post has question "{question}";"""

        for answer in answers:
            queries += f""" $post has answer "{answer}";"""

        return queries

    def comment(
            self,
            parent_id: str,
            comment_text: str,
            tags: list[str],
            creation_timestamp: str = None,
            is_visible: bool = True,
    ) -> str:
        comment_id = self._get_new_comment_id()

        queries = "# comment\n" + " ".join((
            f"""insert""",
            f"""$comment isa comment;""",
            f"""$comment has comment-id "{comment_id}";""",
            f"""$comment has comment-text "{comment_text}";""",
            f"""$comment has creation-timestamp {creation_timestamp};""",
            f"""$comment has is-visible {str(is_visible).lower()};""",
        ))

        for tag in tags:
            queries += f""" $comment has tag {tag};"""

        raise NotImplementedError()

    def _place(
            self,
            place_type: PlaceType,
            name: str,
            place_id: str = None,
            parent_id: str = None,
    ):
        if place_id is None:
            place_id = self._get_new_place_id()
        else:
            self._add_new_place_id(place_id)

        queries = "# place\n"

        if parent_id is not None:
            queries += " ".join((
                f"""match""",
                f"""$parent isa place;""",
                f"""$parent has id "{parent_id}";""",
                f"""insert""",
                f"""({PlaceType.place_role}: $parent, {PlaceType.located_role}: $place) isa {PlaceType.location_type};""",
            ))
        else:
            queries += "insert"

        queries += " " + " ".join((
            f"""$place isa {place_type.value};""",
            f"""$place has place-id "{place_id}";""",
            f"""$place has name "{name}";""",
        ))

        return queries

    def region(
            self,
            name: str,
            place_id: str,
            parent_id: str = None,
    ):
        queries = self._place(
            place_type=PlaceType.REGION,
            name=name,
            place_id=place_id,
            parent_id=parent_id,
        )

        return queries

    def country(
            self,
            name: str,
            place_id: str,
            parent_id: str,
            languages: list[str],
    ):
        queries = self._place(
            place_type=PlaceType.COUNTRY,
            name=name,
            place_id=place_id,
            parent_id=parent_id,
        )

        for language in languages:
            queries += f""" $place has language "{language}";"""

        return queries

    def state(
            self,
            name: str,
            place_id: str,
            parent_id: str,
    ):
        queries = self._place(
            place_type=PlaceType.STATE,
            name=name,
            place_id=place_id,
            parent_id=parent_id,
        )

        return queries

    def city(
            self,
            name: str,
            place_id: str,
            parent_id: str,
    ):
        queries = self._place(
            place_type=PlaceType.CITY,
            name=name,
            place_id=place_id,
            parent_id=parent_id,
        )

        return queries

    def landmark(
            self,
            name: str,
            parent_id: str,
    ):
        queries = self._place(
            place_type=PlaceType.LANDMARK,
            name=name,
            parent_id=parent_id,
        )

        return queries

    def social_relation(
            self,
            usernames: tuple[str, str] = None,
            relation_type: SocialRelationType = None,
            location_id: str = None,
    ):
        if relation_type is None:
            relation_type = self._get_random_social_relation_type()

        if usernames is None:
            if len(self._social_relations) >= len(self._person_usernames) ** 2 - len(self._person_usernames):
                raise RuntimeError("User pool has been saturated with possible social relations.")

            while True:
                usernames = (self._get_random_person_username(), self._get_random_person_username())

                if usernames[0] != usernames[1] and self._get_social_relation_type(usernames) is None:
                    break

        if self._get_social_relation_type(usernames) is not None:
            message = f"Social relation between people already in a social relation is being forcibly generated."
            warn(message, RuntimeWarning)

        for username in usernames:
            if relation_type.is_relationship and self._relationship_count(username) >= 1:
                message = f"Relationship between partner(s) already in other relationships is being forcibly generated."
                warn(message, RuntimeWarning)

        if relation_type is SocialRelationType.PARENTSHIP and self._parent_count(usernames[1]) >= 2:
            message = f"Parentship for person already with two parents is being forcibly generated."
            warn(message, RuntimeWarning)

        if location_id is None:
            location_id = self._get_random_place_id()

        start_date = self._get_random_timestamp(TimestampFormat.DATE, start=self._relationship_range[0], end=self._relationship_range[1])

        match_clause = "# relationship\n" + " ".join((
            f"""match""",
            f"""$partner-0 isa person;""",
            f"""$partner-0 has id "{usernames[0]}";""",
            f"""$partner-1 isa person;""",
            f"""$partner-1 has id "{usernames[1]}";""",
        ))

        insert_clause = "# relationship\n" + " ".join((
            f"""insert""",
            f"""$social-relation ({relation_type.role_first}: $partner-0, {relation_type.role_second}: $partner-1) isa {relation_type.value};""",
        ))

        if relation_type.is_relationship:
            insert_clause += " " + " ".join((
                f"""$social-relation has {relation_type.relationship_date_type} {start_date};""",
                f"""$partner-0 has relationship-status "{relation_type.relationship_status.value}";"""
                f"""$partner-1 has relationship-status "{relation_type.relationship_status.value}";"""
            ))

        if relation_type.has_location:
            match_clause += f""" $place isa place; $place has id "{location_id}";"""
            insert_clause += f""" $location (place: $place, located: $relationship) isa location;"""

        queries = f"# relationship\n{match_clause} {insert_clause}"
        return queries

    def unknown_relationship_statuses(self) -> str:
        queries = ""

        for username in self._person_usernames:
            if self._relationship_count(username) == 0:
                relationship_status = self._get_random_relationship_status()

                queries += "# relationship status\n" + " ".join((
                    f"""match""",
                    f"""$person isa person;""",
                    f"""$person has id "{username}";""",
                    f"""insert""",
                    f"""$person has relationship-status "{relationship_status.value}";""",
                ))

        return queries
