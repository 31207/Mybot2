from pydantic import BaseModel


class Config(BaseModel):
    """Plugin Config Here"""
    blacklist: list = []
    output_pic_and_at_count: bool = False
    output_model_dump: bool = False

