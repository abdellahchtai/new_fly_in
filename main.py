import sys
from data import ParseManager, ParseError, Data, Drones
from render import Visualization


class Manager:

    def __init__(self, input_file: str) -> None:
        self.input_file = input_file

    def main(self, data_dict: dict) -> None:

        data_obj = Data(data_dict)

        drones = [
            Drones(f"Dr_{i + 1}",
                   data_obj.start_zone) for i in range(data_obj.nb_drones)
            ]

        data_obj.start_zone.meta.curr_drones = data_obj.nb_drones
        data_obj.end_zone.meta.max_drones = data_obj.nb_drones

        Visualization.display(data_obj, drones, self.input_file)


if __name__ == '__main__':

    try:

        if len(sys.argv) < 2:
            print('No input file is provided, Please add it in the args.')
            exit(1)

        input_file = sys.argv[1]
        data_dict = ParseManager.read(input_file)

    except (
        ParseError, FileNotFoundError,
        PermissionError, IsADirectoryError
            ) as e:

        print(e)
        exit(1)

    start = Manager(input_file)

    try:
        start.main(data_dict)

    except ParseError as e:
        print(e)
