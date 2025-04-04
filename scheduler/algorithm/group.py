class Group:

    def __init__(self, group_id, size):
        self.group_id = group_id
        self.size = size

    def __eq__(self, other):
        return isinstance(other, Group) and self.group_id == other.group_id

    def __hash__(self):
        return hash(self.group_id)

    def __str__(self):
        return f"{self.group_id}"
