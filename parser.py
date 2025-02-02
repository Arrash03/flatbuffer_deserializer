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

    def __extract_vector(self, root_object, length_function, field_function):
        length = length_function(root_object)
        result = []
        for i in range(length):
            temp_field = field_function(root_object, i)
            deserialized_field = self.__extract_fields(temp_field)
            result.append(deserialized_field)
        return result

    def __extract_fields(self, root_object):
        deserialized_data = None
        if root_object != None:
            if type(root_object) in [int, float]:
                deserialized_data = root_object
            elif type(root_object) == bytes:
                deserialized_data = root_object.decode("utf-8", "strict")
            else:
                deserialized_data = {}
                instance_members, instance_len_members = self.__get_members(type(root_object))
                for name, func in instance_members.items():
                    length_function_name = name + "Length"
                    if length_function_name in instance_len_members:
                        deserialized_data[name] = self.__extract_vector(root_object, instance_len_members[length_function_name], func)
                    else:
                        temp_field = func(root_object)
                        deserialized_data[name] = self.__extract_fields(temp_field)

        return deserialized_data

    def parse(self) -> None:
        for filename in os.listdir(self.binary_path):
            if not os.path.isdir(os.path.join(self.binary_path, filename)):
                with open(os.path.join(self.binary_path, filename), 'rb') as binary_file:
                    monster = Monster.GetRootAs(binary_file.read(), offset=0)
                    deserialized_data = self.__extract_fields(monster)
                    print(deserialized_data)

