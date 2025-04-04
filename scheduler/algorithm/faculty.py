class Faculty:

    def __init__(self, faculty_id, priority, slot_choices):
        self.faculty_id = faculty_id
        self.priority = priority
        self.slot_choices = slot_choices

    def __eq__(self, other):
        return isinstance(other, Faculty) and self.faculty_id == other.faculty_id

    def __hash__(self):
        return hash(self.faculty_id)


    def __str__(self):
        return f"{self.faculty_id}"