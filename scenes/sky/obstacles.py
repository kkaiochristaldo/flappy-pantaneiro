import math
import pygame as pg
from core import Entity, EntityFactory
from config import SCREEN_WIDTH, SCREEN_HEIGHT
import random 


class SkyObstacle(Entity):
    def __init__(self, obstacle_cfg: dict, x, y, speed_x=1.0, speed_y=1.0):
        super().__init__(obstacle_cfg, x, y)

        self._position = pg.math.Vector2(x, y)
        self._velocity = pg.math.Vector2(speed_x, speed_y)

        # Atualiza o rect com a posição inicial
        self.rect.center = (int(self._position.x), int(self._position.y))

    def update(self, delta_time):
        """Atualiza o estado do obstáculo."""
        super().update(delta_time)

        self._position += self._velocity * delta_time
        self.rect.center = (int(self._position.x), int(self._position.y))

        # Verificar se o obstáculo saiu da tela
        if self.rect.right < 0:
            self.kill()


# class FallingRock(SkyObstacle):
#     def __init__(self, cfg):
#         y = -50  # fora da tela
#         super().__init__(
#             cfg["falling_rock_cfg"], SCREEN_WIDTH, y, speed_x=-100, speed_y=200
#         )


class ZigZagBee(SkyObstacle):
    def __init__(self, cfg):
        y = random.randint(50, SCREEN_HEIGHT - 100)
        super().__init__(cfg["zigzag_bee_cfg"], SCREEN_WIDTH + 80, y, speed_x=-150, speed_y=0)  # +80 pixels fora
        
        self.amplitude = random.randint(80, 120)  # Altura do zigue-zague
        self.frequency = random.uniform(3.0, 5.0)  # Velocidade do zigue-zague
        self.timer = 0
        self.original_y = y
        
    def update(self, delta_time):
        self.timer += delta_time * self.frequency
        
        # Movimento senoidal mais suave
        self._position.y = self.original_y + math.sin(self.timer) * self.amplitude
        
        super().update(delta_time)


class ObstacleSpawner:
    """
    Gerencia a criação e o timing de spawn dos obstáculos para a DemoScene.
    """

    def __init__(self, obstacles_cfg: dict):
        """
        Inicializa o gerenciador, cria a fábrica e registra os obstáculos da demo.
        """
        self._config = obstacles_cfg
        self._factory = EntityFactory()
        self._timer = 0.0

        # self._factory.register(FallingRock, weight=10)
        self._factory.register(ZigZagBee, weight=10)
        self._factory.register(GroundTronco, weight=15)

    def update(self, delta_time: float, current_speed: float) -> SkyObstacle | None:
        """
        Atualiza o timer e decide se um novo obstáculo deve ser criado.

        Args:
            delta_time (float): Tempo desde o último frame.
            current_speed (float): A velocidade atual do jogo para ajustar a dificuldade.

        Returns:
            Obstacle | None: Retorna uma nova instância de obstáculo se for hora
                              de gerar um, ou None caso contrário.
        """
        self._timer += delta_time

        spawn_interval = max(0.4, 2.0 - (current_speed / 400))

        if self._timer >= spawn_interval:
            self._timer = 0
            return self._factory.create_random(self._config)

        return None

class GroundTronco(SkyObstacle):
    def __init__(self, cfg):
        # Altura aleatória mais limitada para evitar esticamento excessivo
        tronco_height = random.randint(120, 250)  # Reduzido para ficar mais natural
        
        # Posição: vem da direita
        x = SCREEN_WIDTH + 100  # Mais longe da borda
        
        super().__init__(cfg["tronco_cfg"], x, 0, speed_x=-200, speed_y=0)
        
        # Ajusta a altura limitando o redimensionamento
        if hasattr(self, 'image'):
            original_size = self.image.get_size()
            
            # Se a altura desejada for maior que a original, usa a original
            if tronco_height > original_size[1]:
                final_height = original_size[1]
            else:
                final_height = tronco_height
            
            # Mantém a proporção
            aspect_ratio = original_size[0] / original_size[1]
            new_width = int(final_height * aspect_ratio)
            
            self.image = pg.transform.scale(self.image, (new_width, final_height))
            self.rect = self.image.get_rect()
            self.rect.centerx = x
            self.rect.bottom = SCREEN_HEIGHT  # Base sempre no chão
            self.mask = pg.mask.from_surface(self.image)
    
    def update(self, delta_time):
        """Atualiza o tronco que se move horizontalmente"""
        super().update(delta_time)
        
        # Mantém a base sempre no chão durante o movimento
        self.rect.bottom = SCREEN_HEIGHT