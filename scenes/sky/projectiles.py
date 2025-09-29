import pygame as pg
import math
from core import Entity
from config import SCREEN_WIDTH, SCREEN_HEIGHT

class Projectile(Entity):
    def __init__(self, cfg, x, y, direction):

        super().__init__(cfg, x, y)
        
        self._position = pg.math.Vector2(x, y)

        
        self._velocity = direction * 400  # A velocidade pode ser ajustada
        self.lifetime = 5.0
        
        # Rotaciona sprite na direção do movimento
        if hasattr(self, 'image'):
            angle = pg.math.Vector2(1, 0).angle_to(direction)
            self.image = pg.transform.rotate(self.image, -angle)
            self.rect = self.image.get_rect(center=self.rect.center)
            self.mask = pg.mask.from_surface(self.image)
        
    def update(self, delta_time):
        super().update(delta_time)
        
        self._position += self._velocity * delta_time
        self.rect.center = (int(self._position.x), int(self._position.y))
        
        self.lifetime -= delta_time
        if self.lifetime <= 0 or self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()