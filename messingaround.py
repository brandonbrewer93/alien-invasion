import pygame
import sys

green = (0, 200, 0)


class Box:
	def __init__(self):
		self.height = 10
		self.width = 10
		self.x = 10
		self.y = 10

	def draw(self, screen):
		pygame.draw.rect(screen, (200, 0, 0, 1), (self.x, self.y, self.height, self.width))




clock = pygame.time.Clock()
pygame.init
screen = pygame.display.set_mode((500, 500))
screen.fill(green)
box = Box()
box.draw(screen)
	
while True:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			sys.exit()
		elif event.type == pygame.KEYDOWN:
			if event.key == pygame.K_DOWN:
				box.y += 10

	clock.tick(10)
	pygame.display.flip()