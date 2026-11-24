# app/models/__init__.py
from .base import db
from .tourism_resource import TourismResource
from .administrative_division import AdministrativeDivision
from .evaluation_factor import EvaluationFactor
from .user import User

__all__ = [
    'db',
    'TourismResource',
    'AdministrativeDivision',
    'EvaluationFactor',
    'User'
]