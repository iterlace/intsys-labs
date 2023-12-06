from typing import List

import pydantic


class Subject(pydantic.BaseModel):
    name: str

    def __init__(self, name: str, **kwargs) -> None:
        kwargs["name"] = name
        super().__init__(**kwargs)

    def __hash__(self):
        return hash(self.name)


class GroupSubject(pydantic.BaseModel):
    subject: Subject
    hours: int

    def __init__(self, subject: Subject, hours: int, **kwargs) -> None:
        kwargs["hours"] = hours
        kwargs["subject"] = subject
        super().__init__(**kwargs)

    def __hash__(self):
        return hash(self.name)


class Group(pydantic.BaseModel):
    name: str
    subjects: List[GroupSubject] = []

    def __init__(self, name: str, subjects: List[GroupSubject], **kwargs) -> None:
        kwargs["name"] = name
        kwargs["subjects"] = subjects
        super().__init__(**kwargs)

    def __hash__(self):
        return hash(self.name)


class Teacher(pydantic.BaseModel):
    name: str
    subjects: List[Subject]  # refs to existing subjects

    def __init__(self, name: str, **kwargs) -> None:
        kwargs["name"] = name
        super().__init__(**kwargs)

    def __hash__(self):
        return hash(self.name)


days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
timeslots = [0, 1, 2, 3]
subject = [
    Subject("Discrete Mathematics"),
    Subject("Computer Architecture"),
    Subject("Operating Systems"),
    Subject("Programming"),
    Subject("English"),
    Subject("Mathematical Analysis"),
    Subject("Algebra and Geometry"),
    Subject("Physical Education"),
]
subject_map = {s.name: s for s in subject}
teachers = [
    Teacher(
        "Камаз Павлович",
        subjects=[
            subject_map["Discrete Mathematics"],
            subject_map["Mathematical Analysis"],
        ],
    ),
    Teacher("Макар Бьорнович", subjects=[subject_map["Computer Architecture"]]),
    Teacher(
        "Монстр Хайнєкен",
        subjects=[
            subject_map["Operating Systems"],
            subject_map["Algebra and Geometry"],
        ],
    ),
    Teacher("Замир Безрусні", subjects=[subject_map["Programming"]]),
    Teacher("Володимир Тарануха", subjects=[subject_map["Programming"]]),
    Teacher("Красовська І.В.", subjects=[subject_map["English"]]),
    Teacher("Василь Неміров", subjects=[subject_map["Physical Education"]]),
]

GROUPS = [
    Group(
        "TK-41",
        [
            GroupSubject(subject_map["Programming"], 4),
            GroupSubject(subject_map["Operating Systems"], 2),
            GroupSubject(subject_map["English"], 1),
            GroupSubject(subject_map["Mathematical Analysis"], 1),
            GroupSubject(subject_map["Algebra and Geometry"], 1),
        ],
    ),
    Group(
        "MI-2",
        [
            GroupSubject(subject_map["Programming"], 2),
            GroupSubject(subject_map["English"], 1),
            GroupSubject(subject_map["Mathematical Analysis"], 3),
            GroupSubject(subject_map["Algebra and Geometry"], 3),
            GroupSubject(subject_map["Physical Education"], 1),
        ],
    ),
    Group(
        "ТТП-42",
        [
            GroupSubject(subject_map["Programming"], 2),
            GroupSubject(subject_map["English"], 1),
            GroupSubject(subject_map["Mathematical Analysis"], 3),
            GroupSubject(subject_map["Algebra and Geometry"], 3),
            GroupSubject(subject_map["Physical Education"], 1),
        ],
    ),
]

# Variables: (group, day, timeslot)
variables = [
    (group.name, day, timeslot)
    for group in GROUPS
    for day in days
    for timeslot in timeslots
]
# Domains: lists of subjects that can be taught during a timeslot
domains = {
    var: [gs.subject.name for gs in group.subjects]
    for var in variables
    for group in GROUPS
    if group.name == var[0]
}
# Constraints
constraints = []


# Constraint: A teacher cannot teach more than one class at the same time
def teacher_conflict_constraint(assignment):
    teacher_times = {}
    for (group, day, timeslot), subject in assignment.items():
        teacher = next(
            (t for t in teachers if subject in [s.name for s in t.subjects]), None
        )
        if teacher:
            if (teacher.name, day, timeslot) in teacher_times:
                return False
            teacher_times[(teacher.name, day, timeslot)] = True
    return True


constraints.append(teacher_conflict_constraint)
