import pygame as pg
from core import Button, FontManager, GameState

pg.joystick.init()

if pg.joystick.get_count() > 0:
    joystick = pg.joystick.Joystick(0)
    joystick.init()
else:
    joystick = None

class BaseMenu:
    def __init__(self, game_state: GameState):
        super().__init__()
        self._game_state = game_state
        self.font_manager = FontManager()
        self.small_font = self.font_manager.load_font(None, 50)

        self._options = []
        self._buttons = []  # Lista para armazenar os botões
        self.__btn_idx = 0

    @property
    def _current_button(self):
        return self._buttons[self.__btn_idx]

    def _create_buttons(self):
        if self._options:
            screen_center_x = self._game_state.screen.get_width() // 2
            start_y = 220
            spacing = 80

            for i, (text, function) in enumerate(self._options):
                btn = Button(
                    text=text,
                    font=self.small_font,
                    center_position=(screen_center_x, start_y + i * spacing),
                    callback=function,
                )
                self._buttons.append(btn)

            self._current_button.selected = True

    def handle_event(self, event):
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_DOWN:
                self._move_selection(1)
            elif event.key == pg.K_UP:
                self._move_selection(-1)
            elif event.key == pg.K_RETURN:
                self._select_option()

        if joystick != None and event.type == pg.JOYAXISMOTION:
            if (event.axis == 1):
                self._move_selection(int(event.value))

        if joystick != None and event.type == pg.JOYBUTTONDOWN:
            if (event.button == 0):
                self._select_option()


    def _move_selection(self, direction):
        if self._buttons:
            self._buttons[self.__btn_idx].selected = False  # Desseleciona o botão atual
            self.__btn_idx = (self.__btn_idx + direction) % len(self._buttons)
            self._buttons[self.__btn_idx].selected = True  # Seleciona o novo botão

    def _select_option(self):
        # Este método deve ser implementado pelas subclasses para lidar com a seleção de opções
        raise NotImplementedError("Subclasses devem implementar _select_option")

    def update(self):
        for btn in self._buttons:
            btn.update()

    def render(self, screen):
        screen.fill((255, 255, 255))

        for btn in self._buttons:
            btn.render(screen)