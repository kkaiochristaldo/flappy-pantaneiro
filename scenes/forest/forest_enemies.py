import pygame as pg
import random
from core import Entity, EntityFactory
from config import SCREEN_WIDTH, SCREEN_HEIGHT
from .forest_player import ForestPlayer


class ForestEnemies(Entity):
    """
    Classe base para todos os inimigos que perseguem o jogador.
    """

    def __init__(self, enemy_cfg: dict, x: int, y: int, player_ref: ForestPlayer):
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

class Cobra(ForestEnemies):
    """
    Cobra que spawna no topo e cai na diagonal tentando acertar o jogador.
    """

    def __init__(self, cfg, player_ref):
        # Posição inicial
        start_x = random.randint(350, SCREEN_WIDTH - 50)  
        start_y = random.randint(0, 50)  # no topo da tela
        super().__init__(cfg["cobra_cfg"], start_x, start_y, player_ref)

        # Velocidade
        self.speed =  150 # Pode ajustar conforme desejar

        # Calcula direção diagonal para tentar atingir o jogador
        target_pos = player_ref.position
        direction = pg.math.Vector2(target_pos.x - self._position.x, target_pos.y - self._position.y)
        if direction.length() > 0:
            direction = direction.normalize()
        self._velocity = direction * self.speed

        self.sound_cobra = pg.mixer.Sound("songs/forest/cobra.mp3")  # Carrega o som da cobra
        self.sound_cobra.play()  # toca o som da cobra ao spawnar

    def update(self, delta_time: float):
        # Apenas move na direção definida
        super().update(delta_time)

        # Remover se sair da tela
        if self._position.x < -50 or self._position.y > SCREEN_HEIGHT + 50:
            self.kill()

        super().update(delta_time)

class Javali(ForestEnemies):
    GRAVITY = 750
    JUMP_VELOCITY = -450
    GROUND_Y = SCREEN_HEIGHT - 25

    def __init__(self, cfg, player_ref):
        start_x = SCREEN_WIDTH + 50
        start_y = self.GROUND_Y
        super().__init__(cfg["javali_cfg"], start_x, start_y, player_ref)

        # Javali controla sua posição
        self.allow_parent_movement = False

        self.speed = 150
        self._velocity = pg.math.Vector2(-self.speed, 0)

        # Tempo de corrida antes do pulo
        self.run_time = 0.0
        self.wait_time_before_jump = 1.0

        self.is_jumping = False
        self.has_jumped = False  # garante que pule apenas uma vez

        self._position = pg.math.Vector2(start_x, start_y)
        self.rect.midbottom = (int(self._position.x), int(self._position.y))

        self.set_animation("run")

        self.sound_javali = pg.mixer.Sound("songs/forest/javali.mp3")  # Carrega o som do javali

    def update(self, delta_time: float):
        # Avança animações (Entity.update)
        super().update(delta_time)

        # Corrida constante para a esquerda
        self._velocity.x = -self.speed

        # Contagem do tempo de corrida
        self.run_time += delta_time

        # Pulo único quando estiver perto do jogador e já passou do tempo mínimo
        if not self.has_jumped and self.run_time >= self.wait_time_before_jump:
            # Calcula distância horizontal usando rect do jogador
            player_x = self.player.rect.centerx
            dist_to_player = abs(self._position.x - player_x)

            if dist_to_player < 200:  # ajuste o limiar de proximidade
                self._velocity.y = self.JUMP_VELOCITY
                self.is_jumping = True
                self.has_jumped = True
                self.sound_javali.play()  # toca o som do javali ao pular
                self.set_animation("jump")

        # Aplica gravidade se estiver no ar
        if self.is_jumping or self._velocity.y != 0:
            self._velocity.y += self.GRAVITY * delta_time

        # Atualiza posição
        self._position += self._velocity * delta_time

        # Colisão com o chão
        if self._position.y >= self.GROUND_Y:
            self._position.y = self.GROUND_Y
            self._velocity.y = 0
            if self.is_jumping:
                self.is_jumping = False
                self.set_animation("run")

        # Atualiza rect para desenhar corretamente
        self.rect.midbottom = (int(self._position.x), int(self._position.y))

        # Remove se sair da tela
        if self.rect.right < 0:
            self.kill()

class Mosquito(ForestEnemies):
    """
    Um mosquito da dengue que prioriza a perseguição horizontal, mas se desvia
    levemente na vertical em direção ao jogador.
    """

    def __init__(self, cfg, player_ref):
        start_y = random.randint(50, SCREEN_HEIGHT - 50)
        super().__init__(
            cfg["mosquito_cfg"], SCREEN_WIDTH + 50, start_y, player_ref
        )
        self.speed = 250
        self.disengage_distance = 250

        self.vertical_strength = 0.8

        # Atributos para a perseguição "lenta para reagir"
        self._target_direction = pg.math.Vector2(-1, 0)
        self._update_target_timer = 0.0
        self.reaction_time = 0.3

        self.sound_mosquito = pg.mixer.Sound("songs/forest/mosquito.mp3")  # Carrega o som do mosquito
        self.sound_mosquito.play()  # toca o som do mosquito ao spawnar
        
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

        # Remover se sair da tela
        if self._position.x < -50 or self._position.y > SCREEN_HEIGHT + 50:
            self.kill()

        super().update(delta_time)

class ForestEnemySpawner:
    """
    Gerencia a criação e o timing de spawn dos inimigos da ForestScene.
    """

    def __init__(self, enemies_cfg: dict):
        self._config = enemies_cfg
        self._factory = EntityFactory()
        self._timer = (
            5.0  # Começa com um delay para não aparecer inimigos imediatamente
        )
 
        self._factory.register(Cobra, weight=60)  
        self._factory.register(Javali, weight=60)
        self._factory.register(Mosquito, weight=60)

    def update(
        self, delta_time: float, current_speed: float, player_ref
    ) -> ForestEnemies | None:
        """
        Verifica se é hora de gerar um novo inimigo.
        """
        self._timer += delta_time
        spawn_interval = max(2.0, 5.0 - (current_speed / 60))

        if self._timer >= spawn_interval:
            self._timer = 0
            # Passa a configuração E a referência do jogador para o inimigo ser criado
            return self._factory.create_random(self._config, player_ref=player_ref)

        return None
