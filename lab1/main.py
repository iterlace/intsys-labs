from typing import Dict, List, Optional


class Student:
    def __init__(self, name: str, grade_level: int):
        self.name = name
        self.grade_level = grade_level


class Grade:
    def __init__(self, level: int):
        self.level = level
        self.students: List[Student] = []

    def add_student(self, student: Student):
        self.students.append(student)

    def remove_student(self, student_name: str):
        self.students = [
            student for student in self.students if student.name != student_name
        ]

    def get_students(self) -> List[Student]:
        return self.students


class School:
    def __init__(self, name: str):
        self.name = name
        self.grades: Dict[int, Grade] = {}

    def add_grade(self, grade_level: int):
        if grade_level not in self.grades:
            self.grades[grade_level] = Grade(grade_level)

    def add_student_to_grade(self, student: Student, grade_level: int):
        if grade_level not in self.grades:
            self.add_grade(grade_level)
        self.grades[grade_level].add_student(student)

    def get_students_in_grade(self, grade_level: int) -> List[Student]:
        if grade_level in self.grades:
            return self.grades[grade_level].get_students()
        return []


class City:
    def __init__(self, name: str):
        self.name = name
        self.schools: List[School] = []

    def add_school(self, school: School):
        self.schools.append(school)

    def get_schools(self) -> List[School]:
        return self.schools


def find_city_for_student(
    array_of_cities: List[City], student_name: str
) -> Optional[str]:
    for city in array_of_cities:
        for school in city.schools:
            for grade_level, grade in school.grades.items():
                if any(student.name == student_name for student in grade.students):
                    return city.name
    return None


def main():
    # Example usage
    kyiv = City("Kyiv")
    alice = Student("Alice", 3)
    bob = Student("Bob", 5)
    jack = Student("Jack", 7)
    school_1 = School("School #1")
    school_1.add_student_to_grade(alice, 3)
    school_1.add_student_to_grade(bob, 5)
    school_2 = School("School #2")
    school_2.add_student_to_grade(jack, 7)

    kyiv.add_school(school_1)

    # Display students in School #1 in Kyiv
    for grade_level, grade in school_1.grades.items():
        print(f"Grade: {grade_level}")
        for student in grade.get_students():
            print(f"	Student: {student.name}, Grade: {student.grade_level}")

    print("Looking for Alice in [Kyiv]...")
    c = find_city_for_student([kyiv], "Alice")
    if c is not None:
        print(f"Found Alice in {c}")
    else:
        print("Alice not found")


if __name__ == "__main__":
    main()
