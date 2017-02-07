import sys

import pygame
from pygame.sprite import Group

from settings import Settings
from game_stats import GameStats
from scoreboard import Scoreboard
from button import Button
from ship import Ship
from alien import Alien
from alien_bullet import AlienBullet
import game_functions as gf


def run_game():
	# Initialize game and create screen object.
	pygame.init()
	clock = pygame.time.Clock()
	ai_settings = Settings()
	alien_icon = pygame.image.load('images/new_alien.bmp')
	icon = pygame.transform.scale(alien_icon, (32, 32))
	pygame.display.set_icon(icon)
	screen = pygame.display.set_mode(
		(ai_settings.screen_width, ai_settings.screen_height))
	pygame.display.set_caption("Alien Invasion")
	alien = Alien(ai_settings, screen)
	
	
	# Make the Play button.
	play_button = Button(ai_settings, screen, "Press p to play")
	
	# Create an instance to store game statistics.and create a scoreboard.
	stats = GameStats(ai_settings)
	sb = Scoreboard(ai_settings, screen, stats)
	
	# Make a ship a group of bullets, and a group of aliens.
	ship = Ship(ai_settings, screen)
	bullets = Group()
	aliens = Group()
	alien_bullets = Group()
	
	# Play soundtrack.
	pygame.mixer.music.load('sounds/theme.mp3')
	pygame.mixer.music.set_volume(.5)
	pygame.mixer.music.play(-1)
	
	# Create the fleet of aliens.
	gf.create_fleet(ai_settings, screen, ship, aliens)
	
	# Start the main loop for the game.
	while True:
		gf.check_events(ai_settings, screen, stats, sb, play_button, ship, 
			aliens, bullets, alien_bullets)
		if stats.game_active:
			ship.update()
			gf.update_bullets(ai_settings, screen, stats, sb, ship, alien, aliens, bullets, alien_bullets)
			gf.update_alien_bullets(ai_settings, alien_bullets)
			gf.update_aliens(ai_settings, screen, stats, sb, ship, aliens, bullets, alien, alien_bullets)
		clock.tick(120)
		gf.update_screen(ai_settings, screen, stats, sb, ship, aliens, bullets, alien_bullets, play_button)
run_game()
