import copy
import random
from typing import Dict, List, Optional, Set, Tuple

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
            GroupSubject(SUBJECTS_MAP["English"], 1),
            GroupSubject(SUBJECTS_MAP["Mathematical Analysis"], 3),
            GroupSubject(SUBJECTS_MAP["Algebra and Geometry"], 3),
            GroupSubject(SUBJECTS_MAP["Physical Education"], 1),
        ],
    ),
    Group(
        "ТТП-42",
        [
            GroupSubject(SUBJECTS_MAP["Programming"], 2),
            GroupSubject(SUBJECTS_MAP["English"], 1),
            GroupSubject(SUBJECTS_MAP["Mathematical Analysis"], 3),
            GroupSubject(SUBJECTS_MAP["Algebra and Geometry"], 2),
            GroupSubject(SUBJECTS_MAP["Physical Education"], 1),
        ],
    ),
]
TOTAL_SLOTS_TO_BE_FILLED = 0
for group in GROUPS:
    for subject in group.subjects:
        TOTAL_SLOTS_TO_BE_FILLED += subject.hours


class Variable(pydantic.BaseModel):
    group: Group
    subject: Subject
    subject_no: int

    def __init__(
        self, group: Group, subject: Subject, subject_no: int, **kwargs
    ) -> None:
        kwargs["group"] = group
        kwargs["subject"] = subject
        kwargs["subject_no"] = subject_no
        super().__init__(**kwargs)

    def __hash__(self):
        return hash((self.group, self.subject, self.subject_no))

    def __repr__(self):
        return f"Variable({self.group}, {self.subject}, {self.subject_no})"

    def __str__(self):
        return repr(self)


Assignment = Dict[Variable, Tuple[str, int, Teacher]]


# Variables
variables: List[Variable] = [
    Variable(group, gs.subject, subject_no)
    for group in GROUPS
    for gs in group.subjects
    for subject_no in range(gs.hours)
]

# Domains
domains: Dict[Variable, List[Tuple[str, int, Teacher]]] = {
    var: [
        (day, timeslot, teacher)
        for day in days
        for timeslot in timeslots
        for teacher in TEACHERS
        if var.subject in teacher.subjects
    ]
    for var in variables
}

# Constraints
constraints = []


# Constraint: Ensure each subject is taught the required number of hours per week for each group
def subject_frequency_constraint(assignment: Assignment) -> bool:
    scheduled_counts = {(var.group, var.subject): 0 for var in variables}
    for var, _ in assignment.items():
        scheduled_counts[(var.group, var.subject)] += 1

    for group in GROUPS:
        for group_subject in group.subjects:
            if scheduled_counts[(group, group_subject.subject)] > group_subject.hours:
                return False

    return True


# Constraint: A teacher cannot teach more than one class at the same time
def teacher_conflict_constraint(assignment: Assignment) -> bool:
    teacher_times = {}
    for var, (day, timeslot, teacher) in assignment.items():
        if (teacher, day, timeslot) in teacher_times:
            return False
        teacher_times[(teacher, day, timeslot)] = True
    return True


# Constraint: No group should have more than one class at a time
def timeslot_availability_within_a_group_constraint(assignment: Assignment) -> bool:
    group_times = {}
    for var, (day, timeslot, _) in assignment.items():
        if (var.group, day, timeslot) in group_times:
            return False
        group_times[(var.group, day, timeslot)] = True
    return True


constraints += [
    teacher_conflict_constraint,
    timeslot_availability_within_a_group_constraint,
    subject_frequency_constraint,
]


def least_constraining_value_heuristics(
    var: Variable,
    assignment: Assignment,
    domains_: Dict[Variable, List[Tuple[str, int, Teacher]]],
) -> List[Tuple[str, int, Teacher]]:
    unassigned_vars = [v for v in variables if v not in assignment and v != var]

    def count_legal_values(value: Tuple[str, int, Teacher]) -> int:
        # Count how many legal values are left for other variables if 'value' is chosen for 'var'
        count = 0
        for other_var in unassigned_vars:
            for other_value in domains_[other_var]:
                if not constraints_conflict(var, value, other_var, other_value):
                    count += 1
        return count

    return sorted(domains_[var], key=count_legal_values, reverse=True)


def constraints_conflict(
    var1: Variable,
    value1: Tuple[str, int, Teacher],
    var2: Variable,
    value2: Tuple[str, int, Teacher],
) -> bool:
    # Check if assigning value1 to var1 and value2 to var2 would violate any constraint
    day1, timeslot1, teacher1 = value1
    day2, timeslot2, teacher2 = value2

    if var1.group == var2.group and day1 == day2 and timeslot1 == timeslot2:
        return True  # Same group cannot have two classes at the same time
    if teacher1 == teacher2 and day1 == day2 and timeslot1 == timeslot2:
        return True  # A teacher cannot teach two classes at the same time

    return False


def degree_heuristic(
    variables_: List[Variable],
    assignment: Assignment,
    domains_: Dict[Variable, List[Tuple[str, int, Teacher]]],
) -> Optional[Variable]:
    unassigned_vars = [v for v in variables_ if v not in assignment]
    if not unassigned_vars:
        return None

    def constraint_degree(var: Variable) -> int:
        count = 0
        for other_var in unassigned_vars:
            if other_var != var:
                shared_domains = set(domains_[var]) & set(domains_[other_var])
                count += len(shared_domains)
        return count

    return max(unassigned_vars, key=constraint_degree, default=None)


def least_domains_heuristics(
    variables_: List[Variable],
    assignment: Assignment,
    domains_: Dict[Variable, List[Tuple[str, int, Teacher]]],
) -> Optional[Variable]:
    unassigned_vars = [v for v in variables_ if v not in assignment]
    if not unassigned_vars:
        return None
    return min(unassigned_vars, key=lambda var: len(domains_[var]), default=None)


def select_unassigned_variable(
    variables_: List[Variable],
    assignment: Assignment,
    domains_: Dict[Variable, List[Tuple[str, int, Teacher]]],
) -> Optional[Variable]:
    unassigned_vars = [v for v in variables_ if v not in assignment]
    if not unassigned_vars:
        return None
    return unassigned_vars[0]


def backtrack(
    assignment: Assignment, depth: int = 0
) -> Optional[Dict[Variable, Tuple[str, int, Teacher]]]:
    if len(assignment) == len(variables):
        return assignment

    # #1
    # var = select_unassigned_variable(variables, assignment, domains)
    # #2
    var = least_domains_heuristics(variables, assignment, domains)
    # #3
    # var = degree_heuristic(variables, assignment, domains)

    if var is None:
        return None

    for value in least_constraining_value_heuristics(var, assignment, domains):
        new_assignment = assignment.copy()
        new_assignment[var] = value

        if all(constraint(new_assignment) for constraint in constraints):
            result = backtrack(new_assignment, depth + 1)
            if result is not None:
                return result
        else:
            print(f"Failed check at depth {depth} for {new_assignment}")

    return None


def print_timetable(
    solution: Optional[Dict[Variable, Tuple[str, int, Teacher]]]
) -> None:
    if not solution:
        print("No solution found.")
        return

    timetable = {
        group.name: {day: {ts: None for ts in timeslots} for day in days}
        for group in GROUPS
    }
    for var, (day, timeslot, teacher) in solution.items():
        timetable[var.group.name][day][timeslot] = (var.subject.name, teacher.name)

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


def main() -> Optional[Dict[Variable, Tuple[str, int, Teacher]]]:
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
