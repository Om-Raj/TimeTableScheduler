class Room:

    def __init__(self, room_id, capacity):
        self.room_id = room_id
        self.capacity = capacity

    def __eq__(self, other):
        return isinstance(other, Room) and self.room_id == other.room_id

    def __hash__(self):
        return hash(self.room_id)

    def __str__(self):
        return f"{self.room_id}"