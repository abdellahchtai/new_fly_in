from data import Data, ZoneData
from typing import Optional
import heapq


class Algo:

    @staticmethod
    def djikstra_algo(data: Data, start_zone: ZoneData,
                      end_zone: ZoneData) -> Optional[ZoneData]:

        Algo.reset_goal_cost_zones(data)
        start_zone.goal_cost = (0, None)

        heap = [(0, start_zone)]
        heapq.heapify(heap)

        while heap:

            cost, zone = heapq.heappop(heap)

            if cost > zone.goal_cost[0]:
                continue

            for cnx_obj in zone.cnx:

                neighbor_zone = data.zone_by_name[cnx_obj.cnx_name]

                if zone.name == start_zone.name:

                    if (
                        not neighbor_zone.meta.is_valid() or
                        cnx_obj.mx_cp <= cnx_obj.curr_cp
                    ):
                        continue

                goal_cost = neighbor_zone.cost + zone.goal_cost[0]

                if goal_cost < neighbor_zone.goal_cost[0]:

                    neighbor_zone.goal_cost = (goal_cost, zone.name)
                    heapq.heappush(heap, (goal_cost, neighbor_zone))

        return Algo.get_path(data, start_zone, end_zone)

    @staticmethod
    def get_path(data: Data, start_zone: ZoneData,
                 end_zone: ZoneData) -> Optional[ZoneData]:

        if end_zone.goal_cost[1] is None:
            return None

        curr = end_zone
        path = [curr]

        while curr.name != start_zone.name:

            curr = data.zone_by_name[curr.goal_cost[1]]
            path.append(curr)

        if len(path) >= 2:
            return path[-2]

        return None

    @staticmethod
    def reset_goal_cost_zones(data: Data) -> None:

        for zone in data.zones:
            zone.goal_cost = (float('inf'), None)
