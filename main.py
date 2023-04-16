import zipfile
import yaml


def load_map(name) -> tuple[dict, bytes]:
    with zipfile.ZipFile(name,"r") as zip_ref:
        yaml_file = zip_ref.open("map.yaml", "r", )
        bin_file = zip_ref.open("map.bin")

        map_dict = yaml.safe_load("".join([x.decode('utf-8') for x in yaml_file.readlines()]).replace("\t", "  "))
        map_binary = bin_file.read()
        return map_dict, map_binary


if __name__ == '__main__':
    map_dict, map_binary = load_map("test_01.oramap")
    print(map_dict)
    print(map_binary)
