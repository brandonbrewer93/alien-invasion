import sys
import pygame
from time import sleep
from bullet import Bullet
from alien import Alien
from alien_bullet import AlienBullet
import json
high_score_file = 'high_score.json'

def check_events(ai_settings, screen, stats, sb, play_button, ship, aliens, 
		 bullets, alien_bullets):
	"""Respond to keypresses and mouse events."""
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			with open(high_score_file, 'w') as f_obj:
				json.dump(stats.high_score, f_obj)
			sys.exit()
		elif event.type == pygame.KEYDOWN:
			check_keydown_events(event, ai_settings, screen, stats, sb, ship, aliens, bullets, alien_bullets)
		elif event.type == pygame.KEYUP:
			check_keyup_events(event, ship)
		elif event.type == pygame.MOUSEBUTTONDOWN:
			mouse_x, mouse_y = pygame.mouse.get_pos()
			check_play_button(ai_settings, screen, stats, sb, play_button,
				ship, aliens, bullets, alien_bullets, mouse_x, mouse_y)

def check_play_button(ai_settings, screen, stats, sb, play_button, ship, 
		aliens, bullets, alien_bullets, mouse_x, mouse_y):
	"""Start a new game when the player clicks Play."""
	button_clicked =  play_button.rect.collidepoint(mouse_x, mouse_y)
	if button_clicked or start_game(ai_settings, screen, stats, sb, ship, aliens, bullets, alien_bullets) and not stats.game_active:
		# Reset the game setting
		ai_settings.initialize_dynamic_settings()
		
		# Hide the mouse cursor.
		pygame.mouse.set_visible(False)
			
		# Reset the game statistics.
		stats.reset_stats()
		stats.game_active = True
		
		# Reset the scoreboard images.
		sb.prep_score()
		sb.prep_high_score()
		sb.prep_level()
		sb.prep_ships()
		
		# Empty the list of aliens and bullets.
		aliens.empty()
		bullets.empty()
		
		# Create a new fleet and center the ship.
		create_fleet(ai_settings, screen, ship, aliens)
		ship.center_ship()
				
def check_keydown_events(event, ai_settings, screen, stats, sb, ship, aliens, bullets, alien_bullets):
	"""Respond to keypresses"""
	if event.key == pygame.K_RIGHT:
		ship.moving_right = True
	elif event.key == pygame.K_LEFT:
		ship.moving_left = True
	elif event.key == pygame.K_SPACE:
		fire_bullet(ai_settings, screen, ship, bullets)
	elif event.key == pygame.K_q:
		with open(high_score_file, 'w') as f_obj:
			json.dump(stats.high_score, f_obj)
			sys.exit()
	elif event.key == pygame.K_p and not stats.game_active:
		start_game(ai_settings, screen, stats, sb, ship, 
		aliens, bullets, alien_bullets)
				
def check_keyup_events(event, ship):
	"""Respond to key releases."""
	if event.key == pygame.K_RIGHT:
		ship.moving_right = False
	elif event.key == pygame.K_LEFT:
		ship.moving_left = False

def update_screen(ai_settings, screen, stats, sb, ship, aliens, bullets,
		alien_bullets, play_button):
	"""Update the images on the screen and flip to the new screen."""
	# Redraw the screen during each pass through the loop.
	screen.fill(ai_settings.bg_color)
	# Redraw all bullets behind ship and aliens.
	for bullet in bullets.sprites():
		bullet.draw_bullet()
	for alien_bullet in alien_bullets.sprites():
		alien_bullet.draw_bullet()
	ship.blitme()
	aliens.draw(screen)
	
	# Draw the score information.
	sb.show_score()
	
	# Draw the play button if the game is inactive	
	if not stats.game_active:
		play_button.draw_button()
		
	# Make the most recently drawn screen visible.
	pygame.display.flip()
		
