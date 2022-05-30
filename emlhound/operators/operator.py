class Operator():
    """Base EML Operator Class"""

    def __init__(self,name="Unnamed Operator", description="No description"):
        self.name=name
        self.type="Base_Operator"
        self.description=description

    def setup(self):
        pass

    def run(self):
        pass