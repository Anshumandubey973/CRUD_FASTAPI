from fastapi import APIRouter, HTTPException, Query, Response, status

from database import get_connection
from schemas import Student, StudentCreate, StudentUpdate


router = APIRouter(prefix="/students", tags=["students"])


@router.post("", response_model=Student, status_code=status.HTTP_201_CREATED)
def add_student(student: StudentCreate) -> Student:
    with get_connection() as connection:
        cursor = connection.execute(
            "INSERT INTO students (name, course) VALUES (?, ?)",
            (student.name, student.course),
        )
        student_id = cursor.lastrowid
    if student_id is None:
        raise RuntimeError("Student was inserted without an assigned ID")
    return Student(id=student_id, name=student.name, course=student.course)


@router.get("", response_model=list[Student])
def get_students() -> list[Student]:
    with get_connection() as connection:
        rows = connection.execute(
            "SELECT id, name, course FROM students ORDER BY id"
        ).fetchall()
    return [Student.model_validate(dict(row)) for row in rows]


@router.get("/search", response_model=list[Student])
def search_students(
    q: str = Query(min_length=1, description="Match student names or courses")
) -> list[Student]:
    search_term = f"%{q.strip()}%"
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, name, course FROM students
            WHERE name LIKE ? OR course LIKE ?
            ORDER BY id
            """,
            (search_term, search_term),
        ).fetchall()
    return [Student.model_validate(dict(row)) for row in rows]


@router.get("/{student_id}", response_model=Student)
def get_student(student_id: int) -> Student:
    with get_connection() as connection:
        row = connection.execute(
            "SELECT id, name, course FROM students WHERE id = ?", (student_id,)
        ).fetchone()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
    return Student.model_validate(dict(row))


@router.put("/{student_id}", response_model=Student)
def update_student(student_id: int, student: StudentUpdate) -> Student:
    with get_connection() as connection:
        cursor = connection.execute(
            "UPDATE students SET name = ?, course = ? WHERE id = ?",
            (student.name, student.course, student_id),
        )
        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Student not found"
            )
        row = connection.execute(
            "SELECT id, name, course FROM students WHERE id = ?", (student_id,)
        ).fetchone()
    return Student.model_validate(dict(row))


@router.delete("/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_student(student_id: int) -> Response:
    with get_connection() as connection:
        cursor = connection.execute(
            "DELETE FROM students WHERE id = ?", (student_id,)
        )
    if cursor.rowcount == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
