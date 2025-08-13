import pygame as pg
from config import SCREEN_WIDTH


class BackgroundLayer:
    """
    Representa uma única camada de background que pode rolar horizontalmente.
    A imagem é ladrilhável para criar um efeito de rolagem contínuo.
    """

    def __init__(self, image: pg.Surface, parallax_scale: float = 1.0):
        """
        Inicializa a camada do background.

        Args:
            image (pg.Surface): A imagem da camada, já dimensionada.
            parallax_scale (float): A escala de velocidade para o efeito paralaxe.
                                    Valores menores se movem mais devagar (mais distantes).
        """
        self.image = image
        self.parallax_scale = parallax_scale
        self.scroll_x = 0.0
        self._image_width = self.image.get_width()

    def update(self, global_scroll_x: float):
        """
        Atualiza a posição de rolagem da camada com base no deslocamento global.

        Args:
            global_scroll_x (float): O deslocamento global do cenário.
        """
        self.scroll_x = global_scroll_x * self.parallax_scale

    def render(self, screen: pg.Surface):
        """
        Desenha a camada na tela, repetindo-a para preencher o espaço.
        """
        # Calcula o deslocamento para a rolagem
        offset = self.scroll_x % self._image_width

        # Calcula quantas cópias da imagem são necessárias para preencher a tela
        copies = (SCREEN_WIDTH // self._image_width) + 2

        for i in range(copies):
            # Desenha as cópias lado a lado para o efeito de loop
            x_pos = -offset + (i * self._image_width)
            screen.blit(self.image, (x_pos, 0))
