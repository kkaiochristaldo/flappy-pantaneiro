import pygame as pg
from core import Entity
from config import SCREEN_HEIGHT

class Jacare(Entity):
    def __init__(self, jacare_cfg: dict, x: int, y: int):
        super().__init__(jacare_cfg, x, y)
        self.set_animation("attack")
        self.state = "emerging"; self.speed = 400
        self.target_y = SCREEN_HEIGHT - self.rect.height / 1.5
        self.timer = 0; self.attack_duration = 0.5

    def update(self, delta_time: float):
        super().update(delta_time)
        if self.state == "emerging":
            self.rect.y -= self.speed * delta_time
            if self.rect.y <= self.target_y: self.rect.y = self.target_y; self.state = "attacking"
        elif self.state == "attacking":
            self.timer += delta_time
            if self.timer >= self.attack_duration: self.state = "retreating"
        elif self.state == "retreating":
            self.rect.y += self.speed * delta_time
            if self.rect.top > SCREEN_HEIGHT: self.kill()