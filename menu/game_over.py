import pygame as pg
from core import State, GameState, BaseMenu, FontManager


class GameOverMenu(BaseMenu):
    def __init__(self, game_state: GameState, scene):
        super().__init__(game_state)

        self.font_manager = FontManager()
        self.font_title = self.font_manager.load_font(None, 74)

        self._options = [
            ("TENTAR NOVAMENTE", self.__retry_scene),
            ("MENU PRINCIPAL", self.__return_to_menu),
        ]
        self._create_buttons()

        # Atualiza os scores salvos
        self.scene = scene
        self.score_manager = self.scene.score_manager
        self.score = self.score_manager.get_score()
        self.score_manager.check_high_score()

    def _select_option(self):
        if self._buttons:
            self._current_button.callback()

    def __retry_scene(self):
        self._game_state.change_state(State.PLAYING, self.scene.config["scene_name"])

    def __return_to_menu(self):
        self._game_state.change_state(State.MAIN_MENU)

    def update(self, delta_time=None):
        super().update()  # Chama o update da classe base

    def render(self, screen):
        super().render(screen)

        title = self.font_title.render("GAME OVER", True, (0, 0, 0))
        screen.blit(title, title.get_rect(center=(screen.get_width() // 2, 80)))

        score = self.small_font.render(f"DISTANCIA: {self.score} m", True, (0, 0, 0))
        screen.blit(score, score.get_rect(center=(screen.get_width() // 2, 150)))
