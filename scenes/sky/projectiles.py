from core import Entity
from config import SCREEN_WIDTH

class Projectile(Entity):
    def __init__(self, projectile_cfg: dict, x: int, y: int, speed: int):
        super().__init__(projectile_cfg, x, y)
        self.set_animation("bullet")
        self.speed = speed

    def update(self, delta_time: float):
        self.rect.x += self.speed * delta_time
        if self.rect.left > SCREEN_WIDTH or self.rect.right < 0:
            self.kill()