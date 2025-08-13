import json
import os


class ScoreManager:
    """Gerencia a pontuação do jogador baseada em distância."""

    def __init__(self, scene_data: dict = {}):
        """Inicializa o gerenciador de pontuação."""
        self.scene_name = scene_data.get("scene_name")
        self.distance = 0  # Distância em "metros"
        self.pixels_per_meter = 100  # 100px = 1m
        self.score_per_meter = 1  # 1 scores por metro
        self.high_scores = {}
        self.load_high_scores()

    def update(self, delta_time, speed):
        """Atualiza a distância percorrida.

        Args:
            delta_time (float): Tempo desde o último frame em segundos
            speed (float): Velocidade atual do jogo
        """
        # Calcular distância percorrida neste frame
        distance_this_frame = (speed * delta_time) / self.pixels_per_meter
        self.distance += distance_this_frame

    def get_score(self):
        """Retorna a pontuação atual baseada na distância.

        Returns:
            int: Pontuação atual arredondada
        """
        return int(self.distance * self.score_per_meter)

    def get_distance(self):
        """Retorna a distância percorrida em metros.z

        Returns:
            int: Distância em metros
        """
        return int(self.distance)

    def reset(self):
        """Reinicia a pontuação."""
        self.distance = 0

    def check_high_score(self):
        """Verifica se a pontuação atual é um novo recorde.

        Returns:
            bool: True se for um novo recorde, False caso contrário
        """
        if self.scene_name not in self.high_scores:
            self.high_scores[self.scene_name] = []

        scene_scores = self.high_scores[self.scene_name]

        if not scene_scores or self.get_score() > max(scene_scores):
            scene_scores.append(self.get_score())
            scene_scores.sort(reverse=True)
            self.high_scores[self.scene_name] = scene_scores[:5]  # Top 5
            self.save_high_scores()
            return True

        return False

    def load_high_scores(self):
        """Carrega as pontuações máximas do arquivo."""
        file_path = os.path.join("data", "high_scores.json")

        try:
            if os.path.exists(file_path):
                with open(file_path, "r") as file:
                    self.high_scores = json.load(file)
        except Exception as e:
            print(f"Erro ao carregar pontuações: {e}")
            self.high_scores = {}

    def save_high_scores(self):
        """Salva as pontuações máximas no arquivo."""
        file_path = os.path.join("data", "high_scores.json")

        # Garantir que o diretório existe
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        try:
            with open(file_path, "w") as file:
                json.dump(self.high_scores, file, indent=4)
        except Exception as e:
            print(f"Erro ao salvar pontuações: {e}")
