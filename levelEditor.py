import pygame
import sys
import os
import copy

TILE_SIZE = 48
MIN_TILE_SIZE = 16
MAX_TILE_SIZE = 128
LEVEL_WIDTH = 100
LEVEL_HEIGHT = 30
LEVEL_FILE = 'assets/levels/testLevel.lvl'
SCREEN_WIDTH, SCREEN_HEIGHT = 1200, 800

def resize_level(level, width, height):
    while len(level) < height:
        level.append(['.'] * width)
    while len(level) > height:
        level.pop()
    for row in level:
        while len(row) < width:
            row.append('.')
        while len(row) > width:
            row.pop()
    return level

if os.path.exists(LEVEL_FILE) and os.path.getsize(LEVEL_FILE) > 0:
    with open(LEVEL_FILE) as f:
        level = [list(line.rstrip('\n')) for line in f]
    level = resize_level(level, LEVEL_WIDTH, LEVEL_HEIGHT)
else:
    level = [['.' for _ in range(LEVEL_WIDTH)] for _ in range(LEVEL_HEIGHT)]

ROWS = len(level)
COLS = len(level[0])

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
clock = pygame.time.Clock()

camera_x, camera_y = 0, 0

def save_level():
    with open(LEVEL_FILE, 'w') as f:
        for row in level:
            f.write(''.join(row) + '\n')

def draw_level(tile_size):
    grass_color, dirt_color = (16, 143, 50), (100, 70, 50)
    for y, row in enumerate(level):
        for x, tile in enumerate(row):
            sx = x * tile_size - camera_x
            sy = y * tile_size - camera_y
            rect = pygame.Rect(sx, sy, tile_size, tile_size)
            if tile == 'g':
                pygame.draw.rect(screen, grass_color, rect)
            elif tile == 'd':
                pygame.draw.rect(screen, dirt_color, rect)
            pygame.draw.rect(screen, (40, 40, 40), rect, 1)

running = True
tile_size = TILE_SIZE
mouse_buttons_held = set()
dragging = False

undo_stack = []
redo_stack = []

def push_undo():
    undo_stack.append(copy.deepcopy(level))
    if len(undo_stack) > 100:  # Limit history size
        undo_stack.pop(0)
    redo_stack.clear()

def undo():
    global level, ROWS, COLS
    if undo_stack:
        redo_stack.append(copy.deepcopy(level))
        level = undo_stack.pop()
        ROWS = len(level)
        COLS = len(level[0])

def redo():
    global level, ROWS, COLS
    if redo_stack:
        undo_stack.append(copy.deepcopy(level))
        level = redo_stack.pop()
        ROWS = len(level)
        COLS = len(level[0])

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            save_level()
            running = False
        elif event.type == pygame.VIDEORESIZE:
            SCREEN_WIDTH, SCREEN_HEIGHT = event.w, event.h
            screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
        elif event.type == pygame.KEYDOWN:
            if event.mod & pygame.KMOD_CTRL:
                if event.key == pygame.K_z:
                    undo()
                elif event.key == pygame.K_y:
                    redo()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            push_undo()
            dragging = True
            mouse_buttons_held.add(event.button)
            mx, my = pygame.mouse.get_pos()
            tx = (mx + camera_x) // tile_size
            ty = (my + camera_y) // tile_size
            if 0 <= tx < COLS and 0 <= ty < ROWS:
                if event.button == 1:
                    level[ty][tx] = 'g'
                elif event.button == 3:
                    level[ty][tx] = 'd'
                elif event.button == 2:
                    level[ty][tx] = '.'
                save_level()
        elif event.type == pygame.MOUSEBUTTONUP:
            dragging = False
            if event.button in mouse_buttons_held:
                mouse_buttons_held.remove(event.button)
        elif event.type == pygame.MOUSEMOTION:
            if mouse_buttons_held and dragging:
                mx, my = event.pos
                tx = (mx + camera_x) // tile_size
                ty = (my + camera_y) // tile_size
                if 0 <= tx < COLS and 0 <= ty < ROWS:
                    if 1 in mouse_buttons_held:
                        level[ty][tx] = 'g'
                    elif 3 in mouse_buttons_held:
                        level[ty][tx] = 'd'
                    elif 2 in mouse_buttons_held:
                        level[ty][tx] = '.'
                    save_level()
        elif event.type == pygame.MOUSEWHEEL:
            mx, my = pygame.mouse.get_pos()
            world_x = (mx + camera_x) / tile_size
            world_y = (my + camera_y) / tile_size
            prev_tile_size = tile_size
            if event.y > 0:
                tile_size = min(tile_size + 4, MAX_TILE_SIZE)
            elif event.y < 0:
                tile_size = max(tile_size - 4, MIN_TILE_SIZE)
            camera_x = int(world_x * tile_size - mx)
            camera_y = int(world_y * tile_size - my)

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        camera_x -= 5
    if keys[pygame.K_RIGHT]:
        camera_x += 5
    if keys[pygame.K_UP]:
        camera_y -= 5
    if keys[pygame.K_DOWN]:
        camera_y += 5

    screen.fill((0, 0, 0))
    draw_level(tile_size)
    pygame.display.flip()
    clock.tick(144)

pygame.quit()
sys.exit()