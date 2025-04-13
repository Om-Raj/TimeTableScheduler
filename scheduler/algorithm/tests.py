from django.test import TestCase
from scheduler.organization.models import Organization
from scheduler.models import DateTimeSlot as DB_DateTimeSlot
from scheduler.room.models import Room as DB_Room
from scheduler.course.models import Course as DB_Course
from scheduler.faculty.models import Faculty as DB_Faculty
from scheduler.group.models import Group as DB_Group
from scheduler.timetable.models import TimeTable, Section as DB_Section
from scheduler.timetable.models import Slot as DB_Slot

from .utils import (
    get_days_and_slots,
    get_date_time_slot,
    get_faculty_object,
    get_room_object,
    get_course_object,
    get_group_object,
    get_group_count_and_sections,
    save_slots_to_db
)

from .date_time_slot import DateTimeSlot
from .room import Room
from .course import Course
from .faculty import Faculty
from .group import Group
from .section import Section
from .slot import Slot

class UtilityFunctionTests(TestCase):
    def setUp(self):
        self.org = Organization.objects.create(
            name="Test Org", days_per_week=5, slots_per_day=6
        )

        self.dts1 = DB_DateTimeSlot.objects.create(organization=self.org, day=1, time=1)
        self.room1 = DB_Room.objects.create(organization=self.org, room_id="R1", capacity=40)
        self.course1 = DB_Course.objects.create(
            organization=self.org, course_id="CSE101", title="Intro to CS"
        )
        self.course1.rooms.add(self.room1)

        self.faculty1 = DB_Faculty.objects.create(
            organization=self.org, faculty_id="F001", name="John Doe", priority=1
        )
        self.faculty1.slot_choices.add(self.dts1)

        self.group1 = DB_Group.objects.create(
            organization=self.org, group_id="G1", size=30
        )

        self.timetable = TimeTable.objects.create(
            organization=self.org, timetable_id="2025-Spring-1", year=2025, semester="Spring"
        )

        self.section = DB_Section.objects.create(
            timetable=self.timetable,
            faculty=self.faculty1,
            course=self.course1,
            group=self.group1,
            duration=2
        )

    def test_get_days_and_slots(self):
        days, slots = get_days_and_slots(self.org.id)
        self.assertEqual(days, 5)
        self.assertEqual(slots, 6)

    def test_get_date_time_slot(self):
        slot = get_date_time_slot(self.dts1)
        self.assertEqual(slot, DateTimeSlot(day=1, time=1))

    def test_get_faculty_object(self):
        fac_obj = get_faculty_object(self.faculty1)
        self.assertEqual(fac_obj.faculty_id, "F001")
        self.assertEqual(fac_obj.priority, 1)
        self.assertEqual(fac_obj.slot_choices, [DateTimeSlot(1, 1)])

    def test_get_room_object(self):
        room_obj = get_room_object(self.room1)
        self.assertEqual(room_obj.room_id, "R1")
        self.assertEqual(room_obj.capacity, 40)

    def test_get_course_object(self):
        course_obj = get_course_object(self.course1)
        self.assertEqual(course_obj.course_id, "CSE101")
        self.assertEqual(course_obj.rooms, [Room("R1", 40)])

    def test_get_group_object(self):
        group_obj = get_group_object(self.group1)
        self.assertEqual(group_obj.group_id, "G1")
        self.assertEqual(group_obj.size, 30)

    def test_get_group_count_and_sections(self):
        # Add another section with the same group to test group uniqueness
        DB_Section.objects.create(
            timetable=self.timetable,
            faculty=self.faculty1,
            course=self.course1,
            group=self.group1,  # same group
            duration=1
        )

        count, sections = get_group_count_and_sections(self.org.id, self.timetable.timetable_id)

        self.assertEqual(count, 1)  # Only one unique group: group1
        self.assertEqual(len(sections), 2)  # Two sections present
        self.assertTrue(all(isinstance(section, Section) for section in sections))

        # Check that all fields are mapped correctly for one of the sections
        section_obj = sections[0]
        self.assertEqual(section_obj.faculty.faculty_id, "F001")
        self.assertEqual(section_obj.course.course_id, "CSE101")
        self.assertEqual(section_obj.group.group_id, "G1")


    def test_save_slots_to_db(self):
        section_obj = Section(
            id=self.section.id,
            faculty=get_faculty_object(self.faculty1),
            course=get_course_object(self.course1),
            group=get_group_object(self.group1),
            duration=2
        )
        slot_obj = Slot(
            section=section_obj,
            room=get_room_object(self.room1),
            datetime=DateTimeSlot(day=1, time=1)
        )
        db_slots = save_slots_to_db([slot_obj], self.org.id)
        self.assertEqual(len(db_slots), 1)
        self.assertTrue(DB_Slot.objects.filter(section=self.section).exists())
