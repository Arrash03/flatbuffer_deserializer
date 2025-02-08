import os
from parser import Parser

from MyGame.Sample.Monster import Monster

if __name__ == "__main__":
    binary_directory: str = os.path.join(os.getcwd(), "binary_path")
    parser = Parser(Monster, "binary_path")
    deserialized_data = parser.parse()
    print(deserialized_data)
