from typing import List, Optional

import strawberry
from strawberry.types import Info
from configs.GraphQL import (
    get_AuthorService,
)

from schemas.graphql.Author import AuthorSchema


@strawberry.type(description="Query all entities")
class Query:
    @strawberry.field(description="Get an Author")
    def author(
        self, id: int, info: Info
    ) -> Optional[AuthorSchema]:
        authorService = get_AuthorService(info)
        return authorService.get(id)

    @strawberry.field(description="List all Authors")
    def authors(self, info: Info) -> List[AuthorSchema]:
        authorService = get_AuthorService(info)
        return authorService.list()