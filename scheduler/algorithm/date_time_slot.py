class DateTimeSlot:

    def __init__(self, day, time):
        self.day = day 
        self.time = time

    def __eq__(self, other):
        return (isinstance(other, DateTimeSlot)
                and self.day == other.day
                and self.time == other.time)

    def __hash__(self):
        return hash(self.day) ^ hash(self.time)

    def __str__(self):
        return f"Day: {self.day} Time: {self.time}"