def fire_bullet(ai_settings, screen, ship, bullets):
	"""Fire a bullet if limit not reached yet."""
	# Create a new bullet and add it to the bullets group
	if len(bullets) < ai_settings.bullets_allowed:
		ship.play_sound()
		new_bullet = Bullet(ai_settings, screen, ship)
		bullets.add(new_bullet)

def alien_fire(ai_settings, screen, alien, alien_bullets):
	new_bullet = AlienBullet(ai_settings, screen, alien)
	alien_bullets.add(new_bullet)
	
def update_alien_bullets(ai_settings, alien_bullets):
	alien_bullets.update()
	for alien_bullet in alien_bullets.copy():
		if alien_bullet.rect.top > ai_settings.screen_height:
			alien_bullets.remove(alien_bullet)
	print(len(alien_bullets))
	
def update_bullets(ai_settings, screen, stats, sb, ship, alien, aliens, bullets, alien_bullets):
	"""Update the position of bullets and get rid of od bullets."""
	# Uodate bullet positions.
	bullets.update()
		
	# Get rid of the bullets that have disappeared.
	for bullet in bullets.copy():
		if bullet.rect.bottom <= 0:
			bullets.remove(bullet)
			
	
	check_bullet_alien_collisions(ai_settings, screen, stats, sb, ship, alien, aliens, bullets, alien_bullets)
	
def check_bullet_alien_collisions(ai_settings, screen, stats, sb, ship, alien, aliens, bullets, alien_bullets):
	"""Respond to bullet-alien collisions"""
	# Remove any bullets and aliens that have collided.
	alien = Alien(ai_settings, screen)
	collisions = pygame.sprite.groupcollide(bullets, aliens, True, True)
	if collisions:
		
		alien.play_explosion()
		
		for alien in collisions.values():
			stats.score += ai_settings.alien_points * len(aliens)
			sb.prep_score()
		check_high_score(stats, sb)
	if len(aliens) == 0:
		# If the entire fleet is destroyed, start a new level.
		bullets.empty()
		alien_bullets.empty()
		ai_settings.increase_speed()
		
		# Increase level.
		stats.level += 1
		sb.prep_level()
		
		create_fleet(ai_settings, screen, ship, aliens)
		next_level = pygame.mixer.Sound('sounds/next_level.wav')
		next_level.play()
		sleep(1.0)
			
def get_number_aliens_x(ai_settings, alien_width):
	"""Determine the number of aliens that fit in a row."""		
	available_space_x = ai_settings.screen_width - 2 * alien_width
	number_aliens_x = int(available_space_x / (2 * alien_width))
	return number_aliens_x
	
def get_number_rows(ai_settings, ship_height, alien_height):
	"""Determine the number of rows of aliens that fit on the screen."""
	available_space_y = (ai_settings.screen_height - 
							(3 * alien_height) - ship_height)
	number_rows = int(available_space_y / (2 * alien_height))
	return number_rows
	
def create_alien(ai_settings, screen, aliens, alien_number, row_number):
	"""Create an alien and place it in the row."""	
	alien = Alien(ai_settings, screen)
	alien_width = alien.rect.width
	alien.x = alien_width + 2 * alien_width * alien_number
	alien.rect.x = alien.x
	alien.rect.y = alien.rect.height + 2 * alien.rect.height * row_number
	aliens.add(alien)

def create_fleet(ai_settings, screen, ship, aliens):
	"""Create a full fleet of aliens."""
	# Create an alien and find the number of aliens in a row.
	# Spacing between each alien is equal to one alien width.
	alien = Alien(ai_settings, screen)
	number_aliens_x = get_number_aliens_x(ai_settings, alien.rect.width)
	number_rows = get_number_rows(ai_settings, ship.rect.height, 
		alien.rect.height)
	
	
	# Create the fleet of aliens.
	for row_number in range(number_rows):
		for alien_number in range(number_aliens_x):
			create_alien(ai_settings, screen, aliens, alien_number, row_number)
			
