import copy
import random
from typing import List

import pydantic


class Subject(pydantic.BaseModel):
    name: str

    def __init__(self, name: str, **kwargs) -> None:
        kwargs["name"] = name
        super().__init__(**kwargs)

    def __hash__(self):
        return hash(self.name)

    def __repr__(self):
        return f"Subject({self.name})"

    def __str__(self):
        return repr(self)


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

    def __repr__(self):
        return f"Group({self.name})"

    def __str__(self):
        return repr(self)


class Teacher(pydantic.BaseModel):
    name: str
    subjects: List[Subject]  # refs to existing subjects

    def __init__(self, name: str, **kwargs) -> None:
        kwargs["name"] = name
        super().__init__(**kwargs)

    def __hash__(self):
        return hash(self.name)

    def __repr__(self):
        return f"Teacher({self.name})"

    def __str__(self):
        return repr(self)


days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
timeslots = [0, 1, 2, 3]
SUBJECTS = [
    Subject("Discrete Mathematics"),
    Subject("Computer Architecture"),
    Subject("Operating Systems"),
    Subject("Programming"),
    Subject("English"),
    Subject("Mathematical Analysis"),
    Subject("Algebra and Geometry"),
    Subject("Physical Education"),
]
SUBJECTS_MAP = {s.name: s for s in SUBJECTS}
TEACHERS = [
    Teacher(
        "Камаз Павлович",
        subjects=[
            SUBJECTS_MAP["Discrete Mathematics"],
            SUBJECTS_MAP["Mathematical Analysis"],
        ],
    ),
    Teacher("Макар Бьорнович", subjects=[SUBJECTS_MAP["Computer Architecture"]]),
    Teacher(
        "Монстр Хайнєкен",
        subjects=[
            SUBJECTS_MAP["Operating Systems"],
            SUBJECTS_MAP["Algebra and Geometry"],
        ],
    ),
    Teacher("Замир Безрусні", subjects=[SUBJECTS_MAP["Programming"]]),
    Teacher("Володимир Тарануха", subjects=[SUBJECTS_MAP["Programming"]]),
    Teacher("Красовська І.В.", subjects=[SUBJECTS_MAP["English"]]),
    Teacher("Василь Неміров", subjects=[SUBJECTS_MAP["Physical Education"]]),
]

GROUPS = [
    Group(
        "TK-41",
        [
            GroupSubject(SUBJECTS_MAP["Programming"], 4),
            GroupSubject(SUBJECTS_MAP["Operating Systems"], 2),
            GroupSubject(SUBJECTS_MAP["English"], 1),
            GroupSubject(SUBJECTS_MAP["Mathematical Analysis"], 1),
            GroupSubject(SUBJECTS_MAP["Algebra and Geometry"], 1),
        ],
    ),
    Group(
        "MI-2",
        [
            GroupSubject(SUBJECTS_MAP["Programming"], 1),
            # GroupSubject(SUBJECTS_MAP["English"], 1),
            # GroupSubject(SUBJECTS_MAP["Mathematical Analysis"], 3),
            # GroupSubject(SUBJECTS_MAP["Algebra and Geometry"], 3),
            # GroupSubject(SUBJECTS_MAP["Physical Education"], 1),
        ],
    ),
    # Group(
    #     "ТТП-42",
    #     [
    #         GroupSubject(SUBJECTS_MAP["Programming"], 2),
    #         GroupSubject(SUBJECTS_MAP["English"], 1),
    #         GroupSubject(SUBJECTS_MAP["Mathematical Analysis"], 3),
    #         GroupSubject(SUBJECTS_MAP["Algebra and Geometry"], 2),
    #         GroupSubject(SUBJECTS_MAP["Physical Education"], 1),
    #     ],
    # ),
]
TOTAL_SLOTS_TO_BE_FILLED = 0
for group in GROUPS:
    for subject in group.subjects:
        TOTAL_SLOTS_TO_BE_FILLED += subject.hours


class Variable(pydantic.BaseModel):
    group: Group
    day: str
    timeslot: int

    def __init__(self, group: Group, day: str, timeslot: int, **kwargs) -> None:
        kwargs["group"] = group
        kwargs["day"] = day
        kwargs["timeslot"] = timeslot
        super().__init__(**kwargs)

    def __hash__(self):
        return hash((self.group, self.day, self.timeslot))

    def __repr__(self):
        return f"Variable({self.group}, {self.day}, {self.timeslot})"

    def __str__(self):
        return repr(self)


