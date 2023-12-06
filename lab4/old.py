import random
from typing import Generator, List, Optional, Set, Tuple


class CSP:
    def __init__(self) -> None:
        self.days = ["Понеділок", "Вівторок", "Середа", "Четвер", "П'ятниця"]
        self.disciplines_count = {
            0: 2,
            1: 1,
            2: 1,
            3: 2,
            4: 1,
            5: 2,
            6: 2,
            7: 1,
            8: 1,
            9: 2,
        }
        self.disciplines: List[str] = [
            "ОС з розподілом часу",
            "Проблеми штучного інтелекту",
            "Нейронні мережі",
            "Лаб. Нейронні мережі",
            "Інтелектуальні системи",
            "Лаб. Інтелектуальні системи",
            "Iнформаційні технології в менеджментi",
            "Вибрані розділи трудового права і основ підприємницької діяльності",
            "Розробка програмного забезпечення",
            "Лаб. Розробка програмного забезпечення",
        ]
        self.teachers = list(range(9))
        self.teacher_disciplines = [{0}, {1}, {2, 3}, {4}, {5}, {6, 7}, {8}, {9}, {9}]

        self.num_days = len(self.days)
        self.num_classes = 3
        self.num_classes_total = self.num_days * self.num_classes

        self.num_teachers = len(self.teachers)
        self.num_disciplines = len(self.disciplines)

        self.disciplines_index: Set[int] = set(range(self.num_disciplines))

        self.subject_assignments: List[Optional[int]] = [None] * self.num_classes_total
        self.teacher_assignments: List[Optional[int]] = [None] * self.num_classes_total

        self.checks: int = 0

    def intersection(self, set_a: Set[int], set_b: Set[int]) -> Set[int]:
        return set_a & set_b

    def constraints(self) -> bool:
        self.checks += 1

        for lesson, teacher in enumerate(self.teacher_assignments):
            if teacher is not None and self.subject_assignments[
                lesson
            ] not in self.intersection(
                self.disciplines_index, self.teacher_disciplines[teacher]
            ):
                return False

        subjects = [x for x in self.subject_assignments if x is not None]
        if any(subjects.count(s) > self.disciplines_count[s] for s in subjects):
            return False

        if any(
            self._has_consecutive_assignments(assignments)
            for assignments in [self.teacher_assignments, self.subject_assignments]
        ):
            return False

        return True

    def _has_consecutive_assignments(self, assignments: List[Optional[int]]) -> bool:
        for i in range(len(assignments) - self.num_classes + 1):
            window = assignments[i : i + self.num_classes]
            counts = {item: window.count(item) for item in set(window)}
            if any(
                count > self.num_classes - 1 and item is not None
                for item, count in counts.items()
            ):
                return True
        return False

    def heuristic(self) -> Optional[int]:
        try:
            return self.teacher_assignments.index(None)
        except ValueError:
            return None

    def domain(self) -> Generator[Tuple[int, int], None, None]:
        shuffled_teachers = random.sample(self.teachers, len(self.teachers))
        for teacher in shuffled_teachers:
            available_classes = self.intersection(
                self.disciplines_index, self.teacher_disciplines[teacher]
            )
            shuffled_subjects = random.sample(
                list(available_classes), len(available_classes)
            )

            for subject in shuffled_subjects:
                yield teacher, subject

    def backtracking(self) -> bool:
        lesson = self.heuristic()

        if lesson is None:
            return True

        for teacher, subject in self.domain():
            self.teacher_assignments[lesson], self.subject_assignments[lesson] = (
                teacher,
                subject,
            )

            if self.constraints() and self.backtracking():
                return True

            self.teacher_assignments[lesson], self.subject_assignments[lesson] = (
                None,
                None,
            )

        return False

    def print_schedule(self) -> None:
        for d in range(self.num_days):
            print(f"\n{self.days[d]}")
            for l in range(self.num_classes):
                lesson = d * self.num_classes + l
                teacher = self.teacher_assignments[lesson]
                subject = self.subject_assignments[lesson]

                if subject is not None and teacher is not None:
                    print(
                        f"{lesson + 1}: {self.disciplines[subject]} {self.teachers[teacher]}"
                    )
                else:
                    print(f"{lesson + 1}: No class")


# Example usage
csp = CSP()
if csp.backtracking():
    csp.print_schedule()
else:
    print("No valid schedule found.")
