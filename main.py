import pygame
import sys
import random

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Shooter")

clock = pygame.time.Clock()
FPS = 60

def load_image(name):
    import os
    path = os.path.join("assets", name)
    img = pygame.image.load(path).convert_alpha()
    return img

background = load_image("background.png")
player_img = load_image("player.png")
enemy_img = load_image("enemy.png")
boss_img = load_image("boss.png")
player_bullet_img = load_image("player_bullet.png")
enemy_bullet_img = load_image("enemy_bullet.png")
powerup_big_img = load_image("powerup_pizza_big.png")
powerup_small_img = load_image("powerup_pizza_small.png")

font = pygame.font.SysFont("Arial", 36)
small_font = pygame.font.SysFont("Arial", 22)

def draw_text(text, f, color, x, y):
    surf = f.render(text, True, color)
    rect = surf.get_rect(center=(x, y))
    screen.blit(surf, rect)

def game_over_screen(score):
    while True:
        screen.blit(background, (0, 0))
        draw_text("GAME OVER", font, (255, 50, 50), WIDTH//2, HEIGHT//2 - 80)
        draw_text(f"Final Score: {score}", small_font, (255, 255, 255), WIDTH//2, HEIGHT//2 - 30)
        draw_text("Press R to Retry", small_font, (255, 255, 0), WIDTH//2, HEIGHT//2 + 20)
        draw_text("Press Q to Quit", small_font, (255, 255, 255), WIDTH//2, HEIGHT//2 + 60)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return True
                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()

def win_screen(score):
    while True:
        screen.blit(background, (0, 0))
        draw_text("YOU WIN!", font, (50, 255, 50), WIDTH//2, HEIGHT//2 - 80)
        draw_text(f"Final Score: {score}", small_font, (255, 255, 255), WIDTH//2, HEIGHT//2 - 30)
        draw_text("Press R to Play Again", small_font, (255, 255, 0), WIDTH//2, HEIGHT//2 + 20)
        draw_text("Press Q to Quit", small_font, (255, 255, 255), WIDTH//2, HEIGHT//2 + 60)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return True
                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_img
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH // 2
        self.rect.bottom = HEIGHT - 20
        self.hitbox = pygame.Rect(0, 0, self.rect.width, self.rect.height)
        self.hitbox.center = self.rect.center
        self.speed = 6
        self.shoot_cooldown = 0
        self.lives = 3
        self.rapid_fire = False
        self.rapid_fire_timer = 0
        self.shield = False
        self.shield_timer = 0
        self.invincible = False
        self.invincible_timer = 0

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += self.speed
        if keys[pygame.K_UP] and self.rect.top > 0:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN] and self.rect.bottom < HEIGHT:
            self.rect.y += self.speed
        self.hitbox.center = self.rect.center
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        if self.rapid_fire:
            self.rapid_fire_timer -= 1
            if self.rapid_fire_timer <= 0:
                self.rapid_fire = False
        if self.shield:
            self.shield_timer -= 1
            if self.shield_timer <= 0:
                self.shield = False
        if self.invincible:
            self.invincible_timer -= 1
            if self.invincible_timer <= 0:
                self.invincible = False

    def shoot(self, all_sprites, player_bullets):
        cooldown = 8 if self.rapid_fire else 20
        if self.shoot_cooldown == 0:
            bullet = PlayerBullet(self.rect.centerx, self.rect.top)
            all_sprites.add(bullet)
            player_bullets.add(bullet)
            self.shoot_cooldown = cooldown

    def got_hit(self):
        if self.invincible or self.shield:
            if self.shield:
                self.shield = False
            return False
        self.lives -= 1
        self.invincible = True
        self.invincible_timer = 120
        return True

class PlayerBullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = player_bullet_img
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.hitbox = pygame.Rect(0, 0, self.rect.width, self.rect.height)
        self.hitbox.center = self.rect.center
        self.speed = 10

    def update(self):
        self.rect.y -= self.speed
        self.hitbox.center = self.rect.center
        if self.rect.bottom < 0:
            self.kill()

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, all_sprites, enemy_bullets):
        super().__init__()
        self.image = enemy_img
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.hitbox = pygame.Rect(0, 0, self.rect.width, self.rect.height)
        self.hitbox.center = self.rect.center
        self.speed_x = 2
        self.shoot_cooldown = random.randint(90, 150)
        self.warning_timer = 0
        self.health = 1
        self.all_sprites = all_sprites
        self.enemy_bullets = enemy_bullets

    def update(self):
        self.rect.x += self.speed_x
        if self.rect.right >= WIDTH or self.rect.left <= 0:
            self.speed_x *= -1
            self.rect.y += 20
        self.hitbox.center = self.rect.center
        self.shoot_cooldown -= 1

        if self.shoot_cooldown == 30:
            self.warning_timer = 30
        if self.warning_timer > 0:
            self.warning_timer -= 1
        if self.shoot_cooldown <= 0:
            self.shoot()
            self.shoot_cooldown = random.randint(90, 150)
        if self.rect.top > HEIGHT:
            self.kill()

    def shoot(self):
        bullet = EnemyBullet(self.rect.centerx, self.rect.bottom)
        self.all_sprites.add(bullet)
        self.enemy_bullets.add(bullet)

class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = enemy_bullet_img
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.top = y
        self.hitbox = pygame.Rect(0, 0, self.rect.width // 2, self.rect.height // 2)
        self.hitbox.center = self.rect.center
        self.speed = 6

    def update(self):
        self.rect.y += self.speed
        self.hitbox.center = self.rect.center
        if self.rect.top > HEIGHT:
            self.kill()

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y, kind):
        super().__init__()
        self.kind = kind
        self.image = powerup_big_img if kind == "shield" else powerup_small_img
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.speed = 3

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()

def spawn_wave(wave_num, all_sprites, enemies, enemy_bullets):
    if wave_num == 1:
        # Wave 1: 3 enemies in a single row, slow shooting
        positions = [(150, 60), (400, 60), (650, 60)]
        cooldown_range = (120, 180)
    elif wave_num == 2:
        # Wave 2: 5 enemies in 2 rows, moderate shooting
        positions = [
            (120, 60), (400, 60), (680, 60),
            (250, 160), (550, 160)
        ]
        cooldown_range = (100, 150)
    elif wave_num == 3:
        # Wave 3: 6 enemies in 2 rows, faster shooting
        positions = [
            (100, 60), (300, 60), (500, 60), (700, 60),
            (200, 160), (600, 160)
        ]
        cooldown_range = (80, 120)
    else:
        positions = []
        cooldown_range = (80, 120)

    for (x, y) in positions:
        enemy = Enemy(x, y, all_sprites, enemy_bullets)
        enemy.shoot_cooldown = random.randint(*cooldown_range)
        all_sprites.add(enemy)
        enemies.add(enemy)

def hitbox_collide_group(sprite, group, dokill):
    hits = []
    for s in group:
        if sprite.hitbox.colliderect(s.hitbox):
            hits.append(s)
            if dokill:
                s.kill()
    return hits

def main():
    all_sprites = pygame.sprite.Group()
    player_bullets = pygame.sprite.Group()
    enemy_bullets = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    powerups = pygame.sprite.Group()

    player = Player()
    all_sprites.add(player)

    wave = 1
    score = 0
    spawn_wave(wave, all_sprites, enemies, enemy_bullets)

    while True:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            player.shoot(all_sprites, player_bullets)

        all_sprites.update()

        # Player bullets hit enemies
        for bullet in list(player_bullets):
            for enemy in list(enemies):
                if bullet.hitbox.colliderect(enemy.hitbox):
                    bullet.kill()
                    enemy.health -= 1
                    if enemy.health <= 0:
                        score += 10
                        if random.random() < 0.3:
                            kind = random.choice(["shield", "rapid_fire"])
                            pu = PowerUp(enemy.rect.centerx, enemy.rect.centery, kind)
                            all_sprites.add(pu)
                            powerups.add(pu)
                        enemy.kill()
                    break

        # Enemy bullets hit player
        if not player.invincible:
            hits = hitbox_collide_group(player, enemy_bullets, True)
            if hits:
                player.got_hit()
                if player.lives <= 0:
                    if game_over_screen(score):
                        main()
                    return

        # Power-up pickup
        for pu in list(powerups):
            if player.rect.colliderect(pu.rect):
                if pu.kind == "shield":
                    player.shield = True
                    player.shield_timer = 300
                elif pu.kind == "rapid_fire":
                    player.rapid_fire = True
                    player.rapid_fire_timer = 300
                pu.kill()

        # Next wave
        if len(enemies) == 0:
            wave += 1
            if wave > 3:
                if win_screen(score):
                    main()
                return
            spawn_wave(wave, all_sprites, enemies, enemy_bullets)

        # Draw background
        screen.blit(background, (0, 0))

        # Draw all sprites except player
        for sprite in all_sprites:
            if sprite != player:
                screen.blit(sprite.image, sprite.rect)
                # Draw warning glow and line for enemies about to shoot
                if isinstance(sprite, Enemy) and sprite.warning_timer > 0:
                    alpha = int((sprite.warning_timer / 30) * 180)
                    warning_surf = pygame.Surface((sprite.rect.width, sprite.rect.height), pygame.SRCALPHA)
                    pygame.draw.ellipse(warning_surf, (255, 0, 0, alpha), warning_surf.get_rect())
                    screen.blit(warning_surf, sprite.rect)
                    pygame.draw.line(screen, (255, 50, 50),
                                     (sprite.rect.centerx, sprite.rect.bottom),
                                     (sprite.rect.centerx, HEIGHT), 2)

        # Draw player with invincibility flash
        if not (player.invincible and player.invincible_timer % 10 < 5):
            screen.blit(player.image, player.rect)

        # Shield circle
        if player.shield:
            pygame.draw.circle(screen, (0, 200, 255), player.rect.center, 70, 3)

        # HUD
        screen.blit(font.render(f"Score: {score}", True, (255, 255, 255)), (10, 10))
        screen.blit(font.render(f"Lives: {player.lives}", True, (255, 255, 255)), (10, 45))
        screen.blit(font.render(f"Wave: {wave}", True, (255, 255, 255)), (WIDTH - 140, 10))

        if player.rapid_fire:
            screen.blit(small_font.render("Rapid Fire!", True, (255, 255, 0)), (10, 85))
        if player.shield:
            screen.blit(small_font.render("Shield!", True, (0, 200, 255)), (10, 110))

        pygame.display.flip()

main()