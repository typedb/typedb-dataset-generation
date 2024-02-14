from enum import Enum
from random import Random


class BookType(Enum):
    PAPERBACK = "paperback"
    HARDBACK = "hardback"
    EBOOK = "ebook"


class ParentPlaceType(Enum):
    STATE = "state"
    COUNTRY = "country"


class ContributorRole(Enum):
    AUTHOR = "author"
    EDITOR = "editor"
    ILLUSTRATOR = "illustrator"
    CONTRIBUTOR = "contributor"

    def relation_type(self) -> str:
        if self is ContributorRole.AUTHOR:
            return "authoring"
        elif self is ContributorRole.EDITOR:
            return "editing"
        elif self is ContributorRole.ILLUSTRATOR:
            return "illustrating"
        elif self is ContributorRole.CONTRIBUTOR:
            return "contribution"


class OrderStatus(Enum):
    PAID = "paid"
    DISPATCHED = "dispatched"
    DELIVERED = "delivered"
    RETURNED = "returned"
    CANCELED = "canceled"


class QueryBuilder:
    _user_id_prefix = "U"
    _promotion_id_prefix = "P"
    _order_id_prefix = "O"
    _id_digits = 4

    def __init__(self):
        self._promotion_count = 0
        self._user_count = 0
        self._order_count = 0
        self._random = Random(0)

    def get_new_promotion_id(self) -> str:
        assert self._promotion_count < 10 ** self._id_digits - 1
        self._promotion_count += 1
        return self._promotion_id_prefix + str(self._promotion_count).zfill(self._id_digits)

    def get_random_promotion_id(self) -> str:
        assert self._promotion_count > 0
        promotion_number = self._random.randint(1, self._promotion_count)
        return self._promotion_id_prefix + str(promotion_number).zfill(self._id_digits)

    def get_new_user_id(self) -> str:
        assert self._user_count < 10 ** self._id_digits - 1
        self._user_count += 1
        return self._user_id_prefix + str(self._user_count).zfill(self._id_digits)

    def get_random_user_id(self) -> str:
        assert self._user_count > 0
        user_number = self._random.randint(1, self._user_count)
        return self._user_id_prefix + str(user_number).zfill(self._id_digits)

    def get_new_order_id(self) -> str:
        assert self._order_count < 10 ** self._id_digits - 1
        self._order_count += 1
        return self._order_id_prefix + str(self._order_count).zfill(self._id_digits)

    def get_random_order_id(self) -> str:
        assert self._order_count > 0
        order_number = self._random.randint(1, self._order_count)
        return self._order_id_prefix + str(order_number).zfill(self._id_digits)

    def country(self, name: str) -> str:
        query = " ".join((
            f"insert",
            f"$country isa country;",
            f"$country has name '{name}';",
        ))

        return query

    def state(self, name: str, country_name: str) -> str:
        query = " ".join((
            f"match",
            f"$country isa country;",
            f"$country has name '{country_name}';",
            f"insert",
            f"$state isa state;",
            f"$state has name '{name}';",
            f"(location: $country, located: $state) isa locating;",
        ))

        return query

    def city(self, name: str, parent_type: ParentPlaceType, parent_name: str) -> str:
        query = " ".join((
            f"match",
            f"${parent_type} isa {parent_type};",
            f"${parent_type} has name '{parent_name}';",
            f"insert",
            f"$city isa city;",
            f"$city has name '{name}';",
            f"(location: ${parent_type}, located: $city) isa locating;",
        ))

        return query

    def _book(
            self,
            book_type: BookType,
            isbn_13: str,
            title: str,
            page_count: int,
            price: str,
            stock: int,
            contributors: list[tuple[str, ContributorRole]],
            publisher_name: str,
            publication_year: int,
            publication_city: str,
            isbn_10: str,
    ) -> str:
        query = " ".join((
            f"insert",
            f"$book isa {book_type.value};",
            f"$book has isbn-13 '{isbn_13}';",
            f"$book has title '{title}';",
            f"$book has page-count {page_count};",
            f"$book has price {price};",
            f"$book has stock {stock};",
            f"$book has isbn-10 '{isbn_10}';",
        ))

        for contributor in contributors:
            contributor_name = contributor[0]
            contributor_role = contributor[1]

            query += " " + " ".join((
                f"match",
                f"$contributor-type type contributor;",
                f"not {{",
                f"$contributor isa $contributor-type;",
                f"$contributor has name '{contributor_name}';",
                f"}};",
                f"insert",
                f"$contributor isa $contributor-type;",
                f"$contributor has name '{contributor_name}';",
                f"match",
                f"$book isa {book_type.value};",
                f"$book has isbn-13 '{isbn_13}';",
                f"$contributor isa contributor;",
                f"$contributor has name '{contributor_name}';",
                f"insert",
                f"(work: $book, {contributor_role.value}: $contributor) isa {contributor_role.relation_type()};",
            ))

        query += " " + " ".join((
            f"match",
            f"$publisher-type type publisher;",
            f"not {{",
            f"$publisher isa $publisher-type;",
            f"$publisher has name '{publisher_name}';",
            f"}};",
            f"insert",
            f"$publisher isa $publisher-type;",
            f"$publisher has name '{publisher_name}';",
            f"match",
            f"$book isa {book_type.value};",
            f"$book has isbn-13 '{isbn_13}';",
            f"$publisher isa publisher;",
            f"$publisher has name '{publisher_name}';",
            f"$city isa city;",
            f"$city has name '{publication_city}';",
            f"insert",
            f"$publication isa publication;",
            f"$publication has year {publication_year};",
            f"(published: $book, publisher: $publisher, publication: $publication) isa publishing;",
            f"(location: $city, located: $publication) isa locating;",
        ))

        return query

    def paperback(
            self,
            isbn_13: str,
            title: str,
            page_count: int,
            price: str,
            stock: int,
            contributors: list[tuple[str, ContributorRole]],
            publisher_name: str,
            publication_year: int,
            publication_city: str,
            isbn_10: str = None,
    ) -> str:
        return self._book(
            BookType.PAPERBACK,
            isbn_13,
            title,
            page_count,
            price,
            stock,
            contributors,
            publisher_name,
            publication_year,
            publication_city,
            isbn_10,
        )

    def hardback(
            self,
            isbn_13: str,
            title: str,
            page_count: int,
            price: str,
            stock: int,
            contributors: list[tuple[str, ContributorRole]],
            publisher_name: str,
            publication_year: int,
            publication_city: str,
            isbn_10: str = None,
    ) -> str:
        return self._book(
            BookType.HARDBACK,
            isbn_13,
            title,
            page_count,
            price,
            stock,
            contributors,
            publisher_name,
            publication_year,
            publication_city,
            isbn_10,
        )

    def ebook(
            self,
            isbn_13: str,
            title: str,
            page_count: int,
            price: str,
            stock: int,
            contributors: list[tuple[str, ContributorRole]],
            publisher_name: str,
            publication_year: int,
            publication_city: str,
            isbn_10: str = None,
    ) -> str:
        return self._book(
            BookType.EBOOK,
            isbn_13,
            title,
            page_count,
            price,
            stock,
            contributors,
            publisher_name,
            publication_year,
            publication_city,
            isbn_10,
        )

    def promotion(self, start_timestamp: str, end_timestamp: str, discount: str, book_isbn_13s: list[str]) -> str:
        promotion_id = self.get_new_promotion_id()

        query = " ".join((
            f"insert",
            f"$promotion isa promotion;",
            f"$promotion has id '{promotion_id}';",
            f"$promotion has start-timestamp {start_timestamp};",
            f"$promotion has end-timestamp {end_timestamp};",
            f"$promotion has discount {discount};",
        ))

        for isbn_13 in book_isbn_13s:
            query += " " + " ".join((
                f"match",
                f"$book isa book;",
                f"$book has isbn-13 '{isbn_13}';",
                f"$promotion isa promotion;",
                f"$promotion has id '{promotion_id}';",
                f"insert",
                f"(promotion: $promotion, included: $book) isa promotion-inclusion;",
            ))

        return query

    def user(self, name: str, birth_date: str, city_name) -> str:
        user_id = self.get_new_user_id()

        query = " ".join((
            f"match",
            f"$city isa city;",
            f"$city has name '{city_name}';",
            f"insert",
            f"$user isa user;",
            f"$user has id '{user_id}';",
            f"$user has name '{name}';",
            f"$user has birth-date {birth_date};",
            f"(location: $city, located: $user) isa locating;",
        ))

        return query

    def order(
            self,
            status: OrderStatus,
            execution_timestamp: str,
            address_street: str,
            city_name: str,
            courier_name: str,
            books: list[tuple[str, int]],
            user_id: str = None,
    ) -> str:
        order_id = self.get_new_order_id()

        if user_id is None:
            user_id = self.get_random_user_id()

        query = " ".join((
            f"match",
            f"$courier-type type courier;",
            f"not {{",
            f"$courier isa $courier-type;",
            f"$courier has name '{courier_name}';",
            f"}};",
            f"insert",
            f"$courier isa $courier-type;",
            f"$courier has name '{courier_name}';",
            f"match",
            f"$city isa city;",
            f"$city has name '{city_name}';",
            f"not {{",
            f"$address isa address;",
            f"$address has street '{address_street}';",
            f"(location: $city, located: $address) isa locating;",
            f"}};",
            f"insert",
            f"$address isa address;",
            f"$address has street '{address_street}';",
            f"(location: $city, located: $address) isa locating;",
            f"match",
            f"$user isa user;",
            f"$user has id '{user_id}';",
            f"$courier isa courier;",
            f"$courier has name '{courier_name}';",
            f"$city isa city;",
            f"$city has name '{city_name}';",
            f"$address isa address;",
            f"$address has street '{address_street}';",
            f"(location: $city, located: $address) isa locating;",
            f"insert",
            f"$order isa order;",
            f"$order has order-id '{order_id}';",
            f"$order has status '{status.value}';",
            f"$execution (action: $order, executor: $user) isa action-execution;",
            f"$execution has timestamp {execution_timestamp};",
            f"(delivered: $order, deliverer: $courier, destination: $address) isa delivery;",
        ))

        for book in books:
            book_isbn_13 = book[0]
            book_quantity = book[1]

            query += " " + " ".join((
                f"match",
                f"$order isa order;",
                f"$order has id '{order_id}';",
                f"$book isa book;",
                f"$book has isbn-13 '{book_isbn_13}';",
                f"insert",
                f"$line (order: $order, item: $book) isa order-line;",
                f"$line has quantity {book_quantity};",
            ))

        return query

    def review(self, score: int, execution_timestamp: str, book_isbn_13: str, user_id: str = None) -> str:
        if user_id is None:
            user_id = self.get_random_user_id()

        query = " ".join((
            f"match",
            f"$book isa book;",
            f"$book has isbn-13 '{book_isbn_13}';",
            f"$user isa user;",
            f"$user has id '{user_id}';",
            f"insert",
            f"$review isa review;",
            f"$review has score {score};",
            f"(review: $review, rated: $book) isa rating;",
            f"$execution (action: $review, executor: $user) isa action-execution;",
            f"$execution has timestamp {execution_timestamp};",
        ))

        return query

    def login(self, success: bool, execution_timestamp: str, user_id: str = None) -> str:
        if user_id is None:
            user_id = self.get_random_user_id()

        query = " ".join((
            f"match",
            f"$user isa user;",
            f"$user has id '{user_id}';",
            f"insert",
            f"$login isa login;",
            f"$login has success {str(success).lower()};",
            f"$execution (action: $login, executor: $user) isa action-execution;",
            f"$execution has timestamp {execution_timestamp};",
        ))

        return query