# Variables: (group, day, timeslot)
variables = [
    Variable(group, day, timeslot)
    for group in GROUPS
    for day in days
    for timeslot in timeslots
]
random.shuffle(variables)

# Domains: lists of subjects that can be taught during a timeslot
domains = {
    var: [
        (gs.subject, teacher)
        for gs in var.group.subjects
        for teacher in TEACHERS
        if gs.subject in teacher.subjects
    ]
    for var in variables
}
# Constraints
constraints = []


# Constraint: A teacher cannot teach more than one class at the same time
def teacher_conflict_constraint(assignment):
    teacher_times = {}
    for var, (subject, teacher) in assignment.items():
        if subject not in teacher.subjects:
            return False
        if (teacher, var.day, var.timeslot) in teacher_times:
            return False
        teacher_times[(teacher, var.day, var.timeslot)] = True
    return True


constraints.append(teacher_conflict_constraint)


# Constraint: Ensure each subject is taught the required number of hours per week for each group
def subject_frequency_constraint(assignment):
    counter = {(group, gs.subject): 0 for group in GROUPS for gs in group.subjects}
    for var, (subject, _) in assignment.items():
        if (var.group, subject) not in counter:
            # unsupported subject for this group
            return False
        counter[(var.group, subject)] += 1

    for group in GROUPS:
        for group_subj in group.subjects:
            if counter[(group, group_subj.subject)] > group_subj.hours:
                return False

    return True


constraints.append(subject_frequency_constraint)


# Constraint: No group should have more than one class at a time
def timeslot_availability_within_a_group_constraint(assignment):
    for var1, _ in assignment.items():
        for var2, _ in assignment.items():
            if (
                var1.group == var2.group
                and var1.day == var2.day
                and var1.timeslot == var2.timeslot
                and id(var1) != id(var2)  # TODO: does it work?
            ):
                # print("timeslot_availability_constraint failed")
                return False
    return True


constraints.append(timeslot_availability_within_a_group_constraint)


def select_unassigned_variable(variables, assignment, domains):
    unassigned_vars = [v for v in variables if v not in assignment]

    # If there are no unassigned variables left, return None
    if not unassigned_vars:
        return None

    # Choose the variable with the fewest remaining values in its domain
    # Break ties using the degree heuristic (number of constraints involving the variable)
    def heuristic(var):
        num_remaining_values = len(domains[var])
        degree = sum(
            1
            for other_var in variables
            if var != other_var
            and not other_var in assignment
            and set(domains[var]).intersection(domains[other_var])
        )
        return (num_remaining_values, -degree)

    return min(unassigned_vars, key=heuristic)


def backtrack(assignment, depth=0):
    if len(assignment) == TOTAL_SLOTS_TO_BE_FILLED:
        return assignment

    var = select_unassigned_variable(variables, assignment, domains)
    if var is None:
        return None

    possible_values = copy.copy(domains[var])
    random.shuffle(possible_values)

    for possible_value in possible_values:
        new_assignment = assignment.copy()
        new_assignment[var] = possible_value

        if all(constraint(new_assignment) for constraint in constraints):
            result = backtrack(new_assignment, depth + 1)
            if result is not None:
                return result
        else:
            print(f"Constraint failed at depth {depth} for {new_assignment}")

    return None


def print_timetable(solution):
    if not solution:
        print("No solution found.")
        return

    # Organizing the solution
    timetable = {
        group.name: {day: {ts: None for ts in timeslots} for day in days}
        for group in GROUPS
    }
    for var, (subject, teacher) in solution.items():
        timetable[var.group.name][var.day][var.timeslot] = (subject.name, teacher.name)

    # Printing the timetable
    for group_name, group_timetable in timetable.items():
        print(f"Timetable for {group_name}:")
        for day, day_schedule in group_timetable.items():
            print(f"  {day}:")
            for timeslot, session in day_schedule.items():
                if session:
                    subject_name, teacher_name = session
                    print(
                        f"    Timeslot {timeslot}: {subject_name} (Taught by: {teacher_name})"
                    )
                else:
                    print(f"    Timeslot {timeslot}: Free")
            print()
        print("-" * 40)


def main():
    for var in variables:
        if not domains[var]:
            print(f"Empty domain for variable: {var}")
            return None  # or handle accordingly

    # Solve the CSP
    result = backtrack({})
    if result is None:
        print("No solution found")
        return None

    print_timetable(result)

    return result


solution = main()
print(solution)
