import heapq
from typing import Literal, Tuple

import pygame
from lab2.player import Player
from maps import map1


class Block(pygame.sprite.Sprite):
    def __init__(
        self,
        x: int,
        y: int,
        color: Tuple[int, int, int],
        width: int,
        height: int,
    ):
        super().__init__()
        self.image = pygame.Surface([width, height])
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)


class Ellipse(pygame.sprite.Sprite):
    def __init__(
        self,
        x: int,
        y: int,
        color: Tuple[int, int, int],
        width: int,
        height: int,
    ):
        super().__init__()
        self.image = pygame.Surface([width, height], pygame.SRCALPHA)
        self.image.fill((0, 0, 0, 0))  # Transparent background
        pygame.draw.ellipse(self.image, color, [0, 0, width, height])
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)


class Ghost(pygame.sprite.Sprite):
    def __init__(self, x, y, change_x, change_y):
        pygame.sprite.Sprite.__init__(self)
        self.change_x = change_x
        self.change_y = change_y
        self.image = pygame.image.load("images/ghost.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def choose_direction(
        self,
        player: Player,
        method: Literal["greedy", "astar"],
        horizontal_blocks: pygame.sprite.Group,
        vertical_blocks: pygame.sprite.Group,
    ) -> str:
        if self.rect.top == player.rect.top and self.rect.bottom == player.rect.bottom:
            return "r" if self.rect.left < player.rect.left else "l"
        elif (
            self.rect.left == player.rect.left and self.rect.right == player.rect.right
        ):
            return "d" if self.rect.top < player.rect.top else "u"

        if method == "greedy":
            return self.choose_direction_with_greedy_method(
                player, horizontal_blocks, vertical_blocks
            )
        elif method == "astar":
            return self.choose_direction_with_astar_method(
                player, horizontal_blocks, vertical_blocks
            )
        else:
            raise ValueError("Invalid method")

    @staticmethod
    def heuristic(player, enemy):
        # A simple heuristic based on Manhattan distance
        return abs(player[0] - enemy[0]) + abs(player[1] - enemy[1])

    def choose_direction_with_astar_method(
        self,
        player: Player,
        horizontal_blocks: pygame.sprite.Group,
        vertical_blocks: pygame.sprite.Group,
    ) -> str:
        player_x, player_y = player.rect.x // 32, player.rect.y // 32
        enemy_x, enemy_y = self.rect.x // 32, self.rect.y // 32

        # Define possible moves: up, down, left, right
        moves = [(-1, 0, "l"), (1, 0, "r"), (0, -1, "u"), (0, 1, "d")]
        way_len = abs(player_x - enemy_x) + abs(player_y - enemy_y)

        # Initialize the priority queue (min-heap)
        open_set = []
        heapq.heappush(open_set, (0, (enemy_x, enemy_y), ""))

        while open_set:
            _, current, path = heapq.heappop(open_set)
            if current == (player_x, player_y) or len(path) > way_len // 2:
                return path

            for dx, dy, direction in moves:
                new_x, new_y = current[0] + dx, current[1] + dy
                new_coordinates = (new_x, new_y)
                h = self.heuristic(new_coordinates, (player_x, player_y))
                f = len(path) + h
                heapq.heappush(open_set, (f, new_coordinates, path + direction))

    def choose_direction_with_greedy_method(
        self,
        player: Player,
        horizontal_blocks: pygame.sprite.Group,
        vertical_blocks: pygame.sprite.Group,
    ) -> str:
        player_x, player_y = player.rect.x // 32, player.rect.y // 32
        enemy_x, enemy_y = self.rect.x // 32, self.rect.y // 32

        # Calculate differences in x and y coordinates
        dx = player_x - enemy_x
        dy = player_y - enemy_y

        # Determine primary movement axis based on the greater difference
        primary_axis = "horizontal" if abs(dx) > abs(dy) else "vertical"

        # Initialize direction
        direction = ""

        # Check for collision with a block
        def collides_with_block(test_rect, blocks):
            return any(block.rect.colliderect(test_rect) for block in blocks)

        # Try moving along the primary axis first
        if primary_axis == "horizontal":
            if dx > 0:  # Move right
                test_rect = self.rect.move(32, 0)
                if not collides_with_block(test_rect, horizontal_blocks):
                    direction = "r"
            elif dx < 0:  # Move left
                test_rect = self.rect.move(-32, 0)
                if not collides_with_block(test_rect, horizontal_blocks):
                    direction = "l"
        else:
            if dy > 0:  # Move down
                test_rect = self.rect.move(0, 32)
                if not collides_with_block(test_rect, vertical_blocks):
                    direction = "d"
            elif dy < 0:  # Move up
                test_rect = self.rect.move(0, -32)
                if not collides_with_block(test_rect, vertical_blocks):
                    direction = "u"

        # If primary axis is blocked, try the secondary axis
        if direction == "":
            if primary_axis == "horizontal":
                if dy > 0:  # Move down
                    test_rect = self.rect.move(0, 32)
                    if not collides_with_block(test_rect, vertical_blocks):
                        direction = "d"
                elif dy < 0:  # Move up
                    test_rect = self.rect.move(0, -32)
                    if not collides_with_block(test_rect, vertical_blocks):
                        direction = "u"
            else:
                if dx > 0:  # Move right
                    test_rect = self.rect.move(32, 0)
                    if not collides_with_block(test_rect, horizontal_blocks):
                        direction = "r"
                elif dx < 0:  # Move left
                    test_rect = self.rect.move(-32, 0)
                    if not collides_with_block(test_rect, horizontal_blocks):
                        direction = "l"

        # If still no direction chosen, stay still or implement a random choice
        if direction == "":
            direction = "stay"  # Or use a random choice logic

        return direction

    def update(
        self,
        horizontal_blocks: pygame.sprite.Group,
        vertical_blocks: pygame.sprite.Group,
        player: Player,
    ):
        self.rect.x += self.change_x
        self.rect.y += self.change_y
        if self.rect.right < 0:
            self.rect.left = 800
        elif self.rect.left > 800:
            self.rect.right = 0
        if self.rect.bottom < 0:
            self.rect.top = 576
        elif self.rect.top > 576:
            self.rect.bottom = 0

        if self.rect.topleft in self.get_intersection_position():
            # direction = self.choose_direction(
            #     player, "greedy", horizontal_blocks, vertical_blocks
            # )
            direction = self.choose_direction(
                player, "astar", horizontal_blocks, vertical_blocks
            )
            if direction[0] == "l" and self.change_x == 0:
                self.change_x = -2
                self.change_y = 0
            elif direction[0] == "r" and self.change_x == 0:
                self.change_x = 2
                self.change_y = 0
            elif direction[0] == "u" and self.change_y == 0:
                self.change_x = 0
                self.change_y = -2
            elif direction[0] == "d" and self.change_y == 0:
                self.change_x = 0
                self.change_y = 2

    @staticmethod
    def get_intersection_position():
        items = []
        for i, row in enumerate(map1):
            for j, item in enumerate(row):
                if item == 3:
                    items.append((j * 32, i * 32))

        return items
