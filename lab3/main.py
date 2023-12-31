import random
from typing import List

import pydantic


class BaseModel(pydantic.BaseModel):
    def __repr__(self):
        return f"{self.__class__.__name__}({', '.join(self.model_dump(mode='python'))})"

    def __str__(self):
        return repr(self)


class Group(BaseModel):
    name: str
    required_subjects: List[str]

    def __init__(self, name: str, required_subjects: List[str]) -> None:
        super().__init__(name=name, required_subjects=required_subjects)

    def __hash__(self):
        return hash((self.name, tuple(self.required_subjects)))


class Teacher(BaseModel):
    name: str
    available_time: int
    knowledgeable_subjects: List[str]

    def __init__(
        self, name: str, available_time: int, knowledgeable_subjects: List[str]
    ) -> None:
        super().__init__(
            name=name,
            available_time=available_time,
            knowledgeable_subjects=knowledgeable_subjects,
        )

    def __hash__(self):
        return hash(self.name)


class Timeslot(BaseModel):
    subject_id: int
    teacher_id: int
    group_id: int

    def __init__(self, subject_id: int, teacher_id: int, group_id: int) -> None:
        super().__init__(
            subject_id=subject_id, teacher_id=teacher_id, group_id=group_id
        )

    def __hash__(self):
        return hash((self.subject_id, self.teacher_id, self.group_id))


class Schedule:
    def __init__(self, subjects, teachers, groups, days, timeslots_per_day):
        self.subjects = subjects
        self.teachers = teachers
        self.groups = groups
        self.days = days
        self.timeslots_per_day = timeslots_per_day
        self.timetable = self.generate_random_schedule()

    def generate_random_schedule(self):
        timetable_size = len(self.days) * self.timeslots_per_day
        timetable = []

        for _ in range(timetable_size):
            timetable.append(
                Timeslot(
                    random.randint(0, len(self.subjects) - 1),
                    random.randint(0, len(self.teachers) - 1),
                    random.randint(0, len(self.groups) - 1),
                )
            )

        return timetable

    def check_correctness(self):
        conflicts = 0
        # Teacher's available time conflict
        for i in range(len(self.teachers)):
            if (
                len([t for t in self.timetable if t.teacher_id == i])
                > self.teachers[i].available_time
            ):
                conflicts += 1

        # Subject conflict
        for timeslot in self.timetable:
            # Teachers
            if (
                self.subjects[timeslot.subject_id]
                not in self.teachers[timeslot.teacher_id].knowledgeable_subjects
            ):
                conflicts += 1

            # Groups
            if (
                self.subjects[timeslot.subject_id]
                not in self.groups[timeslot.group_id].required_subjects
            ):
                conflicts += 1

        return 1.0 / (conflicts + 1.0)


