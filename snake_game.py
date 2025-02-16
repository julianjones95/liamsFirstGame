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
GAME_SPEED = 15

# Colors
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
DARK_GREEN = (34, 89, 34)
SNAKE_DARK = (26, 71, 26)
SNAKE_LIGHT = (46, 99, 46)
SNAKE_PATTERN = (38, 85, 38)
EYE_COLOR = (255, 234, 0)  # Yellow snake eyes
PUPIL_COLOR = (0, 0, 0)    # Black pupils
TONGUE_COLOR = (255, 92, 92)  # Red tongue
SOIL_BROWN = (139, 69, 19)
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
title_font = pygame.font.Font(None, 100)  # Bigger font for title
subtitle_font = pygame.font.Font(None, 36)
game_font = pygame.font.Font(None, 36)
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

class EnemySnake:
    def __init__(self):
        self.reset()

    def reset(self):
        # Start enemy snake in opposite corner from player
        self.body = [(0, 0)]
        self.direction = [1, 0]
        self.speed = 0.5  # Moves every other frame
        self.move_counter = 0

    def move(self, player_head):
        self.move_counter += self.speed
        if self.move_counter < 1:
            return True
        
        self.move_counter = 0
        head = self.body[0]
        
        # Calculate direction to player
        dx = player_head[0] - head[0]
        dy = player_head[1] - head[1]
        
        # Choose horizontal or vertical movement based on larger difference
        if abs(dx) > abs(dy):
            new_direction = [1 if dx > 0 else -1, 0]
        else:
            new_direction = [0, 1 if dy > 0 else -1]
        
        self.direction = new_direction
        new_head = (head[0] + self.direction[0], head[1] + self.direction[1])
        
        # Check if enemy hits the wall
        if (new_head[0] < 0 or new_head[0] >= GRID_COUNT or 
            new_head[1] < 0 or new_head[1] >= GRID_COUNT):
            return False
            
        self.body.insert(0, new_head)
        self.body.pop()
        return True

