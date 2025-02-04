"""
Scheme definition on unified data
"""
from pydantic import BaseModel


class MediaResource(BaseModel):

    url: str
    mime_type: str
    filename: str
