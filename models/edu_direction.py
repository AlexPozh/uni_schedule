from dataclasses import dataclass


@dataclass
class StudyDirection:
    code: str
    name: str
    profile: str
    edu_department: str