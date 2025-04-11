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
        self.clock.tick(60)
        #self.vehicle = Vehicle()
        self.maxCars = 320
        self.vehicles = []
        self.carCount = 0
        self.turn = 0
        self.crossing = [
            #start pos       stop line       goal    Direction
            [(0, 435),    (300, 435),   (575, 435),   (1, 0)],  #road 1
            [(0, 470),    (300, 470),   (330, 500),   (1, 0)],  #road 2
            [(435, 800),  (435, 485),   (435, 300),   (0, -1)], #road 3
            [(470, 800),  (470, 485),   (500, 470),   (0, -1)], #road 4
            [(800, 330),  (485, 330),   (300, 360),   (-1, 0)], #road 5
            [(800, 360),  (485, 360),   (300, 360),   (-1, 0)], #road 6
            [(360, 0),    (360, 300),   (370, 500),   (0, 1)],
            [(330, 0),    (330, 300),   (300, 330),   (0, 1)],  #road 7
              #road 8
        ]

        self.spawn_vehicles()
        self.trafficLights = [
            TrafficLight((305, 435), "green"),
            TrafficLight((305, 470), "green"), 
            TrafficLight((435, 490), "red"),
            TrafficLight((470, 490), "red"),
            TrafficLight((490, 330), "green"), 
            TrafficLight((490, 360), "green"),  
            TrafficLight((360, 305), "red"),
            TrafficLight((330, 305), "red")
        ]

        generator = pygame.event.Event(1)

        pygame.time.set_timer(generator, 1050)

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
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                for SL in self.trafficLights:
                    if SL.state == "green":
                        SL.state = "red"
                    else:
                        SL.state = "green"

    def _process_game_logic(self):
        dt = self.clock.tick() / 1000  # Convert to seconds
        for trafficLight in self.trafficLights:
            trafficLight.update(dt)
        for vehicle in self.vehicles:
            vehicle.update(self.vehicles, self.trafficLights)
            if vehicle.position.x < 0 or vehicle.position.x > 1200 or vehicle.position.y < 0 or vehicle.position.y > 800:
                self.vehicles.pop(self.vehicles.index(vehicle))
                self.carCount -= 1
    
    def draw(self):
        self.screen.blit(self.background, (0, 0))
        for traffic_light in self.trafficLights:
            traffic_light.draw(self.screen)
        for vehicle in self.vehicles:
            vehicle.draw(self.screen)
        pygame.display.flip()

    def spawn_vehicles(self):
        goal = 1
        count = self.carCount
        roadI = 0
        for road in self.crossing:
            if roadI % 2 == 1:
                goal = random.randint(1,2)
            if self.carCount + 1 >= self.maxCars:
                return

            vehicle = Vehicle(road, roadI, goal)
            self.vehicles.append(vehicle)
            self.carCount += 1
            roadI += 1

            

# pygame setup


