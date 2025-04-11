import pygame
import time
import argparse
from models import Vehicle, carPortal #explosion
import random
from pythonosc import udp_client

from utils import load_sprite
from traffic_light import TrafficLight


class Simulation:

    def __init__(self):
        random.seed(42)
        self.__init_pygame()
        self.screen = pygame.display.set_mode((630, 630))
        self.screen.fill("white")
        #self.background.copy(self.screen.get_size())
        self.polygonPoints = [ (7*30, 11*30), (0, 11*30), (0, 13*30), (7*30, 13*30), 
                              (8*30, 14*30), (8*30, 21*30), (10*30, 21*30), (10*30, 14*30), 
                              (11*30, 14*30), (11*30, 21*30), (13*30, 21*30), (13*30, 14*30), 
                              (14*30, 13*30), (21*30, 13*30), (21*30, 11*30), (14*30, 11*30),
                              (14*30, 10*30), (21*30, 10*30), (21*30, 8*30), (14*30, 8*30), 
                              (13*30, 7*30), (13*30, 0*30), (11*30, 0*30), (11*30, 7*30),
                              (10*30, 7*30), (10*30, 0*30), (8*30, 0*30), (8*30, 7*30), 
                              (7*30, 8*30), (0*30, 8*30), (0, 10*30), (7*30, 10*30)]
        pygame.draw.polygon(self.screen, (255, 0, 0), self.polygonPoints, 0)
        #self.polygon = pygame.Surface(self.screen.get_size())
        self.background = pygame.Surface(self.screen.get_size())
        #self.background = load_sprite("intersection", False)
        self.clock = pygame.time.Clock()
        self.clock.tick(60)
        #self.vehicle = Vehicle()
        self.maxCars = 32
        self.vehicles = []
        self.carCount = 0
        self.turn = 0
        self.going = 0
        self.stopped = 0
        self.carPorts = []
        self.crossing = [
            #start pos       stop line       goal    Direction
            [(0, 435),    (300, 435),   (575, 435),   (800, 435), (1, 0), 0],  #road 1
            [(0, 470),    (300, 470),   (330, 500),   (330, 800), (1, 0), 1],  #road 2
            [(435, 800),  (435, 500),   (435, 300),   (435, 0), (0, -1), 0], #road 3
            [(470, 800),  (470, 500),   (500, 470),   (800, 470), (0, -1), 1], #road 4
            [(800, 330),  (485, 330),   (470, 300),   (470, 0), (-1, 0), 1], #road 5
            [(800, 360),  (485, 360),   (300, 360),   (0, 360), (-1, 0), 0], #road 6
            [(360, 0),    (360, 300),   (360, 500),   (360, 800), (0, 1), 0],#road 7
            [(330, 0),    (330, 300),   (300, 330),   (0, 330), (0, 1), 1]  #road 8
              
        ]
        self.leftTurns = [
            [(0, 435),    (300, 435),   (435, 330),   (435, 0), (1, 0), 0],  #road 1
            [(435, 800),  (435, 485),   (300, 360),   (0, 360), (0, -1), 0],   #road 3
            [(800, 360),  (485, 360),   (360, 300),   (360, 800), (-1, 0), 0],   #road 6
            [(360, 0),    (360, 300),   (575, 435),   (800, 435), (0, 1), 0]   #road 7
        ]
        for road in self.crossing:
            port = carPortal(road[1])
            self.carPorts.append(port)
        self.spawn_vehicles()
        self.trafficLights = [
            TrafficLight((305, 435), "green"),
            TrafficLight((305, 470), "green"), 
            TrafficLight((435, 500), "red"),
            TrafficLight((470, 500), "red"),
            TrafficLight((490, 330), "green"), 
            TrafficLight((490, 360), "green"),  
            TrafficLight((360, 305), "red"),
            TrafficLight((330, 305), "red")
        ]

        generator = pygame.event.Event(1)
        switch = pygame.event.Event(2)
        pygame.time.set_timer(generator, 2000)
        pygame.time.set_timer(switch, 6000)

    def __init_pygame(self):
        pygame.init()
        pygame.display.set_caption("Traffic Jam")

    def main_loop(self):
        while True:
            self._handle_input()
            self._process_game_logic()
            self.draw()
            #if self.clock.get_time() % 4 == 1:
                #self.message()
            dt = self.clock.tick() / 100
            #self.message()
    def message(self):
        parser = argparse.ArgumentParser(description='Traffic Simulation')
        parser.add_argument('--ip', default = "127.0.0.1", help='IP Address')
        parser.add_argument('--port', default = 6448, type=int, help='Port')
        args = parser.parse_args()
        print(args.ip)
        client = udp_client.SimpleUDPClient(args.ip, args.port)
        #self.going = self.going/self.carCount 
        client.send_message("/wek/inputs", self.going)
        print("sent !", self.going, self.stopped, self.carCount)
       # client.send_message("/stopped", self.stopped)
        #client.send_message("/total", self.carCount)
    
    def _handle_input(self):
        for event in pygame.event.get():
            if event.type == 1:
                self.spawn_vehicles()
            if event.type == 2:
                for SL in self.trafficLights:
                    if SL.state == "green":
                        SL.state = "red"
                    else:
                        SL.state = "green"
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
            if event.type == pygame.KEYDOWN and event.key == pygame.K_UP:
                self.spawn_vehicles()

    def _process_game_logic(self):
        dt = self.clock.tick() / 1000  # Convert to seconds
        for trafficLight in self.trafficLights:
            trafficLight.update(dt)
        self.stopped = 0.0
        self.going = 0.0
        for vehicle in self.vehicles:
            if vehicle.speed == 0:
                self.stopped += 1.0
            if vehicle.speed > 0:
                self.going += 1.0
            vehicle.update(self.vehicles, self.trafficLights, self.crossing)
            if vehicle.position.x < 0 or vehicle.position.x > 1200 or vehicle.position.y < 0 or vehicle.position.y > 800:
                self.vehicles.pop(self.vehicles.index(vehicle))
                self.carCount -= 1
                self.carPorts[vehicle.I].spawned -= 1
                self.carPorts[vehicle.I].spawnedCars.pop(self.carPorts[vehicle.I].spawnedCars.index(vehicle))
            
            if vehicle.pastSL:
                pass
                        
    
    def draw(self):
        self.screen.blit(self.background, (0, 0))
        self.screen.fill("lightGreen")
        pygame.draw.polygon(self.screen, "lightgray", self.polygonPoints, 0)
        pygame.draw.lines(self.screen, "yellow", True, self.polygonPoints, 3)
        for traffic_light in self.trafficLights:
            traffic_light.draw(self.screen)
        for vehicle in self.vehicles:
            vehicle.draw(self.screen)
        pygame.display.flip()

    def spawn_vehicles(self):
        
        roadI = 0
        for road in self.crossing:
            goal = 0
            if road[5] == 1:
                goal = 1
                pass
            if self.carCount + 1 >= self.maxCars or len(self.carPorts[roadI].spawnedCars) >= 5:
                return

            vehicle = Vehicle(road, roadI, goal, self.leftTurns)
            self.carPorts[roadI].spawnedCars.append(vehicle)
            self.carPorts[roadI].spawned += 1
            self.vehicles.append(vehicle)
            self.carCount += 1
            roadI += 1

            

# pygame setup
