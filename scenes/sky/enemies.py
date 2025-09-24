import pygame as pg
import random
from config import SCREEN_WIDTH, SCREEN_HEIGHT
from core import Entity
from .projectiles import Projectile

class SkyEnemy(Entity):
    def __init__(self, enemy_cfg: dict, x: int, y: int):
        super().__init__(enemy_cfg, x, y)
        self.config = enemy_cfg
    def update(self, delta_time, scroll_speed, player, projectile_group, projectile_cfg):
        if self.rect.right < 0: self.kill()

class StraightEnemy(SkyEnemy):
    def __init__(self, enemy_cfg, x, y):
        super().__init__(enemy_cfg, x, y); self.set_animation("straight_fly")
    def update(self, delta_time, scroll_speed, player, projectile_group, projectile_cfg):
        self.rect.x -= scroll_speed * delta_time
        super().update(delta_time, scroll_speed, player, projectile_group, projectile_cfg)

class HomingEnemy(SkyEnemy):
    def __init__(self, enemy_cfg, x, y):
        super().__init__(enemy_cfg, x, y); self.set_animation("homing_fly"); self.homing_strength = 60
    def update(self, delta_time, scroll_speed, player, projectile_group, projectile_cfg):
        self.rect.x -= (scroll_speed * 0.8) * delta_time
        if player.rect.centery < self.rect.centery: self.rect.y -= self.homing_strength * delta_time
        elif player.rect.centery > self.rect.centery: self.rect.y += self.homing_strength * delta_time
        super().update(delta_time, scroll_speed, player, projectile_group, projectile_cfg)

class ShootingEnemy(SkyEnemy):
    def __init__(self, enemy_cfg, x, y):
        super().__init__(enemy_cfg, x, y); self.set_animation("shooter_fly")
        self.shoot_cooldown = 2.5; self.shoot_timer = random.uniform(0.5, self.shoot_cooldown)
    def update(self, delta_time, scroll_speed, player, projectile_group, projectile_cfg):
        self.rect.x -= scroll_speed * delta_time
        self.shoot_timer += delta_time
        if self.shoot_timer >= self.shoot_cooldown:
            self.shoot_timer = 0
            self.shoot(projectile_group, projectile_cfg)
        super().update(delta_time, scroll_speed, player, projectile_group, projectile_cfg)
    def shoot(self, projectile_group, projectile_cfg):
        bullet = Projectile(projectile_cfg, self.rect.centerx, self.rect.centery, speed=-350)
        projectile_group.add(bullet)

class EnemySpawner:
    def __init__(self, enemies_cfg: dict):
        self.config = enemies_cfg
        self.spawn_frequency = enemies_cfg.get("spawn_frequency_seconds", 2.0)
        self.timer = self.spawn_frequency
        self.enemy_types = [StraightEnemy, HomingEnemy, ShootingEnemy]
    def update(self, delta_time, scroll_speed, player, projectile_group, projectile_cfg):
        self.timer += delta_time
        if self.timer >= self.spawn_frequency:
            self.timer = 0
            start_x = SCREEN_WIDTH + 50; rand_y = random.randint(50, SCREEN_HEIGHT - 50)
            EnemyClass = random.choice(self.enemy_types)
            return [EnemyClass(self.config, start_x, rand_y)]
        return []