def update_aliens(ai_settings, screen, stats, sb, ship, aliens, bullets, alien, alien_bullets):
	"""
	Check if the fleet is at an edge, 
		and the update the positions of all aliens in the fleet.
	"""
	check_fleet_edges(ai_settings, aliens, screen, alien, alien_bullets)
	aliens.update()			
	
	# Look for alien-ship collisions.
	if pygame.sprite.spritecollideany(ship, aliens):
		ship_hit(ai_settings, screen, stats, sb, ship, aliens, bullets, alien_bullets)
	if pygame.sprite.spritecollideany(ship, alien_bullets):
		ship_hit(ai_settings, screen, stats, sb, ship, aliens, bullets, alien_bullets)
		
	# Look for aliens hitting the bottom of the screen.
	check_aliens_bottom(ai_settings, screen, stats, sb, ship, aliens, bullets, alien_bullets)
	
def check_aliens_bottom(ai_settings, screen, stats, sb, ship, aliens, bullets, alien_bullets):
	"""Check if any aliens have reached the bottom of the screen"""
	screen_rect = screen.get_rect()
	for alien in aliens.sprites():
		if alien.rect.bottom >= screen_rect.bottom:
			# Treat this the same as if the hsip got hit.
			ship_hit(ai_settings, screen, stats, sb, ship, aliens, bullets, alien_bullets)
			break
	
def check_fleet_edges(ai_settings, aliens, screen, alien, alien_bullets):
	"""Respond appropriately if any aliens have reached an edge."""	
	for alien in aliens.sprites():
		if alien.check_edges():
			change_fleet_direction(ai_settings, aliens, screen, alien, alien_bullets)
			break
			
def change_fleet_direction(ai_settings, aliens, screen, alien, alien_bullets):
	"""Drop the entire fleet and change the fleet's direction."""
	for alien in aliens.sprites():
		alien.rect.y += ai_settings.fleet_drop_speed
		if len(aliens) < 10:
			alien_fire(ai_settings, screen, alien, alien_bullets)
	ai_settings.fleet_direction *= -1
	

def ship_hit(ai_settings, screen, stats, sb, ship, aliens, bullets, alien_bullets):
	"""Respond to ship being hit by alien."""
	if stats.ships_left > 0:
		
		# Decrement ships_left.
		stats.ships_left -= 1
		
		# Update scoreboard.
		sb.prep_ships()
		
		# Empty the list of aliens and bullets.
		aliens.empty()
		bullets.empty()
		alien_bullets.empty()
	
		# Create a new fleet and center the ship.
		create_fleet(ai_settings, screen, ship, aliens)
		ship.center_ship()
	
		# Pause.
		explosion = pygame.mixer.Sound('sounds/ship_explosion.wav')
		pygame.mixer.music.stop()
		explosion.play()
		sleep(2.5)
		pygame.mixer.music.play(-1)
	
	else:
		stats.game_active = False 
		pygame.mouse.set_visible(True)
		
def start_game(ai_settings, screen, stats, sb, ship, 
		aliens, bullets, alien_bullets):
	# Reset the game setting
		ai_settings.initialize_dynamic_settings()
		
		# Hide the mouse cursor.
		pygame.mouse.set_visible(False)
			
		# Reset the game statistics.
		stats.reset_stats()
		stats.game_active = True
		
		# Reset the scoreboard images.
		sb.prep_score()
		sb.prep_high_score()
		sb.prep_level()
		sb.prep_ships()
		
		# Empty the list of aliens and bullets.
		aliens.empty()
		bullets.empty()
		alien_bullets.empty()
		
		# Create a new fleet and center the ship.
		create_fleet(ai_settings, screen, ship, aliens)
		ship.center_ship()



def check_high_score(stats, sb):
	"""Check to see if there's a new high score."""
	if stats.score > stats.high_score:
		stats.high_score = stats.score
		sb.prep_high_score()	
	
