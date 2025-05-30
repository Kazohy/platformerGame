import pygame


with open('assets/levels/testLevel.lvl') as f:
    level = f.read().splitlines()

def get_tile_at(x, y):
    tx, ty = int(x // 48), int(y // 48)
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
                rect = pygame.Rect(x * 48 - camera_x, y * 48 - camera_y, 48, 48)
                pygame.draw.rect(screen, color, rect)

def is_way_down(enemy_x, direction):
    tile_x = int((enemy_x + (32 + 1 if direction > 0 else -1)) // 48)
    for tile_y in range(len(level)):
        if is_solid(tile_x * 48, tile_y * 48):
            return True
    return False