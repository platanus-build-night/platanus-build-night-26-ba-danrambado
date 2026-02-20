import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.adapters.persistence.database import Base


def gen_id() -> str:
    return str(uuid.uuid4())


class UserModel(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=gen_id)
    name = Column(String, nullable=False)
    bio = Column(Text, nullable=False, default="")
    skills = Column(Text, nullable=False, default="[]")       # JSON array
    interests = Column(Text, nullable=False, default="[]")     # JSON array
    open_to = Column(Text, nullable=False, default="[]")       # JSON array
    created_at = Column(DateTime, default=datetime.utcnow)

    opportunities = relationship("OpportunityModel", back_populates="poster")


class OpportunityModel(Base):
    __tablename__ = "opportunities"

    id = Column(String, primary_key=True, default=gen_id)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    type = Column(String, nullable=False)
    posted_by = Column(String, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    poster = relationship("UserModel", back_populates="opportunities")
    matches = relationship("MatchModel", back_populates="opportunity")


class MatchModel(Base):
    __tablename__ = "matches"

    id = Column(String, primary_key=True, default=gen_id)
    opportunity_id = Column(String, ForeignKey("opportunities.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    score = Column(Float, nullable=False)
    embedding_score = Column(Float, nullable=False, default=0.0)
    network_score = Column(Float, nullable=False, default=0.0)
    explanation = Column(Text, nullable=False, default="")
    rank = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    opportunity = relationship("OpportunityModel", back_populates="matches")
    user = relationship("UserModel")


class ConnectionModel(Base):
    __tablename__ = "connections"

    id = Column(String, primary_key=True, default=gen_id)
    user_a = Column(String, ForeignKey("users.id"), nullable=False)
    user_b = Column(String, ForeignKey("users.id"), nullable=False)
    source = Column(String, nullable=False, default="seed")
    strength = Column(Float, nullable=False, default=1.0)
    created_at = Column(DateTime, default=datetime.utcnow)
