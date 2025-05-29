import pygame



# --- Initialization ---
pygame.init()
info = pygame.display.Info()
screen_width, screen_height = info.current_w, info.current_h
screen = pygame.display.set_mode((screen_width, screen_height), pygame.NOFRAME)
pygame.display.set_caption('Schoolscape')
clock = pygame.time.Clock()

# --- Constants ---
TILE_SIZE = 48
PLAYER_WIDTH, PLAYER_HEIGHT = 48, 96
ENEMY_WIDTH, ENEMY_HEIGHT = 48, 48
PLAYER_ACCEL, PLAYER_FRICTION, PLAYER_MAX_SPEED = 30.0, 50.0, 15.0
GRAVITY, JUMP_VELOCITY = 80.0, -30.0
ENEMY_SPEED, ENEMY_JUMP_VELOCITY, ENEMY_GRAVITY = 5.0, -15.0, 80.0
JUMP_LOOKAHEAD = 20
LEFT_MARGIN = screen_width // 3
RIGHT_MARGIN = screen_width * 2
TOP_MARGIN = int(screen_height * 0.5)
BOTTOM_MARGIN = int(screen_height * 0.75)

# --- Level Loading ---
with open('assets/levels/level1.txt') as f:
    level = f.read().splitlines()

def get_tile_at(x, y):
    tx, ty = int(x // TILE_SIZE), int(y // TILE_SIZE)
    if 0 <= ty < len(level) and 0 <= tx < len(level[0]):
        return level[ty][tx]
    return "."

def is_solid(x, y):
    t = get_tile_at(x, y)
    return t in ("g", "d")

def draw_level(screen, level, camera_x, camera_y):
    grass_color, dirt_color = (16, 143, 50), (100, 70, 50)
    for y, row in enumerate(level):
        for x, tile in enumerate(row):
            if tile in ("g", "d"):
                color = grass_color if tile == "g" else dirt_color
                rect = pygame.Rect(x * TILE_SIZE - camera_x, y * TILE_SIZE - camera_y, TILE_SIZE, TILE_SIZE)
                pygame.draw.rect(screen, color, rect)

def is_way_down(enemy_x, direction):
    tile_x = int((enemy_x + (ENEMY_WIDTH + 1 if direction > 0 else -1)) // TILE_SIZE)
    for tile_y in range(len(level)):
        if is_solid(tile_x * TILE_SIZE, tile_y * TILE_SIZE):
            return True
    return False

def player_respawn():
    global player_x, player_y, player_velocity_x, player_velocity_y, on_ground
    player_x, player_y = 100, 0
    player_velocity_x, player_velocity_y = 0, 0
    on_ground = False

# --- Player and Enemy State ---
player_x, player_y = 100, 0
player_velocity_x, player_velocity_y = 0, 0
on_ground = False

enemy_x, enemy_y = player_x + 300, 0
enemy_velocity_x, enemy_velocity_y = -ENEMY_SPEED, 0
enemy_on_ground = False

# --- Main Game Loop ---
running = True
while running:
    dt = clock.tick(144) / 1000.0

    # --- Event Handling ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            running = False

    # --- Player Respawn ---
    if player_y >= 1200:
        player_respawn()

    # --- Player Input ---
    keys = pygame.key.get_pressed()
    left_block = is_solid(player_x - 1, player_y + 1) or is_solid(player_x - 1, player_y + PLAYER_HEIGHT - 1)
    right_block = is_solid(player_x + PLAYER_WIDTH + 1, player_y + 1) or is_solid(player_x + PLAYER_WIDTH + 1, player_y + PLAYER_HEIGHT - 1)

    if keys[pygame.K_UP] and on_ground:
        player_velocity_y = JUMP_VELOCITY
        on_ground = False
    if keys[pygame.K_RIGHT] and not right_block:
        player_velocity_x += PLAYER_ACCEL * dt
    elif keys[pygame.K_LEFT] and not left_block:
        player_velocity_x -= PLAYER_ACCEL * dt
    else:
        if player_velocity_x > 0:
            player_velocity_x = max(0, player_velocity_x - PLAYER_FRICTION * dt)
        elif player_velocity_x < 0:
            player_velocity_x = min(0, player_velocity_x + PLAYER_FRICTION * dt)

    player_velocity_x = max(-PLAYER_MAX_SPEED, min(PLAYER_MAX_SPEED, player_velocity_x))
    player_x += player_velocity_x * dt * 60

    # --- Player Wall Collision ---
    if is_solid(player_x + PLAYER_WIDTH, player_y + 1) or is_solid(player_x + PLAYER_WIDTH, player_y + PLAYER_HEIGHT - 1):
        player_x = (int((player_x + PLAYER_WIDTH) // TILE_SIZE)) * TILE_SIZE - PLAYER_WIDTH
        player_velocity_x = 0
    if is_solid(player_x, player_y + 1) or is_solid(player_x, player_y + PLAYER_HEIGHT - 1):
        player_x = (int(player_x // TILE_SIZE) + 1) * TILE_SIZE
        player_velocity_x = 0

    player_velocity_y += GRAVITY * dt
    player_y += player_velocity_y * dt * 60

    foot_y = player_y + PLAYER_HEIGHT
    if get_tile_at(player_x + PLAYER_WIDTH // 2, foot_y) in ("g", "d"):
        player_y = (int(foot_y // TILE_SIZE)) * TILE_SIZE - PLAYER_HEIGHT
        player_velocity_y = 0
        on_ground = True
    else:
        on_ground = False

    camera_x = player_x - screen_width // 2 + PLAYER_WIDTH // 2
    camera_y = player_y - screen_height // 2 + PLAYER_HEIGHT // 2

    # --- Enemy AI ---
    enemy_velocity_y += ENEMY_GRAVITY * dt
    enemy_y += enemy_velocity_y * dt * 60

    enemy_foot_y = enemy_y + ENEMY_HEIGHT
    if is_solid(enemy_x + ENEMY_WIDTH // 2, enemy_foot_y):
        enemy_y = (int(enemy_foot_y // TILE_SIZE)) * TILE_SIZE - ENEMY_HEIGHT
        enemy_velocity_y = 0
        enemy_on_ground = True
    else:
        enemy_on_ground = False

    # Turn around if about to fall
    if enemy_velocity_x > 0 and not is_way_down(enemy_x, 1) and enemy_on_ground:
        enemy_velocity_x *= -1
    elif enemy_velocity_x < 0 and not is_way_down(enemy_x, -1) and enemy_on_ground:
        enemy_velocity_x *= -1

    # Wall detection and jump
    if enemy_velocity_x < 0:
        ahead_x = enemy_x - JUMP_LOOKAHEAD
        if (is_solid(ahead_x, enemy_y + 1) or is_solid(ahead_x, enemy_y + ENEMY_HEIGHT - 1)) and enemy_on_ground:
            enemy_velocity_y = ENEMY_JUMP_VELOCITY
            enemy_velocity_x = -ENEMY_SPEED
    elif enemy_velocity_x > 0:
        ahead_x = enemy_x + ENEMY_WIDTH + JUMP_LOOKAHEAD
        if (is_solid(ahead_x, enemy_y + 1) or is_solid(ahead_x, enemy_y + ENEMY_HEIGHT - 1)) and enemy_on_ground:
            enemy_velocity_y = ENEMY_JUMP_VELOCITY
            enemy_velocity_x = ENEMY_SPEED

    enemy_x += enemy_velocity_x * dt * 60

    # --- Drawing Player ---
    if player_x > camera_x + 300:
        player_rect = pygame.Rect(screen_width - screen_width / 2, player_y - camera_y, PLAYER_WIDTH, PLAYER_HEIGHT)
    else:
        player_rect = pygame.Rect(player_x, player_y, PLAYER_WIDTH, PLAYER_HEIGHT)

    # --- Camera logic: update BEFORE drawing and collision ---
    if player_x < camera_x + LEFT_MARGIN:
        camera_x = player_x - LEFT_MARGIN
    elif player_x + PLAYER_WIDTH > camera_x + RIGHT_MARGIN:
        camera_x = player_x + PLAYER_WIDTH - RIGHT_MARGIN
    camera_x = max(0, camera_x)

    if player_y < camera_y + TOP_MARGIN:
        camera_y = player_y - TOP_MARGIN
    elif player_y + PLAYER_HEIGHT > camera_y + BOTTOM_MARGIN:
        camera_y = player_y + PLAYER_HEIGHT - BOTTOM_MARGIN

    # Clamp camera_y so the bottom of the level touches the bottom of the screen
    level_pixel_height = len(level) * TILE_SIZE
    max_camera_y = max(0, level_pixel_height - screen_height)
    camera_y = min(camera_y, max_camera_y)

    # --- Drawing ---
    screen.fill((0, 0, 0))
    draw_level(screen, level, camera_x, camera_y)
    player_rect = pygame.Rect(player_x - camera_x, player_y - camera_y, PLAYER_WIDTH, PLAYER_HEIGHT)
    enemy_rect = pygame.Rect(enemy_x - camera_x, enemy_y - camera_y, ENEMY_WIDTH, ENEMY_HEIGHT)
    pygame.draw.rect(screen, (255, 200, 50), player_rect)
    pygame.draw.rect(screen, (200, 50, 50), enemy_rect)

    # --- Collision: Player & Enemy ---
    if player_rect.colliderect(enemy_rect):
        player_respawn()

    pygame.display.flip()