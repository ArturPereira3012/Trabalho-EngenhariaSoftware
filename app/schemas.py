from pydantic import BaseModel
from typing import Optional

class HunterBase(BaseModel):
    name: str
    avatar_url: Optional[str] = None
    current_planet: str
    starship_name: str
    starship_firepower: int

class HunterCreate(HunterBase):
    pass

class HunterResponse(HunterBase):
    id: int
    xp: int
    level: int
    credits_balance: int

    class Config:
        from_attributes = True


class BountyBase(BaseModel):
    target_name: str
    target_image_url: Optional[str] = None
    difficulty_rating: int
    reward_credits: int
    planet_location: str
    bounty_type: str

class BountyCreate(BountyBase):
    pass

class BountyResponse(BountyBase):
    id: int
    status: str
    hunter_id: Optional[int] = None

    class Config:
        from_attributes = True