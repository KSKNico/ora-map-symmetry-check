class Resource:
    def __init__(self, _type, _density):
        self.type = _type
        self.density = _density
    def __str__(self):
        return "Type: " + str(self.type) + " Density: " + str(self.density)
    def __repr__(self):
        return "Type: " + str(self.type) + " Density: " + str(self.density)