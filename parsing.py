from typing import TextIO, List
from data import MetaDataZone, ZoneData, Prefix, \
                MetaKey, ZoneTypes, ParseManager, ConnectionData


class ZoneParse:

    @staticmethod
    def is_start_end(line_nb: int) -> None:

        if Prefix.START.value not in ZoneData.prefixes:
            ParseManager.error('line must define a start_hub zone before '
                               'defining a connection.', line_nb)

        elif Prefix.END.value not in ZoneData.prefixes:
            ParseManager.error('line must define a end_hub zone before '
                               'defining a connection.', line_nb)

    @staticmethod
    def parse_coordinate(x_str: str, y_str: str, line_nb) -> tuple[int, int]:

        try:
            return (int(x_str), int(y_str))

        except ValueError:
            ParseManager.error(
                'Invalid zone coordinate try a integer number.', line_nb)

    @staticmethod
    def parse_zone(meta: dict, line_nb: int, data: List[str]) -> str:

        if MetaKey.ZONE.value in meta:
            ParseManager.error('Redeclaration of zone.', line_nb)

        zone_type = data[1].strip()
        zone_types = [z.value for z in ZoneTypes]

        if zone_type in zone_types:
            return zone_type

        ParseManager.error(
            f'Invalid zone_type ({zone_type}). Expected: "{zone_types}"',
            line_nb)

    @staticmethod
    def parse_color(meta: dict, line_nb: int, data: List[str]) -> str:

        if MetaKey.COLOR.value in meta:
            ParseManager.error('Redeclaration of color.', line_nb)

        return data[1].strip()

    @staticmethod
    def parse_max_drones(meta: dict, line_nb: int, data: List[str]) -> int:

        if MetaKey.MX_DRONES.value in meta:
            ParseManager.error('Redeclaration of max_drones.', line_nb)

        try:

            max_drones = int(data[1])

            if max_drones < 1:
                ParseManager.error('max_drones must be integer greater than'
                                   ' 0.', line_nb)

            return max_drones

        except ValueError:
            ParseManager.error(
                'max_drones must be valid number.', line_nb)

    @staticmethod
    def parse_metadata_tokens(data: str, line_nb: int) -> dict:

        data = data.split('[', 1)[1].split(']', 1)

        if len(data) == 1:
            ParseManager.error('Please close bracket after defining the '
                               'metadata', line_nb)

        if data[1].strip():
            ParseManager.error('No data is allowed after metadata.', line_nb)

        data = data[0].strip().split()

        metadata = {}

        for elm in data:

            meta = elm.split('=', 1)
            key = meta[0].strip()

            if len(meta) != 2 or not meta[1]:
                ParseManager.error(
                    'Invalid metadata format. Expected "key=value" (e.g."color'
                    '=red") without space around "=".', line_nb)

            if key == MetaKey.COLOR.value:
                metadata[MetaKey.COLOR.value] = ZoneParse.parse_color(
                    metadata, line_nb, meta)

            elif key == MetaKey.MX_DRONES.value:
                metadata[MetaKey.MX_DRONES.value] = ZoneParse.parse_max_drones(
                    metadata, line_nb, meta)

            elif key == MetaKey.ZONE.value:
                metadata[MetaKey.ZONE.value] = ZoneParse.parse_zone(
                    metadata, line_nb, meta)

            else:
                ParseManager.error(
                    f'Invalid metadata. Use {[z.value for z in MetaKey]},'
                    'e.g: color=green).', line_nb)

        return metadata

    @staticmethod
    def parse_meta(metadata: List, line_nb: int) -> MetaDataZone:

        if '[' not in metadata[0]:
            ParseManager.error('Invalid syntax. Expected <zone_name> <x> <y> '
                               '<optional: [metadata]> (check if the brackets '
                               'are open to set metadata).', line_nb)

        metadata = " ".join(metadata)
        metadata = ZoneParse.parse_metadata_tokens(metadata, line_nb)

        return MetaDataZone(metadata)

    @staticmethod
    def parse_zone_line(data: str, line_nb: int, prefix: str) -> ZoneData:

        data = data.split()

        if len(data) < 3:
            ParseManager.error('insuffisant data for zone. Expected: '
                               '<zone_name> <x> <y> <optional: [metadata]>',
                               line_nb)

        zone_name = data[0].strip()

        if '-' in zone_name:
            ParseManager.error('Please remove the dash "-" from zone name',
                               line_nb)

        if len(data) == 3:
            meta = MetaDataZone({})

        else:
            meta = ZoneParse.parse_meta(data[3:], line_nb)

        x, y = ZoneParse.parse_coordinate(data[1], data[2], line_nb)

        return ZoneData(prefix, zone_name, x, y, meta, line_nb)

    @staticmethod
    def get_zones(file: TextIO, linenb: int
                  ) -> tuple[List[ZoneData], str, int]:

        zones = list()
        valid_prefix = [prf.value for prf in Prefix
                        if prf.value not in {'connection', 'nb_drones'}]

        for line_nb, line in enumerate(file, linenb + 1):

            line = line.strip()

            if line and not line.startswith('#'):

                line = line.split('#', 1)[0]
                zone_data = line.split(':', 1)
                prefix = zone_data[0].strip()

                if prefix == Prefix.CNX.value:
                    break

                if len(zone_data) < 2:
                    ParseManager.error('Please put ":" to define a zone or a '
                                       'connection.', line_nb)

                elif prefix not in valid_prefix:
                    ParseManager.error('Invalid prefix for this zone. '
                                       f'Expected {valid_prefix}, or '
                                       '"connection" for the start'
                                       ' of connections section.', line_nb)

                zones.append(ZoneParse.parse_zone_line(
                    zone_data[1], line_nb, prefix))

        return zones, line, line_nb


