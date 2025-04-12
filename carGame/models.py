import time
import math, pygame 
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
        distance = Vector2(self.position).distance_to(other_obj.position)
        return distance < self.radius + other_obj.radius

    
class Vehicle(GameObject):
    def __init__(self, path, I, paths, lane):
        self.Initposition = Vector2(path.nodes[0])
        self.position = Vector2(self.Initposition)
        self.stopLine = Vector2(path.nodes[1])
        self.turn = 0
        self.rect = pygame.Rect(self.position.x, self.position.y, 30, 30)
        self.path = path
        self.pathI = I        
        self.lane = lane
        self.goal = path.nodes[-2] ## The goal is the second to last node in the path, essentially the stop line at the other side of the intersection
        self.node = path.nodes[0] ## The first node in the path 
        self.I = self.pathI
        self.pastSL = False
        self.pastGL = False
        self.direction = Vector2(path.direction)
        self.position = Vector2(path.nodes[0])
        self.acceleration = 0.1
        self.distance = 0
        self.sprite = transform.rotozoom(load_sprite("carRight", True), 0, 0.35)

        ## Set the stop line based on the direction
        if self.direction == (1, 0):
            self.stopLine = Vector2(7*30, self.position.y)
        elif self.direction == (-1, 0):
            self.stopLine = Vector2(14*30, self.position.y)
        elif self.direction == (0, 1):
            self.stopLine = Vector2(self.position.x, 7*30)
        elif self.direction == (0, -1):
            self.stopLine = Vector2(self.position.x, 14*30)

        self.distToSL = self.distToSL()
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
    def on_click(self):
        # Handle click event on the vehicle
        print("Vehicle clicked!")
        print(f"Position: {self.position}, Speed: {self.speed}, Direction: {self.direction}, path: {self.path.name}")
        # You can add more functionality here, like showing details or changing color
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

    def updateSprite(self):
        if self.direction == (0, 1):
            self.angle = -90
            self.sprite = transform.rotozoom(load_sprite("carDOWN", True), 0, 0.35)
        elif self.direction == (0, -1):
            self.angle = 90
            self.sprite = transform.rotozoom(load_sprite("carUP", True), 0, 0.35)
        elif self.direction == (1, 0):
            self.angle = 0
            self.sprite = transform.rotozoom(load_sprite("carRIGHT", True), 0, 0.35)
        elif self.direction == (-1, 0):
            self.angle = 180
            self.sprite = transform.rotozoom(load_sprite("carLEFT", True), 0, 0.35)
        else:
            self.sprite = transform.rotozoom(load_sprite("carRIGHT", True), self.angle, 0.35)
    def draw(self, surface):
        
        rotated_surface = self.sprite
        rotated_surface_size = Vector2(rotated_surface.get_size())
        blit_position = self.position - rotated_surface_size * 0.5
        surface.blit(rotated_surface, blit_position)

    def isPathClear(self, vehicles):
        #make lasers to check for other vehicles past the stop line and not past their goal line
        pass

    def update(self, vehicles, trafficLights):
        # Check for traffic lights and vehicle collisions
        self.position += self.direction * self.speed
        for node in self.path.path:
            if self.collides_with(node):
                self.node = self.path.nodes[self.path.nodes.index(node)+1]
                direction_to_node = (self.node - self.position).normalize()
                self.direction = direction_to_node
                self.angle = self.angleTo(self.node.position)
                break
        
        
        # self.distToSLVal = self.distToSL(self)
        # self.distToGLVal = self.distToGL(self)
        
        if not self.pastSL:
            for trafficLight in trafficLights:
                if self.collides_with(trafficLight) and trafficLight.state == "green":
                    self.pastSL = True
                #also need to let cars taking a right turn go if the light is red, avoiding collisions
                if self.collides_with(trafficLight) and trafficLight.state == "red" and self.I%3 == 2:
                    self.pastSL = True
            if trafficLights[self.lane].state == "green":
                self.accelerate()
            elif trafficLights[self.lane].state == "red":
                for vehicle in vehicles:
                    if self.collides_with(vehicle):
                        self.decelerate()
                        self.speed = 0
                        self.updateSprite()
                        return
        
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
    
        if self.pastSL or self.pastGL:
            return -1
        else:
            if self.direction == (1, 0):
                self.stopLine = Vector2(7*30, self.position.y)
                return 7*30 - self.position.x
            elif self.direction == (-1, 0):
                self.stopLine = Vector2(14*30, self.position.y)
                return self.position.x - 14*30
            elif self.direction == (0, 1):
                self.stopLine = Vector2(self.position.x, 7*30)
            elif self.direction == (0, -1):
                self.stopLine = Vector2(self.position.x, 14*30)
                return self.direction[1] * (self.stopLine.y - self.position.y)
        return -1
        
    def distToGL(self):
        return self.position.distance_to(self.goal)

class carPortal(GameObject):
    def __init__(self, position):
        self.position = position
        self.radius = 10

    def spawnCheck(self, vehicles):
        for vehicle in vehicles:
            if self.collides_with(vehicle):
                return False
        return True