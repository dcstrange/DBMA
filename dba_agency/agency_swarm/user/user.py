import uuid
class User:
    name: str = "User"

    def __init__(self, name: str = None):
        # later, we can add more attributes to the user like bio, etc
        self.uuid = uuid.uuid4()
        pass
