import pygame
import sys
import random
import math
import json
import os

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
PADDLE_WIDTH, PADDLE_HEIGHT = 100, 15
BALL_RADIUS = 10
BRICK_WIDTH, BRICK_HEIGHT = 80, 30
BRICK_ROWS, BRICK_COLS = 5, 8
FPS = 60

# Colors
WHITE = (255, 255, 255)
PINK = (255, 105, 180)
LIGHT_PINK = (255, 182, 193)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
PURPLE = (200, 162, 200)
MINT = (170, 240, 209)
BLUE = (173, 216, 230)
LIGHT_BLUE = (100, 149, 237)
DARK_BLUE = (65, 105, 225)
GRAY = (100, 100, 100)
LIGHT_GRAY = (200, 200, 200)
RED = (255, 0, 0)
LIGHT_RED = (255, 100, 100)
DARK_RED = (200, 0, 0)
CRIMSON = (220, 20, 60)
SKY_BLUE = (135, 206, 235)
CLOUD_WHITE = (248, 248, 255)
# Pastel colors for bricks in levels 4 and 5
PASTEL_PINK = (255, 209, 220)
PASTEL_BLUE = (189, 224, 254)
PASTEL_GREEN = (204, 255, 204)
PASTEL_YELLOW = (255, 255, 179)
PASTEL_PURPLE = (221, 204, 255)
PASTEL_ORANGE = (255, 218, 185)
PASTEL_COLORS = [PASTEL_PINK, PASTEL_BLUE, PASTEL_GREEN, PASTEL_YELLOW, PASTEL_PURPLE, PASTEL_ORANGE]
COLORS = [PINK, LIGHT_PINK, YELLOW, PURPLE, MINT, BLUE]

# Screen
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ultimate Brick Breaker")

# Font
FONT = pygame.font.Font(None, 36)
BIG_FONT = pygame.font.Font(None, 72)
COUNTDOWN_FONT = pygame.font.Font(None, 120)  # Large font for countdown

# Clock
clock = pygame.time.Clock()

# Game Data Path
DATA_FILE = "game_data.json"

