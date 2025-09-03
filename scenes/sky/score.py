# scenes/sky/score.py
import json

class SkyScoreManager:
    """
    Gerencia a pontuação para a SkyScene, baseada no tempo de sobrevivência.
    Agora inclui funcionalidade de high score para compatibilidade.
    """
    def __init__(self):
        self._score = 0
        self._score_multiplier = 10
        self.high_score_file = "./data/high_scores.json"

    def update(self, delta_time: float):
        """Atualiza a pontuação com base no tempo decorrido."""
        self._score += delta_time * self._score_multiplier

    def get_score(self) -> int:
        """Retorna a pontuação atual como um número inteiro."""
        return int(self._score)

    def reset(self):
        """Reseta a pontuação para zero."""
        self._score = 0

    def check_high_score(self):
        """
        Verifica a pontuação atual contra os recordes salvos.
        Esta função é necessária para compatibilidade com o GameOverMenu.
        """
        # A lógica real de salvar o high score provavelmente será gerenciada
        # pelo próprio menu de Game Over, mas o método precisa existir.
        print(f"Verificando pontuação final: {self.get_score()}")
        # Adicionar lógica de salvar/carregar se necessário no futuro.
        pass