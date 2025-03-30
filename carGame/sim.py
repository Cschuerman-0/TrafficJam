import pygame
import time

from models import Vehicle
import random
from utils import load_sprite
from traffic_light import TrafficLight


class Simulation:

    def __init__(self):
        self.__init_pygame()
        self.screen = pygame.display.set_mode((800, 800))
        self.background = load_sprite("intersection", False)
        self.clock = pygame.time.Clock()
        #self.vehicle = Vehicle()
        self.maxCars = 32
        self.vehicles = []
        self.carCount = 0
        self.turn = 0
        self.crossing = [
            #start pos       stop line       goal           end            Direction
            [(0, 435),    (225, 435), (575, 435),    (800, 435),   (1, 0)],  #road 1
            [(0, 470),    (225, 470), (257.5, 225),    (257.5, 800),   (1, 0)],  #road 2
            [(435, 800),  (457.5, 575), (457.5, 225),    (457.5, 0),     (0, -1)], #road 3
            [(470, 800),  (532.5, 575), (575, 532.5),    (800, 532.5),   (0, -1)], #road 4
            [(800, 330),  (575, 457.5), (225, 457.5),    (0, 457.5),     (-1, 0)], #road 5
            [(800, 360),  (575, 532.5), (532.5, 225),    (532.5, 0),     (-1, 0)], #road 6
            [(330, 0),    (332.5, 225), (332.5, 575),    (332.5, 800),   (0, 1)],  #road 7
            [(370, 0),    (257.5, 225), (225, 257.5),    (0, 257.5),     (0, 1)],  #road 8
        ]

        self.spawn_vehicles()
        self.traffic_lights = [
            TrafficLight((305, 435), "green"),
            TrafficLight((305, 470), "green"),
            TrafficLight((490, 330), "green"), 
            TrafficLight((490, 360), "green"),   
            TrafficLight((360, 305), "green"),
            TrafficLight((330, 305), "green"),
            TrafficLight((435, 490), "green"),
            TrafficLight((470, 490), "green") 
        ]

        generator = pygame.event.Event(1)

        pygame.time.set_timer(generator, 550)

    def __init_pygame(self):
        pygame.init()
        pygame.display.set_caption("Traffic Jam")

    def main_loop(self):
        while True:
            self._handle_input()
            self._process_game_logic()
            self.draw()
            dt = self.clock.tick() / 100

    def _handle_input(self):
        for event in pygame.event.get():
            if event.type == 1:
                self.spawn_vehicles()
            if event.type == pygame.QUIT or (
            event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
            ):
                quit()

    def _process_game_logic(self):
        dt = self.clock.tick() / 1000  # Convert to seconds
        for traffic_light in self.traffic_lights:
            traffic_light.update(dt)
        for vehicle in self.vehicles:
            vehicle.update(self.vehicles, self.traffic_lights)
            if vehicle.position.x < 0 or vehicle.position.x > 800 or vehicle.position.y < 0 or vehicle.position.y > 800:
                self.vehicles.pop(self.carCount - 1)
                self.carCount -= 1
    
    def draw(self):
        self.screen.blit(self.background, (0, 0))
        for traffic_light in self.traffic_lights:
            traffic_light.draw(self.screen)
        for vehicle in self.vehicles:
            vehicle.draw(self.screen)
        pygame.display.flip()

    def spawn_vehicles(self):
        goal = random.randint(1, 3)
        count = self.carCount
        for road in self.crossing:
            if self.carCount + 1 >= self.maxCars:
                return
            startPoint = road[0]
            direction = road[4]
            vehicle = Vehicle(startPoint, direction, goal, road, count)
            self.vehicles.append(vehicle)
            self.carCount += 1

            

# pygame setup


