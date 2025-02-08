import os
from parser import Parser

from MyGame.Sample.Monster import Monster
from MyGame.Sample.Equipment import Equipment

if __name__ == "__main__":
    binary_directory: str = os.path.join(os.getcwd(), "binary_path")
    parser = Parser(Monster, {"equipped": Equipment}, "binary_path")
    deserialized_data = parser.parse()
    print(deserialized_data)

    json = parser.to_json()
    print(json)
