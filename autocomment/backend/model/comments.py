from typing import List
from pydantic import BaseModel, Field

class Comment(BaseModel):
    row: int = Field(description="The index in the code where the comment should be placed")
    value: str = Field(description="The comment value")

class Comments(BaseModel):
    comments: List[Comment] = []