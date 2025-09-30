import pygame as pg
from enum import Enum


class State(Enum):
    """Estados possíveis do jogo"""

    MAIN_MENU = 0
    SCENE_SELECT = 1
    PLAYING = 2
    PAUSE = 3
    GAME_OVER = 4
    HIGH_SCORES = 5
    FINISH = 6


class GameState:
    """Gerencia os diferentes estados do jogo"""

    def __init__(self, screen: pg.Surface):
        """
        Inicializa o gerenciador de estados.

        Args:
            screen (pygame.Surface): Superfície principal do jogo
        """
        self.screen = screen
        self.current_state = State.MAIN_MENU
        self.current_scene = None
        # Tempo entre dois frames (em s); Para deixar o jogo mais suave
        self.delta_time = 0
        # Tempo do frame anterior (em s)
        self.last_time = pg.time.get_ticks() / 1000.0

        # Importações tardias para evitar importação circular
        from menu import MainMenu

        self.main_menu = MainMenu(self)  # Não passa background_image_path por enquanto
        self.scene_select_menu = None
        self.pause_menu = None
        self.game_over_menu = None
        self.high_scores_menu = None

    def handle_event(self, event: pg.event.Event):
        """
        Processa eventos do Pygame.

        Args:
            event (pygame.event.Event): Evento a ser processado
        """
        if event.type == pg.QUIT or self.current_state == State.FINISH:
            return False
        elif self.current_state == State.MAIN_MENU:
            self.main_menu.handle_event(event)
        elif self.current_state == State.SCENE_SELECT:
            if self.scene_select_menu:
                self.scene_select_menu.handle_event(event)
        elif self.current_state == State.PLAYING:
            if self.current_scene:
                self.current_scene.handle_event(event)
        elif self.current_state == State.PAUSE:
            if self.pause_menu:
                self.pause_menu.handle_event(event)
        elif self.current_state == State.GAME_OVER:
            if self.game_over_menu:
                self.game_over_menu.handle_event(event)
        elif self.current_state == State.HIGH_SCORES:
            if self.high_scores_menu:
                self.high_scores_menu.handle_event(event)

        return True

    def load_scene(self, scene_key: str):
        if scene_key == "Demo":
            from scenes.demo import DemoScene

            return DemoScene(self)
        elif scene_key == "forest":
             from scenes.forest import ForestScene
             return ForestScene(self)
        # elif scene_key == "sky":
        #     from sky_scene import SkyScene
        #     return SkyScene(self)
        # elif scene_key == "water":
        #     from scenes.water import WaterScene

        #     return WaterScene(self)

        return None

    def change_state(self, new_state, scene_key=""):
        """
        Muda o estado atual do jogo.

        Args:
            new_state (State): Novo estado
            scene (str, optional): Nome do cenário (para o estado PLAYING)
        """
        if new_state == State.PLAYING:
            if self.current_state != State.PAUSE:
                self.current_scene = self.load_scene(scene_key)
        elif new_state == State.SCENE_SELECT:
            from menu import SceneSelectMenu  # Importa SceneSelectMenu

            # Não passa background_image_path por enquanto
            self.scene_select_menu = SceneSelectMenu(self)

        elif new_state == State.PAUSE:
            from menu import PauseMenu

            # Não passa background_image_path por enquanto
            self.pause_menu = PauseMenu(self)

        elif new_state == State.GAME_OVER:
            from menu import GameOverMenu

            # Não passa background_image_path por enquanto
            self.game_over_menu = GameOverMenu(self, self.current_scene)

        elif new_state == State.HIGH_SCORES:
            from menu import HighScoresMenu  # Importa HighScoresMenu

            # Não passa background_image_path por enquanto
            self.high_scores_menu = HighScoresMenu(self)

        # Atualizar o novo estado do jogo
        self.current_state = new_state

    def update(self):
        """Atualiza o estado atual do jogo."""
        # Calcular delta time
        current_time = pg.time.get_ticks() / 1000.0
        self.delta_time = current_time - self.last_time  # Converter para segundos
        self.last_time = current_time

        if self.current_state == State.MAIN_MENU:
            self.main_menu.update(self.delta_time)
        elif self.current_state == State.SCENE_SELECT:
            if self.scene_select_menu:
                self.scene_select_menu.update(self.delta_time)
        elif self.current_state == State.PLAYING:
            if self.current_scene:
                self.current_scene.update(self.delta_time)
        elif self.current_state == State.PAUSE:
            if self.pause_menu:
                self.pause_menu.update(self.delta_time)
        elif self.current_state == State.GAME_OVER:
            if self.game_over_menu:
                self.game_over_menu.update(self.delta_time)
        elif self.current_state == State.HIGH_SCORES:
            if self.high_scores_menu:
                self.high_scores_menu.update(self.delta_time)

    def render(self, screen: pg.Surface):
        """
        Renderiza o estado atual do jogo.

        Args:
            screen (pygame.Surface): Superfície onde renderizar
        """
        if self.current_state == State.MAIN_MENU:
            self.main_menu.render(screen)
        elif self.current_state == State.SCENE_SELECT:
            if self.scene_select_menu:
                self.scene_select_menu.render(screen)
        elif self.current_state == State.PLAYING:
            if self.current_scene:
                self.current_scene.render(screen)
        elif self.current_state == State.PAUSE:
            if self.pause_menu:
                self.pause_menu.render(screen)
        elif self.current_state == State.GAME_OVER:
            if self.game_over_menu:
                self.game_over_menu.render(screen)
        elif self.current_state == State.HIGH_SCORES:
            if self.high_scores_menu:
                self.high_scores_menu.render(screen)
