from pydantic import BaseModel

class Game(BaseModel):
    game_name: str
    logo_url: str | None = None
