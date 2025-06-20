import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BROWN = (139, 69, 19)
GRAY = (128, 128, 128)
ORANGE = (255, 165, 0)

# Player settings
PLAYER_WIDTH = 60
PLAYER_HEIGHT = 80
PLAYER_SPEED = 5

# Trash settings
TRASH_WIDTH = 30
TRASH_HEIGHT = 30
TRASH_SPEED = 2

# Bin settings
BIN_WIDTH = 100
BIN_HEIGHT = 80

class Player:
    def __init__(self):
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT - 150
        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT
        self.speed = PLAYER_SPEED
        self.carrying_trash = None
        
    def move_left(self):
        if self.x > 0:
            self.x -= self.speed
    
    def move_right(self):
        if self.x < SCREEN_WIDTH - self.width:
            self.x += self.speed
    
    def draw(self, screen):
        # Draw player as a simple robot
        pygame.draw.rect(screen, BLUE, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, WHITE, (self.x + 10, self.y + 10, 15, 15))  # Left eye
        pygame.draw.rect(screen, WHITE, (self.x + 35, self.y + 10, 15, 15))  # Right eye
        pygame.draw.rect(screen, RED, (self.x + 20, self.y + 35, 20, 10))   # Mouth

class TrashItem:
    def __init__(self):
        self.x = random.randint(0, SCREEN_WIDTH - TRASH_WIDTH)
        self.y = -TRASH_HEIGHT
        self.width = TRASH_WIDTH
        self.height = TRASH_HEIGHT
        self.speed = TRASH_SPEED
        
        # Trash types: 0=Plastic, 1=Paper, 2=Organic
        self.trash_type = random.randint(0, 2)
        self.colors = [BLUE, WHITE, BROWN]  # Plastic=Blue, Paper=White, Organic=Brown
        self.names = ["Plastic", "Paper", "Organic"]
        
    def update(self):
        self.y += self.speed
        
    def draw(self, screen):
        pygame.draw.rect(screen, self.colors[self.trash_type], 
                        (self.x, self.y, self.width, self.height))
        # Add a simple icon/text
        font = pygame.font.Font(None, 16)
        text = font.render(self.names[self.trash_type][0], True, BLACK)
        screen.blit(text, (self.x + 10, self.y + 8))

