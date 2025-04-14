import datetime
import random

from scheduler.timetable.models import TimeTable

import scheduler.algorithm.genetic as genetic
import scheduler.algorithm.utils as utils
from scheduler.algorithm.fitness import Fitness, get_fitness
from scheduler.algorithm.slot import Slot
from scheduler.algorithm.date_time_slot import DateTimeSlot


def create(sections, slots_per_day, room_list):
    slots = []
    for section in sections:
        preferred_slot = random.choice(section.faculty.slot_choices)
        # Overflow of section outside the available hours
        time_overflow = max((preferred_slot.time + section.duration) - 1 - slots_per_day, 0) # 1 based indexing for time
        offset = random.randrange(time_overflow, section.duration)
        time = preferred_slot.time - offset
        slots.append(
            Slot(
                DateTimeSlot(preferred_slot.day, time),
                random.choice(section.course.rooms) if section.course.rooms else random.choice(room_list),
                section
            )
        )
    return slots


def mutate(slots, days_per_week, slots_per_day, room_list):
    slot = random.choice(slots)
    if random.random() < 0.5:
        preferred_slot = random.choice(slot.section.faculty.slot_choices)
        day = preferred_slot.day
        # Overflow of section outside the available hours
        time_overflow = max((preferred_slot.time + slot.section.duration) - 1 - slots_per_day, 0) # 1 based indexing for time
        offset = random.randrange(time_overflow, slot.section.duration)
        time = preferred_slot.time - offset
        slot.datetime = DateTimeSlot(day, time)
        slot.room = random.choice(slot.section.course.rooms) if slot.section.course.rooms else random.choice(room_list)
    else:
        random_slot = utils.generate_random_slot(days_per_week, slots_per_day)
        day = random_slot.day
        # Overflow of section outside the available hours
        time_overflow = max((random_slot.time + slot.section.duration) - 1 - slots_per_day, 0) # 1 based indexing for time
        offset = random.randrange(time_overflow, slot.section.duration)
        time = random_slot.time - offset
        slot.datetime = DateTimeSlot(day, time)
        slot.room = random.choice(slot.section.course.rooms) if slot.section.course.rooms else random.choice(room_list)


def display(schedule, start_time):
    time_diff = datetime.datetime.now() - start_time
    print(f"Fitness: {schedule.fitness}\t{time_diff}")

class Scheduler():
    def __init__(self, **kwargs):
        self.org_id = kwargs['org_id']
        self.timetable_id = kwargs['timetable_id']

    def run(self):
        start_time = datetime.datetime.now()

        org_id = self.org_id
        timetable_id = self.timetable_id

        days_per_week, slots_per_day = utils.get_days_and_slots(org_id)
        room_list = utils.get_rooms(org_id=org_id)
        faculty_list = utils.get_faculties(org_id=org_id)
        group_count, sections = utils.get_group_count_and_sections(org_id=org_id, timetable_id=timetable_id)


        print(f"Group Count: {group_count}")

        for room in room_list:
            print(f"{room}")

        for faculty in faculty_list:
            print(f"{faculty}")

        for section in sections:
            print(f"{section}")


        def fnGetFitness(slots):
            return get_fitness(slots, days_per_week, faculty_list, group_count)

        def fnCreate():
            return create(sections, slots_per_day, room_list)

        def fnMutate(slots):
            return mutate(slots, days_per_week, slots_per_day, room_list)

        def fnDisplay(schedule):
            display(schedule, start_time)

        max_age = 100
        scheduler = genetic.GeneticAlgorithm(fnGetFitness, fnCreate, fnMutate, fnDisplay, max_age)

        optimal_fitness = Fitness(0, 0, 0, 1, 1)
        time_limit = 10
        best = scheduler.get_best(optimal_fitness, time_limit)

        print(best.fitness)

        utils.save_slots_to_db(best.slots, org_id)

