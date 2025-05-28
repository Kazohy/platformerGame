import pygame, random

#Draw screen
pygame.init()
info = pygame.display.Info()
screen_width, screen_height = info.current_w, info.current_h
screen = pygame.display.set_mode(
    (screen_width, screen_height),
    pygame.NOFRAME
)
pygame.display.set_caption('Schoolscape')
running = True

# Tile functions and level loading
TILE_SIZE = 80
level = open('assets/levels/level1.txt').read().splitlines()

def player_respawn():
    global player_x, player_y, player_velocity_x, player_velocity_y, on_ground
    player_x = 100
    player_y = 0
    player_velocity_x = 0
    player_velocity_y = 0
    on_ground = False


def is_solid(x, y):
    t = get_tile_at(x, y)
    return t == "g" or t == "d"

def is_way_down_right(enemy_x):
    tile_x = int((enemy_x + ENEMY_WIDTH + 1) // TILE_SIZE)
    for tile_y in range(len(level)):
        if is_solid(tile_x * TILE_SIZE, tile_y * TILE_SIZE):
            return True
    return False

def is_way_down_left(enemy_x):
    tile_x = int((enemy_x - 1) // TILE_SIZE)
    for tile_y in range(len(level)):
        if is_solid(tile_x * TILE_SIZE, tile_y * TILE_SIZE):
            return True
    return False

def draw_level(screen, level, camera_x, camera_y):
    grass_color = (16, 143, 50)
    dirt_color = (100, 70, 50)
    for y, row in enumerate(level):
        for x, tile in enumerate(row):
            if tile == "g":
                rect = pygame.Rect(x * TILE_SIZE - camera_x, y * TILE_SIZE - camera_y, TILE_SIZE, TILE_SIZE)
                pygame.draw.rect(screen, grass_color, rect)
            if tile == "d":
                rect = pygame.Rect(x * TILE_SIZE - camera_x, y * TILE_SIZE - camera_y, TILE_SIZE, TILE_SIZE)
                pygame.draw.rect(screen, dirt_color, rect)

def get_tile_at(x, y):
    tx = int(x // TILE_SIZE)
    ty = int(y // TILE_SIZE)
    if 0 <= ty < len(level) and 0 <= tx < len(level[0]):
        return level[ty][tx]
    return "."


# Player variables
player_x = 100
player_y = 0
player_velocity_x = 0
player_velocity_y = 0
PLAYER_WIDTH = 64
PLAYER_HEIGHT = 128
PLAYER_ACCEL = 30.0
PLAYER_FRICTION = 50.0
PLAYER_MAX_SPEED = 15.0
GRAVITY = 80.0
JUMP_VELOCITY = -30.0
on_ground = False

#Enemy variables
enemy_x = player_x + 300
enemy_y = 0
enemy_velocity_x = -5.0
enemy_velocity_y = 0
ENEMY_WIDTH = 64
ENEMY_HEIGHT = 128
ENEMY_SPEED = 5.0
ENEMY_JUMP_VELOCITY = -25.0
ENEMY_GRAVITY = 80.0
enemy_on_ground = False

#Make clock
clock = pygame.time.Clock()

#Main game loop
while running:
    dt = clock.tick(144) / 1000.0

    #Pygamme events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            if (event.key == pygame.K_SPACE or event.key == pygame.K_UP) and on_ground:
                player_velocity_y = JUMP_VELOCITY
                on_ground = False

    #Player respawning
    if player_y >= 1200:
        player_respawn()


    #Imputs for player
    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP] and on_ground:
        player_velocity_y = JUMP_VELOCITY
        on_ground = False
    if keys[pygame.K_RIGHT] and not right_block:
        player_velocity_x += PLAYER_ACCEL * dt
    elif keys[pygame.K_LEFT] and not left_block:
        player_velocity_x -= PLAYER_ACCEL * dt
    else:
        if player_velocity_x > 0:
            player_velocity_x -= PLAYER_FRICTION * dt
            if player_velocity_x < 0:
                player_velocity_x = 0
        elif player_velocity_x < 0:
            player_velocity_x += PLAYER_FRICTION * dt
            if player_velocity_x > 0:
                player_velocity_x = 0

    # Player wall detection and velocity control
    left_block = (
            is_solid(player_x - 1, player_y + 1) or
            is_solid(player_x - 1, player_y + PLAYER_HEIGHT - 1)
    )
    right_block = (
            is_solid(player_x + PLAYER_WIDTH + 1, player_y + 1) or
            is_solid(player_x + PLAYER_WIDTH + 1, player_y + PLAYER_HEIGHT - 1)
    )
    player_velocity_x = max(-PLAYER_MAX_SPEED, min(PLAYER_MAX_SPEED, player_velocity_x))
    player_x += player_velocity_x * dt * 60
    if is_solid(player_x + PLAYER_WIDTH, player_y + 1) or is_solid(player_x + PLAYER_WIDTH, player_y + PLAYER_HEIGHT - 1):
        player_x = (int((player_x + PLAYER_WIDTH) // TILE_SIZE)) * TILE_SIZE - PLAYER_WIDTH
        player_velocity_x = 0
    if is_solid(player_x, player_y + 1) or is_solid(player_x, player_y + PLAYER_HEIGHT - 1):
        player_x = (int(player_x // TILE_SIZE) + 1) * TILE_SIZE
        player_velocity_x = 0
    player_velocity_y += GRAVITY * dt
    player_y += player_velocity_y * dt * 60
    foot_y = player_y + PLAYER_HEIGHT
    if get_tile_at(player_x + PLAYER_WIDTH // 2, foot_y) == "g" or get_tile_at(player_x + PLAYER_WIDTH // 2, foot_y) == "d":
        player_y = (int(foot_y // TILE_SIZE)) * TILE_SIZE - PLAYER_HEIGHT
        player_velocity_y = 0
        on_ground = True
    else:
        on_ground = False
    foot_x = player_x + PLAYER_WIDTH

    camera_x = player_x - screen_width // 2 + PLAYER_WIDTH // 2
    camera_y = player_y - screen_height // 2 + PLAYER_HEIGHT // 2

    # AI of the enemy
    enemy_velocity_y += ENEMY_GRAVITY * dt
    enemy_y += enemy_velocity_y * dt * 60

    enemy_foot_y = enemy_y + ENEMY_HEIGHT
    if is_solid(enemy_x + ENEMY_WIDTH // 2, enemy_foot_y):
        enemy_y = (int(enemy_foot_y // TILE_SIZE)) * TILE_SIZE - ENEMY_HEIGHT
        enemy_velocity_y = 0
        enemy_on_ground = True
    else:
        enemy_on_ground = False

    if enemy_velocity_x < 0:
        ahead_x = enemy_x - 5
        below_ahead = enemy_y + ENEMY_HEIGHT + 2
    else:
        ahead_x = enemy_x + ENEMY_WIDTH + 5
        below_ahead = enemy_y + ENEMY_HEIGHT + 2

    # If about to fall, turn around
    if enemy_velocity_x > 0 and not is_way_down_right(enemy_x) and enemy_on_ground:
        enemy_velocity_x *= -1
    elif enemy_velocity_x < 0 and not is_way_down_left(enemy_x) and enemy_on_ground:
        enemy_velocity_x *= -1

    # Wall detection: if blocked, jump in movement direction if on ground
    if enemy_velocity_x < 0:
        left_block = is_solid(enemy_x - 1, enemy_y + 1) or is_solid(enemy_x - 1, enemy_y + ENEMY_HEIGHT - 1)
        if left_block and enemy_on_ground:
            enemy_velocity_y = ENEMY_JUMP_VELOCITY
            # Optional: add a small boost to the left for a more dynamic jump
            enemy_velocity_x = -ENEMY_SPEED
    elif enemy_velocity_x > 0:
        right_block = is_solid(enemy_x + ENEMY_WIDTH + 1, enemy_y + 1) or is_solid(enemy_x + ENEMY_WIDTH + 1,
                                                                                   enemy_y + ENEMY_HEIGHT - 1)
        if right_block and enemy_on_ground:
            enemy_velocity_y = ENEMY_JUMP_VELOCITY
            enemy_velocity_x = ENEMY_SPEED

    enemy_x += enemy_velocity_x * dt * 60


    screen.fill((0, 0, 0))
    draw_level(screen, level, camera_x, camera_y)
    player_rect = pygame.Rect(player_x - camera_x, player_y - camera_y, PLAYER_WIDTH, PLAYER_HEIGHT)
    pygame.draw.rect(screen, (255, 200, 50), player_rect)
    enemy_rect = pygame.Rect(enemy_x - camera_x, enemy_y - camera_y, ENEMY_WIDTH, ENEMY_HEIGHT)
    pygame.draw.rect(screen, (200, 50, 50), enemy_rect)
    # Enemy and player collision mechanic
    if (player_rect.colliderect(enemy_rect)):
        player_respawn()
    pygame.display.flip()