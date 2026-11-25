import os
import pygame
import random
import asyncio
from collections import deque


async def main():
    pygame.init()

    ROWS = 20
    COLS = 20
    CELL_SIZE = 32
    PADDING = 64

    WIDTH = COLS * CELL_SIZE + (2 * PADDING)
    HEIGHT = ROWS * CELL_SIZE + (2 * PADDING)

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Twisting Caves")

    # Color
    BACKGROUND = (31, 28, 43)
    BOARD_BACKGROUND = (29, 25, 36)
    HOVER_COLOR = (105, 100, 145)
    WALL_COLOR = (160, 151, 177)
    WHITE = (255, 255, 255)
    GOAL_COLOR = (245, 194, 91)

    clock = pygame.time.Clock()

    DIRECTORY = os.path.dirname(os.path.abspath(__file__))
    animationCooldown = 50

    horizontal = []
    vertical = []

    VISION_RADIUS = 2
    TOTAL_TILES = 10

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

            self.facingRight = True

            self.sheet = SpriteSheet("assets/player.png")

            self.frames = [
                self.sheet.get_image(0, 0, CELL_SIZE, CELL_SIZE),
                self.sheet.get_image(32, 0, CELL_SIZE, CELL_SIZE),
                self.sheet.get_image(64, 0, CELL_SIZE, CELL_SIZE),
                self.sheet.get_image(96, 0, CELL_SIZE, CELL_SIZE),
            ]

            self.image = self.frames[0]
            self.frameIndex = 0
            self.isAnimating = False
            self.lastFrameTime = 0

        def update(self, nr, nc):
            if nc > self.col:
                self.facingRight = True
            elif nc < self.col:
                self.facingRight = False

            self.row = nr
            self.col = nc

            self.frameIndex = 0
            self.image = self.frames[0]
            self.isAnimating = True
            self.lastFrameTime = pygame.time.get_ticks()

        def animate(self):
            if not self.isAnimating:
                return

            currentTime = pygame.time.get_ticks()

            if currentTime - self.lastFrameTime >= animationCooldown:
                self.lastFrameTime = currentTime
                self.frameIndex += 1

                if self.frameIndex >= len(self.frames):
                    self.frameIndex = 0
                    self.isAnimating = False

            self.image = self.frames[self.frameIndex]

        def draw(self):
            self.animate()

            image = self.image

            if not self.facingRight:
                image = pygame.transform.flip(image, True, False)

            screen.blit(
                image,
                (
                    PADDING + self.col * CELL_SIZE,
                    PADDING + self.row * CELL_SIZE,
                ),
            )

        def reset(self):
            self.row = 0
            self.col = 0

            self.facingRight = True

            self.frameIndex = 0
            self.image = self.frames[0]
            self.isAnimating = False

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

    # Rotation
    def rotate_cell(row, col):  # everything here rotates clockwise
        top = horizontal[row][col]
        right = vertical[row][col + 1]
        bottom = horizontal[row + 1][col]
        left = vertical[row][col]

        horizontal[row][col] = left
        vertical[row][col + 1] = top
        horizontal[row + 1][col] = right
        vertical[row][col] = bottom

    # Generate Adjustable Tiles
    def generateAdjustableTiles():
        possibleTiles = [
            (row, col) for row in range(1, ROWS - 1) for col in range(1, COLS - 1)
        ]

        return random.sample(possibleTiles, TOTAL_TILES)

    # Generate complete puzzle
    def generatePuzzle():
        baseHorizontal, baseVertical = generateMaze()

        tiles = generateAdjustableTiles()

        return baseHorizontal, baseVertical, tiles

    # Inital Maze Generation
    player = Player(0, 0)
    goal = random.choice([(0, COLS - 1), (ROWS - 1, 0), (ROWS - 1, COLS - 1)])

    horizontal, vertical, adjustableTiles = generatePuzzle()
    
    originalHorizontal = [row.copy() for row in horizontal]
    originalVertical = [row.copy() for row in vertical]
    originalAdjustableTiles = adjustableTiles.copy()

    visibleCells = set()

    # Fog
    def updateFog():
        visibleCells.clear()

        for row in range(ROWS):
            for col in range(COLS):
                distance = abs(player.row - row) + abs(player.col - col)

                if distance <= VISION_RADIUS:

                    visibleCells.add((row, col))

    def move(dr, dc):
        global isCompleted

        row = player.row
        col = player.col

        nr = row + dr
        nc = col + dc

        if not (0 <= nr < ROWS and 0 <= nc < COLS):
            return

        if dr == -1 and horizontal[row][col]:
            return

        if dr == 1 and horizontal[row + 1][col]:
            return

        if dc == -1 and vertical[row][col]:
            return

        if dc == 1 and vertical[row][col + 1]:
            return

        player.update(nr, nc)

        updateFog()

        if (nr, nc) == goal:
            isCompleted = True

    def draw():
        screen.fill(BACKGROUND)

        boardRect = pygame.Rect(
            PADDING,
            PADDING,
            COLS * CELL_SIZE,
            ROWS * CELL_SIZE,
        )
        pygame.draw.rect(screen, BOARD_BACKGROUND, boardRect, border_radius=8)

        assets = SpriteSheet("assets/assets.png")

        mouseX, mouseY = pygame.mouse.get_pos()
        hoveredColumn = (mouseX - PADDING) // CELL_SIZE
        hoveredRow = (mouseY - PADDING) // CELL_SIZE

        # Draw hover outline
        mouseX, mouseY = pygame.mouse.get_pos()

        hoveredColumn = (mouseX - PADDING) // CELL_SIZE
        hoveredRow = (mouseY - PADDING) // CELL_SIZE

        if (
            0 <= hoveredRow < ROWS
            and 0 <= hoveredColumn < COLS
            and (hoveredRow, hoveredColumn) in visibleCells
        ):
            rect = pygame.Rect(
                PADDING + hoveredColumn * CELL_SIZE + 1,
                PADDING + hoveredRow * CELL_SIZE + 1,
                CELL_SIZE - 2,
                CELL_SIZE - 2,
            )

            pygame.draw.rect(screen, HOVER_COLOR, rect, 2, border_radius=4)

        # Draw horizontal walls
        for row in range(ROWS + 1):

            for col in range(COLS):

                if not horizontal[row][col]:
                    continue

                cells = []

                if row > 0:
                    cells.append((row - 1, col))

                if row < ROWS:
                    cells.append((row, col))

                visible = any(cell in visibleCells for cell in cells)

                if not visible:
                    continue

                x1 = PADDING + col * CELL_SIZE
                y = PADDING + row * CELL_SIZE
                x2 = PADDING + (col + 1) * CELL_SIZE

                pygame.draw.line(screen, WALL_COLOR, (x1, y), (x2, y), 2)

        # Draw vertical walls
        for row in range(ROWS):
            for col in range(COLS + 1):

                if not vertical[row][col]:
                    continue

                cells = []

                if col > 0:
                    cells.append((row, col - 1))

                if col < COLS:
                    cells.append((row, col))

                visible = any(cell in visibleCells for cell in cells)

                if not visible:
                    continue

                x = PADDING + col * CELL_SIZE
                y1 = PADDING + row * CELL_SIZE
                y2 = PADDING + (row + 1) * CELL_SIZE

                pygame.draw.line(screen, WALL_COLOR, (x, y1), (x, y2), 2)

        # Draw Adjustable Tiles
        for row, col in adjustableTiles:
            if (row, col) not in visibleCells:
                continue

            image = assets.get_image(32, 0, CELL_SIZE - 2, CELL_SIZE - 2)

            screen.blit(
                image,
                (
                    PADDING + col * CELL_SIZE + 2,
                    PADDING + row * CELL_SIZE + 2,
                ),
            )

        # Draw goal
        if tuple(goal) in visibleCells:
            gx, gy = goal[1], goal[0]
            
            image = assets.get_image(96, 0, CELL_SIZE - 2, CELL_SIZE - 2)

            screen.blit(
                image,
                (
                    PADDING + gx * CELL_SIZE + 2,
                    PADDING + gy * CELL_SIZE + 2,
                ),
            )

        # Draw player
        player.draw()

        restartText = font.render("Press R to restart", True, WHITE)
        screen.blit(restartText, (10, 10))

        pygame.display.flip()

    # movement dictionary
    DIRECTIONS = {
        pygame.K_UP: (-1, 0),
        pygame.K_DOWN: (1, 0),
        pygame.K_LEFT: (0, -1),
        pygame.K_RIGHT: (0, 1),
        pygame.K_w: (-1, 0),
        pygame.K_s: (1, 0),
        pygame.K_a: (0, -1),
        pygame.K_d: (0, 1),
    }

    running = True
    isCompleted = False
    updateFog()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    horizontal = [row.copy() for row in originalHorizontal]
                    vertical = [row.copy() for row in originalVertical]

                    adjustableTiles = originalAdjustableTiles.copy()

                    player.reset()
                    isCompleted = False

                    updateFog()

                elif event.key in DIRECTIONS and not isCompleted:
                    dr, dc = DIRECTIONS[event.key]

                    move(dr, dc)

                    if player.row == goal[0] and player.col == goal[1]:
                        isCompleted = True

            # Rotation
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and not isCompleted:
                    mouseX, mouseY = pygame.mouse.get_pos()

                    col = (mouseX - PADDING) // CELL_SIZE
                    row = (mouseY - PADDING) // CELL_SIZE

                    tile = (row, col)

                    if (
                        tile in adjustableTiles
                        and tile in visibleCells
                        and abs(player.row - row) + abs(player.col - col) <= 1
                    ):

                        rotate_cell(row, col)
        draw()
        clock.tick(60)
        await asyncio.sleep(0)
asyncio.run(main())
