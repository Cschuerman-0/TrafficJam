import time
import math 
import pygame.transform as transform
from utils import load_sprite


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
    def __init__(self, position, direction, goal, road, roadI):
        self.Initposition = Vector2(position)
        self.position = Vector2(self.Initposition)
        self.direction = Vector2(direction)
        self.goal = goal
        self.I = roadI
        self.pastSL = False
        self.road = road
        self.acceleration = 0.1
        self.distance = 0
        self.sprite = transform.rotozoom(load_sprite("car", True), 0, 0.5)
        self.speed = 0.32
        self.maxSpeed = 0.52  # meters per second
        self.turnSpeed = 0.5
        self.angle = 0
        super().__init__(position, self.sprite, Vector2(0))
        if self.direction == (0, 1):
            self.sprite = transform.rotozoom(self.sprite, -90, 0.5)
        if self.direction == (0, -1):
            self.sprite = transform.rotozoom(self.sprite, 90, 0.5)
        if self.direction == (1, 0):
            self.sprite = transform.rotozoom(self.sprite, 0, 0.5)
        if self.direction == (-1, 0):
            self.sprite = transform.rotozoom(self.sprite, 180, 0.5)

    def accelerate(self):
        self.velocity += self.direction * self.accel

    def decelerate(self):
        self.velocity += - self.velocity * .05 

    def draw(self, surface):
        
        rotated_surface = self.sprite
        rotated_surface_size = Vector2(rotated_surface.get_size())
        blit_position = self.position - rotated_surface_size * 0.5
        surface.blit(rotated_surface, blit_position)

    def update(self, vehicles, traffic_lights):
        # Check for traffic lights
        traffic_light = traffic_lights[self.I]
        if self.distToSL() < 100 and traffic_light.state == "red" and not self.pastSL:
            if self.speed > self.maxSpeed / 2 :
                self.decelerate()
            elif self.speed <= self.maxSpeed / 2 and self.distToSL() < 10:
                self.velocity = 0
            return
        elif self.distToSL() < 10 and traffic_light.state == "green" and self.speed <= self.maxSpeed and not self.pastSL:
            self.pastSL = True
        
        #if self.position.x < 0 or self.position.x > 800 or self.position.y < 0 or self.position.y > 800:
         #   vehicles.pop(self.count)
        # Check for forward collision
        for other_vehicle in vehicles:
            if other_vehicle != self and other_vehicle.I == self.I:
                distance_to_other = self.position.distance_to(other_vehicle.position)
                if distance_to_other < 50:  # Threshold distance to avoid collision
                    self.decelerate()
                    return
                elif distance_to_other > 50:
                    pass

        # Basic movement
    
        self.position += self.direction * self.speed
        self.distance = math.sqrt(math.pow(self.position.x - self.Initposition.x, 2) + math.pow(self.position.y - self.Initposition.y, 2))
        # Gradually accelerate to max speed
        if self.speed < self.maxSpeed:
            self.speed += self.acceleration
        if self.speed + self.acceleration > self.maxSpeed:
            self.speed = self.maxSpeed
        if self.distance - 225 > 0 and not self.pastSL:
            self.pastSL = True

    def distToSL(self, traffic_light):
        # Check if the vehicle is near a traffic light

        return self.road[1].x - self.position.x

    def is_in_same_lane(self, other_vehicle):
        # Check if the other vehicle is in the same lane based on direction and road
        return self.road == other_vehicle.road