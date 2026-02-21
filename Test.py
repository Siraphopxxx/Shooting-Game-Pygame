import pygame
from pygame import mixer

# Initialize Pygame
pygame.init()

# Load a sound file
sound = pygame.mixer.Sound('sound/grass.wav')

# Play the sound
sound.play()

