from collections import defaultdict

from .date_time_slot import DateTimeSlot

class Fitness:

    def __init__(self, room_conflict, faculty_conflict, group_conflict, faculty_preference_ratio, lunch_overlap_ratio):
        self.room_conflict = room_conflict
        self.faculty_conflict = faculty_conflict
        self.group_conflict = group_conflict
        self.total_conflict = room_conflict + faculty_conflict + group_conflict

        self.faculty_preference_ratio = faculty_preference_ratio
        self.lunch_overlap_ratio = lunch_overlap_ratio
        self.constraint_score = 80 * faculty_preference_ratio + 20 * lunch_overlap_ratio

    def __gt__(self, other):
        if self.total_conflict == other.total_conflict:
            return self.constraint_score > other.constraint_score
        return self.total_conflict < other.total_conflict

    def __str__(self):
        return f"Conflicts: {self.total_conflict} ({self.room_conflict}+{self.faculty_conflict}+{self.group_conflict})\t Ratio: [P:{self.faculty_preference_ratio}, L:{self.lunch_overlap_ratio}]\t Score: {self.constraint_score}"


def get_fitness(slots, max_days, faculty_list, group_count):
    room_conflict = get_room_conflict(slots)
    faculty_conflict = get_faculty_conflict(slots)
    group_conflict = get_group_conflict(slots)

    faculty_preference_ratio = get_faculty_preference(slots, faculty_list)
    lunch_overlap_ratio = get_lunch_overlap(slots, max_days, [4, 5], group_count)

    return Fitness(room_conflict, faculty_conflict, group_conflict, faculty_preference_ratio, lunch_overlap_ratio)

def get_room_conflict(slots):
    room_occupied = set()
    total_rooms = 0
    for slot in slots:
        total_rooms += slot.section.duration
        for hour in range(slot.section.duration):
            room_occupied.add((slot.datetime.day, slot.datetime.time + hour, slot.room))
    return total_rooms - len(room_occupied)

def get_faculty_conflict(slots):
    faculty_assigned = set()
    total_faculties = 0
    for slot in slots:
        total_faculties += slot.section.duration
        for hour in range(slot.section.duration):
            faculty_assigned.add((slot.datetime.day, slot.datetime.time + hour, slot.section.faculty))
    return total_faculties - len(faculty_assigned)

def get_group_conflict(slots):
    group_assigned = set()
    total_groups = 0
    for slot in slots:
        total_groups += slot.section.duration
        for hour in range(slot.section.duration):
            group_assigned.add((slot.datetime.day, slot.datetime.time + hour, slot.section.group))
    return total_groups - len(group_assigned)

def get_faculty_preference(slots, faculty_list):
    max_score = score = 0

    # Number of sections (1 hour equivalent sections) a faculty teaches in a week
    faculty_section_count = defaultdict(int)
    for slot in slots:
        faculty_section_count[slot.section.faculty.faculty_id] += slot.section.duration
        for hour in range(slot.section.duration):
            if DateTimeSlot(slot.datetime.day, slot.datetime.time + hour) in slot.section.faculty.slot_choices:
                score += slot.section.faculty.priority

    for faculty in faculty_list:
        max_good_slots = min(faculty_section_count[faculty.faculty_id], len(faculty.slot_choices))
        max_score += max_good_slots * faculty.priority

    return score / max(max_score, 1)


def get_lunch_overlap(slots, max_days, lunch_time_slots, group_count):
    group_lunch_overlap = defaultdict(int)
    for slot in slots:
        for hour in range(slot.section.duration):
            if slot.datetime.time + hour in lunch_time_slots:
                group_lunch_overlap[(slot.section.group, slot.datetime.day)] += 1
    day_score = 9
    zero_overlap_score = group_count * max_days * day_score
    lunch_overlap = 0
    for value in group_lunch_overlap.values():
        lunch_overlap += value ** 3    # Give worse score for more overlap
    return (zero_overlap_score - lunch_overlap) / max(zero_overlap_score, 1)
