import pygame
import levelFunctionsClass

class Enemy:
    def __init__(self, x, y, type, direction=1):
        self.gravity = 80.0
        self.jumpVelocity = -15
        self.x = x
        self.y = y
        self.type = type
        self.onGround = False
        if self.type == "small":
            self.speed = 5.0
            self.height = 48
            self.width = self.height
        self.velocityX = self.speed * direction
        self.velocityY = 0

    
    def moveEnemy(self, dt):
        self.velocityY += self.gravity * dt
        self.y += self.velocityY * dt * 60

        foot_y = self.y + self.height
        if levelFunctionsClass.is_solid(self.x + self.width // 2, foot_y):
            self.y = (int(foot_y // 48)) * 48 - self.height  # <-- Fix here
            self.velocityY = 0
            self.onGround = True
        else:
            self.onGround = False

        # Turn around if about to fall
        if self.velocityX > 0 and not levelFunctionsClass.is_way_down(self.x, 1) and self.onGround:
            self.velocityX *= -1
        elif self.velocityX < 0 and not levelFunctionsClass.is_way_down(self.x, -1) and self.onGround:
            self.velocityX *= -1

        # Wall detection and jump
        if self.velocityX < 0:
            ahead_x = self.x - 20
            if (levelFunctionsClass.is_solid(ahead_x, self.y + 1) or levelFunctionsClass.is_solid(ahead_x, self.y + self.height - 1)) and self.onGround:
                self.velocityY = self.jumpVelocity
                self.velocityX = -self.speed
        elif self.velocityX > 0:
            ahead_x = self.x + self.width + 20
            if (levelFunctionsClass.is_solid(ahead_x, self.y + 1) or levelFunctionsClass.is_solid(ahead_x, self.y + self.height - 1)) and self.onGround:
                self.velocityY = self.jumpVelocity
                self.velocityX = self.speed



        self.x += self.velocityX * dt * 60

    def enemyRect(self, cameraX, cameraY):
        enemyRect = pygame.Rect(self.x - cameraX, self.y - cameraY, self.width, self.height)
        return enemyRect