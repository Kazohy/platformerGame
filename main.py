import pygame
import enemyClass as Enemy

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
PLAYER_ACCEL, PLAYER_FRICTION = 30.0, 50.0
PLAYER_WALK_MAX_SPEED = 10.0
PLAYER_RUN_MAX_SPEED = 13.0
WALK_TO_RUN_TIME = 0.5  # seconds to start running
GRAVITY, JUMP_VELOCITY = 80.0, -25.0
LEFT_MARGIN = 600
RIGHT_MARGIN = screen_width - 600
TOP_MARGIN = 300
BOTTOM_MARGIN = screen_height - 300

# --- Level Loading ---
with open('assets/levels/level1-1.lvl') as f:
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
    tile_x = int((enemy_x + (32 + 1 if direction > 0 else -1)) // TILE_SIZE)
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

# --- Walk-to-run state ---
walk_time = 0.0
last_move_dir = 0  # -1 for left, 1 for right, 0 for idle

# --- Main Game Loop ---
running = True
camera_x, camera_y = 0, 0

testEnemy = Enemy.Enemy(300, 0, "small", direction=1)

while running:
    dt = clock.tick(60) / 1000.0

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

    move_dir = 0
    if keys[pygame.K_RIGHT] and not right_block:
        move_dir = 1
    elif keys[pygame.K_LEFT] and not left_block:
        move_dir = -1

    # Walk-to-run timer logic
    if move_dir != 0:
        if move_dir == last_move_dir:
            walk_time += dt
        else:
            walk_time = 0.0
        last_move_dir = move_dir
    else:
        walk_time = 0.0
        last_move_dir = 0

    # Set max speed based on walk/run
    if walk_time >= WALK_TO_RUN_TIME:
        max_speed = PLAYER_RUN_MAX_SPEED
    else:
        max_speed = PLAYER_WALK_MAX_SPEED

    if keys[pygame.K_UP] and on_ground:
        player_velocity_y = JUMP_VELOCITY
        on_ground = False
    if move_dir == 1:
        player_velocity_x += PLAYER_ACCEL * dt
    elif move_dir == -1:
        player_velocity_x -= PLAYER_ACCEL * dt
    else:
        if player_velocity_x > 0:
            player_velocity_x = max(0, player_velocity_x - PLAYER_FRICTION * dt)
        elif player_velocity_x < 0:
            player_velocity_x = min(0, player_velocity_x + PLAYER_FRICTION * dt)

    player_velocity_x = max(-max_speed, min(max_speed, player_velocity_x))
    player_x += player_velocity_x * dt * 60

    # --- Player Wall Collision ---
    if is_solid(player_x + PLAYER_WIDTH, player_y + 1) or is_solid(player_x + PLAYER_WIDTH, player_y + PLAYER_HEIGHT - 1):
        player_x = (int((player_x + PLAYER_WIDTH) // TILE_SIZE)) * TILE_SIZE - PLAYER_WIDTH
        player_velocity_x = 0
    if is_solid(player_x, player_y + 1) or is_solid(player_x, player_y + PLAYER_HEIGHT - 1):
        player_x = (int(player_x // TILE_SIZE) + 1) * TILE_SIZE
        player_velocity_x = 0

    # --- Player Head Collision (only green blocks) ---
    head_y = player_y
    if get_tile_at(player_x + PLAYER_WIDTH // 2, head_y) == "g" and player_velocity_y < 0:
        player_y = (int(head_y // TILE_SIZE) + 1) * TILE_SIZE
        player_velocity_y = 0

    player_velocity_y += GRAVITY * dt
    player_y += player_velocity_y * dt * 60

    foot_y = player_y + PLAYER_HEIGHT
    if get_tile_at(player_x + PLAYER_WIDTH // 2, foot_y) in ("g", "d"):
        player_y = (int(foot_y // TILE_SIZE)) * TILE_SIZE - PLAYER_HEIGHT
        player_velocity_y = 0
        on_ground = True
    else:
        on_ground = False

    testEnemy.moveEnemy(dt)

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
    enemyRect = testEnemy.enemyRect(camera_x, camera_y)
    pygame.draw.rect(screen, (255, 0, 0), enemyRect)
    pygame.draw.rect(screen, (255, 200, 50), player_rect)

    # --- Collision: Player & Enemy ---
    if player_rect.colliderect(enemyRect):
        player_respawn()

    pygame.display.flip()
