import pygame as pg
from core import State, GameState, BaseMenu, FontManager

# =========== adicionado para joystick

pg.joystick.init()

joystick = pg.joystick.Joystick(0)
joystick.init()

# ======================================

class SceneSelectMenu(BaseMenu):
    def __init__(self, game_state: GameState):
        super().__init__(game_state)

        self.font_manager = FontManager()
        self.font_title = self.font_manager.load_font(None, 74)
        self.small_font = self.font_manager.load_font(None, 50)

        self._options = [
            ("demo", self.__play_demo)
            # ("forest", self.__play_forest_scene),
            # ("sky", self.__play_sky_scene),
            # ("water", self.__play_water_scene),
        ]
        self._create_buttons()

    def handle_event(self, event):
        super().handle_event(event)  # Chama o handle_event da classe base
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                self._game_state.change_state(State.MAIN_MENU)
        
        # =========== adicionado para joystick

        if (event.type == pg.JOYBUTTONDOWN):
            if (event.button == 4):
                self._game_state.change_state(State.MAIN_MENU)
        
        # =========================================

    def _select_option(self):
        if self._buttons:
            self._current_button.callback()

    def __play_demo(self):
        self._game_state.change_state(State.PLAYING, "Demo")

    def __play_forest_scene(self):
        self._game_state.change_state(State.PLAYING, "forest")

    def __play_sky_scene(self):
        self._game_state.change_state(State.PLAYING, "sky")

    def __play_water_scene(self):
        self._game_state.change_state(State.PLAYING, "water")

    def update(self, delta_time=None):
        super().update()  # Chama o update da classe base

    def render(self, screen):
        super().render(screen)  # Chama o render da classe base para o fundo e botões

        title = self.font_title.render("SELECIONAR CENÁRIO", True, (0, 0, 0))
        screen.blit(
            title,
            title.get_rect(center=(screen.get_width() // 2, screen.get_width() // 8)),
        )
