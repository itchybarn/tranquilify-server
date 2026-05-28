from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

# import all models, so that importing just this file registers every other model on Base.metadata
from app.models.user import User