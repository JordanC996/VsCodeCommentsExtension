from typing import List
from pydantic import BaseModel

class Comment(BaseModel):
    row: str = ""
    comment: str = ""

class Comments(BaseModel):
    comments: List[Comment] = []