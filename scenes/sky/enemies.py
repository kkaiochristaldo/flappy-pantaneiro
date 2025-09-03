# scenes/sky/enemies.py
import pygame as pg
import random
from config import SCREEN_WIDTH, SCREEN_HEIGHT
from core import Entity
from .projectiles import Projectile

class SkyEnemy(Entity):
    """Classe base para todos os inimigos."""
    def __init__(self, enemy_cfg: dict, x: int, y: int):
        super().__init__(enemy_cfg, x, y)
        self.config = enemy_cfg

    def update(self, delta_time: float, scroll_speed: float, player, projectile_group):
        # Lógica de movimento a ser implementada pelas subclasses
        if self.rect.right < 0:
            self.kill()

class StraightEnemy(SkyEnemy):
    """Inimigo que se move em linha reta."""
    def __init__(self, enemy_cfg: dict, x: int, y: int):
        super().__init__(enemy_cfg, x, y)
        self.set_animation("straight_fly")
    
    def update(self, delta_time: float, scroll_speed: float, player, projectile_group):
        self.rect.x -= scroll_speed * delta_time
        super().update(delta_time, scroll_speed, player, projectile_group)

class HomingEnemy(SkyEnemy):
    """Inimigo que persegue lentamente o jogador no eixo Y."""
    def __init__(self, enemy_cfg: dict, x: int, y: int):
        super().__init__(enemy_cfg, x, y)
        self.set_animation("homing_fly")
        self.homing_strength = 50 # Quão rápido ele corrige a rota

    def update(self, delta_time: float, scroll_speed: float, player, projectile_group):
        self.rect.x -= (scroll_speed * 0.8) * delta_time # Um pouco mais lento
        
        # Perseguir o jogador no eixo Y
        if player.rect.centery < self.rect.centery:
            self.rect.y -= self.homing_strength * delta_time
        elif player.rect.centery > self.rect.centery:
            self.rect.y += self.homing_strength * delta_time
            
        super().update(delta_time, scroll_speed, player, projectile_group)

class ShootingEnemy(SkyEnemy):
    """Inimigo que se move em linha reta e atira."""
    def __init__(self, enemy_cfg: dict, x: int, y: int):
        super().__init__(enemy_cfg, x, y)
        self.set_animation("shooter_fly")
        self.shoot_cooldown = 2.0 # Atira a cada 2 segundos
        self.shoot_timer = random.uniform(0, self.shoot_cooldown) # Randomiza o primeiro tiro

    def update(self, delta_time: float, scroll_speed: float, player, projectile_group):
        self.rect.x -= scroll_speed * delta_time
        
        self.shoot_timer += delta_time
        if self.shoot_timer >= self.shoot_cooldown:
            self.shoot_timer = 0
            self.shoot(projectile_group)
            
        super().update(delta_time, scroll_speed, player, projectile_group)

    def shoot(self, projectile_group):
        # Lógica para carregar o JSON do projétil deve ser robusta
        from core import load_json
        projectile_cfg = { "spritesheet": load_json("./assets/images/sky/projectiles.json") }
        
        bullet = Projectile(projectile_cfg, self.rect.centerx, self.rect.centery, speed=-300)
        projectile_group.add(bullet)


class EnemySpawner:
    def __init__(self, enemies_cfg: dict):
        self.config = enemies_cfg
        self.spawn_frequency = enemies_cfg.get("spawn_frequency_seconds", 2.0)
        self.timer = self.spawn_frequency
        self.enemy_types = [StraightEnemy, HomingEnemy, ShootingEnemy]

    def update(self, delta_time: float, scroll_speed: float, player, projectile_group):
        self.timer += delta_time
        if self.timer >= self.spawn_frequency:
            self.timer = 0
            return self.__spawn_enemy(player, projectile_group)
        return []

    def __spawn_enemy(self, player, projectile_group):
        start_x = SCREEN_WIDTH + 50
        rand_y = random.randint(50, SCREEN_HEIGHT - 50)
        
        EnemyClass = random.choice(self.enemy_types)
        new_enemy = EnemyClass(self.config, start_x, rand_y)
        
        return [new_enemy]