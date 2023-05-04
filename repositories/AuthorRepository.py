from typing import Any, List, Union, Optional

from schemas.pydantic.AuthorSchema import Author
from datastore.database import DB, Filters, DatabaseKey


class AuthorRepository(DB):
    model = Author

    def __init__(self) -> None:
        super().__init__(Author)

    def create(self, record: Author) -> Author:  
        return super().create(record)

    def upsert(  
        self, record: Author = None, data_to_add: dict = None, **search_args
    ) -> Author:
        return super().upsert(record, data_to_add, **search_args)

    def get(
        self,
        key: Optional[DatabaseKey] = None,
        *,
        filters: List[Union[tuple, str]] = None,
        **kwargs: Any
    ) -> Optional[Author]:
        return super().get(key, filters=filters, **kwargs)

    def list(
        self, keys: List[DatabaseKey] = None, *, filters: Filters = None, **kwargs: Any
    ) -> List[Author]:
        return super().list(keys, filters=filters, **kwargs)

    def delete(self, record: Union[Author, DatabaseKey]) -> bool:  
        return super().delete(record)