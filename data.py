from enum import Enum
from typing import Any, List, Union, Optional


class ParseError(Exception):
    """
    Class to customize the error type for the project.
    """
    pass


class ZoneTypes(Enum):

    """
    Constant for zone types
    """
    NORMAL = 'normal'
    BLOCKED = 'blocked'
    RESTRICTED = 'restricted'
    PRIORITY = 'priority'


class MetaKey(Enum):

    """
    Constant for metadata types.
    """
    COLOR = 'color'
    ZONE = 'zone'
    MX_DRONES = 'max_drones'


class Prefix(Enum):

    """
    Constant for Prefix types.
    """

    START = 'start_hub'
    END = 'end_hub'
    HUB = 'hub'
    NB_DRONES = 'nb_drones'
    CNX = "connection"


class ParseManager:

    """
    Class that is responsible about the paring of the input file.
    """

    @staticmethod
    def read(input_file: str) -> dict[str, Any]:

        """
        Class that read from the input file and return clean data
        """

        line_nb: int = 0
        data: dict[str, Any] = {}
        from parsing import DroneNumber, ZoneParse, ConnectionParse

        with open(input_file) as f:

            for line_nb, line in enumerate(f, 1):

                line = line.strip()

                if line and not line.startswith('#'):

                    data[Prefix.NB_DRONES.value] = DroneNumber.get_nb_drones(
                        line, line_nb)

                    data['zones'], line, line_nb = ZoneParse.get_zones(
                        f, line_nb)

                    zones_dict = {z.name: z for z in data['zones']}

                    ZoneParse.is_start_end(line_nb)
                    ConnectionParse.get_cnx(f, line, line_nb, zones_dict)

                    return data

        if line_nb == 0:
            ParseManager.error('Empty file.', 0)

        else:
            ParseManager.error(f'Invalid content in {input_file}, '
                               '(blank or comments only)', 0)
        return data

    @staticmethod
    def error(msg: str, line_nb: int) -> None:

        """
        Methode that is responsible about the custum error.
        """
        if line_nb:
            raise ParseError(f"Error ({line_nb}): {msg}")

        raise ParseError(f'Error: {msg}')


class MetaDataZone:

    """
    Class for metada of the zones
    """
    def __init__(self, metadata: dict[str, Any]) -> None:

        self.zone_type: str = metadata.get(MetaKey.ZONE.value,
                                           ZoneTypes.NORMAL.value)

        self.color: Optional[str] = metadata.get(MetaKey.COLOR.value, None)
        self.max_drones: int = metadata.get(MetaKey.MX_DRONES.value, 1)
        self.curr_drones: int = 0

    def is_valid(self) -> bool:

        """
        Method that check if the zone can hold a drone or no.
        """
        return (
            self.zone_type != 'blocked' and
            self.max_drones > self.curr_drones
        )


class ZoneData:

    """
    Class that is responsible for zone data.
    """
    names: set[str] = set()
    coords: set[tuple[int, int]] = set()
    prefixes: set[str] = set()

    def __init__(self, prefix: str, name: str, x: int, y: int,
                 meta: MetaDataZone, line_nb: int) -> None:

        """
        Method tha initialize all the attributs of a zone.
        """
        ZoneData.check_duplicat(prefix, name, line_nb, x, y)

        if prefix in {"start_hub", "end_hub"} and meta.zone_type == 'blocked':
            ParseManager.error(f"The zone '{prefix}' can't be blocked, Please "
                               "change its type in metadata.", line_nb)
        self.prefix: str = prefix
        self.name: str = name
        self.x: int = x
        self.y: int = y
        self.meta: MetaDataZone = meta
        self.cnx: List[ConnectionData] = list()
        self.cnx_names: set[str] = set()
        self.goal_cost: tuple[Union[float, int], Optional[str]
                              ] = (float('inf'), None)
        self.cost: Union[int, float] = ZoneData.get_cost(meta.zone_type)

    def __lt__(self, other: 'ZoneData') -> bool:

        """
        Method for comparing 2 zone.
        """
        return self.goal_cost < other.goal_cost

    @staticmethod
    def get_cost(zone_type: str) -> Union[int, float]:

        """
        Method that calculat the cost of a zone depend on the type
        and return it.
        """
        if zone_type == "normal":
            return 1

        elif zone_type == 'priority':
            return 0.90

        elif zone_type == 'restricted':
            return 2

        return 0

    @classmethod
    def check_duplicat(cls, prefix: str, name: str, line_nb: int,
                       x: int, y: int) -> None:

        """
        Method that check is a cnx or zone is already declared.
        """
        if prefix != Prefix.HUB.value and prefix in cls.prefixes:
            ParseManager.error(f'Redefinition of {prefix}.', line_nb)

        if name in cls.names:
            ParseManager.error('Name already used.', line_nb)

        if (x, y) in cls.coords:
            ParseManager.error('Coordinate already used.', line_nb)

        cls.prefixes.add(prefix)
        cls.names.add(name)
        cls.coords.add((x, y))


class Drones:

    """
    Class for drones.
    """
    def __init__(self, id: str, start_zone: ZoneData) -> None:

        """
        Method that initialise the drone attributs.
        """
        self.id: str = id
        self.curr_zone: ZoneData = start_zone
        self.next_zone: Any = None
        self.in_cnx: bool = False


class Data:

    """
    Class for the whole data (zones, drones...)
    """

    def __init__(self, data: dict[str, Any]) -> None:

        """
        Method that initializ the data attributs.
        """
        self.nb_drones: int = data['nb_drones']
        self.zones: List[ZoneData] = data['zones']
        self.zone_by_name: dict[str, ZoneData
                                ] = {z.name: z for z in self.zones}

        self.start_zone: ZoneData = next((z for z in self.zones
                                          if z.prefix == 'start_hub'))

        self.end_zone: ZoneData = next((z for z in self.zones
                                        if z.prefix == 'end_hub'))


class ConnectionData:

    """
    class for connection between zones.
    """

    def __init__(self, cnx_name: str, mx_cp: int, curr_cp: int) -> None:

        """
        Method that initialze the connection attributs.
        """
        self.cnx_name: str = cnx_name
        self.mx_cp: int = mx_cp
        self.curr_cp: int = curr_cp
