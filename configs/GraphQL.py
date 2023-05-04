from fastapi import Depends
from strawberry.types import Info

from services.AuthorService import AuthorService


# GraphQL Dependency Context
async def get_graphql_context(
    authorService: AuthorService = Depends(),
):
    return {
        "authorService": authorService,
    }


# Extract AuthorService instance from GraphQL context
def get_AuthorService(info: Info) -> AuthorService:
    return info.context["authorService"]
