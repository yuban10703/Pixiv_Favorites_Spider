from datetime import datetime
from typing import List, Union

from pydantic import BaseModel, HttpUrl


class Url(BaseModel):
    original: HttpUrl
    large: HttpUrl
    medium: HttpUrl


class Artwork(BaseModel):
    title: str
    id: int


class Author(BaseModel):
    name: str
    id: int


class Size(BaseModel):
    width: int
    height: int


class Setu(BaseModel):
    artwork: Artwork
    author: Author
    sanity_level: int
    r18: Union[bool, None]
    page: int
    create_date: datetime
    size: Size
    tags: List[str]
    urls: Url

#
# class Setus(BaseModel):
#     data: List[Data]
