import pygame as pg
from config import SCREEN_HEIGHT
from config import SCREEN_WIDTH
from core import Entity

class WaterPlayer(Entity):
    def __init__(self, player_cfg: dict, invincible: bool = True):
        start_x = 100
        start_y = SCREEN_HEIGHT // 2
        super().__init__(player_cfg, start_x, start_y)

        # Vetores de física
        self.__position = pg.math.Vector2(start_x, start_y)
        self.__velocity = pg.math.Vector2(0, 0)

        # Configurações de física VERTICAL
        self.__gravity_acceleration = 0
        self.__thrust_acceleration = 1300
        self.__dive_acceleration = 1800
        self.__tap_impulse = 120
        self.__max_fall_speed = 600
        self.__max_rise_speed = -500

        # NOVO: Configurações de física HORIZONTAL
        self.__horizontal_acceleration = 1000
        self.__horizontal_drag = 0.90  # Atrito: 1.0 = sem atrito, 0.0 = parada instantânea
        self.__max_horizontal_speed = 400

        # Configurações de estado
        self.__is_alive = True
        self.__invincible = invincible
        self.__is_thrusting = False
        self.__is_diving = False
        # NOVO: Estados de movimento horizontal
        self.__is_moving_left = False
        self.__is_moving_right = False

        self.rect.center = (int(self.__position.x), int(self.__position.y))

    # ... (suas properties podem continuar aqui sem alterações) ...
    @property
    def invincible(self):
        return self.__invincible

    @invincible.setter
    def invincible(self, value: bool):
        self.__invincible = value

    @property
    def position(self):
        return self.__position


    def update(self, delta_time: float):
        self.__update_animation_state()
        super().update(delta_time)
        self.__process_physics(delta_time)
        self.rect.center = (int(self.__position.x), int(self.__position.y))

    # MODIFICADO: Lógica de física totalmente reescrita
    def __process_physics(self, delta_time: float):
        """Implementa a física separada para os eixos vertical e horizontal."""

        # --- FÍSICA VERTICAL (EIXO Y) ---
        accel_y = self.__gravity_acceleration
        if self.__is_thrusting:
            accel_y -= self.__thrust_acceleration
        if self.__is_diving:
            accel_y += self.__dive_acceleration
        
        self.__velocity.y += accel_y * delta_time
        self.__velocity.y = max(
            self.__max_rise_speed, min(self.__velocity.y, self.__max_fall_speed)
        )
        self.__position.y += self.__velocity.y * delta_time
    
        # --- FÍSICA HORIZONTAL (EIXO X) ---
        accel_x = 0
        if self.__is_moving_left:
            accel_x -= self.__horizontal_acceleration
        if self.__is_moving_right:
            accel_x += self.__horizontal_acceleration

        self.__velocity.x += accel_x * delta_time
        
        # Aplicar atrito/arrasto se não houver input horizontal
        if not self.__is_moving_left and not self.__is_moving_right:
            self.__velocity.x *= self.__horizontal_drag

        # Limitar velocidade horizontal
        self.__velocity.x = max(
            -self.__max_horizontal_speed, min(self.__velocity.x, self.__max_horizontal_speed)
        )
        self.__position.x += self.__velocity.x * delta_time
        w_player = 70;
        h_player = 30;
        # --- MANTER NA TELA ---
        if self.__position.y < 0 + h_player:
            self.__position.y = h_player
            self.__velocity.y = 0
        if self.__position.y > SCREEN_HEIGHT - h_player:
            self.__position.y = SCREEN_HEIGHT - h_player
            self.__velocity.y = 0
        
        if self.__position.x < 0 + w_player:
            self.__position.x = w_player
            self.__velocity.x = 0
        if self.__position.x > SCREEN_WIDTH - w_player:
            self.__position.x = SCREEN_WIDTH - w_player
            self.__velocity.x = 0

    def __update_animation_state(self):
        # Você pode melhorar isso para incluir animações para esquerda/direita
        if self.__is_diving:
            self.set_animation("down")
        elif self.__is_thrusting:
            self.set_animation("up")
        else:
            self.set_animation("keep")

    # Impulso afeta apenas o eixo Y
    def start_thrust(self):
        self.__is_thrusting = True
        self.__is_diving = False
        self.__velocity.y = max(
            self.__velocity.y - self.__tap_impulse, self.__max_rise_speed
        )

    def stop_thrust(self):
        self.__is_thrusting = False

    def start_dive(self):
        self.__is_diving = True
        self.__is_thrusting = False

    def stop_dive(self):
        self.__is_diving = False

    # Métodos para controlar o movimento horizontal
    def start_move_left(self):
        self.__is_moving_left = True

    def stop_move_left(self):
        self.__is_moving_left = False

    def start_move_right(self):
        self.__is_moving_right = True

    def stop_move_right(self):
        self.__is_moving_right = False

    def die(self):
        self.__is_thrusting = False
        self.__is_diving = False
        self.__is_moving_left = False
        self.__is_moving_right = False