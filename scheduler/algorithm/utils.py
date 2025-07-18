import random

from django.db import transaction

from scheduler.timetable.models import TimeTable, Slot as DB_Slot, Section as DB_Section
from scheduler.organization.models import Organization
from scheduler.models import DateTimeSlot as DB_DateTimeSlot
from scheduler.room.models import Room as DB_Room
from scheduler.faculty.models import Faculty as DB_Faculty

from .course import Course
from .date_time_slot import DateTimeSlot
from .faculty import Faculty
from .group import Group
from .room import Room
from .section import Section


def generate_random_slot(days_per_week, slots_per_day):
    day = random.randint(1, days_per_week)
    time = random.randint(1, slots_per_day)
    return DateTimeSlot(day, time)


def get_days_and_slots(org_id):
    """Return the days per week and slots per day for any organization"""
    try:
        organization = Organization.objects.get(id=org_id)
        return organization.days_per_week, organization.slots_per_day
    except Organization.DoesNotExist:
        raise ValueError(f"Organization with id {org_id} does not exist")


def get_date_time_slot(date_time_slot):
    """Convert DateTimeSlot db object to DateTimeSlot object"""
    if not date_time_slot:
        raise ValueError("DateTimeSlot cannot be None")
    return DateTimeSlot(date_time_slot.day, date_time_slot.time)


def get_faculty_object(faculty):
    """Convert Faculty db object to Faculty object"""
    if not faculty:
        raise ValueError("Faculty cannot be None")
    slot_choices = [
        get_date_time_slot(date_time_slot) 
        for date_time_slot in faculty.slot_choices.all()
    ]
    return Faculty(faculty.faculty_id, faculty.priority, slot_choices)


def get_room_object(room):
    """Convert Room db object to Room object"""
    if not room:
        raise ValueError("Room cannot be None")
    return Room(room.room_id, room.capacity)


def get_course_object(course):
    """Convert Course db object to Course object"""
    if not course:
        raise ValueError("Course cannot be None")
    rooms = [
        get_room_object(room)
        for room in course.rooms.all()
    ]
    return Course(course.course_id, rooms)


def get_group_object(group):
    """Convert Group db object to Group object"""
    if not group:
        raise ValueError("Group cannot be None")
    return Group(group.group_id, group.size)


def get_rooms(org_id):
    """Fetch and convert Room db objects to Room object list"""
    try:
        rooms = DB_Room.objects.filter(
            organization__id=org_id 
        )

        room_list = [
            get_room_object(room)
            for room in rooms
        ]
        return room_list
    except Room.DoesNotExist:
        raise ValueError(f"No rooms in organization {org_id}")


def get_faculties(org_id):
    """Fetch and convert Faculty db objects to Faculty object list"""
    try:
        faculties = DB_Faculty.objects.filter(
            organization__id=org_id
        )

        faculty_list = [
            get_faculty_object(faculty)
            for faculty in faculties
        ]
        return faculty_list
    except Faculty.DoesNotExist:
        raise ValueError(f"No faculties for organization {org_id}")




def get_group_count_and_sections(org_id, timetable_id):
    """Fetch group count and convert Section db objects to Section object list"""
    try:
        timetable = TimeTable.objects.get(
            organization__id=org_id, 
            timetable_id=timetable_id
        )
        # Prefetch related objects for better performance
        sections = timetable.section_set.prefetch_related(
            'faculty__slot_choices', 'course', 'group'
        ).all()

        section_list = [
            Section(
                id=section.id,
                faculty=get_faculty_object(section.faculty),
                course=get_course_object(section.course),
                group=get_group_object(section.group),
                duration=section.duration
            )
            for section in sections
        ]
        groups = {section.group.group_id for section in section_list}
        return len(groups), section_list
    except TimeTable.DoesNotExist:
        raise ValueError(f"TimeTable with id {timetable_id} for organization {org_id} not found")


def save_slots_to_db(slots, org_id):
    """Create or update Slot entries in the database.

    - If *any* section already has a slot, update all existing sections' slots.
    - Otherwise, create new slots for all.

    Args:
        slots: List of Slot objects with section, room, and datetime attributes
        org_id: Organization ID

    Raises:
        ValueError: If any related object (Section, Room, DateTimeSlot) is not found
    """
    with transaction.atomic():
        section_ids = [slot.section.id for slot in slots]
        room_ids = [slot.room.room_id for slot in slots]
        datetime_keys = {(slot.datetime.day, slot.datetime.time) for slot in slots}

        # Validate Sections
        sections = {s.id: s for s in DB_Section.objects.filter(id__in=section_ids)}
        missing_sections = set(section_ids) - set(sections.keys())
        if missing_sections:
            raise ValueError(f"Sections with IDs {missing_sections} do not exist")

        # Validate Rooms
        rooms = {
            r.room_id: r
            for r in DB_Room.objects.filter(organization__id=org_id, room_id__in=room_ids)
        }
        missing_rooms = set(room_ids) - set(rooms.keys())
        if missing_rooms:
            raise ValueError(f"Rooms with IDs {missing_rooms} do not exist for organization {org_id}")

        # Validate DateTimeSlots
        date_time_slots = {
            (d.day, d.time): d
            for d in DB_DateTimeSlot.objects.filter(
                organization__id=org_id,
                day__in=[k[0] for k in datetime_keys],
                time__in=[k[1] for k in datetime_keys]
            )
        }
        missing_dts = datetime_keys - set(date_time_slots.keys())
        if missing_dts:
            raise ValueError(f"DateTimeSlots {missing_dts} do not exist for organization {org_id}")

        # Check if any section already has a DB_Slot
        existing_slot_map = {
            slot.section.id: slot
            for slot in DB_Slot.objects.filter(section__id__in=section_ids)
        }
        should_update = bool(existing_slot_map)  # If any slot exists

        if should_update:
            to_update = []
            for slot in slots:
                db_slot = existing_slot_map.get(slot.section.id)
                if db_slot:
                    db_slot.room = rooms[slot.room.room_id]
                    db_slot.date_time_slot = date_time_slots[(slot.datetime.day, slot.datetime.time)]
                    to_update.append(db_slot)
                else:
                    # Slot missing for an existing section: create it
                    to_update.append(DB_Slot(
                        section=sections[slot.section.id],
                        room=rooms[slot.room.room_id],
                        date_time_slot=date_time_slots[(slot.datetime.day, slot.datetime.time)]
                    ))
            DB_Slot.objects.bulk_update(
                [s for s in to_update if s.id], ['room', 'date_time_slot']
            )
            DB_Slot.objects.bulk_create(
                [s for s in to_update if not s.id]
            )
            return to_update
        else:
            to_create = [
                DB_Slot(
                    section=sections[slot.section.id],
                    room=rooms[slot.room.room_id],
                    date_time_slot=date_time_slots[(slot.datetime.day, slot.datetime.time)]
                )
                for slot in slots
            ]
            DB_Slot.objects.bulk_create(to_create)
            return to_create
