import time
import math 
import pygame.transform as transform
from utils import load_sprite
from traffic_light import TrafficLight


from pygame.math import Vector2
import cv2
UP = Vector2(0, -1)
STOP = Vector2(0, 0)
from utils import load_sprite
from pygame.transform import rotozoom, rotate

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
    def __init__(self, road, roadI, goal, leftTurns):
        self.Initposition = Vector2(road[0])
        self.position = Vector2(self.Initposition)
        self.stopLine = Vector2(road[1])
        self.turn = 0
        self.road = road
        self.roadI = roadI
        if road[5] == 1:
            self.turn = 1
       # if goal == 1:
            # self.turn = -1
            # if self.roadI == 0:
            #     self.road = leftTurns[0]
            # elif self.roadI == 2:
            #     self.road= leftTurns[1]
            # elif self.roadI == 5:
            #     self.road = leftTurns[2]
            # elif self.roadI == 6:
            #     self.road= leftTurns[3]

        self.goal = Vector2(self.road[2])
        self.endLine = Vector2(self.road[3])
        self.direction = Vector2(self.road[4])
        # self.radius
        self.I = roadI
        self.pastSL = False
        self.pastGL = False
        
        
        self.acceleration = 0.1
        self.distance = 0
        self.sprite = transform.rotozoom(load_sprite("carRight", True), 0, 0.35)
        self.speed = 0.02
        self.maxSpeed = 0.2  # meters per second
        self.turnSpeed = 0.5
        self.accel = 0.003
        self.angle = 0
        self.goalDir = Vector2(0)
        self.goalAngle = 0
        self.velocity = self.direction * self.speed
        super().__init__(self.position, self.sprite, Vector2(0))
        if self.direction == (0, 1):
            self.angle = -90
            self.sprite = transform.rotozoom(load_sprite("carDOWN", True), 0, 0.35)
        if self.direction == (0, -1):
            self.angle = 90
            self.sprite = transform.rotozoom(load_sprite("carUP", True), 0, 0.35)
        if self.direction == (1, 0):
            self.angle = 0
            self.sprite = transform.rotozoom(load_sprite("carRIGHT", True), 0, 0.35)
        if self.direction == (-1, 0):
            self.angle = 180
            self.sprite = transform.rotozoom(load_sprite("carLEFT", True), 0, 0.35)
    
    def accelerate(self):
        
        if self.speed + self.accel >= self.maxSpeed:
            self.speed = self.maxSpeed
        else:
            self.speed += self.accel
        self.velocity = self.direction * (self.speed + self.accel)

    def decelerate(self):
        if self.speed - self.accel <= 0:
            self.speed = 0
            self.velocity = self.direction * self.speed
            return
        self.speed -= self.accel
        self.velocity = self.direction * (self.speed)

    def explode(self, other):
        pass

    def decelerateTo(self, other, dist):
        if self.collides_with(other):
            self.speed = 0
            self.velocity = self.direction * self.speed
        if self.speed - self.accel <= 0:
            self.speed = 0
            self.velocity = self.direction * self.speed
            return
        if self.direction == (0, 1) or self.direction == (0, -1):
            if self.direction.y * (other.position.y - self.position.y) > dist:
                self.speed = self.maxSpeed/2
        if self.direction == (1, 0) or self.direction == (-1, 0):
            if self.direction.x * (other.position.x - self.position.x ) <= dist:
                self.speed = 0
        self.velocity = self.direction * 0
    def updateSprite(self):
        if self.direction == (0, 1):
            self.angle = -90
            self.sprite = transform.rotozoom(load_sprite("carDOWN", True), 0, 0.5)
        elif self.direction == (0, -1):
            self.angle = 90
            self.sprite = transform.rotozoom(load_sprite("carUP", True), 0, 0.5)
        elif self.direction == (1, 0):
            self.angle = 0
            self.sprite = transform.rotozoom(load_sprite("carRIGHT", True), 0, 0.5)
        elif self.direction == (-1, 0):
            self.angle = 180
            self.sprite = transform.rotozoom(load_sprite("carLEFT", True), 0, 0.5)
        else:
            self.sprite = transform.rotozoom(load_sprite("carRIGHT", True), self.angle, 0.5)
    def draw(self, surface):
        
        rotated_surface = self.sprite
        rotated_surface_size = Vector2(rotated_surface.get_size())
        blit_position = self.position - rotated_surface_size * 0.5
        surface.blit(rotated_surface, blit_position)

    def isPathClear(self, vehicles):
        if self.turn != -1:
            return True
            
        # Define more focused danger zones based on direction
        if self.roadI == 0:  # Coming from left
            danger_x = range(350, 485)
            danger_y = range(350, 435)
        elif self.roadI == 2:  # Coming from bottom
            danger_x = range(435, 485)
            danger_y = range(350, 450)
        elif self.roadI == 5:  # Coming from right
            danger_x = range(350, 485)
            danger_y = range(360, 450)
        elif self.roadI == 6:  # Coming from top
            danger_x = range(330, 435)
            danger_y = range(350, 450)
        else:
            return True

        # Only check straight-going traffic in opposing directions
        for vehicle in vehicles:
            if vehicle != self and vehicle.turn == 0:  # Only check non-turning vehicles
                if ((self.roadI == 0 and vehicle.roadI == 5) or
                    (self.roadI == 2 and vehicle.roadI == 6) or
                    (self.roadI == 5 and vehicle.roadI == 0) or
                    (self.roadI == 6 and vehicle.roadI == 2)):
                    if (int(vehicle.position.x) in danger_x and 
                        int(vehicle.position.y) in danger_y):
                        return False
                    # Check if vehicle is approaching intersection
                    if not vehicle.pastSL and vehicle.distToSL() and vehicle.distToSL() < 30:
                        return False
        return True

    def update(self, vehicles, trafficLights, crossing):
        # Check for traffic lights and vehicle collisions
        if self.distToSL() and self.distToSL() <= 4:
            self.pastSL = True
        for vehicle in vehicles:
            if vehicle.I == self.I and vehicle != self:
                dist = self.distToOther(vehicle)
                if dist is None or dist < 0:
                    continue
                if dist < 100 + self.radius:
                   self.speed = self.maxSpeed/2
                if dist < 25 + self.radius:
                    self.speed = 0
                    self.velocity = self.direction * self.speed
                    return
        self.position += self.direction * self.speed
        trafficLight = trafficLights[self.I]
        if(self.pastSL and self.turn == 0):
            self.accelerate()
            return
        
        if self.distToSL() and self.distToSL() <= 2:
            self.pastSL = True
        elif self.distToSL() and self.distToSL() > 20:
            self.accelerate()
            return
        if self.distToSL() < 20 and trafficLight.state == "green" and not self.pastSL:
            self.accelerate()
            return
        

        if(not self.pastSL and trafficLight.state == "green"):
            self.accelerate()
        elif self.distToSL() < 20 and trafficLight.state == "red" and not self.pastSL:
                self.decelerateTo(trafficLight, 5)
                return
        self.updateSprite()
        # Handle cars that need to turn
        if self.turn != 0 and self.pastSL:
            if not self.pastGL:  # Move from stop line to goal line
                if self.turn == 1:  # Right turn specific logic
                    direction_to_goal = (self.goal - self.position).normalize()
                    self.direction = direction_to_goal
                    self.position += self.direction * (self.speed * 2)  # Increase turn speed
                    self.angle = self.angleTo(self.goal)
                    self.updateSprite()

                    if self.position.distance_to(self.goal) < 5:  # Increased detection radius
                        self.position = self.goal
                        self.pastGL = True
                        self.direction = (self.endLine - self.goal).normalize()
                        self.speed = self.maxSpeed
                    return

                if self.turn == -1:
                    if not hasattr(self, 'wait_time'):
                        self.wait_time = 0
                    
                    # Reset wait time if path is not clear
                    if not self.isPathClear(vehicles):
                        self.wait_time = 0
                        self.speed = 0
                        return
                    
                    # Increment wait time and check if we should start moving
                    self.wait_time += 1
                    if self.wait_time < 60:  # Increased waiting time
                        self.speed = 0
                        return
                    
                    # Start moving after wait time and path is clear
                    self.speed = self.maxSpeed * 0.5  # Start with reduced speed

                direction_to_goal = (self.goal - self.position).normalize()
                self.direction = direction_to_goal
                self.position += self.direction * self.speed
                self.angle = self.angleTo(self.goal)
                self.updateSprite()

                if self.position.distance_to(self.goal) < 2:
                    self.position = self.goal
                    self.pastGL = True
                    self.direction = (self.endLine - self.goal).normalize()
                    self.speed = self.maxSpeed

            else:  # Move from goal line to end line
                self.position += self.direction * self.speed
                self.angle = self.angleTo(self.endLine)
                self.updateSprite()
            return

        self.distance = math.sqrt(math.pow(self.position.x - self.Initposition.x, 2) + math.pow(self.position.y - self.Initposition.y, 2))
    def angleTo(self, pos):
        dx = pos.x - self.position.x
        dy = pos.y - self.position.y
        rads = math.atan2(-dy, dx)
        rads %= 2 * math.pi 
        degs = math.degrees(rads)
        return degs
    def distToOther(self, other):
        if self.direction == (0, 1) or self.direction == (0, -1):
            if other.I == self.I and other != self:
                return self.direction.y * (other.position.y - self.position.y)
        if self.direction == (1, 0) or self.direction == (-1, 0):
            if other.I == self.I and other != self:
                return self.direction.x * (other.position.x - self.position.x)
        return float('inf')  # Return infinite distance if no valid comparison
                        
    def turnTo(self, pos):
        self.direction = self.angle_to(pos)
        

    def distToSL(self):
        # Check if the vehicle is near a traffic light
        if self.direction == (1, 0) or self.direction == (-1, 0):
            return self.direction[0] * (self.stopLine.x - self.position.x)
        elif self.direction == (0, 1) or self.direction == (0, -1):
            return self.direction[1] * (self.stopLine.y - self.position.y)
        return 0
        
    def distToGL(self):
        #check if vehicle is past goal line
        if self.position.distance_to(self.goal) <= 2:
            self.direction = self.goalDir
            self.turn = False
        return self.position.distance_to(self.goal)

class carPortal(GameObject):
    def __init__(self, position):
        self.position = position
        self.timer = 0
        self.spawnRate = 1
        self.spawnLimit = 6
        self.spawned = 0
        self.spawnedCars = []

