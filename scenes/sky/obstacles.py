import pygame as pg
import random
from config import SCREEN_WIDTH, SCREEN_HEIGHT
from core import Entity

class SkyObstacle(Entity):
    def __init__(self, obstacle_cfg: dict, x: int, y: int):
        super().__init__(obstacle_cfg, x, y)
        self.set_animation("idle")

    def update(self, delta_time: float, scroll_speed: float):
        self.rect.x -= scroll_speed * delta_time
        if self.rect.right < 0:
            self.kill()

class ObstacleSpawner:
    def __init__(self, obstacles_cfg: dict):
        self.config = obstacles_cfg
        self.spawn_frequency = obstacles_cfg.get("spawn_frequency_seconds", 3.5)
        self.center_variance = obstacles_cfg.get("center_variance_pixels", 200)
        self.timer = self.spawn_frequency

    def update(self, delta_time: float, scroll_speed: float) -> list[SkyObstacle]:
        self.timer += delta_time
        if self.timer >= self.spawn_frequency:
            self.timer = 0
            return self.__spawn_obstacle(scroll_speed)
        return []

    def __spawn_obstacle(self, scroll_speed: float) -> list[SkyObstacle]:
        start_x = SCREEN_WIDTH + 100
        rand_y = random.randint(self.center_variance, SCREEN_HEIGHT - self.center_variance)
        obstacle = SkyObstacle(self.config, start_x, rand_y)
        return [obstacle]