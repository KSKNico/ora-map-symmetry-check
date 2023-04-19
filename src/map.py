import struct
from tile import Tile
from maputils import load_map_tileset, get_traversable_terrain_types
from enum import Enum
from typing import Optional
import math
from resource import Resource

class Symmetry(Enum):
	HORIZONTAL = 1
	VERTICAL = 2
	DIAGONAL_BL_TR = 3
	DIAGONAL_TL_BR = 4
	ROTATION = 5

class Map:



	def __init__(self, map_dict, map_binary):
		self.dict: dict = map_dict
		self.binary: bytes = map_binary
		self.tileset: dict = load_map_tileset(self.dict["RequiresMod"], self.dict["Tileset"])
		self.traversable_terrain_types: set = get_traversable_terrain_types(self.dict["RequiresMod"])
		self.map_middle_point = ()
					
	def unpack_header(self):
		self.format, self.width, self.height = struct.unpack("<BHH", self.binary[:5])
		if self.format == 1:
			self.tiles_offset = 5
			self.height_offset = 0
			self.resources_offset = 3 * self.width * self.height + 5
		elif self.format == 2:
			self.tiles_offset, self.height_offset, self.resources_offset = struct.unpack("<III", self.binary[5:17])
		elif self.width <= 0 or self.height <= 0:
			raise ValueError("Map height and width can't be 0 or lesss")
		else:
			raise ValueError("Invalid map format: {self.format}")

	def unpack_tiles(self):
		self.tiles: dict = {}
		self.index = self.tiles_offset
		for x in range(self.width):
			for y in range(self.height):
				tile_type, tile_index = struct.unpack("<HB", self.binary[self.index:self.index+3])
				self.tiles[(x,y)] = Tile(tile_type, tile_index)
				self.index += 3

	def unpack_resources(self):
		self.resources: dict = {}
		self.index = self.resources_offset
		for x in range(self.width):
			for y in range(self.height):
				resource_type, resource_density = struct.unpack("<BB", self.binary[self.index:self.index+2])
				self.resources[(x, y)] = Resource(resource_type, resource_density)
				self.index += 2

	def parse_map(self):
		self.index = 0
		self.unpack_header()
		self.unpack_tiles()
		self.unpack_resources()
		self.update_tiles_with_terrain()
	
	def update_tiles_with_terrain(self):
		tileset_templates = self.tileset["Templates"]
		for tile in self.tiles.values():
			tile.terrain = tileset_templates[f"Template@{tile.type}"]["Tiles"][tile.index]

	def get_tile_symmetry_errors(self, symmetry_type: Symmetry) -> list[tuple[tuple[int, int], tuple[int, int]]]:
		errors = []
		if symmetry_type == Symmetry.DIAGONAL_BL_TR or symmetry_type == Symmetry.DIAGONAL_TL_BR:
			assert self.width == self.height, "Diagonal symmetry can only be checked on square maps"
		
		# checks symmetry of a vertical line through the middle of the map
		if symmetry_type == Symmetry.VERTICAL:
			for x in range(math.ceil(self.width/2)):
				for y in range(self.height):
					if self.tiles[(x,y)].type != self.tiles[(self.width-x-1, y)].type:
						errors.append(((x,y), (self.width-x-1, y)))
		# checks symmetry of a horizontal line through the middle of the map
		elif symmetry_type == Symmetry.HORIZONTAL:
			for x in range(self.width):
				for y in range(math.ceil(self.height/2)):
					if self.tiles[(x,y)].type != self.tiles[(x, self.height-y-1)].type:
						errors.append(((x,y), (x, self.height-y-1)))
		# checks symmetry of a diagonal from bottom left to top right
		elif symmetry_type == Symmetry.DIAGONAL_BL_TR:
			for x in range(self.width):
				for y in range(self.height-x):
					if self.tiles[(x,y)].type != self.tiles[(self.width-y-1, self.height-x-1)].type:
						errors.append(((x,y), (self.width-y-1, self.height-x-1)))
		# checks symmetry of a diagonal from top left to bottom right
		elif symmetry_type == Symmetry.DIAGONAL_TL_BR:
			for x in range(self.width):
				for y in range(x, self.height):
					if self.tiles[(x,y)].type != self.tiles[(y,x)].type:
						errors.append(((x,y), (y,x)))
		# checks symmetry of a rotation
		elif symmetry_type == Symmetry.ROTATION:
			for x in range(self.width):
				for y in range(math.ceil(self.height/2)):
					if self.tiles[(x,y)].type != self.tiles[(self.width-x-1, self.height-y-1)].type:
						errors.append(((x,y), (self.width-x-1, self.height-y-1)))
		return errors
	
	def get_resources_symmetry_errors(self, symmetry_type: Symmetry) -> list[tuple[tuple[int, int], tuple[int, int]]]:
		errors = []
		if symmetry_type == Symmetry.HORIZONTAL:
			for x in range(math.ceil(self.width/2)):
				for y in range(self.height):
					if self.resources[(x,y)] != self.resources[(self.width-x-1, y)]:
						errors.append(((x,y), (self.width-x-1, y)))
		elif symmetry_type == Symmetry.VERTICAL:
			for x in range(self.width):
				for y in range(math.ceil(self.height/2)):
					if self.resources[(x,y)] != self.resources[(x, self.height-y-1)]:
						errors.append(((x,y), (x, self.height-y-1)))
		return errors
	
	# checks symmetry of map by considering terrain types, no visual symmetry is checked for
	def check_tile_symmetry(self, symmetry_type: Symmetry) -> bool:
		if self.get_tile_symmetry_errors(symmetry_type) == []:
			return True
		else:
			return False

	def get_neighbours(self, coordinates: tuple[int, int]) -> list[tuple[int, int]]:
		neighbours = []
		for x in range(coordinates[0]-1, coordinates[0]+2):
			for y in range(coordinates[1]-1, coordinates[1]+2):
				if (x,y) != coordinates and (x,y) in self.tiles:
					neighbours.append((x,y))
		return neighbours
	
	def is_traversable_tile(self, tile: Tile):
		return tile.terrain in self.traversable_terrain_types

	def get_biggest_connected_area(self) -> set[tuple[int, int]]:
		visited = set()
		areas = []
		for coordinates, tile in self.tiles.items():
			if coordinates in visited or not self.is_traversable_tile(tile):
				continue
			to_explore = [coordinates]
			area = set()
			while to_explore != []:
				current = to_explore.pop(0)
				visited.add(current)
				area.add(current)
				for neighbour in self.get_neighbours(current):
					if neighbour not in visited and self.is_traversable_tile(self.tiles[neighbour]) and not neighbour in to_explore:
						to_explore.append(neighbour)
			areas.append(area)
		return max(areas, key=len)
	
	def get_valid_tile_symmetries(self) -> list[Symmetry]:
		valid_symmetries = []
		for symmetry in Symmetry:
			if self.check_tile_symmetry(symmetry):
				valid_symmetries.append(symmetry)
		return valid_symmetries
