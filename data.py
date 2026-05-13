from enum import Enum


class ParseError(Exception):
    pass


class ZoneTypes(Enum):
    NORMAL = 'normal'
    BLOCKED = 'blocked'
    RESTRICTED = 'restricted'
    PRIORITY = 'priority'


class MetaKey(Enum):
    COLOR = 'color'
    ZONE = 'zone'
    MX_DRONES = 'max_drones'


class Prefix(Enum):
    START = 'start_hub'
    END = 'end_hub'
    HUB = 'hub'
    NB_DRONES = 'nb_drones'
    CNX = "connection"


class ParseManager:

    @staticmethod
    def read(input_file: str) -> dict:

        line_nb = 0
        data = {}
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
        return {}

    @staticmethod
    def error(msg: str, line_nb: int) -> None:

        if line_nb:
            raise ParseError(f"Error ({line_nb}): {msg}")

        raise ParseError(f'Error: {msg}')


class MetaDataZone:

    def __init__(self, metadata: dict) -> None:

        self.zone_type = metadata.get(MetaKey.ZONE.value,
                                      ZoneTypes.NORMAL.value)

        self.color = metadata.get(MetaKey.COLOR.value, None)
        self.max_drones = metadata.get(MetaKey.MX_DRONES.value, 1)
        self.curr_drones = 0

    def is_valid(self) -> bool:

        return (
            self.zone_type != 'blocked' and
            self.max_drones > self.curr_drones
        )


class ZoneData:

    names = set()
    coords = set()
    prefixes = set()

    def __init__(self, prefix: str, name: str, x: int, y: int,
                 meta: MetaDataZone, line_nb: int) -> None:

        ZoneData.check_duplicat(prefix, name, line_nb, x, y)

        if prefix in {"start_hub", "end_hub"} and meta.zone_type == 'blocked':
            ParseManager.error(f"The zone '{prefix}' can't be blocked, Please "
                               "change its type in metadata.", line_nb)
        self.prefix = prefix
        self.name = name
        self.x = x
        self.y = y
        self.meta = meta
        self.cnx = list()
        self.cnx_names = set()
        self.goal_cost = (float('inf'), None)
        self.cost = ZoneData.get_cost(meta.zone_type)

    def __lt__(self, other: 'ZoneData'):
        return self.goal_cost < other.goal_cost

    @staticmethod
    def get_cost(zone_type: str) -> int:

        if zone_type == "normal":
            return 1

        elif zone_type == 'priority':
            return 0.90

        elif zone_type == 'restricted':
            return 2

        return None

    @classmethod
    def check_duplicat(cls, prefix: str, name: str, line_nb: int,
                       x: int, y: int) -> None:

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

    def __init__(self, id: str, start_zone: ZoneData) -> None:

        self.id = id
        self.curr_zone = start_zone
        self.next_zone = None
        self.in_cnx = False


class Data:

    def __init__(self, data: dict) -> None:

        self.nb_drones = data['nb_drones']
        self.zones = data['zones']
        self.zone_by_name = {z.name: z for z in self.zones}
        self.start_zone = next((z for z in self.zones
                                if z.prefix == 'start_hub'))

        self.end_zone = next((z for z in self.zones if z.prefix == 'end_hub'))


class ConnectionData:

    def __init__(self, cnx_name: ZoneData, mx_cp: int, curr_cp: int) -> None:

        self.cnx_name = cnx_name
        self.mx_cp = mx_cp
        self.curr_cp = curr_cp
