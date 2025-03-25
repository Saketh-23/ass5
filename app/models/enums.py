# File path: app/models/enums.py
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "ADMIN"
    TRAINER = "TRAINER"
    USER = "USER"

class DifficultyLevel(str, Enum):
    BEGINNER = "BEGINNER"
    INTERMEDIATE = "INTERMEDIATE"
    ADVANCED = "ADVANCED"