class GeneticAlgorithm:
    def __init__(self, population_size):
        self.population = self.generate_population(population_size)

    def generate_population(self, population_size):
        return [
            Schedule(SUBJECTS, teachers, GROUPS, DAYS, TIMESLOTS_PER_DAY)
            for _ in range(population_size)
        ]

    def create_offspring(self, schedule1, schedule2):
        crossover_point1 = random.randint(1, len(schedule1.timetable) - 2)
        crossover_point2 = random.randint(1, len(schedule1.timetable) - 2)
        start = min(crossover_point1, crossover_point2)
        end = max(crossover_point1, crossover_point2)
        child1 = Schedule(
            schedule1.subjects,
            schedule1.teachers,
            schedule1.groups,
            schedule1.days,
            schedule1.timeslots_per_day,
        )
        child2 = Schedule(
            schedule2.subjects,
            schedule2.teachers,
            schedule2.groups,
            schedule2.days,
            schedule2.timeslots_per_day,
        )
        child1.timetable = (
            schedule1.timetable[:start]
            + schedule2.timetable[start:end]
            + schedule1.timetable[end:]
        )

        child2.timetable = (
            schedule2.timetable[:start]
            + schedule1.timetable[start:end]
            + schedule2.timetable[end:]
        )

        return child1, child2

    def select_best(self, fitness_scores):
        best_index = fitness_scores.index(max(fitness_scores))
        return self.population[best_index], fitness_scores[best_index]

    def mutate(self, schedule):
        import random

        if random.random() < MUTATION_RATE:
            timeslot_id = random.randint(
                0, len(schedule.days) * schedule.timeslots_per_day - 1
            )
            timeslot = schedule.timetable[timeslot_id]

            timeslot_property = random.randint(0, 2)

            if timeslot_property == 0:
                timeslot.subject_id = random.randint(0, len(schedule.subjects) - 1)
            elif timeslot_property == 1:
                for _ in range(20):
                    timeslot.teacher_id = random.randint(0, len(schedule.teachers) - 1)

                    if (
                        schedule.subjects[timeslot.subject_id]
                        in schedule.teachers[timeslot.teacher_id].knowledgeable_subjects
                    ):
                        break
            else:
                for _ in range(20):
                    timeslot.group_id = random.randint(0, len(schedule.groups) - 1)

                    if (
                        schedule.subjects[timeslot.subject_id]
                        in schedule.groups[timeslot.group_id].required_subjects
                    ):
                        break

        return schedule

    def tournament_selection(self, k: int) -> Schedule:
        contenders = random.sample(self.population, k)
        fitness_scores = [schedule.check_correctness() for schedule in contenders]
        winner_index = fitness_scores.index(max(fitness_scores))
        return contenders[winner_index]

    def start(self) -> (Schedule, float):
        best_schedule = None
        best_fitness_score = 0

        for generation in range(GENERATIONS):
            fitness_scores = [
                schedule.check_correctness() for schedule in self.population
            ]

            schedule, fitness_score = self.select_best(fitness_scores)
            best_schedule = schedule
            best_fitness_score = fitness_score

            new_population = []

            while len(new_population) < POPULATION_SIZE:
                parent1 = self.tournament_selection(3)  # Турнір між 3 кандидатами
                parent2 = self.tournament_selection(3)  # Турнір між 3 кандидатами
                child1, child2 = self.create_offspring(parent1, parent2)
                new_population.extend([self.mutate(child1), self.mutate(child2)])

            self.population = new_population

        return best_schedule, best_fitness_score


# Constants
TIMESLOTS_PER_DAY = 3
POPULATION_SIZE = 20
MUTATION_RATE = 0.1
GENERATIONS = 100

DAYS = ["Понеділок", "Вівторок", "Середа", "Четвер", "П'ятниця"]
SUBJECTS = [
    "Програмування",
    "Дискретна математика",
    "Іноземна мова",
    "Філософія",
    "Алгоритміка",
]
teachers = [
    Teacher("Камаз Павлович", 6, ["Програмування", "Дискретна математика"]),
    Teacher("Макар Бьорнович", 4, ["Іноземна мова"]),
    Teacher("Монстр Хайнєкен", 5, ["Філософія", "Іноземна мова"]),
    Teacher("Замир Безрусні", 2, ["Програмування", "Філософія", "Алгоритміка"]),
]

GROUPS = [
    Group("TK-41", ["Дискретна математика", "Програмування"]),
    Group("MI-2", ["Програмування", "Іноземна мова", "Філософія"]),
    Group("TTП-41", ["Філософія", "Алгоритміка"]),
]


# Running the genetic algorithm
genetic = GeneticAlgorithm(POPULATION_SIZE)
best_schedule, best_fitness_score = genetic.start()
best_schedule.timetable.reverse()

for day in DAYS:
    for slot in range(TIMESLOTS_PER_DAY):
        timeslot = best_schedule.timetable.pop()

        print(
            f"{day}, {slot+1} пара: {SUBJECTS[timeslot.subject_id]} від "
            f"{teachers[timeslot.teacher_id].name} для {GROUPS[timeslot.group_id].name}"
        )

print(f"Fitness score: {best_fitness_score}")
