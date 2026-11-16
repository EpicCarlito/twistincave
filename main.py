import pygame
import random
import sys

pygame.init()

ROWS = 14
COLS = 14
CELL_SIZE = 42

WIDTH = COLS * CELL_SIZE
HEIGHT = ROWS * CELL_SIZE

SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Twisting Caves")
# to james looking over this, i made this hella bare bones im sorry

# color stuff
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (235, 235, 235)

CLOCK = pygame.time.Clock()

horizontal = []
vertical = []


def generate():

    global horizontal, vertical

    horizontal = [
        [True for _ in range(COLS)]
        for _ in range(ROWS + 1)
    ] 

    vertical = [
        [True for _ in range(COLS + 1)]
        for _ in range(ROWS)
    ]

    visited = set()
    stack = [(0, 0)]

    visited.add((0, 0))

    while stack:

        r, c = stack[-1]

        neighbors = [
            (r - 1, c, "top"),
            (r + 1, c, "bottom"),
            (r, c - 1, "left"),
            (r, c + 1, "right")
        ]

        random.shuffle(neighbors)

        found = False

        for nr, nc, direction in neighbors:

            if not (0 <= nr < ROWS and 0 <= nc < COLS):
                continue

            if (nr, nc) in visited:
                continue

            if direction == "top":
                horizontal[r][c] = False

            elif direction == "bottom":
                horizontal[r + 1][c] = False

            elif direction == "left":
                vertical[r][c] = False

            elif direction == "right":
                vertical[r][c + 1] = False

            visited.add((nr, nc))
            stack.append((nr, nc))

            found = True
            break

        if not found:
            stack.pop()


def rotate_cell(r, c): # everything here rotates clockwise
    top = horizontal[r][c]
    right = vertical[r][c + 1]
    bottom = horizontal[r + 1][c]
    left = vertical[r][c]

    horizontal[r][c] = left
    vertical[r][c + 1] = top
    horizontal[r + 1][c] = right
    vertical[r][c] = bottom


# movement

player = [0, 0]
goal = [ROWS - 1, COLS - 1]

# referral for later
DIRECTIONS = {
    pygame.K_UP: (-1, 0, "top"),
    pygame.K_DOWN: (1, 0, "bottom"),
    pygame.K_LEFT: (0, -1, "left"),
    pygame.K_RIGHT: (0, 1, "right"),

    pygame.K_w: (-1, 0, "top"),
    pygame.K_s: (1, 0, "bottom"),
    pygame.K_a: (0, -1, "left"),
    pygame.K_d: (0, 1, "right")
}


def can_move(r, c, direction):

    if direction == "top":
        return not horizontal[r][c]

    if direction == "bottom":
        return not horizontal[r + 1][c]

    if direction == "left":
        return not vertical[r][c]

    if direction == "right":
        return not vertical[r][c + 1]

    return False


def move(dr, dc, direction):

    r, c = player

    nr = r + dr
    nc = c + dc

    # this check bound (so it dont go ya yeet)
    if not (0 <= nr < ROWS and 0 <= nc < COLS):
        return

    # sharing wall stuff
    if not can_move(r, c, direction):
        return

    player[0] = nr
    player[1] = nc


def draw():

    SCREEN.fill(WHITE)

    mouse_x, mouse_y = pygame.mouse.get_pos()

    hover_c = mouse_x // CELL_SIZE
    hover_r = mouse_y // CELL_SIZE

    # Hover > draw a grey outline
    if 0 <= hover_r < ROWS and 0 <= hover_c < COLS:

        rect = pygame.Rect(
            hover_c * CELL_SIZE,
            hover_r * CELL_SIZE,
            CELL_SIZE,
            CELL_SIZE
        )

        pygame.draw.rect(SCREEN, GRAY, rect, 3)

    # Draw horizontal walls
    for r in range(ROWS + 1):

        for c in range(COLS):

            if horizontal[r][c]:

                x1 = c * CELL_SIZE
                y = r * CELL_SIZE
                x2 = (c + 1) * CELL_SIZE

                pygame.draw.line(
                    SCREEN, BLACK,
                    (x1, y), (x2, y), 2
                )

    # Draw vertical walls
    for r in range(ROWS):

        for c in range(COLS + 1):

            if vertical[r][c]:

                x = c * CELL_SIZE
                y1 = r * CELL_SIZE
                y2 = (r + 1) * CELL_SIZE

                pygame.draw.line(
                    SCREEN, BLACK,
                    (x, y1), (x, y2), 2
                )

    # Draw goal
    gx, gy = goal[1], goal[0]

    goal_rect = pygame.Rect(
        gx * CELL_SIZE + 13,
        gy * CELL_SIZE + 13,
        CELL_SIZE - 26,
        CELL_SIZE - 26
    )

    pygame.draw.rect(SCREEN, BLACK, goal_rect, 2)

    # Draw player
    px, py = player[1], player[0]

    pygame.draw.circle(
        SCREEN,
        BLACK,
        (
            px * CELL_SIZE + CELL_SIZE // 2,
            py * CELL_SIZE + CELL_SIZE // 2
        ),
        9
    )

    pygame.display.flip()

# main game loop
generate()

running = True
won = False

while running:

    CLOCK.tick(60)

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_r:
                generate()
                player = [0, 0]
                won = False

            elif event.key in DIRECTIONS and not won:

                dr, dc, direction = DIRECTIONS[event.key]

                move(dr, dc, direction)

                if player == goal:
                    won = True

        # rotation
        if event.type == pygame.MOUSEBUTTONDOWN:

            if event.button == 1 and not won:

                mx, my = pygame.mouse.get_pos()

                c = mx // CELL_SIZE
                r = my // CELL_SIZE

                if 0 <= r < ROWS and 0 <= c < COLS:
                    rotate_cell(r, c)

    draw()

    if won:
        pygame.display.set_caption("nice!")

pygame.quit()
sys.exit()
