import os

import pygame
import random
import asyncio


async def main():
    pygame.init()

    ROWS = 12
    COLS = 12
    CELL_SIZE = 32
    PADDING = 64

    WIDTH = COLS * CELL_SIZE + (2 * PADDING)
    HEIGHT = ROWS * CELL_SIZE + (2 * PADDING)

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Twisting Caves")

    # Color
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GRAY = (235, 235, 235)

    clock = pygame.time.Clock()

    DIRECTORY = os.path.dirname(os.path.abspath(__file__))
    animationCooldown = 100

    horizontal = []
    vertical = []

    font = pygame.font.Font(None, 26)

    class SpriteSheet:
        def __init__(self, image_path):
            self.sheet = pygame.image.load(
                os.path.join(DIRECTORY, image_path)
            ).convert_alpha()

        def get_image(self, x, y, width, height):
            image = pygame.Surface((width, height), pygame.SRCALPHA)
            image.blit(self.sheet, (0, 0), (x, y, width, height))

            return image

    class Player:
        def __init__(self, row, col):
            self.row = row
            self.col = col
            self.sheet = SpriteSheet("assets/player.png")
            self.image = self.sheet.get_image(0, 0, CELL_SIZE, CELL_SIZE)

        def update(self, nr, nc):
            self.row = nr
            self.col = nc

        def draw(self):
            screen.blit(
                self.image,
                (
                    PADDING + self.col * CELL_SIZE,
                    PADDING + self.row * CELL_SIZE,
                ),
            )

    def generateMaze():
        horizontal = [[True for _ in range(COLS)] for _ in range(ROWS + 1)]
        vertical = [[True for _ in range(COLS + 1)] for _ in range(ROWS)]

        visited = set()  # No repeating!
        stack = [(0, 0)]

        visited.add((0, 0))

        while stack:
            row, col = stack[-1]

            neighbors = [
                (row - 1, col, "top"),
                (row + 1, col, "bottom"),
                (row, col - 1, "left"),
                (row, col + 1, "right"),
            ]

            random.shuffle(neighbors)

            found = False

            for nr, nc, direction in neighbors:
                if not (0 <= nr < ROWS and 0 <= nc < COLS):
                    continue

                if (nr, nc) in visited:
                    continue

                if direction == "top":
                    horizontal[row][col] = False

                elif direction == "bottom":
                    horizontal[row + 1][col] = False

                elif direction == "left":
                    vertical[row][col] = False

                elif direction == "right":
                    vertical[row][col + 1] = False

                visited.add((nr, nc))
                stack.append((nr, nc))

                found = True
                break

            if not found:
                stack.pop()

        return horizontal, vertical

    def rotate_cell(row, col):  # everything here rotates clockwise
        top = horizontal[row][col]
        right = vertical[row][col + 1]
        bottom = horizontal[row + 1][col]
        left = vertical[row][col]

        horizontal[row][col] = left
        vertical[row][col + 1] = top
        horizontal[row + 1][col] = right
        vertical[row][col] = bottom

    player = Player(0, 0)
    goal = [ROWS - 1, COLS - 1]

    # movement dictionary
    DIRECTIONS = {
        pygame.K_UP: (-1, 0, "top"),
        pygame.K_DOWN: (1, 0, "bottom"),
        pygame.K_LEFT: (0, -1, "left"),
        pygame.K_RIGHT: (0, 1, "right"),
        pygame.K_w: (-1, 0, "top"),
        pygame.K_s: (1, 0, "bottom"),
        pygame.K_a: (0, -1, "left"),
        pygame.K_d: (0, 1, "right"),
    }

    def can_move(row, col, direction):
        if direction == "top":
            return not horizontal[row][col]

        if direction == "bottom":
            return not horizontal[row + 1][col]

        if direction == "left":
            return not vertical[row][col]

        if direction == "right":
            return not vertical[row][col + 1]

        return False

    def move(dr, dc, direction):
        row = player.row
        col = player.col

        nr = row + dr
        nc = col + dc

        if not (0 <= nr < ROWS and 0 <= nc < COLS):
            return

        if not can_move(row, col, direction):
            return

        player.update(nr, nc)

    def draw():
        screen.fill(WHITE)

        mouseX, mouseY = pygame.mouse.get_pos()
        hoveredColumn = (mouseX - PADDING) // CELL_SIZE
        hoveredRow = (mouseY - PADDING) // CELL_SIZE

        # Hover > Draw a grey outline
        if 0 <= hoveredRow < ROWS and 0 <= hoveredColumn < COLS:
            rect = pygame.Rect(
                PADDING + hoveredColumn * CELL_SIZE,
                PADDING + hoveredRow * CELL_SIZE,
                CELL_SIZE,
                CELL_SIZE,
            )

            pygame.draw.rect(screen, GRAY, rect, 3)

        # Draw horizontal walls
        for r in range(ROWS + 1):
            for c in range(COLS):
                if horizontal[r][c]:
                    x1 = PADDING + c * CELL_SIZE
                    y = PADDING + r * CELL_SIZE
                    x2 = PADDING + (c + 1) * CELL_SIZE

                    pygame.draw.line(screen, BLACK, (x1, y), (x2, y), 2)

        # Draw vertical walls
        for r in range(ROWS):
            for c in range(COLS + 1):
                if vertical[r][c]:
                    x = PADDING + c * CELL_SIZE
                    y1 = PADDING + r * CELL_SIZE
                    y2 = PADDING + (r + 1) * CELL_SIZE

                    pygame.draw.line(screen, BLACK, (x, y1), (x, y2), 2)

        # Draw goal
        gx, gy = goal[1], goal[0]
        goalRect = pygame.Rect(
            PADDING + gx * CELL_SIZE + 13,
            PADDING + gy * CELL_SIZE + 13,
            CELL_SIZE - 26,
            CELL_SIZE - 26,
        )
        pygame.draw.rect(screen, BLACK, goalRect, 2)

        # Draw player
        player.draw()

        restartText = font.render("Press R to restart", True, BLACK)
        screen.blit(restartText, (10, 10))

        pygame.display.flip()

    # Inital Maze Generation
    horizontal, vertical = generateMaze()

    running = True
    isCompleted = False

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    horizontal, vertical = generateMaze()
                    player.update(0, 0)
                    isCompleted = False

                elif event.key in DIRECTIONS and not isCompleted:
                    dr, dc, direction = DIRECTIONS[event.key]
                    move(dr, dc, direction)

                    if player.row == goal[0] and player.col == goal[1]:
                        isCompleted = True

            # Rotation
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and not isCompleted:
                    mouseX, mouseY = pygame.mouse.get_pos()

                    col = (mouseX - PADDING) // CELL_SIZE
                    row = (mouseY - PADDING) // CELL_SIZE

                    if 0 <= row < ROWS and 0 <= col < COLS:
                        rotate_cell(row, col)
        draw()
        clock.tick(60)


asyncio.run(main())
