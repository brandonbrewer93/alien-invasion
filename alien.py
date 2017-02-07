import pygame
from pygame.sprite import Sprite

class Alien(Sprite):
	"""A class to represent a single alien in the fleet."""
	def __init__(self, ai_settings, screen):
		"""Initialize the alien and set its starting position."""
		super(Alien, self).__init__()
		self.screen = screen
		self.ai_settings = ai_settings
		
		# Load the alien image and set its rect attribute.
		self.image = pygame.image.load('images/new_alien.bmp')
		self.rect = self.image.get_rect()
		
		# Start each new alien near the top left corner of the screen.
		self.rect.x  = self.rect.width
		self.rect.y = self.rect.height
		
		# Store the aliens exact position
		self.x = float(self.rect.x)
		
		# Alien sounds.
		self.explosion_sound = pygame.mixer.Sound('sounds/alien_explosion.ogg')
		self.explosion_sound.set_volume(.5)
		
	def play_explosion(self):
		self.explosion_sound.play()
		
	def blitme(self):
		"""Draw the alien at its current location."""
		self.screen.blit(self.image, self.rect)
	
	def check_edges(self):
		"""Return True if alien is at edge of screen."""
		screen_rect = self.screen.get_rect()
		if self.rect.right>= screen_rect.right:
			return True
		elif self.rect.left <= 0:
			return True
	
	def update(self):
		"""Move the alien to the right."""
		self.x += (self.ai_settings.alien_speed_factor *
						self.ai_settings.fleet_direction)
		self.rect.x = self.x
