from data import Data, Drones, ZoneData, ConnectionData
from algo import Algo
from typing import Generator, List, Any


class Simulation:

    """
    Class for simulation for each turn.
    """
    @staticmethod
    def just_for_printinf(drone: Drones) -> None:

        """
        Method to print to the standar output the drone movement.
        """

        name = drone.next_zone.name if drone.next_zone else None
        if drone.in_cnx:
            name = f"<{drone.curr_zone.name}-{name}>"

        if name:
            print(f"{drone.id}-{name}.", end=' ')

    @staticmethod
    def find_pt_per_drone(data: Data, drones: List[Drones]
                          ) -> Generator[List[Drones]]:

        """
        Methode that use the dikstra algo each turn and decide the drone
        next_zone or the drone must wait if no zone found.
        """

        i = 1

        drones_cp = drones[:]
        rstd_drns: List[Drones] = []

        while drones_cp:

            print(f"Turn {i}: ", end=' ')

            for drone in drones:

                if drone in rstd_drns:
                    Simulation.move_rstd_dr(drone)
                    rstd_drns.remove(drone)

                    continue

                drone.next_zone = Algo.djikstra_algo(
                    data, drone.curr_zone, data.end_zone)

                if drone.next_zone:

                    flag_rstd = False

                    if drone.next_zone.meta.zone_type == 'restricted':
                        drone.in_cnx = True
                        flag_rstd = True
                        rstd_drns.append(drone)

                    Simulation.reload_drone_data(drone, drone.next_zone,
                                                 flag_rstd)

                    Simulation.just_for_printinf(drone)
            print()

            yield drones

            for drone in drones:
                if drone.curr_zone.name == data.end_zone.name:
                    if drone in drones_cp:
                        drones_cp.remove(drone)

            Simulation.reset_curr_cp(data, rstd_drns)

            i += 1

    @staticmethod
    def reset_curr_cp(data: Data, rst_drones: List[Drones]) -> None:

        """
        Methode that reset the connection but it skip the restrectd that hold a
        drone in current turn.
        """
        rstd_cnx = [
            Simulation.get_cnx_obj(drone.curr_zone, drone.next_zone
                                   ) for drone in rst_drones]

        for zone in data.zones:

            for cnx in zone.cnx:
                if cnx not in rstd_cnx:
                    cnx.curr_cp = 0

    @staticmethod
    def reset_all_data(data: Data) -> None:

        """
        Methode that reset the attribut of a zone in case of the user
        click on r key.
        """
        data.start_zone.meta.curr_drones = data.nb_drones

        for zone in data.zones:

            if zone.name != data.start_zone.name:
                zone.meta.curr_drones = 0

            zone.goal_cost = (float('inf'), None)

            for cnx_obj in zone.cnx:
                cnx_obj.curr_cp = 0

    @staticmethod
    def get_cnx_obj(curr_zone: ZoneData, next_zone: Any
                    ) -> ConnectionData:

        """
        Methed that find the connection of a drone and return it.
        """

        for cnx_obj in curr_zone.cnx:

            if cnx_obj.cnx_name == next_zone.name:
                return cnx_obj
# JUST FOR MYPY THIS RETURN IS USELESS
        return cnx_obj

    @staticmethod
    def reload_drone_data(drone: Drones, next_zone: Any,
                          restrectid: bool) -> None:

        """
        Methode that actualise the drone attribut in each turn,
        """
        cnx_obj = Simulation.get_cnx_obj(drone.curr_zone, next_zone)
        cnx_obj.curr_cp += 1

        drone.curr_zone.meta.curr_drones -= 1

        if not restrectid:
            next_zone.meta.curr_drones += 1
            drone.curr_zone = drone.next_zone

    @staticmethod
    def move_rstd_dr(drone: Drones) -> None:

        """
        Methode that move the drone in the second turn of restricted.
        """
        drone.next_zone.meta.curr_drones += 1
        print(f"{drone.id}-{drone.next_zone.name}.", end=' ')
        drone.curr_zone = drone.next_zone
        drone.in_cnx = False
