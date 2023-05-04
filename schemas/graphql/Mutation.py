import strawberry
from strawberry.types import Info
from configs.GraphQL import (
    get_AuthorService,
)

from schemas.graphql.Author import (
    AuthorMutationSchema,
    AuthorSchema,
)

@strawberry.type(description="Mutate all Entity")
class Mutation:
    @strawberry.field(description="Adds a new Author")
    def add_author(
        self, author: AuthorMutationSchema, info: Info
    ) -> AuthorSchema:
        authorService = get_AuthorService(info)
        return authorService.create(author)

    @strawberry.field(
        description="Delets an existing Author"
    )
    def delete_author(
        self, author_id: int, info: Info
    ) -> None:
        authorService = get_AuthorService(info)
        return authorService.delete(author_id)

    @strawberry.field(
        description="Updates an existing Author"
    )
    def update_author(
        self,
        author_id: int,
        author: AuthorMutationSchema,
        info: Info,
    ) -> AuthorSchema:
        authorService = get_AuthorService(info)
        return authorService.update(author_id, author)