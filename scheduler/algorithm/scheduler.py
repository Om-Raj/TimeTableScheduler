import datetime
import random

from scheduler.timetable.models import TimeTable

import genetic
import utils
from fitness import Fitness, get_fitness
from slot import Slot


def create(sections, slots_per_day):
    slots = []
    for section in sections:
        preferred_slot = random.choice(section.faculty.slot_choices)
        # Overflow of section outside the available hours
        time_overflow = max((preferred_slot['time'] + section.duration) - slots_per_day, 0)
        offset = random.randrange(time_overflow, section.duration)
        time = preferred_slot['time'] - offset
        slots.append(Slot(preferred_slot['day'],
                          time,
                          section.course.room_id if section.course.room_id else random.choice(input.room_list)
                          , section))
    return slots


def mutate(slots, slots_per_day):
    slot = random.choice(slots)
    if random.random() < 0.5:
        preferred_slot = random.choice(slot.section.faculty.slot_choices)
        slot.day = preferred_slot['day']
        # Overflow of section outside the available hours
        time_overflow = max((preferred_slot['time'] + slot.section.duration) - slots_per_day, 0)
        offset = random.randrange(time_overflow, slot.section.duration)
        slot.time = preferred_slot['time'] - offset
        slot.room = slot.section.course.room_id if slot.section.course.room_id else random.choice(input.room_list)
    else:
        random_slot = utils.generate_slot_choices(1)[0]
        slot.day = random_slot['day']
        # Overflow of section outside the available hours
        time_overflow = max((random_slot['time'] + slot.section.duration) - slots_per_day, 0)
        offset = random.randrange(time_overflow, slot.section.duration)
        slot.time = random_slot['time'] - offset
        slot.room = slot.section.course.room_id if slot.section.course.room_id else random.choice(input.room_list)


def display(schedule, start_time):
    time_diff = datetime.datetime.now() - start_time
    print(f"Fitness: {schedule.fitness}\t{time_diff}")

class Scheduler():
    def run(self, **kwargs):
        start_time = datetime.datetime.now()

        org_id = kwargs['org_id']
        tt_id = kwargs['tt_id']

        days_per_week, slots_per_day = utils.get_days_and_slots(org_id)
        sections = utils.get_sections(org_id=org_id, timetable_id=tt_id)

        for section in sections:
            print(section)

        def fnGetFitness(slots):
            return get_fitness(slots, days_per_week)

        def fnCreate():
            return create(sections, slots_per_day)

        def fnMutate(slots):
            return mutate(slots, slots_per_day)

        def fnDisplay(schedule):
            display(schedule, start_time)

        max_age = 100
        scheduler = genetic.GeneticAlgorithm(fnGetFitness, fnCreate, fnMutate, fnDisplay, max_age)

        optimal_fitness = Fitness(0, 0, 0, 1, 1)
        time_limit = 60
        best = scheduler.get_best(optimal_fitness, time_limit)

        print(best.fitness)

        # utils.save_slots_to_db(best.slots)

