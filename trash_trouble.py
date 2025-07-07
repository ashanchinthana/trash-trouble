import pygame
import random
import sys
import os
import math
from tkinter import Tk, filedialog

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Constants
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 700
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (34, 139, 34)
BLUE = (30, 144, 255)
RED = (220, 20, 60)
YELLOW = (255, 215, 0)
BROWN = (139, 69, 19)
GRAY = (128, 128, 128)
ORANGE = (255, 140, 0)
PURPLE = (147, 112, 219)
PINK = (255, 192, 203)
LIGHT_GREEN = (144, 238, 144)
DARK_GREEN = (0, 100, 0)
LIGHT_BLUE = (173, 216, 230)
SILVER = (192, 192, 192)
CREAM = (245, 245, 220)

# Player settings
PLAYER_WIDTH = 60
PLAYER_HEIGHT = 80
PLAYER_SPEED = 6

# Trash settings
TRASH_WIDTH = 30
TRASH_HEIGHT = 30
TRASH_SPEED = 2.5

# Bin settings
BIN_WIDTH = 100
BIN_HEIGHT = 80

# Particle system
class Particle:
    def __init__(self, x, y, color, velocity_x=0, velocity_y=0):
        self.x = x
        self.y = y
        self.color = color
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        self.life = 30
        self.max_life = 30
        
    def update(self):
        self.x += self.velocity_x
        self.y += self.velocity_y
        self.velocity_y += 0.2  # gravity
        self.life -= 1
        
    def draw(self, screen):
        alpha = int(255 * (self.life / self.max_life))
        size = int(5 * (self.life / self.max_life))
        if size > 0:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), size)

