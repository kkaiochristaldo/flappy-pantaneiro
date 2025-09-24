import pygame as pg
import random
from config import SCREEN_WIDTH, SCREEN_HEIGHT
from core import Entity

class PowerUp(Entity):
    def __init__(self, powerup_cfg: dict, x: int, y: int, powerup_type: str):
        super().__init__(powerup_cfg, x, y)
        self.type = powerup_type
        self.set_animation(self.type)

    def update(self, delta_time: float, scroll_speed: float):
        self.rect.x -= scroll_speed * delta_time
        if self.rect.right < 0:
            self.kill()

class PowerUpSpawner:
    def __init__(self, powerups_cfg: dict):
        self.config = powerups_cfg
        self.spawn_frequency = powerups_cfg.get("spawn_frequency_seconds", 10.0)
        self.timer = self.spawn_frequency

    def update(self, delta_time: float, scroll_speed: float) -> list[PowerUp]:
        self.timer += delta_time
        if self.timer >= self.spawn_frequency:
            self.timer = 0
            return self.__spawn_powerup(scroll_speed)
        return []

    def __spawn_powerup(self, scroll_speed: float) -> list[PowerUp]:
        start_x = SCREEN_WIDTH + 50
        rand_y = random.randint(100, SCREEN_HEIGHT - 100)
        # Por enquanto, só temos o tipo "shield"
        powerup = PowerUp(self.config, start_x, rand_y, "shield")
        return [powerup]