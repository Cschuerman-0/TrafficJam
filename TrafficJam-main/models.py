import time
import math 
import pygame.transform as transform
from utils import load_sprite
from traffic_light import TrafficLight


from pygame.math import Vector2
UP = Vector2(0, -1)
STOP = Vector2(0, 0)
from utils import load_sprite
from pygame.transform import rotozoom

class GameObject:
    def __init__(self, position, sprite, velocity):
        self.position = Vector2(position)
        self.sprite = sprite
        self.radius = sprite.get_width() / 2
        self.velocity = Vector2(velocity)
    
    def draw(self, surface):
        blit_position = self.position - Vector2(self.radius)
        surface.blit(self.sprite, blit_position)

    def move(self, surface):
        self.position = self.position + self.velocity, surface

    def collides_with(self, other_obj):
        distance = self.position.distance_to(other_obj.position)
        return distance < self.radius + other_obj.radius
    
class Vehicle(GameObject):
    def __init__(self, road, roadI, goal):
        self.Initposition = Vector2(road[0])
        self.position = Vector2(self.Initposition)
        self.stopLine = Vector2(road[1])
        self.turn = False
        if goal == 2:
            self.turn = True
        self.goal = Vector2(road[2])
        self.direction = Vector2(road[3])
        
        self.I = roadI
        self.pastSL = False
        self.road = road
        self.acceleration = 0.1
        self.distance = 0
        self.sprite = transform.rotozoom(load_sprite("car", True), 0, 0.5)
        self.speed = 0.12
        self.maxSpeed = 0.52  # meters per second
        self.turnSpeed = 0.5
        self.accel = 0.03
        self.angle = 0
        self.velocity = self.direction * self.speed
        super().__init__(self.position, self.sprite, Vector2(0))
        if self.direction == (0, 1):
            self.sprite = transform.rotozoom(self.sprite, -90, 0.5)
        if self.direction == (0, -1):
            self.sprite = transform.rotozoom(self.sprite, 90, 0.5)
        if self.direction == (1, 0):
            self.sprite = transform.rotozoom(self.sprite, 0, 0.5)
        if self.direction == (-1, 0):
            self.sprite = transform.rotozoom(self.sprite, 180, 0.5)

    def accelerate(self):
        self.velocity = self.direction * (self.speed + self.accel)
        self.speed += self.accel

    def decelerate(self):
        if self.speed - self.accel <= 0:
            self.speed = 0
            self.velocity = self.direction * self.speed
            return
        self.speed -= self.accel
        self.velocity = self.direction * (self.speed)

    def decelerateTo(self, otherPos, dist):
        if self.collides_with(otherPos):
            self.speed = 0
            self.velocity = self.direction * self.speed
        if self.speed - self.accel <= 0:
            self.speed = 0
            self.velocity = self.direction * self.speed
            return
        if self.direction == (0, 1) or self.direction == (0, -1):
            if self.direction.y * (otherPos.y - self.position.y) > dist:
                self.decelerate
        if self.direction == (1, 0) or self.direction == (-1, 0):
            if self.direction.x * (otherPos.x - self.position.x ) <= dist:
                self.speed = 0
        self.velocity = self.direction * 0
        
    def draw(self, surface):
        
        rotated_surface = self.sprite
        rotated_surface_size = Vector2(rotated_surface.get_size())
        blit_position = self.position - rotated_surface_size * 0.5
        surface.blit(rotated_surface, blit_position)

    def update(self, vehicles, trafficLights):
        # Check for traffic lights
        self.position += self.direction * self.speed
        trafficLight = trafficLights[self.I]
        self.distToOther(vehicles)
        if self.distToSL() <= 0:
            self.pastSL = True
        if(self.pastSL):
            self.accelerate()
        if self.distToSL() < 20 and trafficLight.state == "red" and not self.pastSL:
                self.decelerateTo(trafficLight.position, 30)
                return
        elif trafficLight.state == "green":
            self.accelerate()
            return

        
        #if self.position.x < 0 or self.position.x > 800 or self.position.y < 0 or self.position.y > 800:
         #   vehicles.pop(self.count)
        # Check for forward collision
        # for other_vehicle in vehicles:
        #     if other_vehicle != self and other_vehicle.I == self.I:
        #         distance_to_other = self.position.distance_to(other_vehicle.position)
        #         if distance_to_other < 50 and other_vehicle.speed > self.speed:  # Threshold distance to avoid collision
        #             self.decelerate()
        #             return
        #         elif distance_to_other > 50:
        #             pass

        # Basic movement
    
        self.position += self.direction * self.speed
        self.distance = math.sqrt(math.pow(self.position.x - self.Initposition.x, 2) + math.pow(self.position.y - self.Initposition.y, 2))
        # Gradually accelerate to max speed

    def distToOther(self, others):
        for other in others:
            if self.direction == other.direction and self.I == other.I:
                if abs(other.position.x - self.position.x) < 30:
                    if self.collides_with(other):
                        self.speed = 0 
                        self.velocity = 0 * self.direction
                    if other.speed > self.speed:
                        return -1
                    elif other.speed < 0:
                        self.decelerateTo(other.position, 30)
                else:
                    return


    def distToSL(self):
        # Check if the vehicle is near a traffic light
        if abs(self.direction[0]) == 1:
            return self.direction[0] * (self.stopLine.x - self.position.x)
        elif abs(self.direction[1]) == 1:
            return self.direction[1] * (self.stopLine.y - self. stopLine.y)

    def is_in_same_lane(self, other_vehicle):
        # Check if the other vehicle is in the same lane based on direction and road
        return self.road == other_vehicle.road