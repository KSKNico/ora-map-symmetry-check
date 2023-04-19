class Tile:
	def __init__(self, _type, _index):
		self.type: int = _type
		self.index: int = _index
		self.terrain: str = ""
	def __str__(self):
		return "Type: " + str(self.type) + " Index: " + str(self.index) + " Terrain: " + self.terrain
	def __repr__(self):
		return "Type: " + str(self.type) + " Index: " + str(self.index) + " Terrain: " + self.terrain