# Sound System
class SoundManager:
    def __init__(self):
        self.sounds = {}
        self.muted = False
        self.load_sounds()
    
    def load_sounds(self):
        try:
            # Initialize pygame mixer if not already done
            if pygame.mixer.get_init() is None:
                pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            
            self.create_brick_hit_sound()
            self.create_win_sound() 
            self.create_lose_sound()
            self.create_paddle_hit_sound()
            self.create_countdown_sound()
            print("Sounds loaded successfully!")
        except Exception as e:
            print(f"Sound initialization failed: {e}")
            self.sounds = {
                'brick_hit': None,
                'win': None, 
                'lose': None,
                'paddle_hit': None,
                'countdown': None
            }
    
    def create_brick_hit_sound(self):
        """Create a brick hit sound programmatically"""
        try:
            sound = pygame.mixer.Sound(buffer=bytes([128] * 800))
            sound.set_volume(0.3)
            self.sounds['brick_hit'] = sound
        except:
            self.sounds['brick_hit'] = None
    
    def create_win_sound(self):
        """Create a more distinctive victory sound"""
        try:
            import array
            # Generate a proper sound using array
            samples = []
            duration = 1.5  # seconds
            sample_rate = 22050
            num_samples = int(duration * sample_rate)
            
            # Create a rising victory fanfare
            for i in range(num_samples):
                # Multiple frequencies for a fanfare effect
                t = float(i) / sample_rate
                freq1 = 440 + 200 * t  # Rising pitch
                freq2 = 660 + 300 * t  # Higher rising pitch
                
                # Combine waves
                sample = (0.5 * math.sin(2 * math.pi * freq1 * t) + 
                         0.3 * math.sin(2 * math.pi * freq2 * t))
                
                # Apply envelope
                envelope = 1.0 if t < 0.3 else max(0, 1.0 - (t - 0.3) * 2)
                sample *= envelope
                
                # Convert to 16-bit range
                sample_int = int(sample * 32767 * 0.8)
                samples.append(sample_int)
            
            # Convert to byte array for pygame
            sound_array = array.array('h', samples)
            sound = pygame.mixer.Sound(buffer=sound_array)
            sound.set_volume(0.7)
            self.sounds['win'] = sound
            
        except Exception as e:
            print(f"Could not create win sound: {e}")
            self.sounds['win'] = None
    
    def create_lose_sound(self):
        """Create a game over sound programmatically"""
        try:
            # Create a falling tone for game over
            samples = []
            for i in range(2000):
                # Create a falling tone
                sample = int(127 + 100 * math.sin(i * 0.05) * math.exp(-i * 0.002))
                samples.append(max(0, min(255, sample)))
            sound = pygame.mixer.Sound(buffer=bytes(samples))
            sound.set_volume(0.5)
            self.sounds['lose'] = sound
        except:
            self.sounds['lose'] = None
    
    def create_paddle_hit_sound(self):
        """Create a paddle hit sound programmatically"""
        try:
            sound = pygame.mixer.Sound(buffer=bytes([128] * 400))
            sound.set_volume(0.2)
            self.sounds['paddle_hit'] = sound
        except:
            self.sounds['paddle_hit'] = None

    def create_countdown_sound(self):
        """Create a countdown beep sound"""
        try:
            sound = pygame.mixer.Sound(buffer=bytes([128] * 200))
            sound.set_volume(0.4)
            self.sounds['countdown'] = sound
        except:
            self.sounds['countdown'] = None
    
    def play_sound(self, sound_name):
        """Play a sound if it exists and not muted"""
        if not self.muted and sound_name in self.sounds and self.sounds[sound_name]:
            try:
                self.sounds[sound_name].play()
                return True
            except Exception as e:
                print(f"Could not play sound {sound_name}: {e}")
        return False
    
    def toggle_mute(self):
        """Toggle sound on/off"""
        self.muted = not self.muted
        return self.muted

# Initialize sound manager
sound_manager = SoundManager()

# Utility Functions
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {"high_score": 0, "unlocked_levels": 1}
    return {"high_score": 0, "unlocked_levels": 1}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

def draw_text(surface, text, x, y, size=36, color=WHITE, center=False):
    font = pygame.font.Font(None, size)
    txt_surface = font.render(text, True, color)
    if center:
        x -= txt_surface.get_width() // 2
        y -= txt_surface.get_height() // 2
    surface.blit(txt_surface, (x, y))

