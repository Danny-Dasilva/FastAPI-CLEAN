from datastore import DatastoreEntity



class Author(DatastoreEntity):

    id: int
    name: str
    authors: list = []

    class DatastoreConfig(DatastoreEntity.DatastoreConfig):
        kind = "Book"
        key_pattern = "{id}"

