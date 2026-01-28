import argparse
from pathlib import Path
import re

import pandas as pd

from base_parser import BaseParser
from models.discipline import Discipline
from models.edu_direction import StudyDirection


# 'Table 1' contains information about the direction of study
# 'Table 2' contains information about academic discipline
SHEET_NAMES: list[str] = ["Table 1", "Table 2"]

NEEDED_COLUMNS: list[str] = [
    "Индекс", "Наименование", "Формы контроля", "Unnamed: 3", "Unnamed: 4", "Unnamed: 5", "Unnamed: 6", "Unnamed: 7", "Unnamed: 8", 'Unnamed: 12', 'Unnamed: 13',
    'Unnamed: 14', 'Unnamed: 15', 'Unnamed: 21', 'Unnamed: 22', 'Unnamed: 24', 'Unnamed: 25', 'Unnamed: 27', 'Unnamed: 28', 'Unnamed: 30',
    'Unnamed: 31', 'Закрепленная'
]

FORMS_CONTROL = ["Экзамены", "Зачеты", "Зачеты с оценкой", "Курсовые проекты", "Курсовые работы", "Контрольные", "РГР"]
COURSES = [1, 2, 3, 4]

class CurriculumParser(BaseParser):
    def __init__(self, file_path: Path, study_direction: str) -> None:
        self.file_path = file_path
        self.study_direction = study_direction

        self.__df_title = pd.read_excel(file_path, sheet_name=SHEET_NAMES[0])
        self.__df_academic_discipline = pd.read_excel(file_path, sheet_name=SHEET_NAMES[1])

    def parse(self) -> tuple[StudyDirection, Discipline]:
        study_direction = self._parse_study_direction()
        disciplines = self._parse_academic_discipline()

        return study_direction, disciplines

    def _parse_academic_discipline(self) -> list[Discipline]:
        column_data = [self.__df_academic_discipline[column_name] for column_name in NEEDED_COLUMNS]
        discipline_data = list(zip(*column_data))
        disciplines = [] 
        for data in discipline_data:
            if pd.isna(data[0]) or self._elective_discipline_check(data[0]): # if "Индекс" is not set or if this discipline is not for this direction
                continue

            forms_control = self._get_forms_control(data[2:9])
            edu_course_with_sem = self._get_semester_with_course(data[13:-1])
            disciplines.append(
                Discipline(
                    index=str(data[0]),
                    name=str(data[1]).replace("\n", " "),
                    forms_control=forms_control,
                    lecture_hours=int(data[9]) if not(pd.isna(data[9])) else 0,
                    labs_hours=int(data[10]) if not(pd.isna(data[10])) else 0,
                    practice_hours=int(data[11]) if not(pd.isna(data[11])) else 0,
                    csr_hours=int(data[12]) if not(pd.isna(data[12])) else 0,
                    edu_course_with_semester=edu_course_with_sem,
                    code_edu_department=data[-1]
                )
            )
        return disciplines

    def _get_semester_with_course(self, course_sem_data: tuple[str]) -> list[tuple[int, int]]:
        result: list[tuple[int, int]] = []
        course_index = 0
        for i in range(0, len(course_sem_data), 2):
            course = COURSES[course_index]
            course_index += 1
            first_sem, second_sem = course_sem_data[i], course_sem_data[i+1]
            if pd.isna(first_sem) and pd.isna(second_sem):
                continue
            if not(pd.isna(first_sem)):
                result.append((course, 1))
            if not(pd.isna(second_sem)):
                result.append((course, 2))
        return result

    def _get_forms_control(self, form_control_data: tuple[str]) -> list[tuple[str, int]]:
        return [
            (form_control, 0 if pd.isna(value) else int(value))
            for form_control, value in zip(FORMS_CONTROL, form_control_data)
        ]

    def _parse_study_direction(self) -> StudyDirection:
        patterns = {
            'code': r'Направление\s+(\d{2}\.\d{2}\.\d{2})',
            'name': r'Направление\s+\d{2}\.\d{2}\.\d{2}\s*"([^"]+)"',
            'profile': r'Направленность\s*\(профиль\):\s*"([^"]+)"',
            'edu_department': r'Кафедра:\s*(.+?)(?:\s*$|\.|,)'
        }
        result = {}
        for key, pattern in patterns.items():
            match = re.search(pattern, self.study_direction, re.IGNORECASE)
            result[key] = match.group(1) if match else None
        return StudyDirection(**result)

    def _elective_discipline_check(self, dicp_index: str) -> bool:
        if "ДВ" not in dicp_index:
            return False
        last_two_index_nums = dicp_index.strip().split(".")[-2:]
        if last_two_index_nums[1] == "1":
            return False
        return True

if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('--file', type=str, required=True, help='Путь к .xlsx файлу учебного плана')
    arg_parser.add_argument('--study-direction', type=str, default="""Направление 09.03.02 "Информационные системы и технологии" Направленность (профиль): "Распределенные информационные системы" Кафедра: Компьютерные технологии в проектировании и производстве""", help='Направление подготовки, для которого был добавлен учебный план')
    args = arg_parser.parse_args()

    parser = CurriculumParser(Path(args.file), args.study_direction.strip()).parse()
