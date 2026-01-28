from dataclasses import dataclass


@dataclass
class Discipline:
    index: str
    name: str
    forms_control: list[tuple[str, int]]
    lecture_hours: int
    labs_hours: int
    practice_hours: int
    csr_hours: int
    edu_course_with_semester: list[tuple[int, int]]
    code_edu_department: int
