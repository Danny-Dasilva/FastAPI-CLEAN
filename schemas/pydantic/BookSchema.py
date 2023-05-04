from datastore import DatastoreEntity



class Book(DatastoreEntity):

    id: int
    name: str
    authors: list = []

    class DatastoreConfig(DatastoreEntity.DatastoreConfig):
        kind = "Book"
        key_pattern = "{id}"

