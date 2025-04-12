import pygame, time, argparse, random, math
import numpy as np
from models import Vehicle, carPortal #explosion
import random
random.seed(42)
from pythonosc import udp_client
from path import Path
from utils import load_sprite
from traffic_light import TrafficLight

#pygame.mouse.set_visible(True)

class Simulation:

    def __init__(self):
        
        self.__init_pygame()
        self.screen = pygame.display.set_mode((630, 630))
        self.screen.fill("white")
        #self.background.copy(self.screen.get_size())
        self.spawnQueue = []
        
        #self.polygon = pygame.Surface(self.screen.get_size())
        self.background = pygame.Surface(self.screen.get_size())
        #self.background = load_sprite("intersection", False)
        self.clock = pygame.time.Clock()
        self.clock.tick(60)
        #self.vehicle = Vehicle()
        self.maxCars = 32
        self.spawnQueue = []
        self.vehicles = []
        self.carCount = 0

        #Music OSC Messages
        self.going = 0
        self.stopped = 0

        #self.roads = [(1, 0), (0, -1), (-1, 0), (0, 1)] #right, up, left, down
        self.pathCords = []  

         #list of paths, each path is a list of points
        self.carPorts = [] #list of car portals, each portal represents a starting point for a car.
        self.paths = [#plot map of each possible car path, right turn, left turn, straight, right turn cars have their own lane.
            Path(0, (1,0), "R1L", [(0, 11.5*30), (7*30, 11.5*30), (10*30, 11.5*30), (11*30, 11*30), (11.5*30, 10*30 ), (11.5*30, 7*30)]), 
            Path(1, (1,0), "R1S", [(0, 11.5*30), (7*30, 11.5*30), (14*30, 11.5*30)]), 
            Path(2, (1,0), "R1R", [(0, 12.5*30), (7*30, 12.5*30), (8*30, 13*30), (8.5*30, 14*30)]),    
            
            Path(3, (0,-1), "R2L", [(11.5*30, 21*30), (11.5*30, 14*30),(11.5*30, 11*30), (11*30, 10*30), (10*30, 9.5*30), (0, 9.5*30)]),  
            Path(4, (0,-1), "R2S", [(11.5*30, 21*30), (11.5*30, 14*30),(11.5*30, 7)]), 
            Path(5, (0,-1), "R2R", [(12.5*30, 21*30), (12.5*30, 14*30), (13*30, 13*30), (14*30, 12.5*30)]), 

            Path(6, (-1, 0), "R3L", [(21*30, 9.5*30), (14*30, 9.5*30),(11*30, 9.5*30), (10*30, 10*30), (9.5*30, 11*30), (9.5*30, 21*30)]),
            Path(7, (-1, 0), "R3S", [(21*30, 9.5*30),(14*30, 9.5*30), (7, 9.5*30)]),     
            Path(8, (-1, 0), "R3R", [(21*30, 8.5*30), (14*30, 8.5*30), (13*30, 8*30), (12.5*30, 7*30)]), 

            Path(9,  (0, 1), "R4L", [(9.5*30, 0), (9.5*30, 7*30),(9.5*30, 10*30), (10*30, 11*30), (11*30, 11.5*30), (21*30, 11.5*30)]),  
            Path(10, (0, 1), "R4S", [(9.5*30, 0), (9.5*30, 7*30),(9.5*30, 14*30)]), 
            Path(11, (0, 1), "R4R", [(8.5*30, 0), (8.5*30, 7*30), (8*30, 8*30), (7*30, 8.5*30)])]
        
        self.carPorts = [
            carPortal(self.paths[0].start), carPortal(self.paths[2].start), 
            carPortal(self.paths[3].start), carPortal(self.paths[5].start),
            carPortal(self.paths[6].start), carPortal(self.paths[8].start),
            carPortal(self.paths[9].start), carPortal(self.paths[11].start)]
    
   
        self.trafficLights = [
            TrafficLight((7*30, 11.5*30), "green"),
            TrafficLight((7*30, 12.5*30), "green"), 
            TrafficLight((8.5*30, 7*30), "red"),
            TrafficLight((9.5*30, 7*30), "red"),
            TrafficLight((14*30, 8.5*30), "green"), 
            TrafficLight((14*30, 9.5*30), "green"),  
            TrafficLight((12.5*30, 14*30), "red"),
            TrafficLight((11.5*30, 14*30), "red")
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
                #self.spawn_vehicles()
                pass
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
                pass
            if event.type == pygame.MOUSEBUTTONUP:
                for vehicle in self.vehicles:
                    vehicle.rect = vehicle.sprite.get_rect(center=vehicle.position)
                    if vehicle.rect.collidepoint(event.pos):
                        print("Vehicle clicked at", event.pos)
                        vehicle.on_click()
                    print("Mouse clicked at", event.pos)

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
            vehicle.update(self.vehicles, self.trafficLights)
            if vehicle.position.x < 0 or vehicle.position.x > 1200 or vehicle.position.y < 0 or vehicle.position.y > 800:
                self.vehicles.pop(self.vehicles.index(vehicle))
                self.carCount -= 1
                
            
            if vehicle.pastSL:
                pass
                      
    def draw(self):
        #   Art Part !

        self.polygonPoints= [ 
            (7*30, 11*30), (0, 11*30), (0, 13*30), (7*30, 13*30), 
            (8*30, 14*30), (8*30, 21*30), (10*30, 21*30), (10*30, 14*30), 
            (11*30, 14*30), (11*30, 21*30), (13*30, 21*30), (13*30, 14*30), 
            (14*30, 13*30), (21*30, 13*30), (21*30, 11*30), (14*30, 11*30),
            (14*30, 10*30), (21*30, 10*30), (21*30, 8*30), (14*30, 8*30), 
            (13*30, 7*30), (13*30, 0*30), (11*30, 0*30), (11*30, 7*30),
            (10*30, 7*30), (10*30, 0*30), (8*30, 0*30), (8*30, 7*30), 
            (7*30, 8*30), (0*30, 8*30), (0, 10*30), (7*30, 10*30)]
        pygame.draw.polygon(self.screen, (255, 0, 0), self.polygonPoints, 0)

        self.screen.blit(self.background, (0, 0))
        self.screen.fill("lightGreen")
        pygame.draw.polygon(self.screen, "lightgray", self.polygonPoints, 0)
        pygame.draw.lines(self.screen, "yellow", True, self.polygonPoints, 3)
        for path in self.paths:
            pygame.draw.lines(self.screen, "black", False, path.nodes, 3)
        for traffic_light in self.trafficLights:
            traffic_light.draw(self.screen)
        for vehicle in self.vehicles:
            vehicle.draw(self.screen)
        pygame.display.flip()

    
    def spawn_vehicles(self):
        lane = 0
        self.leftTurnRate = 0.2
        self.rightTurnRate = 1.0
        print(len(self.carPorts), self.carCount, self.maxCars)
        for portal in self.carPorts:
            if portal.spawnCheck(self.vehicles):

                if self.carCount < self.maxCars:
                    self.carCount += 1
                    #print(portal.position, )

                    i = self.carPorts.index(portal)
                    g = math.floor(i/2)
                    if i%2 == 0: #0 2 4 6
                        if random.random() <1:
                            print("Left:", i + math.floor(i/2), i)
                            leftCar = Vehicle(self.paths[i + math.floor(i/2)], i + math.floor(i/2), self.paths, lane)
                            self.vehicles.append(leftCar)
                        else:
                            
                            print("Straight:",i*2 - (math.floor(i/2) - 1), i, g)
                            straightCar= Vehicle(self.paths[i*2 - (math.floor(i/2) - 1)], i*2 - (math.floor(i/2) - 1), self.paths, lane)
                            self.vehicles.append(straightCar)
                        lane += 1
                    else: #1 3 5 7
                        print("Right:", i*2 - math.floor(i/2), i, g)
                        if random.random() * 0 < self.rightTurnRate:
                            rightCar = Vehicle(self.paths[i*2 - math.floor(i/2)], i*2 - math.floor(i/2), self.paths, lane)
                            self.vehicles.append(rightCar)
                        lane += 1
            else:
                print("Lane full")
                lane += 1
                pass


    
            

# pygame setup