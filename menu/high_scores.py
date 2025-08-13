import pygame as pg
from core import State, GameState, ScoreManager, FontManager, BaseMenu


class HighScoresMenu(BaseMenu):
    def __init__(self, game_state: GameState):
        super().__init__(game_state)

        self.font_manager = FontManager()
        self.font_title = self.font_manager.load_font(None, 60)
        self.font_score = self.font_manager.load_font(None, 30)
        self.font_hint = self.font_manager.load_font(None, 24)
        self.scores = ScoreManager().high_scores

    def handle_event(self, event: pg.event.Event):
        if event.type == pg.KEYDOWN:
            self._game_state.change_state(State.MAIN_MENU)

    def update(self, delta_time=None):
        pass

    def render(self, screen: pg.Surface):
        super().render(screen)  # Chama o render da classe base para o fundo

        title = self.font_title.render("TOP 5 SCORES", True, (0, 0, 0))
        screen.blit(
            title,
            title.get_rect(center=(screen.get_width() // 2, screen.get_width() // 8)),
        )

        if not self.scores:
            msg = self.font_score.render("SEM PONTUAÇÕES SALVAS", True, (0, 0, 0))
            screen.blit(
                msg,
                msg.get_rect(
                    center=(screen.get_width() // 2, screen.get_height() // 2)
                ),
            )
        else:
            num_cols = len(self.scores)
            column_width = screen.get_width() // max(1, num_cols)
            start_y = 200
            box_width = column_width - 20
            box_height = 200

            for idx, (scene, scores) in enumerate(sorted(self.scores.items())):
                x = idx * column_width + 10
                y = start_y

                # Caixa ao redor
                pg.draw.rect(screen, (128, 128, 128), (x, y, box_width, box_height), 2)

                # Nome do cenário
                scene_title = self.font_score.render(scene.upper(), True, (0, 0, 0))
                screen.blit(scene_title, (x + 10, y + 10))

                # Lista de scores
                for i, score in enumerate(scores[:5]):
                    score_text = self.font_score.render(
                        f"{i+1}) {score}m", True, (0, 0, 0)
                    )
                    screen.blit(score_text, (x + 10, y + 40 + i * 30))

        hint = self.font_hint.render(
            "Pressione qualquer tecla para voltar", True, (64, 64, 64)
        )
        screen.blit(
            hint,
            hint.get_rect(center=(screen.get_width() // 2, screen.get_height() - 40)),
        )