class Bin:
    def __init__(self, x, bin_type):
        self.x = x
        self.y = SCREEN_HEIGHT - BIN_HEIGHT - 10
        self.width = BIN_WIDTH
        self.height = BIN_HEIGHT
        self.bin_type = bin_type
        self.colors = [BLUE, WHITE, BROWN]
        self.names = ["PLASTIC", "PAPER", "ORGANIC"]
        
    def draw(self, screen):
        pygame.draw.rect(screen, self.colors[self.bin_type], 
                        (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, BLACK, 
                        (self.x, self.y, self.width, self.height), 3)
        
        # Label
        font = pygame.font.Font(None, 24)
        text = font.render(self.names[self.bin_type], True, BLACK)
        text_rect = text.get_rect(center=(self.x + self.width//2, self.y + self.height//2))
        screen.blit(text, text_rect)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Trash Trouble")
        self.clock = pygame.time.Clock()
        
        self.player = Player()
        self.trash_items = []
        self.bins = [
            Bin(50, 0),   # Plastic bin
            Bin(350, 1),  # Paper bin
            Bin(650, 2)   # Organic bin
        ]
        
        self.score = 0
        self.lives = 3
        self.level = 1
        self.timer = 60  # 60 seconds
        self.game_state = "menu"  # menu, playing, game_over
        
        # Spawn timer
        self.spawn_timer = 0
        self.spawn_delay = 60  # frames between spawns
        
    def spawn_trash(self):
        if len(self.trash_items) < 5:  # Limit trash on screen
            new_trash = TrashItem()
            new_trash.speed = TRASH_SPEED + (self.level - 1) * 0.5
            self.trash_items.append(new_trash)
    
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
        
        # Spawn trash
        self.spawn_timer += 1
        if self.spawn_timer >= self.spawn_delay:
            self.spawn_trash()
            self.spawn_timer = 0
        
        # Update trash items
        for trash in self.trash_items[:]:
            trash.update()
            
            # Check if trash hits ground
            if trash.y > SCREEN_HEIGHT - 100:
                self.trash_items.remove(trash)
                self.lives -= 1
                if self.lives <= 0:
                    self.game_state = "game_over"
            
            # Check collision with player
            elif (self.player.carrying_trash is None and 
                  self.check_collision(self.player.x, self.player.y, self.player.width, self.player.height,
                                     trash.x, trash.y, trash.width, trash.height)):
                self.player.carrying_trash = trash
                self.trash_items.remove(trash)
        
        # Timer countdown
        self.timer -= 1/FPS
        if self.timer <= 0:
            self.game_state = "game_over"
        
        # Level progression
        if self.score > 0 and self.score % 100 == 0:
            self.level = self.score // 100 + 1
            self.spawn_delay = max(30, 60 - (self.level - 1) * 5)
    
    def handle_drop(self):
        if self.player.carrying_trash:
            # Check which bin the player is over
            for bin in self.bins:
                if (self.player.x + self.player.width//2 >= bin.x and 
                    self.player.x + self.player.width//2 <= bin.x + bin.width):
                    
                    if self.player.carrying_trash.trash_type == bin.bin_type:
                        # Correct bin!
                        self.score += 10
                    else:
                        # Wrong bin!
                        self.score = max(0, self.score - 5)
                        self.lives -= 1
                        if self.lives <= 0:
                            self.game_state = "game_over"
                    
                    self.player.carrying_trash = None
                    break
    
    def draw_menu(self):
        self.screen.fill(GREEN)
        
        # Title
        font = pygame.font.Font(None, 72)
        title = font.render("TRASH TROUBLE", True, BLACK)
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, 150))
        self.screen.blit(title, title_rect)
        
        # Instructions
        font = pygame.font.Font(None, 36)
        instructions = [
            "Sort the falling trash into correct bins!",
            "Arrow Keys: Move",
            "Spacebar: Drop trash",
            "Press SPACE to Start"
        ]
        
        for i, instruction in enumerate(instructions):
            text = font.render(instruction, True, BLACK)
            text_rect = text.get_rect(center=(SCREEN_WIDTH//2, 250 + i * 50))
            self.screen.blit(text, text_rect)
    
    def draw_game(self):
        self.screen.fill(GREEN)
        
        # Draw bins
        for bin in self.bins:
            bin.draw(self.screen)
        
        # Draw trash items
        for trash in self.trash_items:
            trash.draw(self.screen)
        
        # Draw player
        self.player.draw(self.screen)
        
        # Draw carried trash
        if self.player.carrying_trash:
            carried_trash = self.player.carrying_trash
            carried_trash.x = self.player.x + 15
            carried_trash.y = self.player.y - 40
            carried_trash.draw(self.screen)
        
        # Draw UI
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {self.score}", True, BLACK)
        lives_text = font.render(f"Lives: {self.lives}", True, BLACK)
        level_text = font.render(f"Level: {self.level}", True, BLACK)
        timer_text = font.render(f"Time: {int(self.timer)}", True, BLACK)
        
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(lives_text, (10, 50))
        self.screen.blit(level_text, (10, 90))
        self.screen.blit(timer_text, (SCREEN_WIDTH - 150, 10))
    
    def draw_game_over(self):
        self.screen.fill(RED)
        
        font = pygame.font.Font(None, 72)
        game_over_text = font.render("GAME OVER", True, WHITE)
        game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH//2, 200))
        self.screen.blit(game_over_text, game_over_rect)
        
        font = pygame.font.Font(None, 48)
        final_score = font.render(f"Final Score: {self.score}", True, WHITE)
        score_rect = final_score.get_rect(center=(SCREEN_WIDTH//2, 300))
        self.screen.blit(final_score, score_rect)
        
        font = pygame.font.Font(None, 36)
        restart_text = font.render("Press R to Restart or Q to Quit", True, WHITE)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH//2, 400))
        self.screen.blit(restart_text, restart_rect)
    
    def restart_game(self):
        self.__init__()
        self.game_state = "playing"
    
    def run(self):
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
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
            
            # Update game logic
            if self.game_state == "playing":
                self.update_game()
            
            # Draw everything
            if self.game_state == "menu":
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