def draw_heart(surface, x, y, size, filled=True):
    """Draw a filled heart shape"""
    color = RED if filled else DARK_RED
    
    # Smaller, more refined heart using circles and triangle
    radius = size // 3  # Smaller radius for smaller hearts
    # Left circle
    pygame.draw.circle(surface, color, (x - radius//2, y - radius//3), radius)
    # Right circle
    pygame.draw.circle(surface, color, (x + radius//2, y - radius//3), radius)
    # Triangle (pointing down)
    points = [
        (x - radius, y - radius//3),
        (x + radius, y - radius//3),
        (x, y + radius)
    ]
    pygame.draw.polygon(surface, color, points)

def draw_broken_heart(surface, x, y, size):
    """Draw a broken heart with a crack"""
    # Draw the base heart (dark red)
    radius = size // 3
    color = DARK_RED
    
    # Left circle
    pygame.draw.circle(surface, color, (x - radius//2, y - radius//3), radius)
    # Right circle
    pygame.draw.circle(surface, color, (x + radius//2, y - radius//3), radius)
    # Triangle (pointing down)
    points = [
        (x - radius, y - radius//3),
        (x + radius, y - radius//3),
        (x, y + radius)
    ]
    pygame.draw.polygon(surface, color, points)
    
    # Draw crack through the heart
    crack_color = BLACK
    # Vertical crack line
    pygame.draw.line(surface, crack_color, (x, y - radius//2), (x, y + radius//2), 2)
    # Diagonal crack lines
    pygame.draw.line(surface, crack_color, (x - radius//3, y - radius//6), (x + radius//3, y + radius//6), 2)
    pygame.draw.line(surface, crack_color, (x - radius//3, y + radius//6), (x + radius//3, y - radius//6), 2)

# Game Objects
class Paddle:
    def __init__(self, speed=7, color=None, level=0):
        self.width = PADDLE_WIDTH
        self.height = PADDLE_HEIGHT
        self.x = WIDTH // 2 - self.width // 2
        self.y = HEIGHT - 40
        # Make paddle black for levels 4 and 5, otherwise use provided color or random
        self.color = BLACK if level in [3, 4] else (color if color else random.choice(COLORS))
        self.speed = speed

    def move(self, keys):
        if keys[pygame.K_LEFT] and self.x > 0:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] and self.x < WIDTH - self.width:
            self.x += self.speed

    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.height))
        
class Ball:
    def __init__(self, speed, level=0):
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.radius = BALL_RADIUS
        # Make ball black for levels 4 and 5
        self.color = BLACK if level in [3, 4] else random.choice(COLORS)
        self.speed_x = random.choice([-1, 1]) * speed
        self.speed_y = -speed

    def move(self):
        self.x += self.speed_x
        self.y += self.speed_y

        if self.x - self.radius <= 0 or self.x + self.radius >= WIDTH:
            self.speed_x *= -1
        if self.y - self.radius <= 0:
            self.speed_y *= -1

    def draw(self, win):
        pygame.draw.circle(win, self.color, (int(self.x), int(self.y)), self.radius)

class Brick:
    def __init__(self, x, y, level=0, moving=False, move_speed=1.5):
        self.rect = pygame.Rect(x, y, BRICK_WIDTH, BRICK_HEIGHT)
        # Use pastel colors for levels 4 and 5, normal colors for other levels
        if level in [3, 4]:
            self.color = PASTEL_COLORS[(int(y) // (BRICK_HEIGHT + 10) + int(x) // (BRICK_WIDTH + 10)) % len(PASTEL_COLORS)]
        else:
            self.color = COLORS[(int(y) // (BRICK_HEIGHT + 10) + int(x) // (BRICK_WIDTH + 10)) % len(COLORS)]
        self.destroyed = False
        self.moving = moving
        self.direction = 1 if random.random() > 0.5 else -1
        self.speed = random.uniform(0.5, move_speed)

    def update(self):
        if self.moving and not self.destroyed:
            self.rect.x += self.speed * self.direction
            if self.rect.x <= 0 or self.rect.x + BRICK_WIDTH >= WIDTH:
                self.direction *= -1

    def draw(self, win):
        if not self.destroyed:
            pygame.draw.rect(win, self.color, self.rect)
            # Use black border for pastel bricks, white border for colored bricks
            border_color = BLACK if self.color in PASTEL_COLORS else WHITE
            pygame.draw.rect(win, border_color, self.rect, 2)

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.radius = random.randint(2, 5)
        self.color = color
        self.speed_x = random.uniform(-2, 2)
        self.speed_y = random.uniform(-2, 2)
        self.life = 30

    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        self.life -= 1
        self.radius = max(0, self.radius - 0.1)

    def draw(self, win):
        if self.life > 0:
            pygame.draw.circle(win, self.color, (int(self.x), int(self.y)), int(self.radius))

class PartyPopper:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.particles = []
        self.create_burst()
        self.life = 60  # Duration of the effect

    def create_burst(self):
        # Create a burst of colorful particles
        for _ in range(100):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 8)
            color = random.choice([PINK, YELLOW, BLUE, PURPLE, MINT, LIGHT_PINK])
            self.particles.append({
                'x': self.x,
                'y': self.y,
                'speed_x': math.cos(angle) * speed,
                'speed_y': math.sin(angle) * speed,
                'color': color,
                'size': random.randint(3, 8),
                'life': random.randint(30, 60)
            })

    def update(self):
        self.life -= 1
        for p in self.particles:
            p['x'] += p['speed_x']
            p['y'] += p['speed_y']
            p['life'] -= 1
            # Add gravity
            p['speed_y'] += 0.1

    def draw(self, win):
        for p in self.particles:
            if p['life'] > 0:
                pygame.draw.circle(win, p['color'], (int(p['x']), int(p['y'])), p['size'])

    def is_alive(self):
        return self.life > 0

# Background drawing functions
def draw_gray_background(win):
    """Draw gray background for hard level"""
    win.fill(GRAY)
    
def draw_clouds_background(win):
    """Draw clouds on light blue sky for extreme level"""
    # Sky background
    win.fill(SKY_BLUE)
    
    # Draw clouds
    cloud_positions = [
        (100, 100), (300, 150), (500, 80), (700, 120),
        (200, 250), (400, 300), (600, 200)
    ]
    
    for x, y in cloud_positions:
        draw_cloud(win, x, y)
        
def draw_asian_background(win):
    """Draw clouds only for asian level (no castles)"""
    # Sky background
    win.fill(SKY_BLUE)
    
    # Draw clouds
    cloud_positions = [
        (100, 100), (300, 150), (500, 80), (700, 120),
        (200, 250), (400, 300), (600, 200)
    ]
    
    for x, y in cloud_positions:
        draw_cloud(win, x, y)

def draw_cloud(win, x, y):
    """Draw a fluffy cloud"""
    pygame.draw.circle(win, CLOUD_WHITE, (x, y), 30)
    pygame.draw.circle(win, CLOUD_WHITE, (x + 20, y - 10), 25)
    pygame.draw.circle(win, CLOUD_WHITE, (x + 40, y), 30)
    pygame.draw.circle(win, CLOUD_WHITE, (x + 20, y + 10), 25)

# Game Mechanics
def create_bricks(level=0):
    bricks = []
    offset_x = (WIDTH - (BRICK_COLS * (BRICK_WIDTH + 10))) // 2
    offset_y = 60
    
    if level == 3:  # Extreme level - even arrangement but moving bricks
        for row in range(BRICK_ROWS):
            for col in range(BRICK_COLS):
                x = offset_x + col * (BRICK_WIDTH + 10)
                y = offset_y + row * (BRICK_HEIGHT + 10)
                bricks.append(Brick(x, y, level, moving=True, move_speed=1.5))
    elif level == 4:  # Asian level - even arrangement but moving bricks at higher speed
        for row in range(BRICK_ROWS):
            for col in range(BRICK_COLS):
                x = offset_x + col * (BRICK_WIDTH + 10)
                y = offset_y + row * (BRICK_HEIGHT + 10)
                bricks.append(Brick(x, y, level, moving=True, move_speed=2.5))  # Higher speed
    else:  # Normal arrangement for other levels
        for row in range(BRICK_ROWS):
            for col in range(BRICK_COLS):
                x = offset_x + col * (BRICK_WIDTH + 10)
                y = offset_y + row * (BRICK_HEIGHT + 10)
                bricks.append(Brick(x, y, level))
    return bricks

def collision(ball, paddle, bricks, particles):
    # Paddle collision
    if paddle.y < ball.y + ball.radius < paddle.y + paddle.height and paddle.x < ball.x < paddle.x + paddle.width:
        ball.speed_y *= -1
        ball.y = paddle.y - ball.radius
        sound_manager.play_sound('paddle_hit')
        for _ in range(10):
            particles.append(Particle(ball.x, ball.y, ball.color))

    # Brick collision
    brick_hit = False
    for brick in bricks:
        if not brick.destroyed and brick.rect.collidepoint(ball.x, ball.y):
            brick.destroyed = True
            ball.speed_y *= -1
            brick_hit = True
            sound_manager.play_sound('brick_hit')
            for _ in range(15):
                particles.append(Particle(brick.rect.centerx, brick.rect.centery, brick.color))
            return 10
    
    return 0

def show_countdown(paddle, ball, bricks, level=0):
    """Show a 3-2-1 countdown before the game starts"""
    countdown_time = 3  # 3 seconds countdown
    start_time = pygame.time.get_ticks()
    
    while countdown_time > 0:
        current_time = pygame.time.get_ticks()
        elapsed = (current_time - start_time) / 1000  # Convert to seconds
        
        # Update countdown every second
        if elapsed >= 1:
            countdown_time -= 1
            start_time = current_time
            sound_manager.play_sound('countdown')  # Play beep for each count
        
        # Clear screen with appropriate background
        if level == 2:  # Hard level
            draw_gray_background(WIN)
        elif level == 3:  # Extreme level
            draw_clouds_background(WIN)
        elif level == 4:  # Asian level
            draw_asian_background(WIN)
        else:
            WIN.fill(BLACK)
        
        # Draw the game elements (static during countdown)
        # This gives players time to see the level layout
        for brick in bricks:
            brick.draw(WIN)
        paddle.draw(WIN)
        ball.draw(WIN)
        
        # Draw countdown number with pulsing effect
        countdown_text = str(countdown_time) if countdown_time > 0 else "GO!"
        text_size = 120 + int(20 * math.sin(pygame.time.get_ticks() * 0.01))  # Pulsing effect
        text_color = PINK if countdown_time > 0 else MINT
        
        # Create a semi-transparent background for the countdown
        countdown_bg = pygame.Surface((200, 200), pygame.SRCALPHA)
        pygame.draw.circle(countdown_bg, (0, 0, 0, 150), (100, 100), 100)
        WIN.blit(countdown_bg, (WIDTH//2 - 100, HEIGHT//2 - 100))
        
        # Draw the countdown number
        countdown_surface = COUNTDOWN_FONT.render(countdown_text, True, text_color)
        WIN.blit(countdown_surface, (WIDTH//2 - countdown_surface.get_width()//2, 
                                   HEIGHT//2 - countdown_surface.get_height()//2))
        
        # Draw instruction text
        if countdown_time == 3:
            draw_text(WIN, "Get Ready!", WIDTH//2, HEIGHT//2 + 100, 36, YELLOW, True)
        
        pygame.display.flip()
        
        # Handle events during countdown
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return False  # Allow escaping during countdown
        
        clock.tick(FPS)
    
    return True

def show_party_celebration(score, best_score):
    """Show level complete screen with party poppers"""
    # Play win sound
    print("Playing win sound...")  # Debug
    sound_played = sound_manager.play_sound('win')
    print(f"Sound played: {sound_played}")  # Debug
    
    poppers = []
    # Create multiple party poppers at different positions
    for _ in range(8):
        x = random.randint(100, WIDTH - 100)
        y = random.randint(100, HEIGHT - 200)
        poppers.append(PartyPopper(x, y))
    
    celebration_time = 180  # 3 seconds at 60 FPS
    
    while celebration_time > 0:
        WIN.fill(LIGHT_PINK)  # Light pink background
        
        # Update and draw party poppers
        for popper in poppers[:]:
            popper.update()
            popper.draw(WIN)
            if not popper.is_alive():
                poppers.remove(popper)
                # Add new popper to keep the celebration going
                if celebration_time > 60:
                    x = random.randint(100, WIDTH - 100)
                    y = random.randint(100, HEIGHT - 200)
                    poppers.append(PartyPopper(x, y))
        
        # Draw celebration text
        draw_text(WIN, "LEVEL COMPLETE!", WIDTH // 2, HEIGHT // 2 - 100, 72, PURPLE, True)
        draw_text(WIN, f"Your Score: {score}", WIDTH // 2, HEIGHT // 2, 48, PINK, True)
        draw_text(WIN, f"Best Score: {best_score}", WIDTH // 2, HEIGHT // 2 + 70, 42, BLUE, True)
        draw_text(WIN, "Press ENTER to Continue", WIDTH // 2, HEIGHT // 2 + 150, 32, DARK_BLUE, True)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                return
        
        pygame.display.flip()
        clock.tick(FPS)
        celebration_time -= 1

def show_game_over_screen(current_score, best_score):
    """Show game over screen with broken hearts"""
    # Play lose sound
    sound_manager.play_sound('lose')
    
    WIN.fill(BLACK)
    
    # Draw 5 broken hearts
    heart_size = 25  # Smaller hearts
    heart_spacing = 60  # Closer spacing
    start_x = WIDTH // 2 - (heart_spacing * 2)
    
    for i in range(5):
        x = start_x + i * heart_spacing
        y = HEIGHT // 2 - 50
        draw_broken_heart(WIN, x, y, heart_size)
    
    # Draw game over text
    draw_text(WIN, "GAME OVER", WIDTH // 2, HEIGHT // 2 + 50, 72, RED, True)
    draw_text(WIN, f"Your Score: {current_score}", WIDTH // 2, HEIGHT // 2 + 130, 48, LIGHT_PINK, True)
    draw_text(WIN, f"Best Score: {best_score}", WIDTH // 2, HEIGHT // 2 + 190, 42, YELLOW, True)
    draw_text(WIN, "Press ENTER to Continue", WIDTH // 2, HEIGHT // 2 + 260, 32, WHITE, True)
    
    pygame.display.flip()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                waiting = False

def draw_lives(win, lives, max_lives=5):
    """Draw hearts to represent lives - filled hearts for remaining lives, broken hearts for lost lives"""
    heart_size = 20  # Smaller hearts
    spacing = 30  # Closer spacing
    start_x = WIDTH - (max_lives * spacing) - 20
    
    for i in range(max_lives):
        x = start_x + i * spacing
        y = 20  # Moved slightly higher
        
        if i < lives:
            # Draw filled heart for remaining lives
            draw_heart(win, x, y, heart_size, filled=True)
        else:
            # Draw broken heart for lost lives
            draw_broken_heart(win, x, y, heart_size)

# Game loop
def run_game(level=0):
    # Level progression: 0=Easy, 1=Medium, 2=Hard, 3=Extreme, 4=Asian
    levels = [
        {"speed": 3.5, "lives": 5, "paddle_speed": 7},    # Easy
        {"speed": 4.5, "lives": 5, "paddle_speed": 7},    # Medium  
        {"speed": 6, "lives": 5, "paddle_speed": 7},      # Hard
        {"speed": 7, "lives": 5, "paddle_speed": 9},      # Extreme - faster paddle
        {"speed": 8, "lives": 5, "paddle_speed": 11},     # Asian - even faster paddle
    ]

    data = load_data()
    level_data = levels[min(level, len(levels) - 1)]
    
    # Set paddle color - black for levels 4 and 5, crimson for level 2
    paddle_color = CRIMSON if level == 2 else None
    # Pass level to Paddle constructor to determine color
    paddle = Paddle(level_data["paddle_speed"], paddle_color, level)
    
    # Pass level to Ball constructor to determine color
    ball = Ball(level_data["speed"], level)
    bricks = create_bricks(level)
    particles = []
    score = 0
    lives = level_data["lives"]
    running = True

    # Show countdown before starting the game
    if not show_countdown(paddle, ball, bricks, level):
        return  # User pressed ESC during countdown

    while running:
        clock.tick(FPS)
        
        # Draw appropriate background based on level
        if level == 2:  # Hard level - gray background
            draw_gray_background(WIN)
        elif level == 3:  # Extreme level - clouds on blue sky
            draw_clouds_background(WIN)
        elif level == 4:  # Asian level - clouds only (no castles)
            draw_asian_background(WIN)
        else:
            WIN.fill(BLACK)  # Default black for Easy and Medium
            
        keys = pygame.key.get_pressed()
        paddle.move(keys)
        ball.move()

        # Update moving bricks for extreme and asian levels
        if level == 3 or level == 4:
            for brick in bricks:
                brick.update()

        # Collisions
        score += collision(ball, paddle, bricks, particles)

        if ball.y > HEIGHT:
            lives -= 1
            # Deduct 10 points for losing a life
            score = max(0, score - 10)  # Ensure score doesn't go below 0
            if lives > 0:
                # Pass level to Ball constructor for correct color
                ball = Ball(level_data["speed"], level)
                # Reset paddle with the same speed when ball respawns
                paddle = Paddle(level_data["paddle_speed"], paddle_color, level)
            else:
                running = False

        # Draw everything
        paddle.draw(WIN)
        ball.draw(WIN)
        for brick in bricks:
            brick.draw(WIN)
        for p in particles[:]:
            p.update()
            p.draw(WIN)
            if p.life <= 0:
                particles.remove(p)

        draw_text(WIN, f"Score: {score}", 20, 10, 30, WHITE)
        draw_lives(WIN, lives)  # Draw hearts instead of text for lives

        # Level complete
        if all(b.destroyed for b in bricks):
            data["unlocked_levels"] = max(data["unlocked_levels"], level + 2)
            data["high_score"] = max(data["high_score"], score)
            save_data(data)
            show_party_celebration(score, data["high_score"])
            return

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        pygame.display.flip()

    # Game over screen
    data["high_score"] = max(data["high_score"], score)
    save_data(data)
    show_game_over_screen(score, data["high_score"])

# Level Select
def level_select():
    data = load_data()
    unlocked = data["unlocked_levels"]
    
    # Level names and colors - CORRECTED ORDER
    level_info = [
        {"name": "EASY", "color": MINT},
        {"name": "MEDIUM", "color": BLUE},
        {"name": "HARD", "color": YELLOW},
        {"name": "EXTREME", "color": PINK},
        {"name": "ASIAN", "color": PURPLE}
    ]

    # Calculate dimensions for perfect fit
    total_levels = len(level_info)
    button_height = 70
    vertical_spacing = 15
    total_height_needed = total_levels * button_height + (total_levels - 1) * vertical_spacing
    start_y = (HEIGHT - total_height_needed) // 2
    
    if start_y < 100:
        start_y = 100
        if total_height_needed > HEIGHT - 200:
            button_height = (HEIGHT - 200 - (total_levels - 1) * vertical_spacing) // total_levels

    button_width = 300

    while True:
        WIN.fill(BLACK)
        draw_text(WIN, "SELECT LEVEL", WIDTH // 2, 50, 60, WHITE, True)

        level_buttons = []
        for i in range(total_levels):
            button_x = WIDTH // 2 - button_width // 2
            button_y = start_y + i * (button_height + vertical_spacing)
            
            if i < unlocked:
                color = level_info[i]["color"]
                border_color = WHITE
            else:
                color = GRAY
                border_color = LIGHT_GRAY
                
            rect = pygame.Rect(button_x, button_y, button_width, button_height)
            pygame.draw.rect(WIN, color, rect, border_radius=8)
            pygame.draw.rect(WIN, border_color, rect, 3, border_radius=8)
            
            level_text = f"LEVEL {i+1}  -  {level_info[i]['name']}"
            draw_text(WIN, level_text, WIDTH // 2, button_y + button_height // 2, 32, WHITE, True)
            
            level_buttons.append(rect)

        # Draw back button at bottom
        back_rect = pygame.Rect(20, HEIGHT - 60, 120, 40)
        pygame.draw.rect(WIN, DARK_BLUE, back_rect, border_radius=8)
        pygame.draw.rect(WIN, WHITE, back_rect, 2, border_radius=8)
        draw_text(WIN, "BACK", back_rect.centerx, back_rect.centery, 28, WHITE, True)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                for idx, rect in enumerate(level_buttons):
                    if rect.collidepoint(mx, my) and idx < unlocked:
                        run_game(level=idx)
                        return
                if back_rect.collidepoint(mx, my):
                    return

        pygame.display.flip()

# Pretty gradient background utility used in main menu
def draw_gradient_background(surface, top_color, bottom_color):
    """Draw a vertical gradient background"""
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = int(top_color[0] * (1 - ratio) + bottom_color[0] * ratio)
        g = int(top_color[1] * (1 - ratio) + bottom_color[1] * ratio)
        b = int(top_color[2] * (1 - ratio) + bottom_color[2] * ratio)
        pygame.draw.line(surface, (r, g, b), (0, y), (WIDTH, y))

# Main Menu (pretty, animated)
def main():
    glow_phase = 0
    pulse_speed = 0.05
    particles = []

    play_button = pygame.Rect(WIDTH//2 - 120, HEIGHT//2 + 60, 240, 60)
    quit_button = pygame.Rect(WIDTH//2 - 120, HEIGHT//2 + 140, 240, 60)
    mute_button = pygame.Rect(WIDTH - 100, 20, 80, 40)

    while True:
        # Animated gradient background
        draw_gradient_background(WIN, (255, 182, 193), (173, 216, 230))

        # Animated title glow
        glow_phase += pulse_speed
        glow_opacity = 180 + int(75 * math.sin(glow_phase))
        title_color = (255, 105, 180)
        title_surface = BIG_FONT.render("ULTIMATE BRICK BREAKER", True, title_color)
        # Create a temporary surface to allow alpha without changing the original
        title_surf = pygame.Surface((title_surface.get_width(), title_surface.get_height()), pygame.SRCALPHA)
        title_surf.blit(title_surface, (0, 0))
        title_surf.set_alpha(glow_opacity)
        WIN.blit(title_surf, (WIDTH//2 - title_surface.get_width()//2, HEIGHT//2 - 150))

        # Floating spark particles from bottom
        if random.random() < 0.08:
            particles.append(Particle(random.randint(0, WIDTH), HEIGHT - 10, random.choice(COLORS)))
        for p in particles[:]:
            # Give particles a gentle upward movement for menu
            p.speed_y = random.uniform(-1.5, -0.2)
            p.update()
            p.draw(WIN)
            if p.life <= 0:
                particles.remove(p)

        # Hover detection
        mx, my = pygame.mouse.get_pos()

        # Draw buttons with hover scaling
        for rect, text, color in [
            (play_button, "PLAY", MINT),
            (quit_button, "QUIT", LIGHT_RED),
        ]:
            is_hover = rect.collidepoint(mx, my)
            scale = 1.06 if is_hover else 1.0
            scaled_rect = pygame.Rect(
                rect.x - (rect.width * (scale - 1)) / 2,
                rect.y - (rect.height * (scale - 1)) / 2,
                rect.width * scale,
                rect.height * scale
            )
            # Slight shadow for depth
            shadow_rect = scaled_rect.copy()
            shadow_rect.x += 4
            shadow_rect.y += 4
            pygame.draw.rect(WIN, (0, 0, 0), shadow_rect, border_radius=12)
            pygame.draw.rect(WIN, color, scaled_rect, border_radius=12)
            pygame.draw.rect(WIN, WHITE, scaled_rect, 3, border_radius=12)
            draw_text(WIN, text, scaled_rect.centerx, scaled_rect.centery, 40, WHITE, True)

        # Mute toggle button
        mute_color = LIGHT_GRAY if sound_manager.muted else YELLOW
        pygame.draw.rect(WIN, mute_color, mute_button, border_radius=8)
        pygame.draw.rect(WIN, WHITE, mute_button, 2, border_radius=8)
        mute_text = "UNMUTE" if sound_manager.muted else "MUTE"
        draw_text(WIN, mute_text, mute_button.centerx, mute_button.centery, 20, BLACK, True)

        # Helpful hint
        draw_text(WIN, "Click Play or press ENTER", WIDTH//2, HEIGHT//2 + 10, 20, DARK_BLUE, True)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    level_select()
                elif event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # We check the physical, original rects for click so behavior is consistent even when scaled visually
                if play_button.collidepoint(mx, my):
                    level_select()
                elif quit_button.collidepoint(mx, my):
                    pygame.quit()
                    sys.exit()
                elif mute_button.collidepoint(mx, my):
                    sound_manager.toggle_mute()

        clock.tick(FPS)

if __name__ == "__main__":
    main()