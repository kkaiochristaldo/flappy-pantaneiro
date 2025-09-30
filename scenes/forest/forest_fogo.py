import pygame as pg
from config import SCREEN_HEIGHT
from core import Entity

class ForestFogo(Entity):
    """
    Entidade de fogo estática no canto esquerdo da tela,
    tocando apenas a animação 'burn'.
    """

    def __init__(self, fogo_cfg: dict):
        # Posição inicial: canto esquerdo superior (0,0)
        super().__init__(fogo_cfg, 45, 0)

        # Define a animação inicial como 'burn'
        self.set_animation("burn")

    def update(self, delta_time: float):
        # Só atualiza a animação
        super().update(delta_time)