import base64
from binascii import Error
from datetime import datetime
from functools import partial
from typing import (
    IO,
    Any,
    Callable,
    List,
    Literal,
    Optional,
    Protocol,
    Union,
    overload,
    runtime_checkable,
)
from zlib import compress, decompress, error

import orjson
from orjson import orjson

# Installed Packages
from pydantic import BaseModel

from config import config
from datastore.key import DatastoreKey

orjson_options = (
    # Serialize datetime.datetime objects without a tzinfo as UTC. This has no effect on
    # datetime.datetime objects that have tzinfo set.
    orjson.OPT_NAIVE_UTC
    # Serialize dict keys of type other than str. This allows dict keys to be one of str,
    # int, float, bool, None, datetime.datetime, datetime.date, datetime.time, enum.Enum,
    # and uuid.UUID.
    | orjson.OPT_NON_STR_KEYS
    # Do not serialize the microsecond field on datetime.datetime and datetime.time
    # instances.
    | orjson.OPT_OMIT_MICROSECONDS
)


@runtime_checkable
class CustomJsonObj(Protocol):
    def __json__(self) -> Any:
        ...


def _default_encoder(data_obj: Any, *, default: Optional[Callable] = None) -> Any:
    """
    The encoder to use for object not natively supported by orjson.
    Args:
        data_obj: The object to encode/serialize.
    Returns:
        A supported orjson type object.
    Raises:
        TypeError: Raised when object is not JSON serializable.
    """
    if callable(default):
        data_obj = default(data_obj)

    match data_obj:
        case CustomJsonObj(__json__=json_method):
            if callable(json_method):
                json_method = json_method()
            return json_method
        case bytes():
            return data_obj.decode("utf-8")

        case obj if str(obj):
            return str(obj)

    raise TypeError


encoder = partial(
    _default_encoder,
)


DictOrBaseModel = dict | BaseModel


class DatastoreEntity(BaseModel):
    _key: Optional[DatastoreKey] = None

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True
        use_enum_values = True
        validate_assignment = True
        allow_population_by_field_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }

    class DatastoreConfig:
        kind: str
        key_pattern: str
        private_fields: List[str]
        compressed_fields: List = []
        required_field_defaults: dict = {}
        excluded_indexes: List[str] = ()
        embedded_entity_fields: List[str] = []
        foreign_keys: List[str] = []
        namespace: str = config.NAMESPACE
        project: str = config.PROJECT_ID

    class Mapping:
        pass

    def __init__(self, **data):
        data = self.decompress_values(data)

        super().__init__(**data)

    @property
    def key(self):
        if self._key:
            return self._key
        object_data = self.dict(exclude_none=True)
        return self.make_key(**object_data)

    @classmethod
    def make_key(cls, key_name: Optional[str] = None, **kwargs) -> DatastoreKey:
        if not key_name:
            key_name = cls.DatastoreConfig.key_pattern.format(**kwargs)

        return DatastoreKey(
            {
                "name": key_name,
                "kind": cls.DatastoreConfig.kind,
                "namespace": cls.DatastoreConfig.namespace,
                "project": cls.DatastoreConfig.project,
            }
        )

    def dict(
        self,
        *,
        include: Union["AbstractSetIntStr", "MappingIntStrAny"] = None,
        exclude: Union["AbstractSetIntStr", "MappingIntStrAny"] = None,
        by_alias: bool = False,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
        json_format: bool = False,
    ) -> "DictStrAny":
        """
        Generate a dictionary representation of the model, optionally specifying which fields to
        include or exclude. Also allows for the format to be specified.
        Args:
            include: Fields to include. All other will be excluded.
            exclude: Fields to exclude.
            by_alias: If True, the alias of a field will be the key used in the returned dictionary
            exclude_unset: Whether fields which were not explicitly set when creating the model
                should be excluded
            exclude_defaults: Whether fields which are equal to their default values (whether set
                or otherwise) should be excluded
            exclude_none: Whether fields which are equal to None should be excluded
            json_format: Whether the returned dictionary should be converted to JSON prior to being
                returned. For example, a datetime field would be converted to a string.
        Returns:
            The generated dictionary
        """
        return super().dict(
            include=include,
            exclude=exclude,
            by_alias=by_alias,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
        )

    @property
    def as_entity(self):
        # Installed Packages
        from google.cloud.datastore import Entity

        ds_config = self.DatastoreConfig
        exclude_from_indexes = tuple(ds_config.excluded_indexes) + tuple(
            ds_config.compressed_fields
        )
        entity = Entity(key=self.key, exclude_from_indexes=exclude_from_indexes)
        data = self.compressed_dict()

        def map_child_property(child: Union[list, object], property_name: str):
            for field_name in child or []:
                field = getattr(self, field_name)
                if isinstance(field, list):
                    data[field_name] = [getattr(item, property_name) for item in field]
                elif field:
                    data[field_name] = getattr(field, property_name)

        map_child_property(ds_config.embedded_entity_fields, "as_entity")

        entity.update(**data)
        return entity

    def compressed_dict(self, **kwargs):
        results = self.dict(**kwargs)
        for field in self.DatastoreConfig.compressed_fields:
            if results.get(field) is not None:
                results[field] = compress(
                    orjson.dumps(
                        results.get(field), default=encoder, option=orjson_options
                    )
                )
        return results

    def decompress_values(self, data: dict) -> dict:
        def full_decompress(value: bytes, field: str):
            value = base64.b64decode(value)
            decompressed = decompress(value)
            decoded = decompressed.decode("utf-8")
            return orjson.loads(decoded)

        for field in self.DatastoreConfig.compressed_fields:
            current_value = data.get(field)
            if current_value is not None:
                try:
                    data[field] = full_decompress(current_value, field)
                except (OSError, TypeError, Error, error):
                    pass
        return data