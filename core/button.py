import pygame as pg


class Button:
    def __init__(
        self, text, font, center_position, width=240, height=60, callback=None
    ):
        self.__text = text
        self.__font = font
        self.__center_position = center_position
        self.__width = width
        self.__height = height
        self.__idle_color = (0, 0, 0)
        self.__hover_color = (255, 0, 0)
        self.__color = self.__idle_color
        self.__selected = False
        self.__callback = callback

        # Criar o retângulo do botão uma vez na inicialização
        self.text_surface = font.render(text, True, self.__idle_color)
        self.text_rect = self.text_surface.get_rect()

        if self.__width < self.text_rect.width:
            self.__width = self.text_rect.width * 1.2

        self.rect = pg.Rect(0, 0, self.__width, self.__height)
        self.rect.center = self.__center_position

    @property
    def selected(self):
        return self.__selected

    @selected.setter
    def selected(self, value):
        self.__selected = value

    @property
    def callback(self):
        return self.__callback

    @callback.setter
    def callback(self, function):
        self.__callback = function

    def update(self):
        # Atualiza a cor com base no estado de seleção
        self.__color = self.__hover_color if self.__selected else self.__idle_color

    def render(self, screen):
        self.label = self.__font.render(self.__text, True, self.__color)

        # Caixa de fundo (cinza claro)
        pg.draw.rect(screen, (192, 192, 192), self.rect)
        # Borda do botão
        pg.draw.rect(screen, self.__color, self.rect, 3)

        label_rect = self.label.get_rect(center=self.rect.center)
        screen.blit(self.label, label_rect)
