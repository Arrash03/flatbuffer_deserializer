import inspect
import os

from MyGame.Sample.Equipment import Equipment

# trunk-ignore(ruff/F401)
from MyGame.Sample.Monster import Monster

# trunk-ignore(ruff/F401)
from MyGame.Sample.Weapon import Weapon


class Parser:
    def __init__(self, root_type, binary_path: str):
        self.__root_type = root_type
        self.binary_path = binary_path

    def __get_members(self, class_type):
        members = inspect.getmembers(class_type, predicate=inspect.isfunction)
        instance_type_members = {}
        instance_len_members = {}
        instance_members = {}
        for name, func in members:
            if (
                not isinstance(func, staticmethod)
                and not name.startswith("__")
                and not name.endswith("IsNone")
                and not name.endswith("Numpy")
                and name not in ["Init"]
            ):
                if name.endswith("Length"):
                    instance_len_members[name] = func
                elif name.endswith("Type"):
                    instance_type_members[name] = func
                else:
                    instance_members[name] = func

        return instance_members, instance_len_members, instance_type_members

    def __extract_vector(self, root_object, vector_length_function, field_function):
        length = vector_length_function(root_object)
        result = []
        for i in range(length):
            temp_field = field_function(root_object, i)
            deserialized_field = self.__extract_fields(temp_field)
            result.append(deserialized_field)
        return result

    @staticmethod
    def __find_enum_members():
        # hard coded enum type
        class_vars = Equipment.__dict__
        class_variables = {
            value: key
            for key, value in class_vars.items()
            if not key.startswith("__") and not callable(value)
        }

        return class_variables

    @staticmethod
    def __create_union_object(type_name):
        command = f"union_object = {type_name}()"
        output = locals()
        # trunk-ignore(bandit/B102)
        exec(command, globals(), output)

        return output["union_object"]

    def __extract_union(self, root_object, field_type_function, field_function):
        field_type = field_type_function(root_object)

        result = None
        if field_type is not None:
            class_variables = Parser.__find_enum_members()
            type_name = class_variables[field_type]

            union_object = Parser.__create_union_object(type_name)

            union_data = field_function(root_object)
            union_object.Init(union_data.Bytes, union_data.Pos)
            result = self.__extract_fields(union_object)

        return result

    def __extract_fields(self, root_object):
        deserialized_data = None
        if root_object is not None:
            if type(root_object) in [int, float]:
                deserialized_data = root_object
            # trunk-ignore(ruff/E721)
            elif type(root_object) == bytes:
                deserialized_data = root_object.decode("utf-8", "strict")
            else:
                deserialized_data = {}
                instance_members, instance_len_members, instance_type_members = (
                    self.__get_members(type(root_object))
                )
                for name, func in instance_members.items():
                    length_function_name = name + "Length"
                    type_function_name = name + "Type"
                    if length_function_name in instance_len_members:
                        deserialized_data[name] = self.__extract_vector(
                            root_object,
                            instance_len_members[length_function_name],
                            func,
                        )
                    elif type_function_name in instance_type_members:
                        deserialized_data[name] = self.__extract_union(
                            root_object, instance_type_members[type_function_name], func
                        )
                    else:
                        temp_field = func(root_object)
                        deserialized_data[name] = self.__extract_fields(temp_field)

        return deserialized_data

    def parse(self) -> None:
        for filename in os.listdir(self.binary_path):
            if not os.path.isdir(os.path.join(self.binary_path, filename)):
                with open(
                    os.path.join(self.binary_path, filename), "rb"
                ) as binary_file:
                    command = f"root_object = {self.__root_type.__name__}.GetRootAs({binary_file.read()}, offset=0)"
                    output = locals()
                    # trunk-ignore(bandit/B102)
                    exec(command, globals(), output)

                    root_object = output["root_object"]
                    deserialized_data = self.__extract_fields(root_object)
                    return deserialized_data
