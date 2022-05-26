class Operator():
    """Base EML Operator Class"""

    def __init__(self,name="Unnamed Operator"):
        self.name=name

    def setup(self):
        pass

    def run(self):
        pass