from typing import Annotated
from pydantic import StringConstraints

# Annotated[how it should act in python, stuff to enforce]
Username = Annotated[str, StringConstraints(
    min_length=3, max_length=32, pattern=r"^[a-zA-Z0-9_.-]+$"
)]
Password = Annotated[str, StringConstraints(
    min_length=8, max_length=72
)]