class DroneNumber:

    @staticmethod
    def get_nb_drones(line_drones: str, line_nb) -> int:

        nb_data = line_drones.split('#', 1)[0].split(':', 1)
        key = nb_data[0].strip()

        if len(nb_data) < 2:
            ParseManager.error('Invalid synthax. Use ":" for key value '
                               'separation', line_nb)

        value = nb_data[1].strip()

        if key != Prefix.NB_DRONES.value:
            ParseManager.error(f'Invalid key ({key}), Use nb_drones in first '
                               'line to define the number of drones first.',
                               line_nb)

        elif not value:
            ParseManager.error('Missing value for nb_drones', line_nb)

        try:

            nb_drones = int(value)

            if nb_drones <= 0:
                ParseManager.error(
                    'Drones number must be a integer greater than 0.', line_nb)

            return nb_drones

        except ValueError:
            ParseManager.error(
                'Drones number must be a valid integer.', line_nb)


class ConnectionParse:

    @staticmethod
    def is_define(zone1: str, zone2: str, zones: dict,
                  line_nb: int) -> None:

        if zone1 not in zones:
            ParseManager.error(f'zone "{zone1}" is undefined.', line_nb)

        elif zone2 not in zones:
            ParseManager.error(f'zone "{zone2}" is undefined.', line_nb)

    @staticmethod
    def convert_mx_cp(meta, line_nb: int):

        if not meta[0].strip():
            return 1

        meta = meta[0].split('=', 1)
        key = meta[0].strip()

        max_link_cp = 1

        if len(meta) < 2:
            ParseManager.error('Use "=" to assignme value.', line_nb)

        value = meta[1].strip()

        if not key or not value:
            ParseManager.error('Missing key or value for this connection '
                               'metadata.', line_nb)

        if key != 'max_link_capacity':
            ParseManager.error('Invalid key, use "max_link_capacity" '
                               'without extra characters after "[".',
                               line_nb)
        try:

            max_link_cp = int(value)

            if max_link_cp < 1:
                ParseManager.error('max_link_capacity must be greather '
                                   'than 0.', line_nb)

        except ValueError:
            ParseManager.error('max_link_capacity must be a valid integer '
                               'number. Also the metadata must containe '
                               'only one attribute with one "=".', line_nb)

        return max_link_cp

    @staticmethod
    def calcl_max_cp(line: List[str], line_nb: int) -> int:

        meta = [""]

        if len(line) > 1:

            meta = " ".join(line[1:]).split('[', 1)

            if len(meta) < 2:
                ParseManager.error('Open brackets to define a metadata of '
                                   'connection', line_nb)

            elif meta[0]:
                ParseManager.error('Remove spaces in connection between zones '
                                   'use "-" to separte two zone.', line_nb)

            elif ']' not in meta[-1]:
                ParseManager.error('Close bracket after finishing metadata '
                                   'definition', line_nb)

            meta = meta[1].split(']', 1)

            if meta[1].strip():
                ParseManager.error("No data is allowed after defining "
                                   "max_link_capacity.", line_nb)

        return ConnectionParse.convert_mx_cp(meta, line_nb)

    @staticmethod
    def parse_cnx(conx_zon: str, line_nb: int) -> tuple[str, str]:

        zones = conx_zon.split('-')

        if len(zones) == 1:
            ParseManager.error('Not enough zone to connect.', line_nb)

        elif len(zones) > 2:
            ParseManager.error("To many dashes '-' in this connection, Use "
                               "only one.", line_nb)

        zone1 = zones[0].strip()
        zone2 = zones[1].strip()

        if not zone1 or not zone2:
            ParseManager.error("Missing zone name between '-'.", line_nb)

        if zone1 == zone2:
            ParseManager.error('Impossible to connect a zone with itself.',
                               line_nb)

        return (zone1, zone2)

    @staticmethod
    def parse_line(line: str, line_nb: int) -> tuple[str, str, int]:

        line = line.split('#', 1)[0].strip().split(':', 1)

        if len(line) < 2:
            ParseManager.error('Use ":" to define a connection', line_nb)

        elif line[0].strip() != 'connection':
            ParseManager.error('Invalid key word to define a connection, use '
                               '"connection". Also no data is allowed after '
                               'finishing connections and you must define a'
                               'connection.', line_nb)

        elif not line[1].strip():
            ParseManager.error('Missing data after ":".', line_nb)

        line = line[1].split()

        max_link_cp = ConnectionParse.calcl_max_cp(line, line_nb)
        zone1, zone2 = ConnectionParse.parse_cnx(line[0], line_nb)

        return (zone1, zone2, max_link_cp)

    @staticmethod
    def add_cnx(zones: dict, line_nb, zone1: str, zone2: str,
                mx_cp: int) -> None:

        full_zone1 = zones[zone1]
        full_zone2 = zones[zone2]

        if zone2 in full_zone1.cnx_names:
            ParseManager.error("This connection already define.", line_nb)

        elif zone1 in full_zone2.cnx_names:
            ParseManager.error("Zone conflict: two zones already declared, "
                               "swapping them on this line is not allowed.",
                               line_nb)

        full_zone1.cnx.append(ConnectionData(zone2, mx_cp, 0))
        full_zone1.cnx_names.add(zone2)

    @staticmethod
    def get_cnx(file: TextIO, curr_line: str, line_nb: int,
                zones: dict[ZoneData]) -> None:

        for line_nb, line in enumerate([curr_line, *file], line_nb):

            line = line.strip()

            if line and not line.startswith('#'):

                zone1, zone2, mx_cp = ConnectionParse.parse_line(line, line_nb)
                ConnectionParse.is_define(zone1, zone2, zones, line_nb)
                ConnectionParse.add_cnx(zones, line_nb, zone1, zone2, mx_cp)
