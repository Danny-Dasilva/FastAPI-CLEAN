from typing import Any, Type, Union, Optional

# Installed Packages
from pydantic import BaseModel
from google.cloud.datastore import Key

from config import config


class DatastoreKey(str, Key):
    """
    Google Datastore Key as a string.
    """

    _kind: str = ""
    _project: str = config.PROJECT_ID
    _parent: Optional[Any] = None
    _namespace: Optional[str] = config.NAMESPACE

    def __init__(self, value: Union[Key, dict, Type[BaseModel]]):
        _config = config
        if getattr(self, "DatastoreConfig", None):
            self = value.key
        elif isinstance(value, Key):
            self._kind = value.kind
            self._name = value.id_or_name
            self._parent = value.parent
            self._project = value.project
            self._namespace = value.namespace
        elif isinstance(value, dict):
            self._kind = value.get("kind", self._kind)
            self._name = value.get("id") or value.get("name")
            self._parent = value.get("parent")
            self._project = value.get("project", self._project)
            self._namespace = value.get("namespace", self._namespace)

        super().__init__(
            self._kind,
            self._name,
            parent=self._parent,
            namespace=self._namespace,
            project=self._project,
        )

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if isinstance(v, dict) or isinstance(v, Key):
            return cls(v)
        raise TypeError("dict or Datastore Key required")

    def __repr__(self):
        return f"DatastoreKey('{self._kind.title()}', '{self.id_or_name})'"

    def __class_getitem__(cls, name):
        class DatastoreKey(cls):
            def __init__(self, *args, **kwargs):
                super(DatastoreKey, self).__init__(*args, **kwargs)

        DatastoreKey._kind = name
        return DatastoreKey