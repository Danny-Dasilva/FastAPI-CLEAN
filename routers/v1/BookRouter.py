from typing import List, Optional

from fastapi import APIRouter, Depends, status

from schemas.pydantic.AuthorSchema import Author
from schemas.pydantic.BookSchema import (
    Book
)
from services.BookService import BookService

BookRouter = APIRouter(prefix="/v1/books", tags=["book"])


@BookRouter.get("/", response_model=List[Book])
def index(
    name: Optional[str] = None,
    pageSize: Optional[int] = 100,
    startIndex: Optional[int] = 0,
    bookService: BookService = Depends(),
):
    return [
        book.normalize()
        for book in bookService.list(
            name, pageSize, startIndex
        )
    ]


@BookRouter.get("/{id}", response_model=Book)
def get(id: int, bookService: BookService = Depends()):
    return bookService.get(id).normalize()


@BookRouter.post(
    "/",
    response_model=Book,
    status_code=status.HTTP_201_CREATED,
)
def create(
    book: Book,
    bookService: BookService = Depends(),
):
    return bookService.create(book).normalize()


@BookRouter.patch("/{id}", response_model=Book)
def update(
    id: int,
    book: Book,
    bookService: BookService = Depends(),
):
    return bookService.update(id, book).normalize()


@BookRouter.delete(
    "/{id}", status_code=status.HTTP_204_NO_CONTENT
)
def delete(id: int, bookService: BookService = Depends()):
    return bookService.delete(id)


@BookRouter.get(
    "/{id}/authors/", response_model=List[Author]
)
def get_authors(
    id: int, bookService: BookService = Depends()
):
    return [
        author.normalize()
        for author in bookService.get_authors(id)
    ]


@BookRouter.post(
    "/{id}/authors/", response_model=List[Author]
)
def add_author(
    id: int,
    author: Book,
    bookService: BookService = Depends(),
):
    return [
        author.normalize()
        for author in bookService.add_author(id, author)
    ]


@BookRouter.delete(
    "/{id}/authors/{author_id}",
    response_model=List[Author],
)
def remove_author(
    id: int,
    author_id: int,
    bookService: BookService = Depends(),
):
    return [
        author.normalize()
        for author in bookService.remove_author(
            id, author_id
        )
    ]
