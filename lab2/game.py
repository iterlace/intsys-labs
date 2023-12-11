import pygame
from lab2.enemies import *
from lab2.maps import map1
from lab2.player import Player


class Game(object):
    def __init__(self):
        self.font = pygame.font.Font(None, 40)
        self.game_over = True
        self.score = 0
        self.font = pygame.font.Font(None, 35)
        self.menu = Menu(("Start", "Exit"), font_color=(255, 255, 255), font_size=60)
        self.player = Player(32, 128, "images/player.png")
        self.horizontal_blocks = pygame.sprite.Group()
        self.vertical_blocks = pygame.sprite.Group()
        self.dots_group = pygame.sprite.Group()
        for i, row in enumerate(map1):
            for j, item in enumerate(row):
                if item == 1:
                    self.horizontal_blocks.add(
                        Block(j * 32 + 8, i * 32 + 8, (0, 0, 0), 16, 16)
                    )
                elif item == 2:
                    self.vertical_blocks.add(
                        Block(j * 32 + 8, i * 32 + 8, (0, 0, 0), 16, 16)
                    )
        self.ghosts = pygame.sprite.Group()
        self.ghosts.add(Ghost(288, 96, 0, 2))
        self.ghosts.add(Ghost(544, 128, 0, 2))
        self.ghosts.add(Ghost(160, 64, 2, 0))
        self.ghosts.add(Ghost(640, 448, 2, 0))
        for i, row in enumerate(map1):
            for j, item in enumerate(row):
                if item != 0:
                    self.dots_group.add(
                        Ellipse(j * 32 + 12, i * 32 + 12, (255, 255, 255), 8, 8)
                    )

    def process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True
            self.menu.event_handler(event)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if self.game_over:
                        if self.menu.state == 0:
                            self.__init__()
                            self.game_over = False
                        elif self.menu.state == 1:
                            return True

                elif event.key == pygame.K_RIGHT:
                    self.player.move_right()

                elif event.key == pygame.K_LEFT:
                    self.player.move_left()

                elif event.key == pygame.K_UP:
                    self.player.move_up()

                elif event.key == pygame.K_DOWN:
                    self.player.move_down()

                elif event.key == pygame.K_ESCAPE:
                    self.game_over = True

            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_RIGHT:
                    self.player.stop_move_right()
                elif event.key == pygame.K_LEFT:
                    self.player.stop_move_left()
                elif event.key == pygame.K_UP:
                    self.player.stop_move_up()
                elif event.key == pygame.K_DOWN:
                    self.player.stop_move_down()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.player.explosion = True

        return False

    def run_logic(self):
        if not self.game_over:
            self.player.update(self.horizontal_blocks, self.vertical_blocks)
            block_hit_list = pygame.sprite.spritecollide(
                self.player, self.dots_group, True
            )
            if len(block_hit_list) > 0:
                self.score += 1
            block_hit_list = pygame.sprite.spritecollide(self.player, self.ghosts, True)
            if len(block_hit_list) > 0:
                self.player.explosion = True
            self.game_over = self.player.game_over or (
                True if self.score == 156 else False
            )
            self.ghosts.update(
                self.horizontal_blocks, self.vertical_blocks, self.player
            )

    def display_frame(self, screen):
        screen.fill((0, 0, 0))
        if self.game_over:
            self.menu.display_frame(screen)
        else:
            self.horizontal_blocks.draw(screen)
            self.vertical_blocks.draw(screen)
            draw_environment(screen)
            self.dots_group.draw(screen)
            self.ghosts.draw(screen)
            screen.blit(self.player.image, self.player.rect)
            text = self.font.render("Score: " + str(self.score), True, (0, 255, 0))
            screen.blit(text, [120, 20])

        pygame.display.flip()

    def display_message(self, screen, message, color=(255, 0, 0)):
        label = self.font.render(message, True, color)
        width = label.get_width()
        height = label.get_height()
        posX = (800 / 2) - (width / 2)
        posY = (576 / 2) - (height / 2)
        screen.blit(label, (posX, posY))


def draw_environment(screen):
    for i, row in enumerate(map1):
        for j, item in enumerate(row):
            if item == 1:
                pygame.draw.line(
                    screen, (0, 0, 255), [j * 32, i * 32], [j * 32 + 32, i * 32], 3
                )
                pygame.draw.line(
                    screen,
                    (0, 0, 255),
                    [j * 32, i * 32 + 32],
                    [j * 32 + 32, i * 32 + 32],
                    3,
                )
            elif item == 2:
                pygame.draw.line(
                    screen, (0, 0, 255), [j * 32, i * 32], [j * 32, i * 32 + 32], 3
                )
                pygame.draw.line(
                    screen,
                    (0, 0, 255),
                    [j * 32 + 32, i * 32],
                    [j * 32 + 32, i * 32 + 32],
                    3,
                )


class Menu(object):
    state = 0

    def __init__(
        self,
        items,
        font_color=(0, 0, 0),
        select_color=(255, 0, 0),
        ttf_font=None,
        font_size=25,
    ):
        self.font_color = font_color
        self.select_color = select_color
        self.items = items
        self.font = pygame.font.Font(ttf_font, font_size)

    def display_frame(self, screen):
        for index, item in enumerate(self.items):
            if self.state == index:
                label = self.font.render(item, True, self.select_color)
            else:
                label = self.font.render(item, True, self.font_color)

            width = label.get_width()
            height = label.get_height()

            posX = (800 / 2) - (width / 2)
            t_h = len(self.items) * height
            posY = (576 / 2) - (t_h / 2) + (index * height)

            screen.blit(label, (posX, posY))

    def event_handler(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                if self.state > 0:
                    self.state -= 1
            elif event.key == pygame.K_DOWN:
                if self.state < len(self.items) - 1:
                    self.state += 1
