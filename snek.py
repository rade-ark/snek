import pygame
import random
import math
from enum import Enum

class Direction(Enum):
    UP    = (0, -1)
    DOWN  = (0, 1)
    LEFT  = (-1, 0)
    RIGHT = (1, 0)

pygame.init()

WINDOW_WIDTH  = 640
WINDOW_HEIGHT = 480
GRID_SIZE     = 20
FPS           = 10

BLACK        = (0,   0,   0)
VOID         = (5,   2,  15)
GRID_LINE    = (20,  10,  40)
HOT_PINK     = (255,  20, 147)
NEON_MAGENTA = (255,   0, 255)
CYAN_GLOW    = (0,  255, 255)
GOLD_GLITCH  = (255, 215,   0)
WHITE        = (255, 255, 255)
DARK_PINK    = (140,  10,  80)
GLITCH_BLUE  = (50,   0, 200)

#window

screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("✦ SNEK ✦")
clock = pygame.time.Clock()

#fonts

font_big   = pygame.font.SysFont("couriernew", 28, bold=True)
font_small = pygame.font.SysFont("couriernew", 14)
font_score = pygame.font.SysFont("couriernew", 18, bold=True)

class Particle:
    def __init__(self, x, y, color):
        self.x = x + random.randint(-5, 5)
        self.y = y + random.randint(-5, 5)
        self.vx = random.uniform(-2.5, 2.5)
        self.vy = random.uniform(-3.5, 0.5)
        self.life = random.randint(12, 28)
        self.max_life = self.life
        self.color = color
        self.size = random.randint(2, 5)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.15
        self.life -= 1

    def draw(self, surface):
        alpha = int(255 * (self.life / self.max_life))
        r, g, b = self.color
        faded = (r, g, b)
        size = max(1, int(self.size * (self.life / self.max_life)))
        pygame.draw.circle(surface, faded, (int(self.x), int(self.y)), size)

particles = []

glitch_timer = 0
glitch_active = False

