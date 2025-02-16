import pygame
import random
import sys
import math

# Initialize Pygame
pygame.init()

# Constants
WINDOW_SIZE = 600
GRID_SIZE = 20
GRID_COUNT = WINDOW_SIZE // GRID_SIZE

# Colors
BLACK = (0, 0, 0)
DARK_GREEN = (0, 100, 0)
GREEN = (0, 255, 0)
LIGHT_GREEN = (144, 238, 144)
RED = (255, 0, 0)
DARK_RED = (139, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
GOLD = (255, 215, 0)

# Initialize the game window
screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
pygame.display.set_caption('Snake Game')
clock = pygame.time.Clock()

# Initialize fonts
title_font = pygame.font.Font(None, 74)
font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 24)

class Snake:
    def __init__(self):
        self.reset()

    def reset(self):
        self.body = [(GRID_COUNT//2, GRID_COUNT//2)]
        self.direction = [1, 0]
        self.grow = False
        self.eyes_offset = [(4, -3), (4, 3)]  # Relative to head position

    def move(self):
        head = self.body[0]
        new_head = (head[0] + self.direction[0], head[1] + self.direction[1])
        
        # Check if snake hits the wall
        if (new_head[0] < 0 or new_head[0] >= GRID_COUNT or 
            new_head[1] < 0 or new_head[1] >= GRID_COUNT):
            return False
        
        # Check if snake hits itself
        if new_head in self.body[1:]:
            return False
            
        self.body.insert(0, new_head)
        if not self.grow:
            self.body.pop()
        else:
            self.grow = False
        return True

    def change_direction(self, new_direction):
        # Prevent 180-degree turns
        if (self.direction[0] + new_direction[0] != 0 or 
            self.direction[1] + new_direction[1] != 0):
            self.direction = new_direction
            # Update eyes offset based on direction
            if new_direction == [1, 0]:  # Right
                self.eyes_offset = [(4, -3), (4, 3)]
            elif new_direction == [-1, 0]:  # Left
                self.eyes_offset = [(-4, -3), (-4, 3)]
            elif new_direction == [0, 1]:  # Down
                self.eyes_offset = [(-3, 4), (3, 4)]
            elif new_direction == [0, -1]:  # Up
                self.eyes_offset = [(-3, -4), (3, -4)]

def draw_snake_segment(screen, pos, is_head=False):
    x, y = pos[0] * GRID_SIZE, pos[1] * GRID_SIZE
    segment_size = GRID_SIZE - 2

    # Draw main body segment with gradient
    pygame.draw.rect(screen, DARK_GREEN, 
                    (x, y, segment_size, segment_size))
    pygame.draw.rect(screen, GREEN,
                    (x + 2, y + 2, segment_size - 4, segment_size - 4))
    
    if is_head:
        # Draw eyes
        eye_radius = 3
        eye_color = WHITE
        eye_pos1 = (x + GRID_SIZE//2 + snake.eyes_offset[0][0], 
                    y + GRID_SIZE//2 + snake.eyes_offset[0][1])
        eye_pos2 = (x + GRID_SIZE//2 + snake.eyes_offset[1][0],
                    y + GRID_SIZE//2 + snake.eyes_offset[1][1])
        
        pygame.draw.circle(screen, eye_color, eye_pos1, eye_radius)
        pygame.draw.circle(screen, eye_color, eye_pos2, eye_radius)

def draw_food(screen, pos):
    x, y = pos[0] * GRID_SIZE, pos[1] * GRID_SIZE
    center_x = x + GRID_SIZE // 2
    center_y = y + GRID_SIZE // 2
    radius = GRID_SIZE // 2 - 2

    # Draw apple body
    pygame.draw.circle(screen, DARK_RED, (center_x, center_y), radius)
    pygame.draw.circle(screen, RED, (center_x - 1, center_y - 1), radius - 2)

    # Draw apple stem
    stem_color = DARK_GREEN
    pygame.draw.rect(screen, stem_color, 
                    (center_x - 1, center_y - radius - 3, 2, 4))

    # Draw apple leaf
    leaf_points = [
        (center_x + 2, center_y - radius - 2),
        (center_x + 6, center_y - radius - 4),
        (center_x + 2, center_y - radius - 6)
    ]
    pygame.draw.polygon(screen, GREEN, leaf_points)

def draw_game_over(screen, score):
    # Create semi-transparent overlay
    overlay = pygame.Surface((WINDOW_SIZE, WINDOW_SIZE))
    overlay.fill(BLACK)
    overlay.set_alpha(128)
    screen.blit(overlay, (0, 0))

    # Game Over text with shadow
    game_over_text = title_font.render('Game Over!', True, GOLD)
    score_text = font.render('Final Score: %d' % score, True, WHITE)
    restart_text = font.render('Press SPACE to restart', True, WHITE)
    high_score_text = small_font.render('Try to beat your high score!', True, GRAY)
    
    # Calculate positions
    center_y = WINDOW_SIZE // 2
    game_over_rect = game_over_text.get_rect(center=(WINDOW_SIZE//2, center_y - 80))
    score_rect = score_text.get_rect(center=(WINDOW_SIZE//2, center_y))
    restart_rect = restart_text.get_rect(center=(WINDOW_SIZE//2, center_y + 60))
    high_score_rect = high_score_text.get_rect(center=(WINDOW_SIZE//2, center_y + 100))
    
    # Draw text with decorative elements
    pygame.draw.rect(screen, DARK_GREEN, 
                    (game_over_rect.left - 20, game_over_rect.top - 20,
                     game_over_rect.width + 40, game_over_rect.height + 40), 2)
    
    screen.blit(game_over_text, game_over_rect)
    screen.blit(score_text, score_rect)
    screen.blit(restart_text, restart_rect)
    screen.blit(high_score_text, high_score_rect)

def draw_score(screen, score):
    score_text = font.render('Score: %d' % score, True, WHITE)
    score_rect = score_text.get_rect(topleft=(10, 10))
    
    # Draw score background
    padding = 5
    bg_rect = score_rect.inflate(padding * 2, padding * 2)
    pygame.draw.rect(screen, DARK_GREEN, bg_rect)
    pygame.draw.rect(screen, GREEN, bg_rect, 2)
    
    screen.blit(score_text, score_rect)

def main():
    global snake  # Make snake global so draw functions can access eye positions
    snake = Snake()
    food = (random.randint(0, GRID_COUNT-1), random.randint(0, GRID_COUNT-1))
    game_over = False
    score = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if game_over:
                    if event.key == pygame.K_SPACE:
                        # Reset the game
                        snake = Snake()
                        food = (random.randint(0, GRID_COUNT-1), random.randint(0, GRID_COUNT-1))
                        game_over = False
                        score = 0
                else:
                    if event.key == pygame.K_UP:
                        snake.change_direction([0, -1])
                    elif event.key == pygame.K_DOWN:
                        snake.change_direction([0, 1])
                    elif event.key == pygame.K_LEFT:
                        snake.change_direction([-1, 0])
                    elif event.key == pygame.K_RIGHT:
                        snake.change_direction([1, 0])

        if not game_over:
            # Move snake
            if not snake.move():
                game_over = True

            # Check if snake ate food
            if snake.body[0] == food:
                snake.grow = True
                score += 1
                # Generate new food position
                while True:
                    food = (random.randint(0, GRID_COUNT-1), 
                           random.randint(0, GRID_COUNT-1))
                    if food not in snake.body:
                        break

        # Draw everything
        screen.fill(BLACK)
        
        # Draw snake
        for i, segment in enumerate(snake.body):
            draw_snake_segment(screen, segment, is_head=(i == 0))
        
        # Draw food
        draw_food(screen, food)

        # Draw score
        draw_score(screen, score)

        # Draw game over screen if game is over
        if game_over:
            draw_game_over(screen, score)

        pygame.display.flip()
        clock.tick(10)  # Control game speed

if __name__ == "__main__":
    main()
