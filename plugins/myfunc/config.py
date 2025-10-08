from pydantic import BaseModel


class Config(BaseModel):
    """Plugin Config Here"""
    blacklist: list = []