class Player:
    def __init__(self):
        self.x = SCREEN_WIDTH // 2 - PLAYER_WIDTH // 2
        self.y = SCREEN_HEIGHT - 200
        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT
        self.speed = PLAYER_SPEED
        self.carrying_trash = None
        self.animation_frame = 0
        self.facing_right = True
        self.face_image = None
        
    def move_left(self):
        if self.x > 0:
            self.x -= self.speed
            self.facing_right = False
            self.animation_frame += 0.2
    
    def move_right(self):
        if self.x < SCREEN_WIDTH - self.width:
            self.x += self.speed
            self.facing_right = True
            self.animation_frame += 0.2
    
    def draw(self, screen):
        # Clean robot design like the reference image
        body_color = WHITE
        outline_color = BLACK
        
        # Body with slight animation bobbing
        bob_offset = int(math.sin(self.animation_frame) * 1)
        
        # Head (large white circle)
        head_center_x = self.x + self.width // 2
        head_center_y = self.y + 20 + bob_offset
        head_radius = 18
        
        # Head
        pygame.draw.circle(screen, body_color, (head_center_x, head_center_y), head_radius)
        pygame.draw.circle(screen, outline_color, (head_center_x, head_center_y), head_radius, 2)
        
        # Custom face or default face
        if self.face_image:
            # Create a circular surface for the face
            face_surface = pygame.Surface((head_radius * 2 - 6, head_radius * 2 - 6), pygame.SRCALPHA)
            
            # Scale the face image to fit the circle
            face_size = head_radius * 2 - 6
            scaled_face = pygame.transform.scale(self.face_image, (face_size, face_size))
            
            # Create circular mask
            mask = pygame.Surface((face_size, face_size), pygame.SRCALPHA)
            pygame.draw.circle(mask, (255, 255, 255, 255), (face_size//2, face_size//2), face_size//2)
            
            # Apply mask to the scaled face
            face_surface.blit(scaled_face, (0, 0))
            face_surface.blit(mask, (0, 0), special_flags=pygame.BLEND_ALPHA_SDL2)
            
            # Draw the masked face
            face_rect = face_surface.get_rect(center=(head_center_x, head_center_y))
            screen.blit(face_surface, face_rect)
        else:
            # Default robot eyes (simple black dots)
            eye_y = head_center_y - 3
            left_eye_x = head_center_x - 6
            right_eye_x = head_center_x + 6
            
            pygame.draw.circle(screen, BLACK, (left_eye_x, eye_y), 3)
            pygame.draw.circle(screen, BLACK, (right_eye_x, eye_y), 3)
        
        # Body (rounded rectangle)
        body_rect = pygame.Rect(self.x + 8, self.y + 35 + bob_offset, self.width - 16, self.height - 45)
        pygame.draw.rect(screen, LIGHT_BLUE, body_rect, border_radius=8)
        pygame.draw.rect(screen, outline_color, body_rect, 2, border_radius=8)
        
        # Chest panel
        chest_rect = pygame.Rect(self.x + 15, self.y + 42 + bob_offset, self.width - 30, 15)
        pygame.draw.rect(screen, CREAM, chest_rect, border_radius=3)
        pygame.draw.rect(screen, outline_color, chest_rect, 1, border_radius=3)
        
        # Simple chest lights
        light_y = self.y + 49 + bob_offset
        pygame.draw.circle(screen, GREEN, (self.x + 22, light_y), 2)
        pygame.draw.circle(screen, RED, (self.x + 30, light_y), 2)
        pygame.draw.circle(screen, YELLOW, (self.x + 38, light_y), 2)
        
        # Arms (simple rectangles)
        arm_y = self.y + 38 + bob_offset
        arm_width = 8
        arm_height = 25
        
        # Left arm
        left_arm_rect = pygame.Rect(self.x - 2, arm_y, arm_width, arm_height)
        pygame.draw.rect(screen, body_color, left_arm_rect, border_radius=4)
        pygame.draw.rect(screen, outline_color, left_arm_rect, 2, border_radius=4)
        
        # Right arm
        right_arm_rect = pygame.Rect(self.x + self.width - 6, arm_y, arm_width, arm_height)
        pygame.draw.rect(screen, body_color, right_arm_rect, border_radius=4)
        pygame.draw.rect(screen, outline_color, right_arm_rect, 2, border_radius=4)
        
        # Legs (simple rectangles)
        leg_y = self.y + self.height - 20 + bob_offset
        leg_width = 12
        leg_height = 16
        
        # Left leg
        left_leg_rect = pygame.Rect(self.x + 12, leg_y, leg_width, leg_height)
        pygame.draw.rect(screen, SILVER, left_leg_rect, border_radius=3)
        pygame.draw.rect(screen, outline_color, left_leg_rect, 2, border_radius=3)
        
        # Right leg
        right_leg_rect = pygame.Rect(self.x + self.width - 24, leg_y, leg_width, leg_height)
        pygame.draw.rect(screen, SILVER, right_leg_rect, border_radius=3)
        pygame.draw.rect(screen, outline_color, right_leg_rect, 2, border_radius=3)

class TrashItem:
    def __init__(self, trash_type=None):
        self.x = random.randint(50, SCREEN_WIDTH - TRASH_WIDTH - 50)
        self.y = -TRASH_HEIGHT
        self.width = TRASH_WIDTH
        self.height = TRASH_HEIGHT
        self.speed = TRASH_SPEED
        self.rotation = 0
        self.rotation_speed = random.uniform(-2, 2)
        
        # Extended trash types: 0=Plastic, 1=Paper, 2=Organic, 3=Metal, 4=Glass
        if trash_type is None:
            self.trash_type = random.randint(0, 4)
        else:
            self.trash_type = trash_type
            
        self.colors = [BLUE, WHITE, BROWN, GRAY, LIGHT_GREEN]
        self.names = ["Plastic", "Paper", "Organic", "Metal", "Glass"]
        
    def update(self):
        self.y += self.speed
        self.rotation += self.rotation_speed
        
    def draw(self, screen):
        # Simple geometric shapes for trash
        center_x = self.x + self.width // 2
        center_y = self.y + self.height // 2
        
        if self.trash_type == 0:  # Plastic - Blue square
            pygame.draw.rect(screen, BLUE, (self.x, self.y, self.width, self.height))
            pygame.draw.rect(screen, BLACK, (self.x, self.y, self.width, self.height), 2)
        elif self.trash_type == 1:  # Paper - White square
            pygame.draw.rect(screen, WHITE, (self.x, self.y, self.width, self.height))
            pygame.draw.rect(screen, BLACK, (self.x, self.y, self.width, self.height), 2)
        elif self.trash_type == 2:  # Organic - Brown square
            pygame.draw.rect(screen, BROWN, (self.x, self.y, self.width, self.height))
            pygame.draw.rect(screen, BLACK, (self.x, self.y, self.width, self.height), 2)
        elif self.trash_type == 3:  # Metal - Gray square
            pygame.draw.rect(screen, GRAY, (self.x, self.y, self.width, self.height))
            pygame.draw.rect(screen, BLACK, (self.x, self.y, self.width, self.height), 2)
        elif self.trash_type == 4:  # Glass - Light green square
            pygame.draw.rect(screen, LIGHT_GREEN, (self.x, self.y, self.width, self.height))
            pygame.draw.rect(screen, BLACK, (self.x, self.y, self.width, self.height), 2)

class Bin:
    def __init__(self, x, bin_type):
        self.x = x
        self.y = SCREEN_HEIGHT - BIN_HEIGHT - 30
        self.width = BIN_WIDTH
        self.height = BIN_HEIGHT
        self.bin_type = bin_type
        self.colors = [BLUE, WHITE, BROWN, GRAY, LIGHT_GREEN]
        self.names = ["PLASTIC", "PAPER", "ORGANIC", "METAL", "GLASS"]
        self.glow = 0
        
    def draw(self, screen):
        # Glow effect
        if self.glow > 0:
            pygame.draw.rect(screen, GREEN, 
                           (self.x - 5, self.y - 5, self.width + 10, self.height + 10), border_radius=5)
            self.glow -= 1
        
        # Main bin (rounded rectangle like reference image)
        pygame.draw.rect(screen, self.colors[self.bin_type], 
                        (self.x, self.y, self.width, self.height), border_radius=8)
        pygame.draw.rect(screen, BLACK, 
                        (self.x, self.y, self.width, self.height), 3, border_radius=8)
        
        # Label
        font = pygame.font.Font(None, 18)
        text = font.render(self.names[self.bin_type], True, BLACK)
        text_rect = text.get_rect(center=(self.x + self.width//2, self.y + self.height//2))
        screen.blit(text, text_rect)

class PowerUp:
    def __init__(self):
        self.x = random.randint(50, SCREEN_WIDTH - 50)
        self.y = -30
        self.width = 30
        self.height = 30
        self.speed = 3
        self.type = random.choice(['slow_time', 'extra_time', 'double_points', 'extra_life'])
        self.colors = {
            'slow_time': PURPLE,
            'extra_time': YELLOW,
            'double_points': ORANGE,
            'extra_life': PINK
        }
        self.symbols = {
            'slow_time': '⏰',
            'extra_time': '⏲️',
            'double_points': '×2',
            'extra_life': '♥'
        }
        self.bounce = 0
        
    def update(self):
        self.y += self.speed
        self.bounce += 0.2
        
    def draw(self, screen):
        bounce_offset = int(math.sin(self.bounce) * 2)
        y_pos = self.y + bounce_offset
        
        # Simple circle power-up
        pygame.draw.circle(screen, self.colors[self.type], 
                         (self.x + self.width//2, y_pos + self.height//2), 15)
        pygame.draw.circle(screen, BLACK, 
                         (self.x + self.width//2, y_pos + self.height//2), 15, 2)
        
        # Symbol
        font = pygame.font.Font(None, 20)
        text = font.render(self.symbols[self.type], True, BLACK)
        text_rect = text.get_rect(center=(self.x + self.width//2, y_pos + self.height//2))
        screen.blit(text, text_rect)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Trash Trouble - Clean Interface")
        self.clock = pygame.time.Clock()
        
        self.player = Player()
        self.trash_items = []
        self.power_ups = []
        self.particles = []
        
        # 5 bins evenly spaced
        bin_spacing = SCREEN_WIDTH // 6
        self.bins = [
            Bin(bin_spacing * 1 - BIN_WIDTH//2, 0),      # Plastic
            Bin(bin_spacing * 2 - BIN_WIDTH//2, 1),      # Paper
            Bin(bin_spacing * 3 - BIN_WIDTH//2, 2),      # Organic
            Bin(bin_spacing * 4 - BIN_WIDTH//2, 3),      # Metal
            Bin(bin_spacing * 5 - BIN_WIDTH//2, 4),      # Glass
        ]
        
        self.score = 0
        self.lives = 3
        self.level = 1
        self.timer = 180
        
        # Game state
        self.game_state = "enter_name"
        self.player_name = ""
        self.input_active = True
        
        # UI elements
        self.input_box_rect = pygame.Rect(SCREEN_WIDTH//2 - 150, 200, 300, 50)
        self.upload_button_rect = pygame.Rect(SCREEN_WIDTH//2 - 100, 280, 200, 40)
        self.reset_face_button_rect = pygame.Rect(SCREEN_WIDTH//2 - 100, 330, 200, 40)
        
        self.player_face_image = self.load_player_face()
        if self.player_face_image:
            self.player.face_image = self.player_face_image
            
        self.high_score = 0
        
        # Power-up effects
        self.slow_time_timer = 0
        self.double_points_timer = 0
        self.score_multiplier = 1
        
        # Spawn timers
        self.spawn_timer = 0
        self.spawn_delay = 90
        self.powerup_spawn_timer = 0
        self.powerup_spawn_delay = 600
        
        # Combo system
        self.combo_count = 0
        self.combo_timer = 0
        
        # Background elements
        self.background_elements = []
        for i in range(15):
            self.background_elements.append({
                'x': random.randint(0, SCREEN_WIDTH),
                'y': random.randint(0, SCREEN_HEIGHT),
                'size': random.randint(2, 5),
                'color': (255, 255, 255, 50),
                'speed': random.uniform(0.5, 1.5)
            })
    
    def open_file_dialog_and_load_face(self):
        root = Tk()
        root.withdraw()
        file_path = filedialog.askopenfilename(
            title="Select a face image for your robot",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp *.gif")]
        )
        root.destroy()
        
        if file_path:
            try:
                # Load and process the image
                image = pygame.image.load(file_path).convert_alpha()
                
                # Scale to appropriate size
                target_size = 32
                image = pygame.transform.scale(image, (target_size, target_size))
                
                self.player_face_image = image
                self.player.face_image = image
                print(f"Face image loaded successfully: {file_path}")
            except Exception as e:
                print(f"Error loading face image: {e}")

    def load_player_face(self, file_path=None):
        try:
            if file_path and os.path.exists(file_path):
                image = pygame.image.load(file_path).convert_alpha()
                image = pygame.transform.scale(image, (32, 32))
                return image
        except Exception as e:
            print(f"Could not load face image: {e}")
        return None
    
    def reset_face(self):
        self.player.face_image = None
        self.player_face_image = None
        print("Robot face reset to default")
    
    def create_particles(self, x, y, color, count=5):
        for _ in range(count):
            velocity_x = random.uniform(-3, 3)
            velocity_y = random.uniform(-5, -1)
            self.particles.append(Particle(x, y, color, velocity_x, velocity_y))
    
    def spawn_trash(self):
        if len(self.trash_items) < 4:
            new_trash = TrashItem()
            speed_multiplier = 1.0
            if self.slow_time_timer > 0:
                speed_multiplier = 0.5
            new_trash.speed = (TRASH_SPEED + (self.level - 1) * 0.2) * speed_multiplier
            self.trash_items.append(new_trash)
    
    def spawn_powerup(self):
        if len(self.power_ups) < 1 and random.random() < 0.2:
            self.power_ups.append(PowerUp())
    
    def check_collision(self, rect1_x, rect1_y, rect1_w, rect1_h, 
                       rect2_x, rect2_y, rect2_w, rect2_h):
        return (rect1_x < rect2_x + rect2_w and
                rect1_x + rect1_w > rect2_x and
                rect1_y < rect2_y + rect2_h and
                rect1_y + rect1_h > rect2_y)
    
    def update_game(self):
        keys = pygame.key.get_pressed()
        
        # Player movement
        if keys[pygame.K_LEFT]:
            self.player.move_left()
        if keys[pygame.K_RIGHT]:
            self.player.move_right()
        
        # Update timers
        if self.slow_time_timer > 0:
            self.slow_time_timer -= 1
        if self.double_points_timer > 0:
            self.double_points_timer -= 1
            self.score_multiplier = 2
        else:
            self.score_multiplier = 1
        
        if self.combo_timer > 0:
            self.combo_timer -= 1
        else:
            self.combo_count = 0
        
        # Spawn trash
        self.spawn_timer += 1
        if self.spawn_timer >= self.spawn_delay:
            self.spawn_trash()
            self.spawn_timer = 0
        
        # Spawn power-ups
        self.powerup_spawn_timer += 1
        if self.powerup_spawn_timer >= self.powerup_spawn_delay:
            self.spawn_powerup()
            self.powerup_spawn_timer = 0
        
        # Update trash items
        for trash in self.trash_items[:]:
            trash.update()
            
            if trash.y > SCREEN_HEIGHT - 120:
                self.trash_items.remove(trash)
                self.lives -= 1
                self.combo_count = 0
                self.create_particles(trash.x, trash.y, RED, 3)
                if self.lives <= 0:
                    self.game_state = "game_over"
            
            elif (self.player.carrying_trash is None and 
                  self.check_collision(self.player.x, self.player.y, self.player.width, self.player.height,
                                     trash.x, trash.y, trash.width, trash.height)):
                self.player.carrying_trash = trash
                self.trash_items.remove(trash)
        
        # Update power-ups
        for powerup in self.power_ups[:]:
            powerup.update()
            
            if powerup.y > SCREEN_HEIGHT:
                self.power_ups.remove(powerup)
            elif self.check_collision(self.player.x, self.player.y, self.player.width, self.player.height,
                                    powerup.x, powerup.y, powerup.width, powerup.height):
                self.activate_powerup(powerup)
                self.power_ups.remove(powerup)
        
        # Update particles
        for particle in self.particles[:]:
            particle.update()
            if particle.life <= 0:
                self.particles.remove(particle)
        
        # Update background
        for element in self.background_elements:
            element['y'] += element['speed']
            if element['y'] > SCREEN_HEIGHT:
                element['y'] = -10
                element['x'] = random.randint(0, SCREEN_WIDTH)
        
        # Timer countdown
        timer_speed = 1.0
        if self.slow_time_timer > 0:
            timer_speed = 0.5
        self.timer -= timer_speed / FPS
        
        if self.timer <= 0:
            self.game_state = "game_over"
        
        # Level progression
        if self.score > 0 and self.score % 100 == 0:
            self.level = self.score // 100 + 1
            self.spawn_delay = max(30, 90 - (self.level - 1) * 5)
    
    def activate_powerup(self, powerup):
        self.create_particles(powerup.x, powerup.y, powerup.colors[powerup.type], 8)
        
        if powerup.type == 'slow_time':
            self.slow_time_timer = 300
        elif powerup.type == 'extra_time':
            self.timer += 15
        elif powerup.type == 'double_points':
            self.double_points_timer = 300
        elif powerup.type == 'extra_life':
            self.lives += 1
    
    def handle_drop(self):
        if self.player.carrying_trash:
            for bin in self.bins:
                if (self.player.x + self.player.width//2 >= bin.x and 
                    self.player.x + self.player.width//2 <= bin.x + bin.width):
                    
                    if self.player.carrying_trash.trash_type == bin.bin_type:
                        # Correct bin!
                        points = 10 * self.score_multiplier
                        self.combo_count += 1
                        self.combo_timer = 180
                        
                        # Combo bonus
                        if self.combo_count >= 3:
                            points += self.combo_count * 2
                        
                        self.score += points
                        bin.glow = 30
                        self.create_particles(bin.x + bin.width//2, bin.y, GREEN, 8)
                        
                    else:
                        # Wrong bin!
                        self.score = max(0, self.score - 5)
                        self.lives -= 1
                        self.combo_count = 0
                        self.create_particles(bin.x + bin.width//2, bin.y, RED, 5)
                        if self.lives <= 0:
                            self.game_state = "game_over"
                    
                    self.player.carrying_trash = None
                    break
    
    def draw_background(self):
        # Clean sky blue background like reference image
        self.screen.fill((135, 206, 235))
        
        # Simple white floating elements
        for element in self.background_elements:
            pygame.draw.circle(self.screen, (255, 255, 255, 100), 
                             (int(element['x']), int(element['y'])), element['size'])
    
    def draw_menu(self):
        self.draw_background()
        
        # Title
        font = pygame.font.Font(None, 72)
        title = font.render("TRASH TROUBLE", True, WHITE)
        title_shadow = font.render("TRASH TROUBLE", True, BLACK)
        self.screen.blit(title_shadow, (SCREEN_WIDTH//2 - title.get_width()//2 + 2, 102))
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 100))
        
        # Instructions
        font = pygame.font.Font(None, 28)
        instructions = [
            "Sort falling trash into correct bins!",
            "",
            "Controls: ← → Move, SPACE Drop",
            "",
            "Press SPACE to Start"
        ]
        
        for i, instruction in enumerate(instructions):
            if instruction:
                color = WHITE if not instruction.startswith("Press") else YELLOW
                text = font.render(instruction, True, color)
                self.screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, 250 + i * 40))
    
    def draw_game(self):
        self.draw_background()
        
        # Draw bins
        for bin in self.bins:
            bin.draw(self.screen)
        
        # Draw trash items
        for trash in self.trash_items:
            trash.draw(self.screen)
        
        # Draw power-ups
        for powerup in self.power_ups:
            powerup.draw(self.screen)
        
        # Draw particles
        for particle in self.particles:
            particle.draw(self.screen)
        
        # Draw player
        self.player.draw(self.screen)
        
        # Draw carried trash
        if self.player.carrying_trash:
            carried_trash = self.player.carrying_trash
            carried_trash.x = self.player.x + 15
            carried_trash.y = self.player.y - 40
            carried_trash.draw(self.screen)
        
        # UI
        self.draw_ui()
    
    def draw_ui(self):
        # Clean UI like reference image
        font = pygame.font.Font(None, 24)
        
        # Score
        score_text = f"Score: {self.score}"
        if self.score_multiplier > 1:
            score_text += f" (×{self.score_multiplier})"
        score_surface = font.render(score_text, True, BLACK)
        self.screen.blit(score_surface, (10, 10))
        
        # Level
        level_surface = font.render(f"Level: {self.level}", True, BLACK)
        self.screen.blit(level_surface, (10, 35))
        
        # Player Name
        name_surface = font.render(f"Player: {self.player_name}", True, BLACK)
        self.screen.blit(name_surface, (SCREEN_WIDTH // 2 - name_surface.get_width() // 2, 10))
        
        # Timer
        timer_color = BLACK if self.timer > 20 else RED
        timer_surface = font.render(f"Time: {int(self.timer)}", True, timer_color)
        self.screen.blit(timer_surface, (SCREEN_WIDTH - 120, 10))
        
        # Lives (hearts)
        for i in range(self.lives):
            heart_x = SCREEN_WIDTH - 120 + i * 20
            pygame.draw.circle(self.screen, RED, (heart_x, 45), 6)
        
        # Combo
        if self.combo_count > 1:
            combo_surface = font.render(f"Combo: {self.combo_count}×", True, ORANGE)
            self.screen.blit(combo_surface, (10, 60))
    
    def draw_game_over(self):
        self.draw_background()
        font = pygame.font.Font(None, 64)
        over_text = font.render("GAME OVER", True, RED)
        self.screen.blit(over_text, (SCREEN_WIDTH//2 - over_text.get_width()//2, 200))
        
        font_small = pygame.font.Font(None, 32)
        score_text = font_small.render(f"{self.player_name}'s Score: {self.score}", True, BLACK)
        self.screen.blit(score_text, (SCREEN_WIDTH//2 - score_text.get_width()//2, 280))
        
        high_score_text = font_small.render(f"High Score: {self.high_score}", True, BLACK)
        self.screen.blit(high_score_text, (SCREEN_WIDTH//2 - high_score_text.get_width()//2, 320))
        
        tip_text = font_small.render("Press R to Restart or Q to Quit", True, BLACK)
        self.screen.blit(tip_text, (SCREEN_WIDTH//2 - tip_text.get_width()//2, 380))
    
    def draw_enter_name(self):
        self.draw_background()
        font_title = pygame.font.Font(None, 48)
        font_input = pygame.font.Font(None, 36)
        font_inst = pygame.font.Font(None, 24)

        # Title
        title_text = font_title.render("Create Your Robot Player", True, BLACK)
        self.screen.blit(title_text, (SCREEN_WIDTH//2 - title_text.get_width()//2, 100))
        
        # Input Box
        input_color = YELLOW if self.input_active else GRAY
        pygame.draw.rect(self.screen, WHITE, self.input_box_rect)
        pygame.draw.rect(self.screen, input_color, self.input_box_rect, 3)
        
        # Player name text
        name_surface = font_input.render(self.player_name, True, BLACK)
        self.screen.blit(name_surface, (self.input_box_rect.x + 10, self.input_box_rect.y + 10))
        
        # Upload button
        pygame.draw.rect(self.screen, ORANGE, self.upload_button_rect)
        upload_text = font_inst.render("Upload Face Image", True, BLACK)
        text_rect = upload_text.get_rect(center=self.upload_button_rect.center)
        self.screen.blit(upload_text, text_rect)
        
        # Reset button
        pygame.draw.rect(self.screen, RED, self.reset_face_button_rect)
        reset_text = font_inst.render("Reset to Default", True, WHITE)
        reset_rect = reset_text.get_rect(center=self.reset_face_button_rect.center)
        self.screen.blit(reset_text, reset_rect)
        
        # Instructions
        inst_text1 = font_inst.render("Enter your name and press ENTER to continue", True, BLACK)
        self.screen.blit(inst_text1, (SCREEN_WIDTH//2 - inst_text1.get_width()//2, 400))
        
        # Face status
        if self.player.face_image:
            face_text = font_inst.render("✓ Custom face loaded!", True, GREEN)
            self.screen.blit(face_text, (SCREEN_WIDTH//2 - face_text.get_width()//2, 430))
        else:
            face_text = font_inst.render("Using default robot face", True, GRAY)
            self.screen.blit(face_text, (SCREEN_WIDTH//2 - face_text.get_width()//2, 430))
        
        # Robot preview
        preview_player = Player()
        preview_player.x = SCREEN_WIDTH//2 - 30
        preview_player.y = 480
        preview_player.face_image = self.player.face_image
        preview_player.draw(self.screen)

    def restart_game(self):
        if self.score > self.high_score:
            self.high_score = self.score
        
        # Keep important data
        face_image = self.player.face_image
        player_name = self.player_name
        high_score = self.high_score
        
        self.__init__()
        self.player_name = player_name
        self.player.face_image = face_image
        self.high_score = high_score
        self.game_state = "playing"
    
    def run(self):
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                if self.game_state == "enter_name":
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if self.upload_button_rect.collidepoint(event.pos):
                            self.open_file_dialog_and_load_face()
                        elif self.reset_face_button_rect.collidepoint(event.pos):
                            self.reset_face()
                        elif self.input_box_rect.collidepoint(event.pos):
                            self.input_active = True
                        else:
                            self.input_active = False

                    if event.type == pygame.KEYDOWN:
                        if self.input_active:
                            if event.key == pygame.K_RETURN:
                                if self.player_name.strip():
                                    self.game_state = "menu"
                            elif event.key == pygame.K_BACKSPACE:
                                self.player_name = self.player_name[:-1]
                            else:
                                if len(self.player_name) < 15:
                                    self.player_name += event.unicode
                
                elif event.type == pygame.KEYDOWN:
                    if self.game_state == "menu":
                        if event.key == pygame.K_SPACE:
                            self.game_state = "playing"
                    
                    elif self.game_state == "playing":
                        if event.key == pygame.K_SPACE:
                            self.handle_drop()
                    
                    elif self.game_state == "game_over":
                        if event.key == pygame.K_r:
                            self.restart_game()
                        elif event.key == pygame.K_q:
                            running = False
            
            # Update
            if self.game_state == "playing":
                self.update_game()
            
            # Draw
            if self.game_state == "enter_name":
                self.draw_enter_name()
            elif self.game_state == "menu":
                self.draw_menu()
            elif self.game_state == "playing":
                self.draw_game()
            elif self.game_state == "game_over":
                self.draw_game_over()
            
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

# Run the game
if __name__ == "__main__":
    game = Game()
    game.run()