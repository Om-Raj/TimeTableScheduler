class Slot:

    def __init__(self, datetime, room, section):
        self.datetime = datetime
        self.room = room
        self.section = section

    def __str__(self):
        return f"[{self.datetime}, Duration: {self.section.duration}, Room: {self.room}, Section: {self.section}]"