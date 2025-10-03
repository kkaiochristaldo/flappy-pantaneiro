import pygame as pg
from core import State, GameState, ScoreManager, FontManager, BaseMenu

# =========== adicionado para joystick
pg.joystick.init()

if pg.joystick.get_count() > 0:
    joystick = pg.joystick.Joystick(0)
    joystick.init()
else:
    joystick = None
# ====================================

class HighScoresMenu(BaseMenu):
    def __init__(self, game_state: GameState):
        super().__init__(game_state)

        self.font_manager = FontManager()
        self.font_score = self.font_manager.load_font(None, 45)
        self.font_hint = self.font_manager.load_font(None, 40)
        self.scores = ScoreManager().high_scores

        # Carregar fundo do HighScores (apenas uma imagem estática)
        self.background = pg.image.load("assets/images/menus/Scores/fundo_scores_sheet.png").convert_alpha()
        self.background_rect = self.background.get_rect(center=(
            self._game_state.screen.get_width() // 2,
            self._game_state.screen.get_height() // 2
        ))

                # --- Controle de música ---
        # salvar posição da trilha sonora antes de pausar
        self.sound_selected = pg.mixer.Sound("songs/menus/selected.mp3")  # Pré carrega o som de efeito selecionado
        self.music_pos = pg.mixer.music.get_pos() / 1000.0  # posição em segundos
        pg.mixer.music.pause()
        # tocar música calma em loop infinito
        pg.mixer.music.load("songs/menus/scores.mp3")
        pg.mixer.music.play(loops=-1)

    def handle_event(self, event: pg.event.Event):
        if event.type == pg.KEYDOWN or (joystick is not None and event.type == pg.JOYBUTTONDOWN):
            # pausa ou para a música do score
            pg.mixer.music.stop()

            # toca o som de seleção primeiro
            self.sound_selected.play()

            # restaura a trilha principal
            pg.mixer.music.load("songs/menus/trilha_sonora.mp3")
            pg.mixer.music.play(loops=-1, start=self.music_pos)

            # muda o estado
            self._game_state.change_state(State.MAIN_MENU)

    def update(self, delta_time=None):
        pass

    def render(self, screen: pg.Surface):
        # Renderiza fundo
        screen.blit(self.background, self.background_rect)

        # Renderiza os scores
        if not self.scores:
            msg = self.font_score.render("SEM PONTUAÇÕES SALVAS", True, (255, 200, 0))
            screen.blit(msg, msg.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2)))
        else:
            num_cols = len(self.scores)
            column_width = screen.get_width() // max(1, num_cols)
            start_y = 200
            box_width = column_width - 20
            box_height = 200

            for idx, (scene, scores) in enumerate(sorted(self.scores.items())):
                x = idx * column_width + 10
                y = start_y + 20

                # Caixa ao redor
                pg.draw.rect(screen, (255, 200, 0), (x, y, box_width, box_height), 2)

                # Nome do cenário
                scene_title = self.font_score.render(scene.upper(), True, (255, 200, 0))
                screen.blit(scene_title, (x + 10, y + 10))

                # Lista de scores
                for i, score in enumerate(scores[:5]):
                    score_text = self.font_score.render(f"{i+1}) {score}m", True, (255, 200, 0))
                    screen.blit(score_text, (x + 10, y + 40 + i * 30))

        # Hint para voltar
        hint = self.font_hint.render("Pressione X para voltar", True, (255, 200, 0))
        screen.blit(hint, hint.get_rect(center=(screen.get_width() // 2, screen.get_height() - 140)))
