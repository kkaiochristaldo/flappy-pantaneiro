import pygame as pg
from config import SCREEN_HEIGHT
from core import Entity


class SkyPlayer(Entity):
    def __init__(self, player_cfg: dict, invincible: bool = False):
        start_x = 100
        start_y = SCREEN_HEIGHT // 2
        super().__init__(player_cfg, start_x, start_y)

        # Configurações de física
        self.__position = pg.math.Vector2(start_x, start_y)
        self.__velocity = pg.math.Vector2(0, 0)
        self.__gravity_acceleration = 980
        self.__thrust_acceleration = 1300
        self.__dive_acceleration = 1800
        self.__tap_impulse = 120
        self.__max_fall_speed = 600
        self.__max_rise_speed = -500

        # Configurações de estado
        self.__is_alive = True
        self.__is_thrusting = False
        self.__is_diving = False
        self.__invincible = invincible

        # Posicionamento do rect
        self.rect.center = (int(self.__position.x), int(self.__position.y))

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
        """
        Atualiza o estado do jogador. A lógica de física deve ser
        implementada na classe filha.
        """
        # Primeiro, atualiza a lógica de animação
        self.__update_animation_state()

        # A classe base cuida da animação recém definida
        super().update(delta_time)

        # Processamento da física
        self.__process_physics(delta_time)

        # Atualiza a posição do rect
        self.rect.center = (int(self.__position.x), int(self.__position.y))

    def __process_physics(self, delta_time: float):
        """Implementa a física de gravidade, propulsão e mergulho."""

        # 1. Calcular a aceleração resultante
        current_acceleration = self.__gravity_acceleration
        if self.__is_thrusting:
            current_acceleration -= self.__thrust_acceleration
        if self.__is_diving:
            current_acceleration += self.__dive_acceleration

        # 2. Aplicar a aceleração à velocidade
        self.__velocity.y += current_acceleration * delta_time

        # 3. Limitar a velocidade
        self.__velocity.y = max(
            self.__max_rise_speed, min(self.__velocity.y, self.__max_fall_speed)
        )

        # 4. Aplicar a velocidade à posição
        self.__position.y += self.__velocity.y * delta_time

        # 5. Manter o jogador dentro da tela
        if self.__position.y < 0:
            self.__position.y = 0
            self.__velocity.y = 0
        if self.__position.y > SCREEN_HEIGHT:
            self.__position.y = SCREEN_HEIGHT
            self.__velocity.y = 0
            # self.die()  # O jogador morre se tocar o chão (exemplo)

    def __update_animation_state(self):
        """Define a animação correta com base no estado atual."""
        if self.__is_diving:
            self.set_animation("down")
        elif self.__is_thrusting:
            self.set_animation("up")
        else:
            self.set_animation("keep")

    def start_thrust(self):
        self.__is_thrusting = True
        self.__is_diving = False
        # Aplicar um impulso inicial para dar mais responsividade
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

    def die(self):
        """Sobrescreve o método die para parar os movimentos."""
        self.__is_thrusting = False
        self.__is_diving = False
