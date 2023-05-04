from typing import Any, List, Union, Optional

from schemas.pydantic.BookSchema import Book
from datastore.database import DB, Filters, DatabaseKey


class BookRepository(DB):
    model = Book

    def __init__(self) -> None:
        super().__init__(Book)

    def create(self, record: Book) -> Book:  
        return super().create(record)

    def upsert(  
        self, record: Book = None, data_to_add: dict = None, **search_args
    ) -> Book:
        return super().upsert(record, data_to_add, **search_args)

    def get(
        self,
        key: Optional[DatabaseKey] = None,
        *,
        filters: List[Union[tuple, str]] = None,
        **kwargs: Any
    ) -> Optional[Book]:
        return super().get(key, filters=filters, **kwargs)

    def list(
        self, keys: List[DatabaseKey] = None, *, filters: Filters = None, **kwargs: Any
    ) -> List[Book]:
        return super().list(keys, filters=filters, **kwargs)

    def delete(self, record: Union[Book, DatabaseKey]) -> bool:  
        return super().delete(record)