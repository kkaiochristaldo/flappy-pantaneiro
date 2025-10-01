import pygame as pg
import random
from core import Entity
from config import SCREEN_WIDTH, SCREEN_HEIGHT

class PowerUp(Entity):
    def __init__(self, power_type):
        cfg = {
            "fallback_size": [32, 32],
            "fallback_color": self._get_color(power_type)
        }
        
        x = SCREEN_WIDTH + 50
        y = random.randint(100, SCREEN_HEIGHT - 200)
        super().__init__(cfg, x, y)
        
        self._position = pg.math.Vector2(x, y)
        self._velocity = pg.math.Vector2(-180, 0)
        self.power_type = power_type
        self._create_sprite()
        
    def _get_color(self, power_type):
        colors = {
            "shield": (0, 150, 255),
            "speed": (255, 255, 0),
            "shoot": (255, 50, 50)  # Vermelho para tiro
        }
        return colors.get(power_type, (255, 0, 255))

    def _create_sprite(self):
        surface = pg.Surface((32, 32), pg.SRCALPHA)
        color = self._get_color(self.power_type)
        
        if self.power_type == "shield":
            pg.draw.circle(surface, color, (16, 16), 14)
            pg.draw.circle(surface, (255, 255, 255), (16, 16), 10, 2)
        elif self.power_type == "speed":
            points = [(16, 5), (12, 12), (18, 12), (14, 27), (20, 15), (14, 15)]
            pg.draw.polygon(surface, color, points)
        elif self.power_type == "shoot":
            # Raio/explosão
            center = (16, 16)
            for angle in range(0, 360, 45):
                import math
                rad = math.radians(angle)
                x = center[0] + int(12 * math.cos(rad))
                y = center[1] + int(12 * math.sin(rad))
                pg.draw.line(surface, color, center, (x, y), 3)
            
        self.image = surface
        self.mask = pg.mask.from_surface(self.image)
    
    def update(self, delta_time):
        self._position += self._velocity * delta_time
        self.rect.center = (int(self._position.x), int(self._position.y))
        
        if self.rect.right < 0:
            self.kill()