def spawn_eat_particles(x, y):
    for _ in range(18):
        c = random.choice([HOT_PINK, NEON_MAGENTA, CYAN_GLOW, GOLD_GLITCH, WHITE])
        particles.append(Particle(x + GRID_SIZE // 2, y + GRID_SIZE // 2, c))

def draw_grid():
    for x in range(0, WINDOW_WIDTH, GRID_SIZE):
        pygame.draw.line(screen, GRID_LINE, (x, 0), (x, WINDOW_HEIGHT))
    for y in range(0, WINDOW_HEIGHT, GRID_SIZE):
        pygame.draw.line(screen, GRID_LINE, (0, y), (WINDOW_WIDTH, y))

def draw_snake(snake, tick):
    for i, segment in enumerate(snake):
        t = tick * 0.3 + i * 0.4
        if i == 0:
            color = NEON_MAGENTA
            glow_color = HOT_PINK
        else:
            # gradient from head to tail
            ratio = i / max(1, len(snake) - 1)
            r = int(HOT_PINK[0] * (1 - ratio) + DARK_PINK[0] * ratio)
            g = int(HOT_PINK[1] * (1 - ratio) + DARK_PINK[1] * ratio)
            b = int(HOT_PINK[2] * (1 - ratio) + DARK_PINK[2] * ratio)
            color = (r, g, b)
            glow_color = (min(255, r + 60), g, min(255, b + 60))

        x, y = segment
        rect = pygame.Rect(x + 1, y + 1, GRID_SIZE - 2, GRID_SIZE - 2)

        glow_rect = pygame.Rect(x - 1, y - 1, GRID_SIZE + 2, GRID_SIZE + 2)
        pygame.draw.rect(screen, glow_color, glow_rect, border_radius=4)

        pygame.draw.rect(screen, color, rect, border_radius=3)

        shine_rect = pygame.Rect(x + 3, y + 2, GRID_SIZE - 8, 3)
        pygame.draw.rect(screen, WHITE, shine_rect, border_radius=2)

        if i == 0:
            eye_offset_x = 4 if direction in (Direction.RIGHT, Direction.LEFT) else 3
            eye_offset_y = 4 if direction in (Direction.UP, Direction.DOWN) else 3
            pygame.draw.circle(screen, WHITE, (x + eye_offset_x + 2, y + eye_offset_y + 2), 3)
            pygame.draw.circle(screen, WHITE, (x + GRID_SIZE - eye_offset_x - 3, y + eye_offset_y + 2), 3)
            pygame.draw.circle(screen, BLACK, (x + eye_offset_x + 3, y + eye_offset_y + 3), 1)
            pygame.draw.circle(screen, BLACK, (x + GRID_SIZE - eye_offset_x - 2, y + eye_offset_y + 3), 1)

def draw_food(food, tick):
    x, y = food
    cx = x + GRID_SIZE // 2
    cy = y + GRID_SIZE // 2
    pulse = math.sin(tick * 0.4) * 3

    for r, alpha in [(14, 40), (10, 80), (7, 140)]:
        r_mod = int(r + pulse)
        s = pygame.Surface((r_mod * 2 + 2, r_mod * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*CYAN_GLOW, alpha), (r_mod + 1, r_mod + 1), r_mod)
        screen.blit(s, (cx - r_mod - 1, cy - r_mod - 1))

    points = [
        (cx, cy - int(7 + pulse)),
        (cx + int(6 + pulse * 0.5), cy),
        (cx, cy + int(7 + pulse)),
        (cx - int(6 + pulse * 0.5), cy),
    ]
    pygame.draw.polygon(screen, CYAN_GLOW, points)
    pygame.draw.polygon(screen, WHITE, [(cx, cy - 3), (cx + 3, cy), (cx, cy + 3), (cx - 3, cy)])

def draw_hud(score, tick):

    hud_surf = pygame.Surface((WINDOW_WIDTH, 28), pygame.SRCALPHA)
    hud_surf.fill((20, 0, 40, 200))
    screen.blit(hud_surf, (0, 0))

    # score
    score_text = font_score.render(f" SCORE: {score:04d} ", True, HOT_PINK)
    screen.blit(score_text, (10, 5))

    # tag
    if (tick // 8) % 2 == 0:
        tag = font_small.render("[ SNEK ]", True, CYAN_GLOW)
        screen.blit(tag, (WINDOW_WIDTH - tag.get_width() - 10, 7))

    # bottom bar
    bot_surf = pygame.Surface((WINDOW_WIDTH, 18), pygame.SRCALPHA)
    bot_surf.fill((20, 0, 40, 160))
    screen.blit(bot_surf, (0, WINDOW_HEIGHT - 18))
    tip = font_small.render("↑↓←→ navigate  //  stay alive, darling ♥", True, DARK_PINK)
    screen.blit(tip, (WINDOW_WIDTH // 2 - tip.get_width() // 2, WINDOW_HEIGHT - 15))

def draw_scanlines():
    for y in range(0, WINDOW_HEIGHT, 4):
        s = pygame.Surface((WINDOW_WIDTH, 1), pygame.SRCALPHA)
        s.fill((0, 0, 0, 30))
        screen.blit(s, (0, y))

def draw_glitch(tick):
    if random.random() < 0.03:  # random glitch flash
        glitch_h = random.randint(2, 8)
        glitch_y = random.randint(0, WINDOW_HEIGHT - glitch_h)
        glitch_w = random.randint(40, 200)
        glitch_x = random.randint(0, WINDOW_WIDTH - glitch_w)
        s = pygame.Surface((glitch_w, glitch_h), pygame.SRCALPHA)
        s.fill((*random.choice([HOT_PINK, CYAN_GLOW, NEON_MAGENTA]), 60))
        screen.blit(s, (glitch_x, glitch_y))

def draw_game_over(score, tick):
    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))

    border_color = HOT_PINK if (tick // 6) % 2 == 0 else NEON_MAGENTA
    pygame.draw.rect(screen, border_color, (80, 120, 480, 240), 2, border_radius=8)
    pygame.draw.rect(screen, CYAN_GLOW, (84, 124, 472, 232), 1, border_radius=6)

    title = font_big.render("SYSTEM FAILURE", True, HOT_PINK)
    screen.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 148))

    sub = font_score.render("the serpent met her end", True, NEON_MAGENTA)
    screen.blit(sub, (WINDOW_WIDTH // 2 - sub.get_width() // 2, 192))

    score_disp = font_big.render(f"FINAL SCORE: {score:04d}", True, GOLD_GLITCH)
    screen.blit(score_disp, (WINDOW_WIDTH // 2 - score_disp.get_width() // 2, 230))

    hint = font_small.render("press  [ R ]  to respawn  or  [ Q ]  to exit", True, CYAN_GLOW)
    screen.blit(hint, (WINDOW_WIDTH // 2 - hint.get_width() // 2, 300))

# game state
def reset_game():
    snake = [(WINDOW_WIDTH // 2 // GRID_SIZE * GRID_SIZE,
              WINDOW_HEIGHT // 2 // GRID_SIZE * GRID_SIZE)]
    direction = Direction.RIGHT
    food = spawn_food(snake)
    score = 0
    return snake, direction, food, score

def spawn_food(snake):
    while True:
        pos = (
            random.randint(0, WINDOW_WIDTH  // GRID_SIZE - 1) * GRID_SIZE,
            random.randint(1, WINDOW_HEIGHT // GRID_SIZE - 2) * GRID_SIZE,  # avoid hud rows
        )
        if pos not in snake:
            return pos

snake, direction, food, score = reset_game()
running    = True
game_over  = False
tick       = 0

while running:
    clock.tick(FPS)
    tick += 1

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if game_over:
                if event.key == pygame.K_r:
                    snake, direction, food, score = reset_game()
                    particles.clear()
                    game_over = False
                elif event.key == pygame.K_q:
                    running = False
            else:
                if event.key == pygame.K_UP    and direction != Direction.DOWN:
                    direction = Direction.UP
                elif event.key == pygame.K_DOWN  and direction != Direction.UP:
                    direction = Direction.DOWN
                elif event.key == pygame.K_LEFT  and direction != Direction.RIGHT:
                    direction = Direction.LEFT
                elif event.key == pygame.K_RIGHT and direction != Direction.LEFT:
                    direction = Direction.RIGHT

    if not game_over:
        head_x, head_y = snake[0]
        dx, dy = direction.value
        new_head = (head_x + dx * GRID_SIZE, head_y + dy * GRID_SIZE)

        if new_head == food:
            snake.insert(0, new_head)
            score += 1
            spawn_eat_particles(*food)
            food = spawn_food(snake)
        else:
            snake.insert(0, new_head)
            snake.pop()

        if (new_head[0] < 0 or new_head[0] >= WINDOW_WIDTH or
            new_head[1] < 28 or new_head[1] >= WINDOW_HEIGHT - 18 or
            new_head in snake[1:]):
            spawn_eat_particles(*new_head)
            game_over = True

    particles = [p for p in particles if p.life > 0]
    for p in particles:
        p.update()

    screen.fill(VOID)
    draw_grid()
    draw_glitch(tick)

    for p in particles:
        p.draw(screen)

    draw_food(food, tick)
    draw_snake(snake, tick)
    draw_hud(score, tick)
    draw_scanlines()

    if game_over:
        draw_game_over(score, tick)

    pygame.display.flip()

pygame.quit()
print(f"\n✦ SNEK ✦  |  Final Score: {score} ♥\n")