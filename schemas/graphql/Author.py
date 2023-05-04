from typing import List
import strawberry


@strawberry.type(description="Author Schema")
class AuthorSchema:
    id: int
    name: str


@strawberry.input(description="Author Mutation Schema")
class AuthorMutationSchema:
    name: str
