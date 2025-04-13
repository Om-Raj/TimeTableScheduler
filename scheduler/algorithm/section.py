class Section:

    def __init__(self, id, faculty, course, group, duration):
        self.id = id
        self.faculty = faculty
        self.course = course
        self.group = group
        self.duration = duration
        # self.seats_required = group.group_size


    def __str__(self):
        return f"({self.faculty}, {self.course}, {self.group})"

