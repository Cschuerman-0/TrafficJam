import random
from pygame import Color
from pygame.mixer import Sound
from pygame.image import load
from pygame.math import Vector2

def load_sprite(name, with_alpha=True):
    path = f"carGame/models/{name}.png"
    loaded_sprite = load(path)

    if with_alpha:
        return loaded_sprite.convert_alpha()
    else:
        return loaded_sprite.convert()

def load_sound(name):
    path = f"carGame/sounds/{name}.wav"
    return Sound(path)