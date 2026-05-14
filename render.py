from simulation import Simulation
from data import Data, ParseManager, Drones
import pygame


class Visualization:

    @staticmethod
    def draw(data: Data, window, new_center: tuple[int, int]):

        info = pygame.display.Info()
        w = info.current_w
        h = info.current_h
        font = pygame.font.Font(None, 20)
        font2 = pygame.font.Font(None, 17)

        for zone in data.zones:

            x = zone.x * 100 + w // 2 + new_center[0]
            y = zone.y * 140 + h // 2 + new_center[1]

            for cnx in zone.cnx:

                zone_cnx = data.zone_by_name[cnx.cnx_name]
                x_cnx = zone_cnx.x * 100 + w // 2 + new_center[0]
                y_cnx = zone_cnx.y * 140 + h // 2 + new_center[1]

                pygame.draw.line(window, 'black', (x, y), (x_cnx, y_cnx), 3)

        for zone in data.zones:

            x = zone.x * 100 + w // 2 + new_center[0]
            y = zone.y * 140 + h // 2 + new_center[1]

            try:
                color = pygame.Color(zone.meta.color)

            except (ValueError, TypeError):
                color = pygame.Color('yellow')

            pygame.draw.circle(window, color, (x, y), 30)
            pen = font
            if len(zone.name) > 12:
                pen = font2

            window.blit(pen.render(zone.name, True, 'black'),
                        (x - 30, y - 60))
            window.blit(font.render(zone.meta.zone_type, True, 'black'),
                        (x - 30, y + 32))
            window.blit(
                font.render(f"Max_dr: {zone.meta.max_drones}", True, 'black'),
                (x - 30, y + 45))
            window.blit(font.render(
                f"Curr_dr: {zone.meta.curr_drones}", True, 'black'),
                        (x - 30, y - 45))

    @staticmethod
    def draw_drones(window, img_drn, new_center, drones, i):

        info = pygame.display.Info()
        w = info.current_w
        h = info.current_h
        font = pygame.font.Font(None, 100)
        font2 = pygame.font.Font(None, 20)

        for drone in drones:

            if drone.in_cnx:
                x = ((drone.curr_zone.x + drone.next_zone.x
                      ) / 2) * 100 + w // 2 + new_center[0]

                y = ((drone.curr_zone.y + drone.next_zone.y
                      ) / 2) * 140 + h // 2 + new_center[1]

            else:
                x = drone.curr_zone.x * 100 + w // 2 + new_center[0]
                y = drone.curr_zone.y * 140 + h // 2 + new_center[1]

            window.blit(img_drn, (x - 30, y - 29))
            window.blit(font.render(f"Turn: {i}", True, 'black'),
                        (0, 0))
            window.blit(font2.render(
                f"{'-' * 15}Instruction: {'-' * 15}", True, 'black'),
                        (10, 60))
            window.blit(font2.render(
                "Press 'm' to move drones.", True, 'black'),
                        (15, 80))
            window.blit(font2.render(
                "Press 'r' to restart from beginning.", True, 'black'),
                        (15, 100))

    @staticmethod
    def display(data: Data, drones: Drones, name_map: str) -> None:

        pygame.init()
        info = pygame.display.Info()
        w = info.current_w
        h = info.current_h
        gen_drones = Simulation.find_pt_per_drone(data, drones)

        pygame.display.set_caption(f"FLY-IN/Map: {name_map}")
        window = pygame.display.set_mode((w, h), pygame.RESIZABLE)
        run = True
        bouton = False
        new_center = [0, 0]
        img_drn = pygame.image.load('drone.png')
        i = 0

        while run:

            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    run = False

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    bouton = True

                elif event.type == pygame.MOUSEBUTTONUP:
                    bouton = False

                elif event.type == pygame.MOUSEMOTION and bouton:
                    new_x, new_y = event.rel
                    new_center[0] += new_x
                    new_center[1] += new_y

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_m:
                        try:

                            drones = next(gen_drones)

                            if i == 0 and not drones[0].next_zone:
                                ParseManager.error('No path is found to the '
                                                   'end zone.', 0)
                            i += 1

                        except StopIteration:
                            pass

                    elif event.key == pygame.K_r:

                        i = 0
                        drones = [
                            Drones(f"Dr_{j}", data.start_zone)
                            for j in range(data.nb_drones)
                            ]

                        Simulation.reset_all_data(data)

                        gen_drones = Simulation.find_pt_per_drone(data, drones)

            window.fill((128, 128, 128))
            Visualization.draw(data, window, new_center)

            Visualization.draw_drones(window, img_drn, new_center, drones, i)

            pygame.display.flip()

        pygame.quit()
