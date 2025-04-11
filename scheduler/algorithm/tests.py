from django.test import TestCase
from types import SimpleNamespace

from scheduler.algorithm.utils import (
    get_days_and_slots,
    get_date_time_slot,
    get_faculty_object,
    get_room_object,
    get_course_object,
    get_group_object,
    get_sections,
    save_slots_to_db,
)
from scheduler.organization.models import Organization
from scheduler.timetable.models import TimeTable, Section as DB_Section, Slot as DB_Slot
from scheduler.models import DateTimeSlot as DB_DateTimeSlot
from scheduler.room.models import Room as DB_Room
from scheduler.faculty.models import Faculty as DB_Faculty
from scheduler.course.models import Course as DB_Course
from scheduler.group.models import Group as DB_Group

class UtilsFunctionTests(TestCase):
    """
    Test class for utility functions in scheduler.algorithm.utils.
    """
    def setUp(self):
        """Set up common test data: an organization."""
        self.org = Organization.objects.create(name="Test Org", days_per_week=5, slots_per_day=8)

    ### Tests for get_days_and_slots
    def test_get_days_and_slots_valid(self):
        """Test get_days_and_slots with a valid organization ID."""
        days, slots = get_days_and_slots(self.org.id)
        self.assertEqual(days, 5)
        self.assertEqual(slots, 8)

    def test_get_days_and_slots_invalid(self):
        """Test get_days_and_slots with an invalid organization ID."""
        with self.assertRaises(ValueError):
            get_days_and_slots(999)

    ### Tests for get_date_time_slot
    def test_get_date_time_slot_valid(self):
        """Test get_date_time_slot with a valid DateTimeSlot object."""
        db_dt_slot = DB_DateTimeSlot.objects.create(day="Monday", time="09:00")
        result = get_date_time_slot(db_dt_slot)
        self.assertEqual(result.day, "Monday")
        self.assertEqual(result.time, "09:00")

    def test_get_date_time_slot_none(self):
        """Test get_date_time_slot with None input."""
        with self.assertRaises(ValueError):
            get_date_time_slot(None)

    ### Tests for get_faculty_object
    def test_get_faculty_object_valid(self):
        """Test get_faculty_object with a valid Faculty object."""
        db_dt_slot1 = DB_DateTimeSlot.objects.create(day="Monday", time="09:00")
        db_dt_slot2 = DB_DateTimeSlot.objects.create(day="Tuesday", time="10:00")
        db_faculty = DB_Faculty.objects.create(
            organization=self.org, faculty_id="F1", name="Dr. Smith", priority=1
        )
        db_faculty.slot_choices.add(db_dt_slot1, db_dt_slot2)
        result = get_faculty_object(db_faculty)
        self.assertEqual(result.faculty_id, "F1")
        self.assertEqual(result.priority, 1)
        self.assertEqual(len(result.slot_choices), 2)
        self.assertEqual(result.slot_choices[0].day, "Monday")
        self.assertEqual(result.slot_choices[0].time, "09:00")
        self.assertEqual(result.slot_choices[1].day, "Tuesday")
        self.assertEqual(result.slot_choices[1].time, "10:00")

    def test_get_faculty_object_none(self):
        """Test get_faculty_object with None input."""
        with self.assertRaises(ValueError):
            get_faculty_object(None)

    ### Tests for get_room_object
    def test_get_room_object_valid(self):
        """Test get_room_object with a valid Room object."""
        db_room = DB_Room.objects.create(organization=self.org, room_id="R1", capacity=30)
        result = get_room_object(db_room)
        self.assertEqual(result.room_id, "R1")
        self.assertEqual(result.capacity, 30)

    def test_get_room_object_none(self):
        """Test get_room_object with None input."""
        with self.assertRaises(ValueError):
            get_room_object(None)

    ### Tests for get_course_object
    def test_get_course_object_valid(self):
        """Test get_course_object with a valid Course object."""
        db_room1 = DB_Room.objects.create(organization=self.org, room_id="R1", capacity=30)
        db_room2 = DB_Room.objects.create(organization=self.org, room_id="R2", capacity=40)
        db_course = DB_Course.objects.create(organization=self.org, course_id="C1", title="Math")
        db_course.rooms.add(db_room1, db_room2)
        result = get_course_object(db_course)
        self.assertEqual(result.course_id, "C1")
        self.assertEqual(len(result.rooms), 2)
        self.assertEqual(result.rooms[0].room_id, "R1")
        self.assertEqual(result.rooms[1].room_id, "R2")

    def test_get_course_object_none(self):
        """Test get_course_object with None input."""
        with self.assertRaises(ValueError):
            get_course_object(None)

    ### Tests for get_group_object
    def test_get_group_object_valid(self):
        """Test get_group_object with a valid Group object."""
        db_group = DB_Group.objects.create(organization=self.org, group_id="G1", size=25)
        result = get_group_object(db_group)
        self.assertEqual(result.group_id, "G1")
        self.assertEqual(result.size, 25)

    def test_get_group_object_none(self):
        """Test get_group_object with None input."""
        with self.assertRaises(ValueError):
            get_group_object(None)

    ### Tests for get_sections
    def test_get_sections_valid(self):
        """Test get_sections with valid org_id and timetable_id."""
        db_timetable = TimeTable.objects.create(organization=self.org, year=2023, semester="Fall")
        db_course = DB_Course.objects.create(organization=self.org, course_id="C1", title="Math")
        db_group = DB_Group.objects.create(organization=self.org, group_id="G1", size=25)
        db_faculty = DB_Faculty.objects.create(
            organization=self.org, faculty_id="F1", name="Dr. Smith", priority=1
        )
        db_section = DB_Section.objects.create(
            timetable=db_timetable, faculty=db_faculty, course=db_course, group=db_group, duration=2
        )
        sections = get_sections(self.org.id, db_timetable.timetable_id)
        self.assertEqual(len(sections), 1)
        section = sections[0]
        self.assertEqual(section.id, db_section.id)
        self.assertEqual(section.faculty.faculty_id, "F1")
        self.assertEqual(section.course.course_id, "C1")
        self.assertEqual(section.group.group_id, "G1")
        self.assertEqual(section.duration, 2)

    def test_get_sections_invalid_timetable(self):
        """Test get_sections with an invalid timetable_id."""
        with self.assertRaises(ValueError):
            get_sections(self.org.id, "nonexistent")

    ### Tests for save_slots_to_db
    def test_save_slots_to_db_valid(self):
        """Test save_slots_to_db with valid slot data."""
        db_timetable = TimeTable.objects.create(organization=self.org, year=2023, semester="Fall")
        db_course = DB_Course.objects.create(organization=self.org, course_id="C1", title="Math")
        db_group = DB_Group.objects.create(organization=self.org, group_id="G1", size=25)
        db_section = DB_Section.objects.create(timetable=db_timetable, course=db_course, group=db_group)
        db_room = DB_Room.objects.create(organization=self.org, room_id="R1", capacity=30)
        db_dt_slot = DB_DateTimeSlot.objects.create(day="Monday", time="09:00")
        
        custom_section = SimpleNamespace(id=db_section.id)
        custom_room = SimpleNamespace(room_id="R1")
        custom_datetime = SimpleNamespace(day="Monday", time="09:00")
        slot = SimpleNamespace(section=custom_section, room=custom_room, datetime=custom_datetime)
        
        save_slots_to_db([slot], self.org.id)
        
        db_slots = DB_Slot.objects.all()
        self.assertEqual(len(db_slots), 1)
        db_slot = db_slots[0]
        self.assertEqual(db_slot.section, db_section)
        self.assertEqual(db_slot.room, db_room)
        self.assertEqual(db_slot.date_time_slot, db_dt_slot)

    def test_save_slots_to_db_missing_attributes(self):
        """Test save_slots_to_db with slots missing required attributes."""
        slot = SimpleNamespace(section=None, room=None, datetime=None)
        with self.assertRaises(ValueError):
            save_slots_to_db([slot], self.org.id)

    def test_save_slots_to_db_invalid_section(self):
        """Test save_slots_to_db with a non-existent section ID."""
        custom_section = SimpleNamespace(id=999)  # Non-existent section
        custom_room = SimpleNamespace(room_id="R1")
        custom_datetime = SimpleNamespace(day="Monday", time="09:00")
        slot = SimpleNamespace(section=custom_section, room=custom_room, datetime=custom_datetime)
        with self.assertRaises(ValueError):
            save_slots_to_db([slot], self.org.id)