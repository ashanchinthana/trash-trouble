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

# Player settings
PLAYER_WIDTH = 70
PLAYER_HEIGHT = 90
PLAYER_SPEED = 6

# Trash settings
TRASH_WIDTH = 35
TRASH_HEIGHT = 35
TRASH_SPEED = 2.5

# Bin settings
BIN_WIDTH = 110
BIN_HEIGHT = 90

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
        color = (*self.color[:3], alpha)
        size = int(5 * (self.life / self.max_life))
        if size > 0:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), size)

class Player:
    def __init__(self):
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT - 180
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
        # Enhanced robot design with animation
        body_color = BLUE
        detail_color = WHITE
        
        # Body with slight animation bobbing
        bob_offset = int(math.sin(self.animation_frame) * 2)
        
        # Main body
        pygame.draw.rect(screen, body_color, 
                        (self.x, self.y + bob_offset, self.width, self.height))
        pygame.draw.rect(screen, BLACK, 
                        (self.x, self.y + bob_offset, self.width, self.height), 3)
        
        # Head
        if self.face_image:
            # Blit custom face
            face_rect = self.face_image.get_rect(center=(self.x + self.width // 2, self.y + 20 + bob_offset))
            screen.blit(self.face_image, face_rect)
        else:
            # Draw original face if no image
            pygame.draw.circle(screen, body_color, 
                              (self.x + self.width//2, self.y + 20 + bob_offset), 25)
            pygame.draw.circle(screen, BLACK, 
                              (self.x + self.width//2, self.y + 20 + bob_offset), 25, 3)
            
            # Eyes
            eye_y = self.y + 15 + bob_offset
            if self.facing_right:
                pygame.draw.circle(screen, detail_color, (self.x + 20, eye_y), 6)
                pygame.draw.circle(screen, detail_color, (self.x + 40, eye_y), 6)
                pygame.draw.circle(screen, BLACK, (self.x + 22, eye_y), 3)
                pygame.draw.circle(screen, BLACK, (self.x + 42, eye_y), 3)
            else:
                pygame.draw.circle(screen, detail_color, (self.x + 20, eye_y), 6)
                pygame.draw.circle(screen, detail_color, (self.x + 40, eye_y), 6)
                pygame.draw.circle(screen, BLACK, (self.x + 18, eye_y), 3)
                pygame.draw.circle(screen, BLACK, (self.x + 38, eye_y), 3)
            
            # Mouth
            pygame.draw.arc(screen, RED, 
                           (self.x + 15, self.y + 25 + bob_offset, 30, 15), 0, math.pi, 3)
        
        # Arms
        arm_y = self.y + 35 + bob_offset
        pygame.draw.rect(screen, body_color, (self.x - 10, arm_y, 15, 30))
        pygame.draw.rect(screen, body_color, (self.x + self.width - 5, arm_y, 15, 30))
        
        # Legs
        leg_y = self.y + self.height - 20 + bob_offset
        pygame.draw.rect(screen, DARK_GREEN, (self.x + 10, leg_y, 15, 25))
        pygame.draw.rect(screen, DARK_GREEN, (self.x + self.width - 25, leg_y, 15, 25))

class TrashItem:
    def __init__(self, trash_type=None):
        self.x = random.randint(50, SCREEN_WIDTH - TRASH_WIDTH - 50)
        self.y = -TRASH_HEIGHT
        self.width = TRASH_WIDTH
        self.height = TRASH_HEIGHT
        self.speed = TRASH_SPEED
        self.rotation = 0
        self.rotation_speed = random.uniform(-3, 3)
        
        # Extended trash types: 0=Plastic, 1=Paper, 2=Organic, 3=Metal, 4=Glass
        if trash_type is None:
            self.trash_type = random.randint(0, 4)
        else:
            self.trash_type = trash_type
            
        self.colors = [BLUE, WHITE, BROWN, GRAY, LIGHT_GREEN]
        self.names = ["Plastic", "Paper", "Organic", "Metal", "Glass"]
        self.icons = ["🥤", "📄", "🍌", "🥫", "🍶"]
        
    def update(self):
        self.y += self.speed
        self.rotation += self.rotation_speed
        
    def draw(self, screen):
        # Create a surface for rotation
        surf = pygame.Surface((self.width + 20, self.height + 20), pygame.SRCALPHA)
        
        # Draw trash item on the surface
        color = self.colors[self.trash_type]
        
        if self.trash_type == 0:  # Plastic bottle
            pygame.draw.rect(surf, color, (10, 5, 20, 30))
            pygame.draw.rect(surf, color, (12, 2, 16, 8))
        elif self.trash_type == 1:  # Paper
            pygame.draw.rect(surf, color, (5, 5, 25, 30))
            pygame.draw.lines(surf, BLACK, False, [(8, 10), (27, 10)], 2)
            pygame.draw.lines(surf, BLACK, False, [(8, 15), (27, 15)], 2)
        elif self.trash_type == 2:  # Organic (banana)
            pygame.draw.ellipse(surf, YELLOW, (8, 5, 20, 30))
            pygame.draw.arc(surf, BROWN, (8, 5, 20, 30), 0, math.pi, 3)
        elif self.trash_type == 3:  # Metal can
            pygame.draw.rect(surf, color, (8, 5, 20, 30))
            pygame.draw.ellipse(surf, color, (8, 5, 20, 8))
        elif self.trash_type == 4:  # Glass bottle
            pygame.draw.rect(surf, color, (10, 10, 16, 25))
            pygame.draw.rect(surf, color, (12, 5, 12, 10))
        
        # Add outline
        pygame.draw.rect(surf, BLACK, (5, 5, 25, 30), 2)
        
        # Rotate the surface
        rotated_surf = pygame.transform.rotate(surf, self.rotation)
        
        # Get the rect and center it
        rect = rotated_surf.get_rect(center=(self.x + self.width//2, self.y + self.height//2))
        screen.blit(rotated_surf, rect)

class Bin:
    def __init__(self, x, bin_type):
        self.x = x
        self.y = SCREEN_HEIGHT - BIN_HEIGHT - 20
        self.width = BIN_WIDTH
        self.height = BIN_HEIGHT
        self.bin_type = bin_type
        self.colors = [BLUE, WHITE, BROWN, GRAY, LIGHT_GREEN]
        self.names = ["PLASTIC", "PAPER", "ORGANIC", "METAL", "GLASS"]
        self.glow = 0
        
    def draw(self, screen):
        # Glow effect
        glow_color = (*self.colors[self.bin_type][:3], 100)
        if self.glow > 0:
            pygame.draw.rect(screen, GREEN, 
                           (self.x - 5, self.y - 5, self.width + 10, self.height + 10))
            self.glow -= 1
        
        # Main bin
        pygame.draw.rect(screen, self.colors[self.bin_type], 
                        (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, BLACK, 
                        (self.x, self.y, self.width, self.height), 4)
        
        # 3D effect
        pygame.draw.polygon(screen, tuple(max(0, c-30) for c in self.colors[self.bin_type][:3]),
                          [(self.x, self.y), (self.x + 10, self.y - 10), 
                           (self.x + self.width + 10, self.y - 10), (self.x + self.width, self.y)])
        
        # Lid
        pygame.draw.ellipse(screen, tuple(min(255, c+20) for c in self.colors[self.bin_type][:3]),
                          (self.x - 5, self.y - 15, self.width + 10, 20))
        pygame.draw.ellipse(screen, BLACK, (self.x - 5, self.y - 15, self.width + 10, 20), 3)
        
        # Label with better font
        font = pygame.font.Font(None, 20)
        text = font.render(self.names[self.bin_type], True, BLACK)
        text_rect = text.get_rect(center=(self.x + self.width//2, self.y + self.height//2))
        screen.blit(text, text_rect)

class PowerUp:
    def __init__(self):
        self.x = random.randint(50, SCREEN_WIDTH - 50)
        self.y = -30
        self.width = 40
        self.height = 40
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
        bounce_offset = int(math.sin(self.bounce) * 3)
        y_pos = self.y + bounce_offset
        
        # Glow effect
        pygame.draw.circle(screen, (*self.colors[self.type][:3], 100), 
                         (self.x + self.width//2, y_pos + self.height//2), 25)
        
        # Main power-up
        pygame.draw.circle(screen, self.colors[self.type], 
                         (self.x + self.width//2, y_pos + self.height//2), 20)
        pygame.draw.circle(screen, WHITE, 
                         (self.x + self.width//2, y_pos + self.height//2), 20, 3)
        
        # Symbol
        font = pygame.font.Font(None, 24)
        text = font.render(self.symbols[self.type], True, BLACK)
        text_rect = text.get_rect(center=(self.x + self.width//2, y_pos + self.height//2))
        screen.blit(text, text_rect)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Trash Trouble - Enhanced Edition")
        self.clock = pygame.time.Clock()
        
        self.player = Player()
        self.trash_items = []
        self.power_ups = []
        self.particles = []
        
        # 5 bins now for all trash types
        bin_spacing = SCREEN_WIDTH // 6
        self.bins = [
            Bin(bin_spacing - BIN_WIDTH//2, 0),      # Plastic
            Bin(bin_spacing * 2 - BIN_WIDTH//2, 1),  # Paper
            Bin(bin_spacing * 3 - BIN_WIDTH//2, 2),  # Organic
            Bin(bin_spacing * 4 - BIN_WIDTH//2, 3),  # Metal
            Bin(bin_spacing * 5 - BIN_WIDTH//2, 4),  # Glass
        ]
        
        self.score = 0
        self.lives = 3
        self.level = 1
        self.timer = 180  # Extended timer for more play time
        
        # Game state
        self.game_state = "enter_name"
        self.player_name = ""
        self.input_active = True
        
        # Define rects for input elements
        self.input_box_rect = pygame.Rect(SCREEN_WIDTH//2 - 150, 180, 300, 50)
        self.upload_button_rect = pygame.Rect(SCREEN_WIDTH//2 - 150, 260, 300, 50)
        
        self.player_face_image = self.load_player_face()
        if self.player_face_image:
            self.player.face_image = self.player_face_image
            
        self.high_score = 0  # Track highest score in session
        
        # Power-up effects
        self.slow_time_timer = 0
        self.double_points_timer = 0
        self.score_multiplier = 1
        
        # Spawn timers
        self.spawn_timer = 0
        self.spawn_delay = 60
        self.powerup_spawn_timer = 0
        self.powerup_spawn_delay = 600  # 10 seconds
        
        # Combo system
        self.combo_count = 0
        self.combo_timer = 0
        
        # Background elements
        self.background_elements = []
        for i in range(20):
            self.background_elements.append({
                'x': random.randint(0, SCREEN_WIDTH),
                'y': random.randint(0, SCREEN_HEIGHT),
                'size': random.randint(3, 8),
                'color': random.choice([LIGHT_GREEN, WHITE, YELLOW]),
                'speed': random.uniform(0.5, 2)
            })
    
    def open_file_dialog_and_load_face(self):
        root = Tk()
        root.withdraw()  # Hide the main Tkinter window
        file_path = filedialog.askopenfilename(
            title="Select a face image for your character",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg")]
        )
        root.destroy()
        
        if file_path:
            self.player_face_image = self.load_player_face(file_path)
            if self.player_face_image:
                self.player.face_image = self.player_face_image

    def load_player_face(self, file_path=None):
        try:
            path_to_load = file_path
            if not path_to_load:
                if os.path.exists("face.png"):
                    path_to_load = "face.png"
                elif os.path.exists("face.jpg"):
                    path_to_load = "face.jpg"
                
            if path_to_load:
                image = pygame.image.load(path_to_load).convert_alpha()
                image = pygame.transform.scale(image, (40, 40))
                return image
        except Exception as e:
            print(f"Could not load custom face image: {e}")
        return None
    
    def create_particles(self, x, y, color, count=5):
        for _ in range(count):
            velocity_x = random.uniform(-3, 3)
            velocity_y = random.uniform(-5, -1)
            self.particles.append(Particle(x, y, color, velocity_x, velocity_y))
    
    def spawn_trash(self):
        if len(self.trash_items) < 6:
            new_trash = TrashItem()
            speed_multiplier = 1.0
            if self.slow_time_timer > 0:
                speed_multiplier = 0.5
            new_trash.speed = (TRASH_SPEED + (self.level - 1) * 0.3) * speed_multiplier
            self.trash_items.append(new_trash)
    
    def spawn_powerup(self):
        if len(self.power_ups) < 1 and random.random() < 0.3:
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
        if self.score > 0 and self.score % 150 == 0:
            self.level = self.score // 150 + 1
            self.spawn_delay = max(25, 60 - (self.level - 1) * 4)
    
    def activate_powerup(self, powerup):
        self.create_particles(powerup.x, powerup.y, powerup.colors[powerup.type], 8)
        
        if powerup.type == 'slow_time':
            self.slow_time_timer = 300  # 5 seconds
        elif powerup.type == 'extra_time':
            self.timer += 15
        elif powerup.type == 'double_points':
            self.double_points_timer = 300  # 5 seconds
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
                        self.combo_timer = 180  # 3 seconds
                        
                        # Combo bonus
                        if self.combo_count >= 3:
                            points += self.combo_count * 2
                        
                        self.score += points
                        bin.glow = 20
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
        # Gradient background
        for y in range(SCREEN_HEIGHT):
            color_ratio = y / SCREEN_HEIGHT
            r = int(135 + (175 - 135) * color_ratio)
            g = int(206 + (238 - 206) * color_ratio)
            b = int(235 + (255 - 235) * color_ratio)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (SCREEN_WIDTH, y))
        
        # Background elements
        for element in self.background_elements:
            pygame.draw.circle(self.screen, element['color'], 
                             (int(element['x']), int(element['y'])), element['size'])
    
    def draw_menu(self):
        self.draw_background()
        
        # Title with shadow
        font = pygame.font.Font(None, 84)
        shadow = font.render("TRASH TROUBLE", True, BLACK)
        title = font.render("TRASH TROUBLE", True, WHITE)
        self.screen.blit(shadow, (SCREEN_WIDTH//2 - shadow.get_width()//2 + 3, 103))
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 100))
        
        # Subtitle
        font = pygame.font.Font(None, 36)
        subtitle = font.render("Enhanced Edition", True, YELLOW)
        self.screen.blit(subtitle, (SCREEN_WIDTH//2 - subtitle.get_width()//2, 180))
        
        # Instructions
        font = pygame.font.Font(None, 32)
        instructions = [
            "Sort falling trash into correct bins!",
            "5 types: Plastic, Paper, Organic, Metal, Glass",
            "Collect power-ups for special effects!",
            "",
            "Controls:",
            "← → Arrow Keys: Move",
            "Spacebar: Drop trash",
            "",
            "Press SPACE to Start",
            "",
            "Tip: Combo correct drops for bonus points!"
        ]
        
        for i, instruction in enumerate(instructions):
            if instruction:
                color = WHITE if not instruction.startswith("Press") else YELLOW
                text = font.render(instruction, True, color)
                self.screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, 220 + i * 35))
    
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
            carried_trash.x = self.player.x + 17
            carried_trash.y = self.player.y - 45
            carried_trash.draw(self.screen)
        
        # Enhanced UI
        self.draw_ui()
    
    def draw_ui(self):
        # UI Background
        ui_surface = pygame.Surface((SCREEN_WIDTH, 60), pygame.SRCALPHA)
        ui_surface.fill((0, 0, 0, 12))
        self.screen.blit(ui_surface, (0, 0))
        
        font = pygame.font.Font(None, 32)
        
        # Score with multiplier
        score_text = f"Score: {self.score}"
        if self.score_multiplier > 1:
            score_text += f" (×{self.score_multiplier})"
        score_surface = font.render(score_text, True, YELLOW)
        self.screen.blit(score_surface, (10, 10))
        
        # Lives with hearts
        lives_text = "Lives: "
        lives_surface = font.render(lives_text, True, WHITE)
        self.screen.blit(lives_surface, (10, 40))
        for i in range(self.lives):
            heart_x = 80 + i * 25
            pygame.draw.circle(self.screen, RED, (heart_x, 50), 8)
        
        # Level
        level_surface = font.render(f"Level: {self.level}", True, WHITE)
        self.screen.blit(level_surface, (250, 10))
        
        # Player Name
        name_surface = font.render(f"Player: {self.player_name}", True, WHITE)
        self.screen.blit(name_surface, (SCREEN_WIDTH // 2 - name_surface.get_width() // 2, 10))
        
        # Timer with color coding
        timer_color = WHITE if self.timer > 20 else RED
        timer_surface = font.render(f"Time: {int(self.timer)}", True, timer_color)
        self.screen.blit(timer_surface, (SCREEN_WIDTH - 150, 10))
        
        # Combo counter
        if self.combo_count > 1:
            combo_surface = font.render(f"Combo: {self.combo_count}×", True, ORANGE)
            self.screen.blit(combo_surface, (SCREEN_WIDTH - 200, 40))
        
        # Active power-ups
        powerup_y = 70
        font_small = pygame.font.Font(None, 24)
        
        if self.slow_time_timer > 0:
            text = font_small.render(f"Slow Time: {self.slow_time_timer//60 + 1}s", True, PURPLE)
            self.screen.blit(text, (10, powerup_y))
            powerup_y += 25
            
        if self.double_points_timer > 0:
            text = font_small.render(f"Double Points: {self.double_points_timer//60 + 1}s", True, ORANGE)
            self.screen.blit(text, (10, powerup_y))
    
    def draw_game_over(self):
        self.draw_background()
        font = pygame.font.Font(None, 72)
        over_text = font.render("GAME OVER", True, RED)
        self.screen.blit(over_text, (SCREEN_WIDTH//2 - over_text.get_width()//2, 120))
        font_small = pygame.font.Font(None, 40)
        score_text = font_small.render(f"{self.player_name}'s Score: {self.score}", True, YELLOW)
        self.screen.blit(score_text, (SCREEN_WIDTH//2 - score_text.get_width()//2, 220))
        high_score_text = font_small.render(f"High Score: {self.high_score}", True, ORANGE)
        self.screen.blit(high_score_text, (SCREEN_WIDTH//2 - high_score_text.get_width()//2, 270))
        tip_text = font_small.render("Press R to Restart or Q to Quit", True, WHITE)
        self.screen.blit(tip_text, (SCREEN_WIDTH//2 - tip_text.get_width()//2, 340))
        font_tip = pygame.font.Font(None, 32)
        motivational = font_tip.render("Tip: Try to keep your combo going for max points!", True, GREEN)
        self.screen.blit(motivational, (SCREEN_WIDTH//2 - motivational.get_width()//2, 400))
    
    def draw_enter_name(self):
        self.draw_background()
        font_title = pygame.font.Font(None, 60)
        font_input = pygame.font.Font(None, 48)
        font_inst = pygame.font.Font(None, 28)

        # Title
        title_text = font_title.render("Create Your Player", True, WHITE)
        self.screen.blit(title_text, (SCREEN_WIDTH//2 - title_text.get_width()//2, 100))
        
        # Input Box
        input_box_color = YELLOW if self.input_active else WHITE
        pygame.draw.rect(self.screen, input_box_color, self.input_box_rect, 2)
        
        # Player name text
        name_surface = font_input.render(self.player_name, True, YELLOW)
        self.screen.blit(name_surface, (self.input_box_rect.x + 10, self.input_box_rect.y + 5))
        
        # Upload button
        pygame.draw.rect(self.screen, ORANGE, self.upload_button_rect)
        upload_text_font = pygame.font.Font(None, 36)
        upload_text = upload_text_font.render("Upload Face Image", True, BLACK)
        self.screen.blit(upload_text, (self.upload_button_rect.x + (self.upload_button_rect.width - upload_text.get_width()) // 2, self.upload_button_rect.y + 10))
        
        # Instructions
        inst_text1 = font_inst.render("Type your name and press ENTER to start", True, WHITE)
        self.screen.blit(inst_text1, (SCREEN_WIDTH//2 - inst_text1.get_width()//2, 350))
        
        # Display if face is loaded
        if self.player.face_image:
            face_loaded_text = font_inst.render("Face image loaded!", True, LIGHT_GREEN)
            self.screen.blit(face_loaded_text, (SCREEN_WIDTH//2 - face_loaded_text.get_width()//2, 400))
        else:
            inst_text2 = font_inst.render("No face image loaded.", True, GRAY)
            self.screen.blit(inst_text2, (SCREEN_WIDTH//2 - inst_text2.get_width()//2, 400))

    def restart_game(self):
        if self.score > self.high_score:
            self.high_score = self.score
        self.__init__()
        self.high_score = max(self.high_score, self.score)  # Retain high score
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
                                if len(self.player_name) < 15: # Limit name length
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
            
            # Update game state
            if self.game_state == "playing":
                self.update_game()
            
            # Draw everything
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