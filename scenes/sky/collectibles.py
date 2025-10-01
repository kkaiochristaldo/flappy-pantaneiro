import pygame as pg
import random
import math  # Adiciona import do math
from core import Entity
from config import SCREEN_WIDTH, SCREEN_HEIGHT

class Coin(Entity):
    def __init__(self):
        # Criar sprite simples da moeda
        coin_cfg = {
            "fallback_size": [32, 32],
            "fallback_color": [255, 215, 0]  # Dourado
        }
        
        x = SCREEN_WIDTH + 50
        y = random.randint(50, SCREEN_HEIGHT - 150)
        
        super().__init__(coin_cfg, x, y)
        
        self._position = pg.math.Vector2(x, y)
        self._velocity = pg.math.Vector2(-200, 0)
        self.collected = False
        self.bob_timer = 0
        
        # Efeito visual na moeda
        self._create_coin_sprite()
    
    def _create_coin_sprite(self):
        """Cria sprite visual da moeda"""
        surface = pg.Surface((32, 32), pg.SRCALPHA)
        pg.draw.circle(surface, (255, 215, 0), (16, 16), 14)  # Dourado
        pg.draw.circle(surface, (255, 255, 100), (16, 16), 10)  # Centro claro
        pg.draw.circle(surface, (200, 150, 0), (16, 16), 14, 2)  # Borda escura
        self.image = surface
        self.mask = pg.mask.from_surface(self.image)
    
    def update(self, delta_time):
        if not self.collected:
            # Movimento flutuante
            self.bob_timer += delta_time * 5
            bob_offset = pg.math.Vector2(0, 10 * math.sin(self.bob_timer))  # Usar math.sin
            
            self._position += self._velocity * delta_time + bob_offset * delta_time
            self.rect.center = (int(self._position.x), int(self._position.y))
            
            # Remove se saiu da tela
            if self.rect.right < 0:
                self.kill()

class CoinSpawner:
    def __init__(self):
        self.timer = 0
        self.spawn_interval = 3.0  # A cada 3 segundos
    
    def update(self, delta_time):
        self.timer += delta_time
        if self.timer >= self.spawn_interval:
            self.timer = 0
            return Coin()
        return None