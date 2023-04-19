
import yaml
import struct
import pathlib

from maputils import load_map_by_filename, load_map_tileset, get_traversable_terrain_types
from map import Map, Symmetry
from tile import Tile
from resource import Resource

def check_maps_in_dir(directory: str):
	map_path = pathlib.Path(directory)
	for map_file in map_path.glob("*.oramap"):
		try:
			map_dict, map_binary = load_map_by_filename(map_file)
			map = Map(map_dict, map_binary)
			map.parse_map()
			biggest_area = map.get_biggest_connected_area()
			valid_symmetries = map.get_valid_tile_symmetries()

			print("Map has the name ", map.dict["Title"], " the size ", map.width, "x", map.height, " biggest area is ", 
			biggest_area, " and valid symmetries are ", valid_symmetries)
		except Exception as e:
			print("Error while parsing map ", map_file, " with error ", e)
		
	



if __name__ == '__main__':
	map_dict, map_binary = load_map_by_filename("test_04.oramap")
	# print("Binary data: ", map_binary)
	map = Map(map_dict, map_binary)
	map.parse_map()
	# print(map.tiles)
	# print(map.dict)
	# print(get_traversable_terrain_types(mod_name="ca"))

	# symmetries = [Symmetry.HORIZONTAL, Symmetry.VERTICAL, Symmetry.DIAGONAL_BL_TR, Symmetry.DIAGONAL_TL_BR, Symmetry.ROTATION]
	# conflicts = {symmetry: map.get_tile_symmetry_errors(symmetry) for symmetry in symmetries}
	# for symmetry_type, conflict in conflicts.items():
	# 	print("Symmetry type: ", symmetry_type)
	# 	if conflict:
	# 		print("Conflicts: ", conflict)
	# 	else:
	# 		print("No conflicts found")
	# 	print("")

	# valid_symmetries = map.get_valid_tile_symmetries()
	# for symmetry in valid_symmetries:
	# 	print("Valid symmetry: ", symmetry)

	# biggest_area = map.get_biggest_connected_area()
	# print("Biggest connected area has the size: ", len(biggest_area))

	check_maps_in_dir("/snap/openra/1403/usr/lib/openra/mods/ra/maps")