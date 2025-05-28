import pygame


pygame.init()
info = pygame.display.Info()
screen_width, screen_height = info.current_w, info.current_h

def show_quit_dialog(screen):
    yesButtonTexture = pygame.image.load('assets/yes.png')
    yesButtonTextureScaled = pygame.transform.scale(yesButtonTexture, (60, 40))
    noButtonTexture = pygame.image.load('assets/no.png')
    noButtonTextureScaled = pygame.transform.scale(noButtonTexture, (60, 40))
    dialog_rect = pygame.Rect(screen.get_width() // 2 - 150, screen.get_height() // 2 - 75, 300, 150)
    font = pygame.font.SysFont(None, 36)
    yes_rect = pygame.Rect(dialog_rect.x + 50, dialog_rect.y + 80, 60, 40)
    no_rect = pygame.Rect(dialog_rect.x + 200, dialog_rect.y + 80, 60, 40)
    font = pygame.font.SysFont(None, 36)
    yes_text_surf = font.render("Yes", True, (255, 255, 255))
    no_text_surf = font.render("No", True, (255, 255, 255))
    yes_text_rect = (yesButtonTextureScaled.get_width()/2, yesButtonTextureScaled.get_height()/2)
    no_text_rect = (no_text_surf.get_rect(center=no_rect.center))
    quitting = True
    while quitting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if yes_rect.collidepoint(event.pos):
                    return True
                if no_rect.collidepoint(event.pos):
                    quitting = False
                    return False
        if quitting:
            screen.blit(yesButtonTextureScaled, yes_rect)
            screen.blit(noButtonTextureScaled, no_rect)
            screen.blit(yes_text_surf, yes_text_rect)
            screen.blit(no_text_surf, no_text_rect)
            pygame.draw.rect(screen, (220, 220, 220), dialog_rect)
            screen.blit(yesButtonTextureScaled, yes_rect)
            screen.blit(noButtonTextureScaled, no_rect)
            screen.blit(font.render("Do you want to quit?", True, (0, 0, 0)), (dialog_rect.x + 20, dialog_rect.y + 20))
            screen.blit(font.render("Yes", True, (255, 255, 255)), (yes_rect.x + 25, yes_rect.y + 5))
            screen.blit(font.render("No", True, (255, 255, 255)), (no_rect.x + 35, no_rect.y + 5))
            pygame.display.flip()


screen = pygame.display.set_mode(
    (screen_width, screen_height),
    pygame.NOFRAME
)
pygame.display.set_caption('Schoolscape')
running = True

buttonTexture = pygame.image.load('assets/quit.png')
buttonTextureScaled = pygame.transform.scale(buttonTexture, (85, 50))
buttonHoverTexture = pygame.image.load('assets/quitHover.png')
buttonHoverTextureScaled = pygame.transform.scale(buttonHoverTexture, (85, 50))
buttonRect = pygame.Rect(screen_width - 120, 20, 85, 50)
font = pygame.font.SysFont(None, 45)
text = font.render('Quit', True, (255, 255, 255))

clicked = False

while running:
    mouse_pos = pygame.mouse.get_pos()
    for event in pygame.event.get():
        if event.type == pygame.QUIT or clicked:
            QuitDialogue = show_quit_dialog(screen)
            if QuitDialogue:
                running = False
            else:
                clicked = False

        if event.type == pygame.MOUSEBUTTONDOWN and buttonRect.collidepoint(mouse_pos):
            clicked = True


    screen.fill((65, 172, 204))
    buttonState = buttonHoverTextureScaled if buttonRect.collidepoint(mouse_pos) else buttonTextureScaled
    screen.blit(buttonState, buttonRect)
    screen.blit(text, (buttonRect.x + 10, buttonRect.y + 10))
    pygame.display.flip()

pygame.quit()