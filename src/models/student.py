"""Student record and input validation."""
from dataclasses import dataclass, asdict
import re

@dataclass(frozen=True)
class Student:
    student_id: str
    name: str
    age: int
    course: str
    year_level: int
    email: str

    def __post_init__(self):
        for field in ('student_id', 'name', 'course', 'email'):
            value = getattr(self, field)
            if not isinstance(value, str) or not value.strip() or len(value) > 150:
                raise ValueError(f'{field} must contain 1 to 150 characters.')
            if any(ord(char) < 32 for char in value):
                raise ValueError(f'{field} cannot contain control characters.')
            object.__setattr__(self, field, value.strip())
        if not re.fullmatch(r'[A-Za-z0-9_-]{1,30}', self.student_id):
            raise ValueError('ID must use 1 to 30 letters, numbers, hyphens or underscores.')
        if type(self.age) is not int or not 1 <= self.age <= 120:
            raise ValueError('Age must be a whole number from 1 to 120.')
        if type(self.year_level) is not int or not 1 <= self.year_level <= 6:
            raise ValueError('Year level must be from 1 to 6.')
        if not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', self.email):
            raise ValueError('Enter a valid email address.')

    def to_dict(self):
        return asdict(self)
