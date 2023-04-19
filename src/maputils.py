import zipfile
import yaml
import dotenv
import os
import pathlib
import re

dotenv.load_dotenv()

OPENRA_DIR = os.getenv("OPENRA_DIR")

def get_traversable_terrain_types(mod_name: str) -> set[str]:

    world_path = pathlib.Path(OPENRA_DIR, "mods", mod_name, "rules", "world.yaml")


    # Load the mod's yaml file
    with open(world_path, "r") as file:
        yaml_string = file.read()

    # Extract terrain types using regular expression
    pattern = r'Locomotor@FOOT:.*?TerrainSpeeds:\n((?:\s*\w+?: \d+?\n)+)'
    matches = re.findall(pattern, yaml_string, re.DOTALL)

    # Extract terrain types from matches
    terrain_types = set()
    for match in matches:
        terrain_lines = match.split("\n")
        for line in terrain_lines:
            if ":" in line:
                terrain_type = line.split(":")[0].strip()
                if terrain_type != "":
                    terrain_types.add(terrain_type)

    return terrain_types

def load_map_tileset(mod_name: str, tileset_name: str) -> dict:
    root_path = pathlib.Path(OPENRA_DIR)
    tileset_path = pathlib.Path.joinpath(root_path, "mods", mod_name, "tilesets", tileset_name.lower() + ".yaml")
    with open(tileset_path, "r") as file:
        return yaml.safe_load(file.read().replace("\t", "  "))


def load_map_by_filename(name) -> tuple[dict, bytes]:
    with zipfile.ZipFile(name,"r") as zip_ref:
        yaml_file = zip_ref.open("map.yaml", mode='r')
        bin_file = zip_ref.open("map.bin", mode='r')

        map_dict = yaml.safe_load("\n".join([x.decode('utf-8') for x in yaml_file.readlines()]).replace("\t", "  "))
        map_binary = bin_file.read()

        yaml_file.close()
        bin_file.close()

        return map_dict, map_binary


