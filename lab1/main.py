from owlready2 import *

onto = get_ontology("http://example.org/school_ontology.owl")


# Class definitions
class Student(Thing):
    namespace = onto

    def display_info(self) -> None:
        print(f"Student: {self.name}, Grade Level: {self.grade_level}")


class Grade(Thing):
    namespace = onto

    def display_students(self) -> None:
        students = [
            student for student in Student.instances() if student.in_grade == self
        ]
        print(f"Students in Grade {self.level}:")
        for student in students:
            print(f"    {student.name}")


class School(Thing):
    namespace = onto

    def display_grades(self) -> None:
        print(f"Grades in {self.name} School:")
        for grade in self.contains_grade:
            print(f"    Grade {grade.level}")


class City(Thing):
    namespace = onto

    def display_schools(self) -> None:
        print(f"Schools in {self.name} City:")
        for school in self.has_school:
            print(f"    {school.name}")


# Property definitions
class name(DataProperty):
    namespace = onto
    domain = [Student, School, City]
    range = [str]


class grade_level(DataProperty, FunctionalProperty):
    namespace = onto
    domain = [Student]
    range = [int]


class level(DataProperty, FunctionalProperty):
    namespace = onto
    domain = [Grade]
    range = [int]


class in_grade(ObjectProperty, FunctionalProperty):
    namespace = onto
    domain = [Student]
    range = [Grade]


class contains_grade(ObjectProperty):
    namespace = onto
    domain = [School]
    range = [Grade]


class has_school(ObjectProperty):
    namespace = onto
    domain = [City]
    range = [School]


if __name__ == "__main__":
    # Example usage
    grade_10 = Grade("grade_10")
    grade_10.level = 10

    school_X = School("school_X")
    school_X.contains_grade.append(grade_10)

    city_Y = City("city_Y")
    city_Y.has_school.append(school_X)

    # Create students
    student_A = Student("student_A")
    student_A.name = "Alice"
    student_A.grade_level = 10
    student_A.in_grade = grade_10

    student_B = Student("student_B")
    student_B.name = "Bob"
    student_B.grade_level = 10
    student_B.in_grade = grade_10

    # Display information
    student_A.display_info()
    student_B.display_info()
    grade_10.display_students()
    school_X.display_grades()
    city_Y.display_schools()

    onto.save(file="school_ontology.owl", format="rdfxml")
