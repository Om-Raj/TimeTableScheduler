from django.db import transaction

from scheduler.timetable.models import TimeTable, Slot as DB_Slot, Section as DB_Section
from scheduler.organization.models import Organization
from scheduler.models import DateTimeSlot as DB_DateTimeSlot
from scheduler.room.models import Room as DB_Room

from .course import Course
from .date_time_slot import DateTimeSlot
from .faculty import Faculty
from .group import Group
from .room import Room
from .section import Section



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


def get_sections(org_id, timetable_id):
    """Fetch and convert Section db objects to Section object list"""
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
        return section_list
    except TimeTable.DoesNotExist:
        raise ValueError(f"TimeTable with id {timetable_id} for organization {org_id} not found")


def save_slots_to_db(slots, org_id):
    """Save a list of Slot objects to the database as DB_Slot instances.

    Args:
        slots: List of Slot objects with section, room, and datetime attributes
        org_id: Organization ID
        timetable_id: Timetable ID (unused in original, included for context)

    Raises:
        ValueError: If any related object (Section, Room, DateTimeSlot) is not found
    """
    with transaction.atomic():  # Ensure all-or-nothing save
        # Pre-fetch related objects to minimize queries
        section_ids = [slot.section.id for slot in slots]
        room_ids = [slot.room.room_id for slot in slots]
        datetime_keys = [(slot.datetime.day, slot.datetime.time) for slot in slots]

        # Bulk fetch sections
        sections = {s.id: s for s in DB_Section.objects.filter(id__in=section_ids)}
        missing_sections = set(section_ids) - set(sections.keys())
        if missing_sections:
            raise ValueError(f"Sections with IDs {missing_sections} do not exist")

        # Bulk fetch rooms
        rooms = {r.room_id: r for r in DB_Room.objects.filter(org_id=org_id, room_id__in=room_ids)}
        missing_rooms = set(room_ids) - set(rooms.keys())
        if missing_rooms:
            raise ValueError(f"Rooms with IDs {missing_rooms} do not exist for organization {org_id}")

        # Bulk fetch date_time_slots
        date_time_slots = {
            (d.day, d.time): d 
            for d in DB_DateTimeSlot.objects.filter(
                org_id=org_id, 
                day__in=[k[0] for k in datetime_keys], 
                time__in=[k[1] for k in datetime_keys]
            )
        }
        missing_dts = set(datetime_keys) - set(date_time_slots.keys())
        if missing_dts:
            raise ValueError(f"DateTimeSlots {missing_dts} do not exist for organization {org_id}")

        # Create DB_Slot objects
        db_slots = [
            DB_Slot(
                section=sections[slot.section.id],
                room=rooms[slot.room.room_id],
                date_time_slot=date_time_slots[(slot.datetime.day, slot.datetime.time)]
            )
            for slot in slots
        ]

        # Bulk save all slots
        DB_Slot.objects.bulk_create(db_slots)

    return db_slots  # Optional: return saved objects if needed