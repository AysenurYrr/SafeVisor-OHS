from pydantic import BaseModel


class RoleRead(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True
