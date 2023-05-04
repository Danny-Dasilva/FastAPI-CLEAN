from datastore import DatastoreEntity



class Author(DatastoreEntity):

    id: int
    name: str
    books: list = []

    class DatastoreConfig(DatastoreEntity.DatastoreConfig):
        kind = "Author"
        key_pattern = "{id}"

