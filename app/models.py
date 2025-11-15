from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
try:
    from app.database import Base
except ImportError:
    from database import Base

class Hunter(Base):
    __tablename__ = "hunters"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    avatar_url = Column(String, nullable=True)
    current_planet = Column(String, default="Tatooine")
    starship_name = Column(String, default="Razor Crest")
    starship_firepower = Column(Integer, default=10)
    xp = Column(Integer, default=0)
    level = Column(Integer, default=1)
    credits_balance = Column(Integer, default=1000)

    bounties = relationship("Bounty", back_populates="hunter")


class Bounty(Base):
    __tablename__ = "bounties"

    id = Column(Integer, primary_key=True, index=True)
    target_name = Column(String, index=True, nullable=False)
    target_image_url = Column(String, nullable=True)
    difficulty_rating = Column(Integer, default=3)
    reward_credits = Column(Integer, default=1500)
    planet_location = Column(String, default="Mandalore")
    bounty_type = Column(String, default="Terrestre")
    status = Column(String, default="Disponível")
    
    hunter_id = Column(Integer, ForeignKey("hunters.id"), nullable=True)

    hunter = relationship("Hunter", back_populates="bounties")