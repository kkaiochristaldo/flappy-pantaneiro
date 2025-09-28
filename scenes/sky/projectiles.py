import pygame as pg
import math
from core import Entity
from config import SCREEN_WIDTH, SCREEN_HEIGHT

class Projectile(Entity):
    def __init__(self, cfg, x, y, target_pos):
        super().__init__(cfg["projectile_cfg"], x, y)
        
        self._position = pg.math.Vector2(x, y)
        
        # Calcula direção para o target
        direction = target_pos - self._position
        if direction.length() > 0:
            direction.normalize_ip()
        
        self._velocity = direction * 300  # Velocidade do projétil
        self.lifetime = 5.0  # 5 segundos de vida
        
    def update(self, delta_time):
        super().update(delta_time)
        
        self._position += self._velocity * delta_time
        self.rect.center = (int(self._position.x), int(self._position.y))
        
        self.lifetime -= delta_time
        if self.lifetime <= 0 or self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()