import os
import inspect

from MyGame.Sample.Monster import Monster


class Parser:
    def __init__(self, binary_path: str):
        self.binary_path = binary_path

    def __get_members(self, class_type):
        members = inspect.getmembers(class_type, predicate=inspect.isfunction)
        instance_len_members = {}
        instance_members = {}
        for name, func in members:
            if not isinstance(func, staticmethod) and not name.startswith("__") and not name.endswith("IsNone") and not name.endswith("Numpy") and not name in ["Init"]:
                if name.endswith("Length"):
                    instance_len_members[name] = func
                else:
                    instance_members[name] = func        

        return instance_members, instance_len_members


    def __extract_fields(self, root_object):
        deserialized_data = None
        if root_object != None:
            deserialized_data = {}
            instance_members, instance_len_members = self.__get_members(type(root_object))
            for name, func in instance_members.items():
                length_function_name = name + "Length"
                if length_function_name in instance_len_members:
                    length = instance_len_members[length_function_name](root_object)
                    temp_vector = []
                    for i in range(length):
                        temp_vector.append(func(root_object, i))
                    deserialized_data[name] = temp_vector
                else:
                    temp_field = func(root_object)
                    if type(temp_field) in [int, float]:
                        deserialized_data[name] = temp_field
                    elif type(temp_field) == bytes:
                        deserialized_data[name] = temp_field.decode("utf-8", "strict")
                    else:
                        deserialized_data[name] = self.__extract_fields(temp_field)

        return deserialized_data

    def parse(self) -> None:
        for filename in os.listdir(self.binary_path):
            if not os.path.isdir(os.path.join(self.binary_path, filename)):
                with open(os.path.join(self.binary_path, filename), 'rb') as binary_file:
                    monster = Monster.GetRootAs(binary_file.read(), offset=0)
                    deserialized_data = self.__extract_fields(monster)
                    print(deserialized_data)

