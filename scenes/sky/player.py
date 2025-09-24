import pygame as pg
from config import SCREEN_HEIGHT
from core import Entity

class SkyPlayer(Entity):
    def __init__(self, player_cfg: dict):
        start_x = SCREEN_HEIGHT * 0.2; start_y = SCREEN_HEIGHT // 2
        super().__init__(player_cfg, start_x, start_y)

        physics = player_cfg.get("physics", {})
        self.__thrust_accel = physics.get("thrust_acceleration", 1500)
        self.__gravity_accel = physics.get("gravity_acceleration", 900)
        self.__max_fall_speed = physics.get("max_fall_speed", 600)
        self.__max_rise_speed = physics.get("max_rise_speed", -600)

        self.__position = pg.math.Vector2(start_x, start_y)
        self.__velocity = pg.math.Vector2(0, 0)

        self.__is_thrusting = False
        self.is_alive = True
        self.invincible = False

        self.set_animation("fly")
        self.shield_surf = pg.Surface((self.rect.width * 1.5, self.rect.height * 1.5), pg.SRCALPHA)
        pg.draw.circle(self.shield_surf, (173, 216, 230, 120), self.shield_surf.get_rect().center, self.rect.width * 0.7, 5)

    def update(self, delta_time: float):
        super().update(delta_time)
        if self.is_alive: self.__process_physics(delta_time)
        self.rect.center = self.__position

    def draw(self, screen: pg.Surface):
        screen.blit(self.image, self.rect)
        if self.invincible:
            shield_rect = self.shield_surf.get_rect(center=self.rect.center)
            screen.blit(self.shield_surf, shield_rect)

    def __process_physics(self, delta_time: float):
        current_acceleration = self.__gravity_accel
        if self.__is_thrusting: current_acceleration -= self.__thrust_accel
        self.__velocity.y += current_acceleration * delta_time
        self.__velocity.y = max(self.__max_rise_speed, min(self.__velocity.y, self.__max_fall_speed))
        self.__position.y += self.__velocity.y * delta_time
        if self.__position.y < 0: self.__position.y = 0; self.__velocity.y = 0
        if self.__position.y > SCREEN_HEIGHT: self.die()

    def start_thrust(self): self.__is_thrusting = True
    def stop_thrust(self): self.__is_thrusting = False
    def activate_shield(self, active: bool): self.invincible = active
    def die(self): self.is_alive = False
    
    def apply_repulsion(self):
        """Aplica um forte impulso vertical para cima, usado pelo jacaré."""
        self.__velocity.y = self.__max_rise_speed * 1.2