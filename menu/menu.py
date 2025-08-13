import pygame as pg
from core import State, GameState, BaseMenu, FontManager


class MainMenu(BaseMenu):
    def __init__(self, game_state: GameState):
        super().__init__(game_state)

        self.font_manager = FontManager()
        self.font_title = self.font_manager.load_font(None, 74)

        self._options = [
            ("JOGAR", self.__select_scene),
            ("SCORES", self.__view_high_scores),
            ("SAIR", self.__end_game),
        ]
        self._create_buttons()

    def _select_option(self):
        if self._buttons:
            self._current_button.callback()

    def __select_scene(self):
        self._game_state.change_state(State.SCENE_SELECT)

    def __view_high_scores(self):
        self._game_state.change_state(State.HIGH_SCORES)

    def __end_game(self):
        self._game_state.change_state(State.FINISH)

    def handle_event(self, event: pg.event.Event):
        super().handle_event(event)  # Chama o handle_event da classe base

    def update(self, delta_time=None):
        super().update()  # Chama o update da classe base

    def render(self, screen: pg.Surface):
        super().render(screen)  # Chama o render da classe base para o fundo e botões

        # Título do jogo
        title = self.font_title.render("FLAPPY PANTANEIRO", True, (0, 0, 0))
        screen.blit(
            title,
            title.get_rect(center=(screen.get_width() // 2, screen.get_width() // 8)),
        )
