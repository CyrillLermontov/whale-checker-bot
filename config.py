from pathlib import Path
from json import load


root_folder = Path(__file__).parents[0]
settings_path = root_folder / "settings.json"
abi_path = root_folder / "erc20.abi.json"


with open(settings_path, 'r', encoding='utf-8-sig') as file:
    settings_json = load(file)


with open(abi_path, 'r', encoding='utf-8-sig') as file:
    erc20_abi = load(file)