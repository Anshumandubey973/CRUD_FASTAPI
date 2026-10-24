from pydantic import BaseModel, Field, field_validator


class StudentCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    course: str = Field(min_length=1, max_length=100)

    @field_validator("name", "course")
    @classmethod
    def strip_and_validate_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Value must not be blank")
        return value


class StudentUpdate(StudentCreate):
    pass


class Student(StudentCreate):
    id: int
