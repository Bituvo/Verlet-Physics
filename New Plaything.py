from time import perf_counter, sleep
from math import sqrt
from random import randint, random
from colorsys import hsv_to_rgb
import pygame

SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1200
RADIUS = 500
CURSOR_RADIUS = 200
FPS = 60
GRAVITY = (0, 1)

ID = 0

def clamp(x, minimum, maximum):
    return max(min(x, maximum), minimum)

class Node:
    def __init__(self, x, y, radius, mass=None, restitution=None):
        global ID

        self.id = ID
        ID += 1

        self.x, self.y = x, y
        self.old_x, self.old_y = x, y
        self.radius = radius
        self.mass = mass or radius ** 2
        self.restitution = restitution or 0.8

        self.color = random()

class App:
    def __init__(self):
        self.initialize_window()
        self.initialize_world()

        while self.running:
            self.solve()
            self.render()

            self.handle_keys()
            self.clock.tick(FPS)

        pygame.quit()

    def initialize_window(self):
        pygame.init()
        pygame.display.set_caption('Verlet Physics')

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 28)
        self.running = True

    def add_node(self, x, y, radius):
        self.nodes.append(Node(x, y, radius))

    def initialize_world(self):
        self.nodes = []

        for _ in range(5):
            self.add_node(randint(-20, 20), randint(-20, 20), 60)

        for _ in range(70):
            self.add_node(randint(-20, 20), randint(-20, 20), 40)

        for _ in range(20):
            self.add_node(randint(-20, 20), randint(-20, 20), 20)

    def handle_keys(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                self.running = False

    def solve(self):
        for node in self.nodes:
            x_velocity = node.x - node.old_x + GRAVITY[0]
            y_velocity = node.y - node.old_y + GRAVITY[1]

            node.old_x, node.old_y = node.x, node.y
            node.x += x_velocity * 0.99
            node.y += y_velocity * 0.99

        self.mouse_repulsion()

        for _ in range(5):
            self.handle_collisions()
        
        self.constrain()

    def mouse_repulsion(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()

        for node in self.nodes:
            distance_x = mouse_x - node.x
            distance_y = mouse_y - node.y
            distance = sqrt(distance_x ** 2 + distance_y ** 2)

            if distance < CURSOR_RADIUS:
                repulsion = CURSOR_RADIUS - distance
                repulsion_x = distance_x / distance * repulsion
                repulsion_y = distance_y / distance * repulsion

                node.x -= repulsion_x
                node.y -= repulsion_y

    def handle_collisions(self):
        for node1 in self.nodes:
            for node2 in self.nodes:
                if node1.id < node2.id:
                    distance_x = node2.x - node1.x
                    distance_y = node2.y - node1.y
                    distance = sqrt(distance_x ** 2 + distance_y ** 2)
                    minimum_distance = node1.radius + node2.radius

                    if distance < minimum_distance and distance > 0:
                        penetration = (minimum_distance - distance) / 2
                        push_x = distance_x / distance * penetration
                        push_y = distance_y / distance * penetration

                        total_mass = node1.mass + node2.mass
                        mass_ratio1 = node2.mass / total_mass
                        mass_ratio2 = node1.mass / total_mass

                        node1.x -= push_x * mass_ratio1
                        node1.y -= push_y * mass_ratio1
                        node2.x += push_x * mass_ratio2
                        node2.y += push_y * mass_ratio2

                        restitution = min(node1.restitution, node2.restitution)

                        node1.old_x += push_x * mass_ratio1 * restitution
                        node1.old_y += push_y * mass_ratio1 * restitution
                        node2.old_x -= push_x * mass_ratio2 * restitution
                        node2.old_y -= push_y * mass_ratio2 * restitution

    def constrain(self):
        for node in self.nodes:
            distance_from_origin = sqrt((SCREEN_WIDTH / 2 - node.x) ** 2 + (SCREEN_HEIGHT / 2 - node.y) ** 2)
            max_distance = RADIUS - node.radius

            if distance_from_origin > max_distance:
                normal_x = (node.x - SCREEN_WIDTH / 2) / distance_from_origin
                normal_y = (node.y - SCREEN_HEIGHT / 2) / distance_from_origin

                node.x = SCREEN_WIDTH / 2 + normal_x * max_distance
                node.y = SCREEN_HEIGHT / 2 + normal_y * max_distance

            # node.x = clamp(node.x, node.radius, SCREEN_WIDTH - node.radius)
            # node.y = clamp(node.y, node.radius, SCREEN_HEIGHT - node.radius)

    def render(self):
        self.screen.fill((10, 25, 50))
        pygame.draw.circle(self.screen, (10, 35, 65), (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2), RADIUS)

        for node in self.nodes:
            color = [round(i * 255) for i in hsv_to_rgb(node.color, 0.1, 1)]
            pygame.draw.circle(self.screen, color, (node.x, node.y), node.radius)

        fps_text = self.font.render("FPS: {:.2f}".format(self.clock.get_fps()), True, (255, 255, 255))
        self.screen.blit(fps_text, (10, 10))

        pygame.display.flip()

if __name__ == '__main__':
    app = App()
