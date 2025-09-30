import pygame as pg
import random
from core import Entity, EntityFactory
from config import SCREEN_WIDTH, SCREEN_HEIGHT
from .water_player import WaterPlayer


class WaterEnemy(Entity):
    """
    Classe base para todos os inimigos que perseguem o jogador.
    """

    def __init__(self, enemy_cfg: dict, x: int, y: int, player_ref: WaterPlayer):
        """
        Inicializa o inimigo. Requer uma referência ao jogador para saber quem seguir.
        """
        super().__init__(enemy_cfg, x, y)

        # A referência ao jogador é essencial para a lógica de perseguição
        self.player = player_ref

        self._position = pg.math.Vector2(x, y)
        self._velocity = pg.math.Vector2(1, 1)

        self._is_homing = True

        self.rect.center = (int(self._position.x), int(self._position.y))

    def update(self, delta_time: float):
        """
        Aplica o movimento e remove o inimigo se ele sair muito da tela.
        A lógica de como calcular a velocidade é deixada para as subclasses.
        """
        super().update(delta_time)

        self._position += self._velocity * delta_time
        self.rect.center = (int(self._position.x), int(self._position.y))

        # Remove o inimigo se ele sair da tela pela esquerda
        if self.rect.right < 0:
            self.kill()


class Anzol(WaterEnemy):
    """
    Um drone rápido que prioriza a perseguição horizontal, mas se desvia
    levemente na vertical em direção ao jogador.
    """

    def __init__(self, cfg, player_ref):
        start_y = random.randint(50, SCREEN_HEIGHT - 50)
        super().__init__(
            cfg["anzol_cfg"], SCREEN_WIDTH + 50, start_y, player_ref
        )
        self.speed = 250
        self.disengage_distance = 250

        self.vertical_strength = 0.8

        # Atributos para a perseguição "lenta para reagir"
        self._target_direction = pg.math.Vector2(-1, 0)
        self._update_target_timer = 0.0
        self.reaction_time = 0.3

    def update(self, delta_time: float):
        if self._is_homing:
            distance = self._position.distance_to(self.player.position)
            if distance < self.disengage_distance:
                self._is_homing = False
                self.speed *= 1.25

            self._update_target_timer += delta_time
            if self._update_target_timer >= self.reaction_time:
                self._update_target_timer = 0

                # 1. Calcula o vetor de direção completo (X e Y).
                direction = self.player.position - self._position

                # 2. Reduz a força da componente vertical.
                direction.y *= self.vertical_strength

                # 3. Normaliza o vetor modificado para obter a direção final.
                if direction.length() > 0:
                    self._target_direction = direction.normalize()

        # O drone sempre se move na última direção calculada
        self._velocity = self._target_direction * self.speed

        super().update(delta_time)


class HomingMissile(WaterEnemy):
    """
    Um míssil rápido que persegue o jogador em ambos os eixos,
    mas com uma capacidade de virada vertical muito reduzida.
    """

    def __init__(self, cfg, player_ref):
        start_y = random.randint(50, SCREEN_HEIGHT - 50)
        super().__init__(
            cfg["homing_missile_cfg"], SCREEN_WIDTH + 50, start_y, player_ref
        )

        self.speed = 120
        self.acceleration = 75
        self.turn_speed = 2.0
        self._lifetime = 8.0
        self.disengage_distance = 350

        self.vertical_strength = 0.25

    def update(self, delta_time: float):
        self._lifetime -= delta_time
        if self._lifetime <= 0:
            self.kill()
            return

        # A lógica de perseguição só acontece se o míssil ainda estiver no modo "homing"
        if self._is_homing:
            distance = self._position.distance_to(self.player.position)
            if distance < self.disengage_distance:
                self._is_homing = False
                self.acceleration *= 3

            self.speed += self.acceleration * delta_time

            # 1. Calcula a direção ideal completa (X e Y).
            target_direction = self.player.position - self._position

            # 2. Amortece o componente Y do vetor alvo.
            target_direction.y *= self.vertical_strength

            if target_direction.length() > 0:
                target_direction.normalize_ip()

                # 3. A lógica de interpolação (lerp) agora usa este vetor "amortecido"
                current_direction = self._velocity.normalize()
                new_direction = current_direction.lerp(
                    target_direction, self.turn_speed * delta_time
                )
                self._velocity = new_direction * self.speed
        else:
            # Se não está mais em modo homing, apenas continua acelerando
            self.speed += self.acceleration * delta_time
            self._velocity = self._velocity.normalize() * self.speed

        super().update(delta_time)


class WaterEnemySpawner:
    """
    Gerencia a criação e o timing de spawn dos inimigos da DemoScene.
    """

    def __init__(self, enemies_cfg: dict):
        self._config = enemies_cfg
        self._factory = EntityFactory()
        self._timer = (
            5.0  # Começa com um delay para não aparecer inimigos imediatamente
        )

        self._factory.register(Anzol, weight=60)
        self._factory.register(HomingMissile, weight=40)

    def update(
        self, delta_time: float, current_speed: float, player_ref
    ) -> WaterEnemy | None:
        """
        Verifica se é hora de gerar um novo inimigo.
        """
        self._timer += delta_time
        spawn_interval = max(2.0, 8.0 - (current_speed / 100))

        if self._timer >= spawn_interval:
            self._timer = 0
            # Passa a configuração E a referência do jogador para o inimigo ser criado
            return self._factory.create_random(self._config, player_ref=player_ref)

        return None
