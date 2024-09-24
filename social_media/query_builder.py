from collections.abc import Iterator
from dataclasses import dataclass
from itertools import product
from random import Random
from typing import Any, Self
from uuid import UUID
from warnings import warn
from yaml import safe_load
from enums import (
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
    PageType,
    InstituteType,
    GroupMemberRank,
)
from conversation import Conversation


@dataclass
class Page:
    type: PageType
    id: str
    name: str


@dataclass
class Place:
    type: PlaceType
    id: str
    name: str
    parent: Self = None


@dataclass
class SocialRelation:
    type: SocialRelationType
    persons: tuple[Page, Page]


@dataclass
class Education:
    institute: Page
    attendee: Page


@dataclass
class Employment:
    employer: Page
    employee: Page


@dataclass
class GroupMembership:
    group: Page
    member: Page
    rank: GroupMemberRank


class QueryBuilder:
    _username_suffix_digits = 3
    _group_id_prefix = "grp"
    _post_id_prefix = "pst"
    _comment_id_prefix = "cmt"
    _place_id_prefix = "plc"
    _media_id_prefix = "med"
    _birth_range = ("1980-01-01", "1985-01-01")
    _social_relation_range = ("2003-01-01", "2025-01-01")
    _education_range = ("2003-01-01", "2008-01-01")
    _employment_range = ("2008-01-01", "2025-01-01")
    _post_range = ("2020-01-01T00:00:00.000", "2025-01-01T00:00:00.000")
    _start_year = 2020
    _end_year = 2024
    _username_warning_threshold = 10 ** _username_suffix_digits

    def __init__(self, seed=0):
        self._random = Random(seed)
        self._pages: dict[str, Page] = dict()
        self._places: dict[str, Place] = dict()
        self._social_relations: list[SocialRelation] = list()
        self._educations: list[Education] = list()
        self._employments: list[Employment] = list()
        self._group_memberships: list[GroupMembership] = list()
        self._post_ids: list[str] = list()
        self._comment_ids: list[str] = list()

        with open("resources/female_names.yml", "r") as file:
            self._female_names: list[dict[str, Any]] = safe_load(file)

        with open("resources/male_names.yml", "r") as file:
            self._male_names: list[dict[str, Any]] = safe_load(file)

        with open("resources/last_names.yml", "r") as file:
            self._last_names: list[dict[str, Any]] = safe_load(file)

    @property
    def _persons(self) -> Iterator[Page]:
        return (page for page in self._pages.values() if page.type is PageType.PERSON)

    @property
    def _organisations(self) -> Iterator[Page]:
        return (page for page in self._pages.values() if page.type.is_organisation)

    @property
    def _institutes(self) -> Iterator[Page]:
        return (page for page in self._pages.values() if page.type.is_institute)

    @property
    def _groups(self) -> Iterator[Page]:
        return (page for page in self._pages.values() if page.type is PageType.GROUP)

    @property
    def _profiles(self) -> Iterator[Page]:
        return (page for page in self._pages.values() if page.type.is_profile)

    def _get_social_relation(self, persons: tuple[Page, Page]) -> SocialRelation | None:
        for relation in self._social_relations:
            if persons[0] in relation.persons and persons[1] in relation.persons:
                return relation

        return None

    def _get_education(self, person: Page) -> Education | None:
        for education in self._educations:
            if person is education.attendee:
                return education

        return None

    def _get_employment(self, person: Page) -> Employment | None:
        for employment in self._employments:
            if person is employment.employee:
                return employment

        return None

    def _get_members(self, group: Page) -> Iterator[Page]:
        for membership in self._group_memberships:
            if group is membership.group:
                yield membership.member

    def _social_relation_count(self, person: Page) -> int:
        return len([relation for relation in self._social_relations if person in relation.persons])

    def _relationship_count(self, person: Page) -> int:
        return len([relation for relation in self._social_relations if relation.type.is_relationship and person in relation.persons])

    def _parent_count(self, person: Page) -> int:
        return len([relation for relation in self._social_relations if relation.type is SocialRelationType.PARENTSHIP and relation.persons[1] == person])

    def _has_owner(self, group: Page) -> bool:
        for membership in self._group_memberships:
            if membership.group is group and membership.rank is GroupMemberRank.OWNER:
                return True

        return False

    def _generate_new_uuid(self) -> str:
        return UUID(version=4, int=self._random.getrandbits(128)).hex

    def _generate_new_group_id(self) -> str:
        return f"{self._group_id_prefix}-{self._generate_new_uuid()}"

    def _generate_new_post_id(self) -> str:
        return f"{self._post_id_prefix}-{self._generate_new_uuid()}"

    def _generate_new_comment_id(self) -> str:
        return f"{self._comment_id_prefix}-{self._generate_new_uuid()}"

    def _generate_new_place_id(self) -> str:
        return f"{self._place_id_prefix}-{self._generate_new_uuid()}"

    def _get_random_place(self, place_type: PlaceType = None) -> Place:
        if place_type is None:
            choices = list(self._places.values())
        else:
            choices = [place for place in self._places.values() if place.type is place_type]

        if len(choices) == 0:
            raise RuntimeError("No places of the desired type exist.")

        return self._random.choice(choices)

    def _get_random_organisation(self, organisation_type: OrganisationType = None) -> Page:
        if organisation_type is None:
            choices = list(self._organisations)
        else:
            choices = [organisation for organisation in self._organisations if organisation.type is organisation_type.page_type]

        if len(choices) == 0:
            raise RuntimeError("No organisations of the desired type exist.")

        return self._random.choice(choices)

    def _get_random_institute(self, institute_type: InstituteType = None) -> Page:
        if institute_type is None:
            choices = list(self._institutes)
        else:
            choices = [institute for institute in self._institutes if institute.type is institute_type.page_type]

        if len(choices) == 0:
            raise RuntimeError("No institutes of the desired type exist.")

        return self._random.choice(choices)

    def _generate_new_media_id(self) -> str:
        return f"{self._media_id_prefix}-{self._generate_new_uuid()}"

    def _choose_random_name(self, name_list: list[dict[str, Any]]):
        percentile = self._random.uniform(0.0, name_list[-1]["percentile"])

        for name in name_list:
            if name["percentile"] >= percentile:
                return name["value"]

    def _generate_new_name(self, name_type: NameType, gender: Gender) -> str:
        match name_type:
            case NameType.FIRST:
                match gender:
                    case Gender.FEMALE:
                        return self._choose_random_name(self._female_names)
                    case Gender.MALE:
                        return self._choose_random_name(self._male_names)
                    case Gender.OTHER:
                        gender = self._random.choice([Gender.FEMALE, Gender.MALE])
                        return self._generate_new_name(NameType.FIRST, gender)
                    case _:
                        raise RuntimeError()
            case NameType.LAST:
                return self._choose_random_name(self._last_names)
            case NameType.FULL:
                return f"{self._generate_new_name(NameType.FIRST, gender)} {self._generate_new_name(NameType.LAST, gender)}"
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

    def _generate_new_person_username(self, name: str) -> str:
        if len(list(self._persons)) >= self._username_warning_threshold:
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

            if username not in (person.id for person in self._persons):
                return username

    def _generate_new_email(self, username: str) -> str:
        domain = EmailDomain.choose(self._random)
        return f"{username}@{domain}"

    def _get_random_timestamp(self, format: TimestampFormat, range: tuple[str, str]) -> str:
        start = format.parse_string(range[0])
        end = format.parse_string(range[1])
        timestamp = start + (end - start) * self._random.random()
        return format.to_string(timestamp)

    def person(
            self,
            bio: str,
            location_id: str = None,
            birth_location_id: str = None,
            languages: list[str] = ["English"],
            is_active: bool = True,
            is_visible: bool = True,
            can_publish: bool = True,
            page_visibility: PageVisibility = PageVisibility.PUBLIC,
            post_visibility: PageVisibility = PostVisibility.PUBLIC,
    ) -> str:
        gender = self._get_random_gender()
        name = self._generate_new_name(NameType.FULL, gender)
        username = self._generate_new_person_username(name)
        email = self._generate_new_email(username)
        profile_picture = self._generate_new_media_id()
        birth_date = self._get_random_timestamp(TimestampFormat.DATE, self._birth_range)
        self._pages[username] = Page(PageType.PERSON, username, name)

        if location_id is None:
            location_id = self._get_random_place(PlaceType.CITY).id

        if birth_location_id is None:
            birth_location_id = self._get_random_place(PlaceType.CITY).id

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
            f"""$person has is-active {str(is_active).lower()};""",
            f"""$person has is-visible {str(is_visible).lower()};""",
            f"""$person has can-publish {str(can_publish).lower()};""",
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
            tags: list[str],
            location_id: str = None,
            is_active: bool = True,
            is_visible: bool = True,
            can_publish: bool = True,
    ) -> str:
        username = "".join(name.split())
        self._pages[username] = Page(organisation_type.page_type, username, name)
        profile_picture = self._generate_new_media_id()

        if location_id is None:
            location_id = self._get_random_place(place_type=PlaceType.CITY).id

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
            f"""$organisation has is-active {str(is_active).lower()};""",
            f"""$organisation has is-visible {str(is_visible).lower()};""",
            f"""$organisation has can-publish {str(can_publish).lower()};""",
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
            page_visibility: PageVisibility = PageVisibility.PUBLIC,
            post_visibility: PageVisibility = PostVisibility.PUBLIC,
    ) -> str:
        group_id = self._generate_new_group_id()
        profile_picture = self._generate_new_media_id()
        self._pages[group_id] = Page(PageType.GROUP, group_id, name)

        queries = "# group\n" + " ".join((
            f"""insert""",
            f"""$group isa group;""",
            f"""$group has group-id "{group_id}";""",
            f"""$group has name "{name}";""",
            f"""$group has bio "{bio}";""",
            f"""$group has profile-picture "{profile_picture}";""",
            f"""$group has is-active {str(is_active).lower()};""",
            f"""$group has is-visible {str(is_visible).lower()};""",
            f"""$group has page-visibility "{page_visibility.value}";""",
            f"""$group has post-visibility "{post_visibility.value}";""",
        ))

        for tag in tags:
            queries += f""" $group has tag "{tag}";"""

        return queries

    def _post(
            self,
            post_type: PostType,
            page_id: str,
            author_username: str,
            post_text: str,
            tags: list[str],
            post_id: str = None,
            creation_timestamp: str = None,
            location_id: str = None,
            language: str = "English",
            is_visible: bool = True,
            post_visibility: PostVisibility = PostVisibility.DEFAULT,
    ) -> str:
        if post_id is None:
            post_id = self._generate_new_post_id()

        self._post_ids.append(post_id)

        if creation_timestamp is None:
            creation_timestamp = self._get_random_timestamp(TimestampFormat.PRECISE_DATETIME, range=self._post_range)

        match_clause = " ".join((
            f"""match""",
            f"""$page isa page;""",
            f"""$page has id "{page_id}";""",
            f"""$profile isa profile;""",
            f"""$profile has id "{author_username}";""",
        ))

        insert_clause = " ".join((
            f"""insert""",
            f"""$post isa {post_type.value};""",
            f"""$post has post-id "{post_id}";""",
            f"""$post has post-text "{post_text}";""",
            f"""$post has creation-timestamp {creation_timestamp};""",
            f"""$post has language "{language}";""",
            f"""$post has is-visible {str(is_visible).lower()};""",
            f"""$post has post-visibility "{post_visibility.value}";""",
            f"""$posting (page: $page, post: $post, author: $profile) isa posting;""",
        ))

        for tag in tags:
            insert_clause += f""" $post has tag "{tag}";"""

        if location_id is not None:
            match_clause += f""" $place isa place; $place has id "{location_id}";"""
            insert_clause += f""" $location (place: $place, located: $post) isa location;"""

        queries = f"# post\n{match_clause} {insert_clause}"

        return queries

    def text_post(
            self,
            page_id: str,
            author_username: str,
            post_text: str,
            tags: list[str],
            post_id: str = None,
            creation_timestamp: str = None,
            location_id: str = None,
            language: str = "English",
            is_visible: bool = True,
            post_visibility: PostVisibility = PostVisibility.DEFAULT,
    ) -> str:
        return self._post(
            PostType.TEXT,
            page_id=page_id,
            author_username=author_username,
            post_text=post_text,
            tags=tags,
            post_id=post_id,
            creation_timestamp=creation_timestamp,
            location_id=location_id,
            language=language,
            is_visible=is_visible,
            post_visibility=post_visibility,
        )

    def share_post(
            self,
            page_id: str,
            author_username: str,
            post_text: str,
            original_post_id: str,
            tags: list[str],
            post_id: str = None,
            creation_timestamp: str = None,
            location_id: str = None,
            language: str = "English",
            is_visible: bool = True,
            post_visibility: PostVisibility = PostVisibility.DEFAULT,
    ) -> str:
        queries = self._post(
            post_type=PostType.SHARE,
            page_id=page_id,
            author_username=author_username,
            post_text=post_text,
            tags=tags,
            post_id=post_id,
            creation_timestamp=creation_timestamp,
            location_id=location_id,
            language=language,
            is_visible=is_visible,
            post_visibility=post_visibility,
        )

        raise NotImplementedError()

    def image_post(
            self,
            page_id: str,
            author_username: str,
            post_text: str,
            tags: list[str],
            post_id: str = None,
            creation_timestamp: str = None,
            location_id: str = None,
            language: str = "English",
            is_visible: bool = True,
            post_visibility: PostVisibility = PostVisibility.DEFAULT,
    ) -> str:
        post_image = self._generate_new_media_id()

        queries = self._post(
            PostType.IMAGE,
            page_id=page_id,
            author_username=author_username,
            post_text=post_text,
            tags=tags,
            post_id=post_id,
            creation_timestamp=creation_timestamp,
            location_id=location_id,
            language=language,
            is_visible=is_visible,
            post_visibility=post_visibility,
        )

        queries += f""" $post has post-image "{post_image}";"""
        return queries

    def video_post(
            self,
            page_id: str,
            author_username: str,
            post_text: str,
            tags: list[str],
            post_id: str = None,
            creation_timestamp: str = None,
            location_id: str = None,
            language: str = "English",
            is_visible: bool = True,
            post_visibility: PostVisibility = PostVisibility.DEFAULT,
    ) -> str:
        post_video = self._generate_new_media_id()

        queries = self._post(
            PostType.VIDEO,
            page_id=page_id,
            author_username=author_username,
            post_text=post_text,
            tags=tags,
            post_id=post_id,
            creation_timestamp=creation_timestamp,
            location_id=location_id,
            language=language,
            is_visible=is_visible,
            post_visibility=post_visibility,
        )

        queries += f""" $post has post-video "{post_video}";"""
        return queries

    def live_video_post(
            self,
            page_id: str,
            author_username: str,
            post_text: str,
            tags: list[str],
            post_id: str = None,
            creation_timestamp: str = None,
            location_id: str = None,
            language: str = "English",
            is_visible: bool = True,
            post_visibility: PostVisibility = PostVisibility.DEFAULT,
    ) -> str:
        post_video = self._generate_new_media_id()

        queries = self._post(
            PostType.LIVE,
            page_id=page_id,
            author_username=author_username,
            post_text=post_text,
            tags=tags,
            post_id=post_id,
            creation_timestamp=creation_timestamp,
            location_id=location_id,
            language=language,
            is_visible=is_visible,
            post_visibility=post_visibility,
        )

        queries += f""" $post has post-video "{post_video}";"""
        return queries

    def poll_post(
            self,
            page_id: str,
            author_username: str,
            post_text: str,
            tags: list[str],
            question: str,
            answers: list[str],
            post_id: str = None,
            creation_timestamp: str = None,
            location_id: str = None,
            language: str = "English",
            is_visible: bool = True,
            post_visibility: PostVisibility = PostVisibility.DEFAULT,
    ) -> str:
        queries = self._post(
            PostType.POLL,
            page_id=page_id,
            author_username=author_username,
            post_text=post_text,
            tags=tags,
            post_id=post_id,
            creation_timestamp=creation_timestamp,
            location_id=location_id,
            language=language,
            is_visible=is_visible,
            post_visibility=post_visibility,
        )

        queries += f""" $post has question "{question}";"""

        for answer in answers:
            queries += f""" $post has answer "{answer}";"""

        return queries

    def comment(
            self,
            parent_id: str,
            author_username: str,
            comment_text: str,
            tags: list[str],
            comment_id: str = None,
            creation_timestamp: str = None,
            is_visible: bool = True,
    ) -> str:
        if comment_id is None:
            comment_id = self._generate_new_comment_id()

        self._comment_ids.append(comment_id)

        queries = "# comment\n" + " ".join((
            f"""match""",
            f"""$parent isa content;""",
            f"""$parent has id "{parent_id}";""",
            f"""$profile isa profile;""",
            f"""$profile has id "{author_username}";""",
            f"""insert""",
            f"""$comment isa comment;""",
            f"""$comment has comment-id "{comment_id}";""",
            f"""$comment has comment-text "{comment_text}";""",
            f"""$comment has creation-timestamp {creation_timestamp};""",
            f"""$comment has is-visible {str(is_visible).lower()};""",
            f"""$commenting (parent: $parent, comment: $comment, author: $profile) isa commenting;""",
        ))

        for tag in tags:
            queries += f""" $comment has tag "{tag}";"""

        return queries

    def conversation(
            self,
            conversation: Conversation,
            posting_type: str,
            page_name: str = None,
            location_name: str = None
    ) -> list[str]:
        if posting_type not in ["person-self", "person-group"]:
            raise NotImplementedError()

        if len(conversation.usertags - conversation.participants) != 0:
            raise RuntimeError("Conversation has non-participants tagged.")

        commenter_count = len(conversation.commenters)
        participant_count = len(conversation.participants)

        match posting_type:
            case "person-self":
                choices = [person for person in self._persons if self._social_relation_count(person) >= commenter_count]

                if len(choices) == 0:
                    raise RuntimeError("No users have sufficient social relations to build conversation.")

                page_id = self._random.choice(choices).id
                post_author = self._pages[page_id]
                choices = [person for person in self._persons if self._get_social_relation((post_author, person)) is not None]
                commenters = self._random.sample(choices, commenter_count)
            case "person-group":
                if page_name is None:
                    choices = [group for group in self._groups if len([self._get_members(group)]) >= participant_count]

                    if len(choices) == 0:
                        raise RuntimeError("No groups has sufficient members to build conversation.")

                    page_id = self._random.choice(choices).id
                else:
                    pages = [page for page in self._pages.values() if page.name == page_name]

                    if len(pages) == 0:
                        raise RuntimeError("No page with the specified name exists.")
                    elif len(pages) == 1:
                        page_id = pages[0].id
                    else:
                        raise RuntimeError("Multiple pages with the specified name exist.")

                choices = [person for person in self._persons if person in self._get_members(self._pages[page_id])]
                participants = self._random.sample(choices, participant_count)
                post_author = participants.pop()
                commenters = participants
            case _:
                raise RuntimeError()

        if location_name is None:
            location_id = None
        else:
            places = [place for place in self._places.values() if place.name == location_name]

            if len(places) == 0:
                raise RuntimeError("No place with the specified name exists.")
            elif len(places) == 1:
                location_id = places[0].id
            else:
                raise RuntimeError("Multiple places with the specified name exist.")

        usertag_mapping: dict[str, str] = {
            local_usertag: f"@{commenter.id}"
            for local_usertag, commenter in zip(conversation.commenters, commenters)
        }

        usertag_mapping[conversation.root_author] = f"@{post_author.id}"
        content_id_mapping: dict[str, str] = dict()

        for node in conversation.nodes:
            match node.content_type:
                case PostType.TEXT:
                    content_id = self._generate_new_post_id()
                case PostType.SHARE:
                    content_id = self._generate_new_post_id()
                case PostType.IMAGE:
                    content_id = self._generate_new_post_id()
                case PostType.VIDEO:
                    content_id = self._generate_new_post_id()
                case PostType.LIVE:
                    content_id = self._generate_new_post_id()
                case PostType.POLL:
                    content_id = self._generate_new_post_id()
                case "comment":
                    content_id = self._generate_new_comment_id()
                case _:
                    raise RuntimeError()

            content_id_mapping[node.local_id] = content_id

        queries: list[str] = list()

        for node in conversation.nodes:
            match node.content_type:
                case PostType.TEXT:
                    queries.append(self.text_post(
                        post_id=content_id_mapping[node.local_id],
                        page_id=page_id,
                        author_username=node.author_global_usertag(usertag_mapping).lstrip("@"),
                        creation_timestamp=node.timestamp,
                        location_id=location_id,
                        post_text=node.globalised_body(usertag_mapping),
                        tags=list(node.globalised_tags(usertag_mapping)),
                    ))
                case PostType.SHARE:
                    raise NotImplementedError()
                case PostType.IMAGE:
                    queries.append(self.image_post(
                        post_id=content_id_mapping[node.local_id],
                        page_id=page_id,
                        author_username=node.author_global_usertag(usertag_mapping).lstrip("@"),
                        creation_timestamp=node.timestamp,
                        location_id=location_id,
                        post_text=node.globalised_body(usertag_mapping),
                        tags=list(node.globalised_tags(usertag_mapping)),
                    ))
                case PostType.VIDEO:
                    queries.append(self.video_post(
                        post_id=content_id_mapping[node.local_id],
                        page_id=page_id,
                        author_username=node.author_global_usertag(usertag_mapping).lstrip("@"),
                        creation_timestamp=node.timestamp,
                        location_id=location_id,
                        post_text=node.globalised_body(usertag_mapping),
                        tags=list(node.globalised_tags(usertag_mapping)),
                    ))
                case PostType.LIVE:
                    queries.append(self.live_video_post(
                        post_id=content_id_mapping[node.local_id],
                        page_id=page_id,
                        author_username=node.author_global_usertag(usertag_mapping).lstrip("@"),
                        creation_timestamp=node.timestamp,
                        location_id=location_id,
                        post_text=node.globalised_body(usertag_mapping),
                        tags=list(node.globalised_tags(usertag_mapping)),
                    ))
                case PostType.POLL:
                    queries.append(self.poll_post(
                        post_id=content_id_mapping[node.local_id],
                        page_id=page_id,
                        author_username=node.author_global_usertag(usertag_mapping).lstrip("@"),
                        creation_timestamp=node.timestamp,
                        location_id=location_id,
                        post_text=node.globalised_body(usertag_mapping),
                        question=node.question,
                        answers=node.answers,
                        tags=list(node.globalised_tags(usertag_mapping)),
                    ))
                case "comment":
                    queries.append(self.comment(
                        comment_id=content_id_mapping[node.local_id],
                        parent_id=content_id_mapping[node.parent_local_id],
                        author_username=node.author_global_usertag(usertag_mapping).lstrip("@"),
                        creation_timestamp=node.timestamp,
                        comment_text=node.globalised_body(usertag_mapping),
                        tags=list(node.globalised_tags(usertag_mapping)),
                    ))
                case _:
                    raise RuntimeError()

        return queries

    def _place(
            self,
            place_type: PlaceType,
            name: str,
            place_id: str = None,
            parent_id: str = None,
    ):
        if place_id is None:
            place_id = self._generate_new_place_id()

        if parent_id is None:
            parent = None
        else:
            parent = self._places[parent_id]

        self._places[place_id] = Place(place_type, place_id, name, parent)
        queries = "# place\n"

        if parent_id is not None:
            queries += " ".join((
                f"""match""",
                f"""$parent isa place;""",
                f"""$parent has id "{parent_id}";""",
                f"""insert""",
                f"""$location ({place_type.place_role}: $parent, {place_type.located_role}: $place) isa {place_type.location_type};""",
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
            parent_id: str = None,
    ):
        if parent_id is None:
            parent_id = self._get_random_place(PlaceType.CITY).id

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
        if usernames is None:
            choices: list[tuple[Page, Page]] = list(
                persons for persons in product(self._persons, self._persons)
                if persons[0] != persons[1] and self._get_social_relation(persons) is None
            )

            if len(choices) == 0:
                raise RuntimeError("User pool has been saturated with plausible social relations.")

            persons = self._random.choice(choices)
        else:
            persons = self._pages[usernames[0]], self._pages[usernames[1]]

        if relation_type is None:
            choices: list[SocialRelationType] = [SocialRelationType.FRIENDSHIP, SocialRelationType.FAMILY, SocialRelationType.SIBLINGSHIP]

            if self._parent_count(persons[1]) < 2:
                choices += [SocialRelationType.PARENTSHIP]

            if all(self._relationship_count(person) == 0 for person in persons):
                choices += [SocialRelationType.RELATIONSHIP, SocialRelationType.ENGAGEMENT, SocialRelationType.MARRIAGE]

            relation_type = SocialRelationType.choose(self._random, choices)

        if self._get_social_relation(persons) is not None:
            message = f"Social relation between people already in a social relation is being forcibly generated."
            warn(message, RuntimeWarning)

        if relation_type.is_relationship and any(self._relationship_count(person) >= 1 for person in persons):
            message = f"Relationship between partner(s) already in other relationships is being forcibly generated."
            warn(message, RuntimeWarning)

        if relation_type is SocialRelationType.PARENTSHIP and self._parent_count(persons[1]) >= 2:
            message = f"Parentship for person already with two parents is being forcibly generated."
            warn(message, RuntimeWarning)

        if location_id is None:
            location_id = self._get_random_place(PlaceType.CITY).id

        start_date = self._get_random_timestamp(TimestampFormat.DATE, self._social_relation_range)
        self._social_relations.append(SocialRelation(relation_type, persons))

        match_clause = " ".join((
            f"""match""",
            f"""$partner-0 isa person;""",
            f"""$partner-0 has id "{persons[0].id}";""",
            f"""$partner-1 isa person;""",
            f"""$partner-1 has id "{persons[1].id}";""",
        ))

        insert_clause = " ".join((
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
            insert_clause += f""" $location (place: $place, located: $social-relation) isa location;"""

        queries = f"# social relation\n{match_clause} {insert_clause}"
        return queries

    def education(
            self,
            person_username: str = None,
            institute_username: str = None,
            institute_type: InstituteType = None,
            date_range: tuple[str, str | None] = None,
            description: str = None,
    ) -> str:
        if person_username is None:
            choices = list(person for person in self._persons if self._get_education(person) is None)

            if len(choices) == 0:
                raise RuntimeError("User pool has been saturated with plausible educations.")

            person = self._random.choice(choices)
        else:
            person = self._pages[person_username]

        if institute_username is None:
            institute = self._get_random_institute(institute_type)
        else:
            institute = self._pages[institute_username]

        if date_range is None:
            start_date = self._get_random_timestamp(TimestampFormat.DATE, self._education_range)
            end_date = self._get_random_timestamp(TimestampFormat.DATE, range=(start_date, self._education_range[1]))
        else:
            start_date, end_date = date_range

        self._educations.append(Education(institute, person))

        queries = "# education\n" + " ".join((
            f"""match""",
            f"""$person isa person;""",
            f"""$person has id "{person.id}";""",
            f"""$institute isa educational-institute;""",
            f"""$institute has id "{institute.id}";""",
            f"""insert""",
            f"""$education (institute: $institute, attendee: $person) isa education;""",
            f"""$education has start-date {start_date};""",
        ))

        if end_date is not None:
            queries += f""" $education has end-date {end_date};"""

        if description is not None:
            queries += f""" $education has description {description};"""

        return queries

    def employment(
            self,
            person_username: str = None,
            organisation_username: str = None,
            organisation_type: OrganisationType = None,
            date_range: tuple[str, str | None] = None,
            description: str = None,
    ) -> str:
        if person_username is None:
            choices = list(person for person in self._persons if self._get_employment(person) is None)

            if len(choices) == 0:
                raise RuntimeError("User pool has been saturated with plausible employments.")

            person = self._random.choice(choices)
        else:
            person = self._pages[person_username]

        if organisation_username is None:
            organisation = self._get_random_organisation(organisation_type)
        else:
            organisation = self._pages[organisation_username]

        if date_range is None:
            start_date = self._get_random_timestamp(TimestampFormat.DATE, self._employment_range)
            end_date = None
        else:
            start_date, end_date = date_range

        self._employments.append(Employment(organisation, person))

        queries = "# employment\n" + " ".join((
            f"""match""",
            f"""$person isa person;""",
            f"""$person has id "{person.id}";""",
            f"""$organisation isa organisation;""",
            f"""$organisation has id "{organisation.id}";""",
            f"""insert""",
            f"""$employment (employer: $organisation, employee: $person) isa employment;""",
            f"""$employment has start-date {start_date};""",
        ))

        if end_date is not None:
            queries += f""" $employment has end-date {end_date};"""

        if description is not None:
            queries += f""" $employment has description {description};"""

        return queries

    def group_membership(
            self,
            username: str = None,
            group_id: str = None,
            timestamp_range: tuple[str, str | None] = None,
            rank: GroupMemberRank = None,
            badges: list[str] = [],
    ) -> str:
        if group_id is None:
            group = self._random.choice(list(group for group in self._groups))
        else:
            group = self._pages[group_id]

        if username is None:
            choices = list(profile for profile in self._profiles if profile not in self._get_members(group))

            if len(choices) == 0:
                raise RuntimeError("Group is saturated with members.")

            profile = self._random.choice(choices)
        else:
            profile = self._pages[username]

        if timestamp_range is None:
            start_timestamp = self._get_random_timestamp(TimestampFormat.PRECISE_DATETIME, self._post_range)
            end_timestamp = None
        else:
            start_timestamp, end_timestamp = timestamp_range

        if rank is None:
            if not self._has_owner(group):
                rank = GroupMemberRank.OWNER
            else:
                rank = GroupMemberRank.choose(self._random)

        self._group_memberships.append(GroupMembership(group, profile, rank))

        queries = "# group membership\n" + " ".join((
            f"""match""",
            f"""$profile isa profile;""",
            f"""$profile has id "{profile.id}";""",
            f"""$group isa group;""",
            f"""$group has id "{group.id}";""",
            f"""insert""",
            f"""$membership (group: $group, member: $profile) isa group-membership;""",
            f"""$membership has start-timestamp {start_timestamp};""",
            f"""$membership has rank "{rank.value}";""",
        ))

        if end_timestamp is not None:
            queries += f""" $membership has end-timestamp {end_timestamp};"""

        for badge in badges:
            queries += f""" $membership has badge "{badge}";"""

        return queries

    def unset_relationship_statuses(self) -> str:
        queries = ""

        for person in self._persons:
            if self._relationship_count(person) == 0:
                relationship_status = RelationshipStatus.choose(self._random)

                queries += "# relationship status\n" + " ".join((
                    f"""match""",
                    f"""$person isa person;""",
                    f"""$person has id "{person.id}";""",
                    f"""insert""",
                    f"""$person has relationship-status "{relationship_status.value}";""",
                ))

        return queries
