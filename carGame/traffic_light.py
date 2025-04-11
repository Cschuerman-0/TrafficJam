import pygame
from pygame.math import Vector2

class TrafficLight:
    def __init__(self, position, state="red", green_duration=5, yellow_duration=2, red_duration=5):
        self.position = Vector2(position)
        self.green_duration = green_duration
        self.yellow_duration = yellow_duration
        self.red_duration = red_duration
        self.state = state # Initial state
        self.timer = 0.0
        self.radius = 0
        self.x = position[0]
        self.y = position[1]

    def update(self, dt):
        self.timer += dt
        if self.state == "red" and self.timer >= self.red_duration:
            self.state = "green"
            self.timer = 0
        elif self.state == "green" and self.timer >= self.green_duration:
            self.state = "yellow"
            self.timer = 0
        elif self.state == "yellow" and self.timer >= self.yellow_duration:
            self.state = "red"
            self.timer = 0

    def draw(self, surface):
        color = (255, 0, 0) if self.state == "red" else (255, 255, 0) if self.state == "yellow" else (0, 255, 0)
        pygame.draw.circle(surface, color, (int(self.position.x), int(self.position.y)), 10)