def draw_snake_segment(screen, pos, snake_obj=None, is_head=False, segment_index=0):
    x = pos[0] * GRID_SIZE
    y = pos[1] * GRID_SIZE
    segment_size = GRID_SIZE - 2
    
    # Create gradient effect for snake body
    gradient_rect = pygame.Surface((segment_size, segment_size))
    for i in range(segment_size):
        progress = i / segment_size
        color = [
            int(SNAKE_DARK[j] + (SNAKE_LIGHT[j] - SNAKE_DARK[j]) * progress)
            for j in range(3)
        ]
        pygame.draw.line(gradient_rect, color, (i, 0), (i, segment_size))
    
    # Add scale pattern every few segments
    if segment_index % 2 == 0:
        scale_height = segment_size // 3
        pygame.draw.ellipse(gradient_rect, SNAKE_PATTERN,
                          (segment_size//4, 0, segment_size//2, scale_height))
    
    # Apply the gradient surface
    screen.blit(gradient_rect, (x + 1, y + 1))
    
    # Draw head details if this is the head
    if is_head and snake_obj:
        # Draw larger, more detailed eyes
        eye_size = 6
        pupil_size = 3
        
        # Calculate eye positions based on direction
        eye_pos1 = (x + GRID_SIZE//2 + snake_obj.eyes_offset[0][0],
                   y + GRID_SIZE//2 + snake_obj.eyes_offset[0][1])
        eye_pos2 = (x + GRID_SIZE//2 + snake_obj.eyes_offset[1][0],
                   y + GRID_SIZE//2 + snake_obj.eyes_offset[1][1])
        
        # Draw eye whites
        pygame.draw.circle(screen, EYE_COLOR, eye_pos1, eye_size)
        pygame.draw.circle(screen, EYE_COLOR, eye_pos2, eye_size)
        
        # Draw pupils (slightly offset based on movement direction)
        pupil_offset_x = snake_obj.direction[0] * 2
        pupil_offset_y = snake_obj.direction[1] * 2
        pygame.draw.circle(screen, PUPIL_COLOR,
                         (eye_pos1[0] + pupil_offset_x, eye_pos1[1] + pupil_offset_y),
                         pupil_size)
        pygame.draw.circle(screen, PUPIL_COLOR,
                         (eye_pos2[0] + pupil_offset_x, eye_pos2[1] + pupil_offset_y),
                         pupil_size)
        
        # Draw flickering tongue
        if pygame.time.get_ticks() % 1000 < 500:  # Tongue flicks every half second
            tongue_start = (x + GRID_SIZE//2 + snake_obj.direction[0] * GRID_SIZE//2,
                          y + GRID_SIZE//2 + snake_obj.direction[1] * GRID_SIZE//2)
            tongue_end1 = (tongue_start[0] + snake_obj.direction[0] * 8 + snake_obj.direction[1] * 4,
                          tongue_start[1] + snake_obj.direction[1] * 8 + snake_obj.direction[0] * 4)
            tongue_end2 = (tongue_start[0] + snake_obj.direction[0] * 8 - snake_obj.direction[1] * 4,
                          tongue_start[1] + snake_obj.direction[1] * 8 - snake_obj.direction[0] * 4)
            
            pygame.draw.line(screen, TONGUE_COLOR, tongue_start, tongue_end1, 2)
            pygame.draw.line(screen, TONGUE_COLOR, tongue_start, tongue_end2, 2)

def draw_enemy_snake(screen, pos):
    x, y = pos[0] * GRID_SIZE, pos[1] * GRID_SIZE
    segment_size = GRID_SIZE - 2

    # Draw enemy snake segment with red color
    pygame.draw.rect(screen, DARK_RED, 
                    (x, y, segment_size, segment_size))
    pygame.draw.rect(screen, RED,
                    (x + 2, y + 2, segment_size - 4, segment_size - 4))

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

def draw_victory(screen, score):
    # Draw background with gradient
    for i in range(WINDOW_SIZE):
        color = (int(255 * (i / WINDOW_SIZE)), 
                255, 
                int(100 * (1 - i / WINDOW_SIZE)))
        pygame.draw.line(screen, color, (0, i), (WINDOW_SIZE, i))
    
    # Draw giant apple
    apple_size = WINDOW_SIZE // 2
    center_x = WINDOW_SIZE // 2
    center_y = WINDOW_SIZE // 2 - 50
    
    # Draw apple body
    pygame.draw.circle(screen, RED, (center_x, center_y), apple_size // 2)
    
    # Draw apple shine
    shine_pos = (center_x - apple_size//6, center_y - apple_size//6)
    shine_size = apple_size // 4
    pygame.draw.circle(screen, (255, 150, 150), shine_pos, shine_size)
    
    # Draw apple stem
    stem_start = (center_x, center_y - apple_size//2)
    stem_end = (center_x + 20, center_y - apple_size//2 - 30)
    pygame.draw.line(screen, DARK_GREEN, stem_start, stem_end, 8)
    
    # Draw apple leaf
    leaf_points = [
        stem_end,
        (stem_end[0] + 20, stem_end[1] - 10),
        (stem_end[0], stem_end[1] - 20)
    ]
    pygame.draw.polygon(screen, GREEN, leaf_points)
    
    # Draw victory text
    title_text = title_font.render('VICTORY!', True, GOLD)
    title_rect = title_text.get_rect(center=(WINDOW_SIZE//2, 50))
    screen.blit(title_text, title_rect)
    
    score_text = font.render('Final Score: {score}', True, WHITE)
    score_rect = score_text.get_rect(center=(WINDOW_SIZE//2, WINDOW_SIZE - 100))
    screen.blit(score_text, score_rect)
    
    restart_text = small_font.render('Press SPACE to play again', True, WHITE)
    restart_rect = restart_text.get_rect(center=(WINDOW_SIZE//2, WINDOW_SIZE - 50))
    screen.blit(restart_text, restart_rect)

def draw_tree(screen, x, y):
    # Draw tree trunk
    trunk_width = random.randint(30, 40)
    trunk_height = random.randint(100, 150)
    
    # Create a gradient effect for the trunk
    for i in range(trunk_width):
        progress = i / trunk_width
        color = [
            int(DARK_BROWN[0] + (LIGHT_BROWN[0] - DARK_BROWN[0]) * progress),
            int(DARK_BROWN[1] + (LIGHT_BROWN[1] - DARK_BROWN[1]) * progress),
            int(DARK_BROWN[2] + (LIGHT_BROWN[2] - DARK_BROWN[2]) * progress)
        ]
        pygame.draw.line(screen, color, 
                        (x + i, y), 
                        (x + i, y - trunk_height))
    
    # Draw tree foliage (multiple circular clusters)
    foliage_radius = random.randint(50, 70)
    center_x = x + trunk_width // 2
    top_y = y - trunk_height
    
    # Draw multiple overlapping circles for fuller foliage
    for _ in range(5):
        offset_x = random.randint(-20, 20)
        offset_y = random.randint(-20, 20)
        pygame.draw.circle(screen, TREE_GREEN,
                         (center_x + offset_x, top_y + offset_y),
                         foliage_radius)

def draw_background(screen):
    # Fill with soil color
    screen.fill(SOIL_BROWN)
    
    # Add more detailed soil texture with varying shades
    for _ in range(2000):  # Increased number of details
        x = random.randint(0, WINDOW_SIZE)
        y = random.randint(0, WINDOW_SIZE)
        size = random.randint(1, 4)  # Varying sizes for texture
        color_offset = random.randint(-20, 20)
        color = (
            max(0, min(255, SOIL_BROWN[0] + color_offset)),
            max(0, min(255, SOIL_BROWN[1] + color_offset)),
            max(0, min(255, SOIL_BROWN[2] + color_offset))
        )
        pygame.draw.circle(screen, color, (x, y), 2)

def draw_how_to_play(screen):
    # Fill with black background
    screen.fill(BLACK)
    
    # Draw title
    title = title_font.render("How to Play", True, GREEN)
    title_rect = title.get_rect(center=(WINDOW_SIZE//2, 80))
    screen.blit(title, title_rect)
    
    # Instructions text
    instructions = [
        "Control your snake with arrow keys",
        "Collect golden food to grow",
        "Avoid hitting the walls",
        "Don't collide with yourself",
        "Watch out for the enemy snake!",
        "Score 10 points to win",
        "",
        "Press ESC to return to title"
    ]
    
    # Draw instructions
    for i, text in enumerate(instructions):
        instruction = game_font.render(text, True, WHITE)
        rect = instruction.get_rect(center=(WINDOW_SIZE//2, 180 + i * 50))
        screen.blit(instruction, rect)

def draw_title_screen(screen, after_game=False):
    # Fill background based on whether we're coming from a game
    if after_game:
        screen.fill(BLACK)
    else:
        screen.fill(SOIL_BROWN)
        # Add soil texture only for initial title screen
        for _ in range(1000):
            x = random.randint(0, WINDOW_SIZE)
            y = random.randint(0, WINDOW_SIZE)
            color_offset = random.randint(-10, 10)
            color = (
                max(0, min(255, SOIL_BROWN[0] + color_offset)),
                max(0, min(255, SOIL_BROWN[1] + color_offset)),
                max(0, min(255, SOIL_BROWN[2] + color_offset))
            )
            pygame.draw.circle(screen, color, (x, y), 2)
    
    # Create animated snake title
    current_time = pygame.time.get_ticks()
    wave_offset = math.sin(current_time / 500) * 10
    
    # Draw "SNAKE" text with wave effect
    title_text = "SNAKE"
    for i, letter in enumerate(title_text):
        letter_surf = title_font.render(letter, True, GREEN)
        letter_rect = letter_surf.get_rect()
        x = WINDOW_SIZE//2 - (len(title_text) * 50)//2 + i * 50
        y = WINDOW_SIZE//3 + math.sin(current_time/500 + i/2) * 10
        screen.blit(letter_surf, (x, y))
    
    # Draw subtitle with pulsing effect
    pulse = (math.sin(current_time / 400) + 1) / 2
    subtitle_color = (int(255 * pulse), 255, int(255 * pulse))
    
    # Draw "Press SPACE to Start" text
    start_text = subtitle_font.render("Press SPACE to Start", True, subtitle_color)
    start_rect = start_text.get_rect(center=(WINDOW_SIZE//2, WINDOW_SIZE * 2//3))
    screen.blit(start_text, start_rect)
    
    # Draw "How to Play (H)" text
    how_to_play_text = subtitle_font.render("How to Play (H)", True, WHITE)
    how_to_play_rect = how_to_play_text.get_rect(center=(WINDOW_SIZE//2, WINDOW_SIZE * 2//3 + 50))
    screen.blit(how_to_play_text, how_to_play_rect)
    
    # Draw decorative snake
    snake_color = GREEN
    snake_points = []
    time_offset = current_time / 1000
    for i in range(20):
        x = WINDOW_SIZE//2 + math.cos(time_offset + i/3) * (100 - i*3)
        y = WINDOW_SIZE * 3//4 + math.sin(time_offset + i/3) * (50 - i*2)
        snake_points.append((int(x), int(y)))
    if len(snake_points) > 1:
        pygame.draw.lines(screen, snake_color, False, snake_points, 5)
    
    # Draw snake eyes
    head_x, head_y = snake_points[0]
    pygame.draw.circle(screen, WHITE, (head_x - 8, head_y - 8), 4)
    pygame.draw.circle(screen, WHITE, (head_x - 8, head_y + 8), 4)

def main():
    snake = Snake()
    enemy_snake = EnemySnake()
    food_pos = (random.randint(0, GRID_COUNT-1), random.randint(0, GRID_COUNT-1))
    score = 0
    game_over = False
    victory = False
    in_title_screen = True
    in_how_to_play = False
    after_game = False
    
    # Create static background surface
    background = pygame.Surface((WINDOW_SIZE, WINDOW_SIZE))
    draw_background(background)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if in_how_to_play:
                    if event.key == pygame.K_ESCAPE:
                        in_how_to_play = False
                        in_title_screen = True
                elif in_title_screen:
                    if event.key == pygame.K_SPACE:
                        in_title_screen = False
                        after_game = False
                        snake.reset()
                        enemy_snake.reset()
                        food_pos = (random.randint(0, GRID_COUNT-1), 
                                  random.randint(0, GRID_COUNT-1))
                        score = 0
                        game_over = False
                        victory = False
                    elif event.key == pygame.K_h:
                        in_title_screen = False
                        in_how_to_play = True
                elif game_over or victory:
                    if event.key == pygame.K_SPACE:
                        in_title_screen = True
                        after_game = True
                        game_over = False
                        victory = False
                else:
                    if event.key == pygame.K_UP and snake.direction != [0, 1]:
                        snake.change_direction([0, -1])
                    elif event.key == pygame.K_DOWN and snake.direction != [0, -1]:
                        snake.change_direction([0, 1])
                    elif event.key == pygame.K_LEFT and snake.direction != [1, 0]:
                        snake.change_direction([-1, 0])
                    elif event.key == pygame.K_RIGHT and snake.direction != [-1, 0]:
                        snake.change_direction([1, 0])
        
        # Clear the screen at the start of each frame
        screen.fill(BLACK)
        
        if in_how_to_play:
            draw_how_to_play(screen)
        elif in_title_screen:
            draw_title_screen(screen, after_game)
        elif not game_over and not victory:
            # Draw the game screen
            screen.blit(background, (0, 0))
            
            # Move snake and check for collisions
            if not snake.move():
                game_over = True
            
            # Move enemy snake
            if not enemy_snake.move(snake.body[0]):
                game_over = True
            
            # Check if enemy caught the player
            if snake.body[0] in enemy_snake.body:
                game_over = True
            
            # Check for food collision
            if snake.body[0] == food_pos:
                snake.grow = True
                score += 1
                
                # Check for victory
                if score >= 10:
                    victory = True
                else:
                    food_pos = (random.randint(0, GRID_COUNT-1), 
                              random.randint(0, GRID_COUNT-1))
                    while (food_pos in snake.body or 
                          food_pos in enemy_snake.body):
                        food_pos = (random.randint(0, GRID_COUNT-1), 
                                  random.randint(0, GRID_COUNT-1))
            
            # Draw everything
            for i, segment in enumerate(snake.body):
                draw_snake_segment(screen, segment, snake, i == 0, i)
            
            for segment in enemy_snake.body:
                draw_enemy_snake(screen, segment)
            
            # Draw food
            pygame.draw.rect(screen, GOLD, 
                           (food_pos[0] * GRID_SIZE, food_pos[1] * GRID_SIZE,
                            GRID_SIZE - 2, GRID_SIZE - 2))
            
            draw_score(screen, score)
        
        if game_over:
            draw_game_over(screen, score)
        elif victory:
            draw_victory(screen, score)
        
        pygame.display.flip()
        clock.tick(GAME_SPEED)

if __name__ == "__main__":
    main()
