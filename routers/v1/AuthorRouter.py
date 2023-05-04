from typing import List, Optional

from fastapi import APIRouter, Depends, status

from schemas.pydantic.AuthorSchema import (
    Author,
)
from services.AuthorService import AuthorService

AuthorRouter = APIRouter(
    prefix="/v1/authors", tags=["author"]
)


@AuthorRouter.get("/", response_model=List[Author])
def index(
    name: Optional[str] = None,
    pageSize: Optional[int] = 100,
    startIndex: Optional[int] = 0,
    authorService: AuthorService = Depends(),
):
    return [
        author
        for author in authorService.list(pageSize=pageSize
        )
    ]


@AuthorRouter.get("/{id}", response_model=Author)
def get(id: int, authorService: AuthorService = Depends()):
    return authorService.get(id)


@AuthorRouter.post(
    "/",
    response_model=Author,
    status_code=status.HTTP_201_CREATED,
)
def create(
    author: Author,
    authorService: AuthorService = Depends(),
):
    return authorService.create(author)


@AuthorRouter.patch("/{id}", response_model=Author)
def update(
    id: int,
    author: Author,
    authorService: AuthorService = Depends(),
):
    return authorService.update(id, author)


@AuthorRouter.delete(
    "/{id}", status_code=status.HTTP_204_NO_CONTENT
)
def delete(
    id: int, authorService: AuthorService = Depends()
):
    return authorService.delete(id)