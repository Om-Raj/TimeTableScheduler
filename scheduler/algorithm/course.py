class Course:

    def __init__(self, course_id, rooms):
        self.course_id = course_id
        self.rooms = rooms

    def __str__(self):
        return f"{self.course_id}"