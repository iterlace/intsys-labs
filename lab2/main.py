import pygame
from lab2.game import Game


def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 576))
    pygame.display.set_caption("Pacman")
    done = False
    clock = pygame.time.Clock()
    game = Game()
    while not done:
        done = game.process_events()
        game.run_logic()
        game.display_frame(screen)
        clock.tick(30)
    pygame.quit()


if __name__ == "__main__":
    main()
