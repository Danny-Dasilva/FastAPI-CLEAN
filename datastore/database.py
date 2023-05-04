"""
This module is responsible for interacting with the Google Datastore Database.
This module exports the class `DB` to be used as the parent class for any class that accesses the
database.
"""
import re

from typing import Any, Set, List, Type, Tuple, Union, TypeVar, Iterator, Optional, overload
from dataclasses import dataclass

# Installed Packages
from pydantic import parse_obj_as, ValidationError
from google.cloud.datastore import Client

from config import config
from datastore import DatastoreKey, DatastoreEntity


Filters = List[Union[tuple, str]]
DatabaseRecord = TypeVar("DatabaseRecord", bound="DatastoreEntity")
DatabaseKey = TypeVar("DatabaseKey", bound="DatastoreKey")


class DatabaseError(Exception):
    """Database Error default Class"""


class _BaseClient(Client):
    """Base client class"""

    def __init__(
        self,
        project: str = None,
        namespace: str = None,
        credentials: Any = None,
        http_client: Any = None,
        use_grpc: bool = None,
    ):
        """Initialize client"""
        super().__init__(
            project=project,
            namespace=namespace,
            credentials=credentials,
            _http=http_client,
            _use_grpc=use_grpc,
        )
        self.credentials = credentials

    def __enter__(self) -> Client:
        """Enter client method"""
        return Client(
            project=self.project,
            namespace=self.namespace,
            credentials=self.credentials,
            _http=self._http,
            _use_grpc=self._use_grpc,
        )

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit client method"""


@dataclass
class DatastoreOperators:
    """Functionally an Enum for Datastore query operations"""

    equals = "="
    greater_than = ">"
    greater_than_or_equal = ">="
    less_than = "<"
    less_than_or_equal = "<="

    @classmethod
    def list_all(cls) -> list:
        """All Operators"""

        return [
            cls.greater_than_or_equal,
            cls.less_than_or_equal,
            cls.equals,
            cls.less_than,
            cls.greater_than,
        ]


def parse_filter_string(filter_string: str) -> tuple:
    """
    Parses a datastore filter string into the proper format. For example,
    "product_id>1" => ("product_id", ">", "1")
    Args:
        filter_string (str): The string representing the Datastore filter.
    Returns:
        (tuple) The tuple representation of the Datastore filter.
    """
    match = re.split(r"([><=]+)", filter_string)
    if match[1] not in DatastoreOperators.list_all():
        raise ValueError(
            "filter_string must contain a valid operator. "
            f"{match[1]} not in {DatastoreOperators.list_all()}"
        )
    return tuple(match)


model_type = TypeVar("model_type", bound="DatastoreEntity")

base_client = _BaseClient(
    credentials=config.service_credentials,
    project=config.PROJECT_ID,
    namespace=config.NAMESPACE,
    use_grpc=False,
)


class DB(object):
    """Base class to interact with DB, specific entities subclass this.
    Gets, lists, updates, deletes, and creates entities in Google Datastore.
    """ 

    model: Type[model_type]

    def __init__(self, database_model: Type[model_type]):

        self.model = database_model
        self.model_config = database_model.DatastoreConfig
        self.client = base_client

    def key(self, **kwargs):
        return self.model_config.key_pattern.format()

    def _build_query(self, filters: List[tuple] = None, **kwargs):
        """Build query for retrieving entities from database.
        Args:
            **kwargs: Entity properties or key to search for.
        Returns:
            Query: Google Datastore query to search with.
        """
        filters = filters or []
        filters = list(f if isinstance(f, tuple) else parse_filter_string(f) for f in filters)
        order = kwargs.pop("order", [])

        for key, value in kwargs.items():
            if getattr(value, "DatastoreConfig", None):
                kwargs[key] = value.key
            filters.append((key, DatastoreOperators.equals, value))

        query = self.client.query(kind=self.model_config.kind, filters=filters)
        if order:
            query.order = order
        return query


    def _record_to_datastore(self, record: Union[model_type, dict]):
        """Parse record to datastore"""
        if isinstance(record, dict):
            record = self.model(**record)
        return record

    def create(self, record: model_type) -> model_type:
        """Create a Record in the Database
        Args:
            record (_Record): record to create
        Returns:
            DatastoreEntity: Created item
        """
        return self.upsert(record)

    def upsert(
        self, record: model_type = None, data_to_add: dict = None, **search_args
    ) -> model_type:
        """
        Upsert a record in the database. If no record is provided, the record will be searched
        for via the `search_args` param.
        Args:
            record (DatabaseRecord): record to create
            data_to_add (dict): data to modify in record
            search_args: key/value pais to use in the `get` call made when record is `None`.
        Returns:
            list[DatastoreEntity]: list of datastore entities created
        """
        if record is None and not search_args:
            raise ValueError("A `record` or `search_args` are required.")
        elif record is None and search_args:
            record = self.get(**search_args)
        record_data = record.dict() if record else {}
        record_data.update(data_to_add or {})
        entity = self._record_to_datastore(record_data).as_entity
        self.client.put(entity)
        return self.parse_to_model(entity)

    def get(
        self, key: DatabaseKey = None, *, filters: Filters = None, **kwargs: Any
    ) -> Optional[DatabaseRecord]:
        """Get a single record from the database.
        Args:
            key (DatastoreKey): Primary Key of Entry
            filters (List[tuple]): List of filters which should be applied in search for entry
            **kwargs: Any keyword arguments to filter by during the database query
        Returns:
            The record as the provided read_record schema.
        """
        entity = None
        if key:
            entity = self.client.get(key)
        else:
            query = self._build_query(filters, **kwargs)
            entities = list(query.fetch(limit=1))
            if isinstance(entities, list) and len(entities):
                entity = entities[0]
        return self.parse_to_model(entity)

    def _parse_entities(self, entities: Iterator) -> Iterator[Type[DatabaseRecord]]:
        """Try to parse entity to object, yield it if success, otherwise ignore it"""

        for entity in entities:
            try:
                yield self.model.parse_obj(entity)
            except ValidationError:
                print(
                    f"{self.model.__class__.__name__} Validation Error"
                )

    def list(
        self,
        keys_only: bool = False,
        filters: Filters = None,
        cursor=None,
        limit=100,
        offset=0,
        **kwargs: Any,
    ) -> Union[List[Type[DatabaseRecord]], List[DatabaseKey]]:
        """List all records from the database.
        Args:
            keys_only (bool): if search should include keys only (faster than regular query)
            filters (List[tuple]): List of filters which should be applied in search for entry
            **kwargs: Any keyword arguments to filter by during the database query
        Returns:
            A list of records as a read_record schema of the model
        """
        query = self._build_query(filters, **kwargs)

        if keys_only:
            query.keys_only()
            return list(query.fetch(start_cursor=cursor, limit=limit, offset=offset))
        else:
            query = query.fetch(start_cursor=cursor, limit=limit, offset=offset)
            entities = list(query)
            next_cursor = query.next_page_token
            print(next_cursor)
            results = list(self._parse_entities(entities))
            return self.parse_to_model(results)

    def delete(self, record: Union[DatabaseRecord, DatabaseKey]) -> bool:
        """Delete a record from the database.
        Args:
            record: The record data as a read_record schema of the model
        """
        key = getattr(record, "key", record)
        self.client.delete(key)
        return True

    @overload
    def parse_to_model(self, data: Union[dict, object]) -> model_type:
        ...

    @overload
    def parse_to_model(self, data: Union[list, Iterator]) -> List[model_type]:
        ...

    @overload
    def parse_to_model(self, data: set) -> Set[model_type]:
        ...

    @overload
    def parse_to_model(self, data: tuple) -> Tuple[model_type]:
        ...

    def parse_to_model(self, data):
        if not data:
            return data
        if isinstance(data, (list, Iterator)):
            return parse_obj_as(List[self.model], list(data))
        if isinstance(data, set):
            return parse_obj_as(Set[self.model], data)
        if isinstance(data, tuple):
            return parse_obj_as(Tuple[self.model], data)
        return parse_obj_as(self.model, data)