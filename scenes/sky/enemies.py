import pygame as pg
import random
from core import Entity, EntityFactory
from config import SCREEN_WIDTH, SCREEN_HEIGHT
from .player import SkyPlayer
from .projectiles import Projectile


class Enemy(Entity):
    """
    Classe base para todos os inimigos que perseguem o jogador.
    """

    def __init__(self, enemy_cfg: dict, x: int, y: int, player_ref: SkyPlayer):
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


class ChaserDrone(Enemy):
    """
    Um drone rápido que prioriza a perseguição horizontal, mas se desvia
    levemente na vertical em direção ao jogador.
    """

    def __init__(self, cfg, player_ref):
        start_y = random.randint(50, SCREEN_HEIGHT - 50)
        super().__init__(
            cfg["chaser_drone_cfg"], SCREEN_WIDTH + 50, start_y, player_ref
        )
        self.speed = 200
        self.disengage_distance = 250

        self.vertical_strength = 0.8

        # Atributos para a perseguição "lenta para reagir"
        self._target_direction = pg.math.Vector2(-1, 0)
        self._update_target_timer = 0.0
        self.reaction_time = 0.2

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


class EnemySpawner:
    """
    Gerencia a criação e o timing de spawn dos inimigos da DemoScene.
    """

    def __init__(self, enemies_cfg: dict):
        self._config = enemies_cfg
        self._factory = EntityFactory()
        self._timer = (
            5.0  # Começa com um delay para não aparecer inimigos imediatamente
        )

        self._factory.register(ChaserDrone, weight=60)

    def update(
        self, delta_time: float, current_speed: float, player_ref, allow_drones: bool = False
    ) -> Enemy | None:
        """
        Verifica se é hora de gerar um novo inimigo.
        """
        self._timer += delta_time
        spawn_interval = max(2.0, 8.0 - (current_speed / 100))

        if self._timer >= spawn_interval:
            self._timer = 0
            # Passa a configuração E a referência do jogador para o inimigo ser criado
            enemy = self._factory.create_random(self._config, player_ref=player_ref)
            # Bloqueia drones se boss ainda não apareceu
            if isinstance(enemy, ChaserDrone) and not allow_drones:
                return None
            return enemy

        return None


class JacareWarning:
    """
    Bolinha verde de aviso que aparece quando o player se aproxima da borda.
    """
    def __init__(self):
        self.visible = False
        self.radius = 8
        self.color = (0, 255, 0)
        self.x = SCREEN_WIDTH - 20
        self.y = SCREEN_HEIGHT - 50
        
    def update(self, player_y):
        warning_threshold = SCREEN_HEIGHT - 150
        
        if player_y >= warning_threshold:
            self.visible = True
            # A bolinha segue a posição Y do player
            self.y = min(player_y, SCREEN_HEIGHT - 20)
        else:
            self.visible = False
            
    def render(self, screen):
        if self.visible:
            pg.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)


class Jacare(Entity):
    """
    Jacaré que sobe de baixo da tela quando o player toca a borda inferior.
    """
    
    def __init__(self, cfg, player_ref):
        # Começa escondido abaixo da tela, mais à direita do player
        start_x = player_ref.position.x + 60  # 40 pixels à direita
        start_y = SCREEN_HEIGHT + 150
        
        # Chama o construtor da Entity corretamente
        super().__init__(cfg["jacare_cfg"], start_x, start_y)
        
        self.player = player_ref
        self._position = pg.math.Vector2(start_x, start_y)
        self.target_y = SCREEN_HEIGHT - 30
        self.speed = 200
        self.state = "rising"
        self.attack_timer = 0
        self.mouth_opened = False  # Controla se a boca já abriu
        
        # Atualiza a posição inicial do rect
        self.rect.center = (int(self._position.x), int(self._position.y))
        
    def update(self, delta_time: float):
        if self.state == "rising":
            # Sobe até a posição alvo
            self._position.y -= self.speed * delta_time
            
            if self._position.y <= self.target_y:
                self._position.y = self.target_y
                self.state = "waiting"
                self.attack_timer = 0
                
        elif self.state == "waiting":
            self.attack_timer += delta_time
            if self.attack_timer >= 1.0:  # Espera 1 segundo
                self.state = "attacking"
                self.attack_timer = 0
                
        elif self.state == "attacking":
            if not self.mouth_opened:
                # Para a animação em um frame específico (boca aberta)
                self._current_frame = 4
                self._animation_finished = True
                self.mouth_opened = True
            
            # Mantém o player SEMPRE na posição da boca durante todo o ataque
            self.player._SkyPlayer__position.x = self._position.x - 60  # Negativo para ir à esquerda
            self.player._SkyPlayer__position.y = self._position.y  # Ajusta para ficar mais na boca
                
            self.attack_timer += delta_time
            if self.attack_timer >= 2.0:  # Mantém por 2 segundos
                self.player.die()
                self.state = "finished"
        
        # Atualiza posição do rect
        self.rect.center = (int(self._position.x), int(self._position.y))
        
        # Só chama super().update() se a animação não estiver pausada
        if not self.mouth_opened:
            super().update(delta_time)

class FlyBoss(Entity):
    def __init__(self, cfg, player_ref):
        super().__init__(cfg["fly_boss_cfg"], SCREEN_WIDTH + 150, 150)

        self.player = player_ref
        self._position = pg.math.Vector2(SCREEN_WIDTH + 150, 150)  # Começa fora da tela
        self._original_x = SCREEN_WIDTH - 100  # Posição final
        self.entering = True  # Flag para entrada
        self.speed = 100
        self.state = "idle"
        self.attack_timer = 0
        self.attack_cooldown = 8.0
        self.move_direction = 1
        self.config = cfg
        self.is_charging = False
        self.telegraph_timer = 0
        self.telegraph_duration = 1.0
        self.is_telegraphing = False
        self.charge_direction = None  # Direção fixa do ataque
        self.battle_duration = 30.0  # Boss fica 20 segundos na tela
        self.battle_timer = 0
        self.leaving = False
        self.charge_start_pos = None

        self.shoot_timer = 0
        self.shoot_interval = 2.0 
        
        if hasattr(self, 'image'):
            self.image = pg.transform.flip(self.image, True, False)
            self.mask = pg.mask.from_surface(self.image)
        
        self.rect.center = self._position
    
    def update(self, delta_time):
        # Entrada suave do boss
        if self.entering:
            self._position.x -= 200 * delta_time  # Move para esquerda
            if self._position.x <= self._original_x:
                self._position.x = self._original_x
                self.entering = False
            # Não faz outras ações durante entrada
            self.rect.center = (int(self._position.x), int(self._position.y))
            super().update(delta_time)
            return None
        
        # Contador de tempo de batalha
        if not self.entering and not self.leaving:
            self.battle_timer += delta_time
            if self.battle_timer >= self.battle_duration:
                self.leaving = True

        # Boss saindo da tela
        if self.leaving:
            self._position.x += 250 * delta_time  # Sai pela direita
            if self._position.x > SCREEN_WIDTH + 200:
                self.kill()  # Remove o boss
            self.rect.center = (int(self._position.x), int(self._position.y))
            super().update(delta_time)
            return None
        
        # Movimento vertical normal
        if not self.is_charging:
            self._position.y += self.move_direction * self.speed * delta_time
            
            if self._position.y <= 100:
                self.move_direction = 1
            elif self._position.y >= SCREEN_HEIGHT - 200:
                self.move_direction = -1
            
            # Retorna suavemente para posição X original
            if self._position.x < self._original_x:
                self._position.x += 150 * delta_time
                if self._position.x > self._original_x:
                    self._position.x = self._original_x
        
        # Sistema de ataque com telegrafação
        self.attack_timer += delta_time

        # Inicia telegrafação
        if self.attack_timer >= self.attack_cooldown and not self.is_telegraphing and not self.is_charging:
            self.is_telegraphing = True
            self.telegraph_timer = 0
            self.attack_timer = 0
            
            # CALCULA E TRAVA a direção do ataque AGORA
            target = pg.math.Vector2(self.player.position.x, self.player.position.y)
            self.charge_direction = target - self._position
            if self.charge_direction.length() > 0:
                self.charge_direction.normalize_ip()

        # Conta tempo de telegrafação
        if self.is_telegraphing:
            self.telegraph_timer += delta_time
            if self.telegraph_timer >= self.telegraph_duration:
                self.is_telegraphing = False
                self.is_charging = True
                self.charge_start_pos = self._position.copy()

        if self.is_charging:
            # Investida em linha reta na direção TRAVADA
            self._position += self.charge_direction * 450 * delta_time  # Mais rápido mas previsível
            
            # Para quando sair da tela ou ir muito longe
            if (self._position.x < -100 or self._position.x > SCREEN_WIDTH + 100 or
                self._position.y < -100 or self._position.y > SCREEN_HEIGHT + 100):
                self.is_charging = False
        
        # Retorna suavemente após ataque
        if not self.is_charging and not self.is_telegraphing and self._position.x != self._original_x:
            # Move de volta para posição original
            diff = self._original_x - self._position.x
            if abs(diff) > 5:
                self._position.x += (diff / abs(diff)) * 150 * delta_time
            else:
                self._position.x = self._original_x
            
            # Também corrige Y se necessário
            if self._position.y < 100:
                self._position.y = 100
            elif self._position.y > SCREEN_HEIGHT - 200:
                self._position.y = SCREEN_HEIGHT - 200
        
        # Sistema de tiro
        self.shoot_timer += delta_time
        projectile = None
        
        if self.shoot_timer >= self.shoot_interval and not self.is_charging:
            self.shoot_timer = 0
            projectile = self._shoot_at_player()
        
        self.rect.center = (int(self._position.x), int(self._position.y))
        super().update(delta_time)
        
        # Flip da sprite
        if hasattr(self, '_animations') and self._current_animation:
            anim_data = self._animations[self._current_animation]
            if anim_data["frames"]:
                self.image = pg.transform.flip(anim_data["frames"][self._current_frame], True, False)
                self.mask = pg.mask.from_surface(self.image)
        
        return projectile

    def _shoot_at_player(self):
            """
            Cria e retorna um projétil direcionado à posição atual do jogador.
            """
            # Calcula o vetor de direção do chefe para o jogador
            direction = self.player.position - self._position
            if direction.length() > 0:
                direction.normalize_ip()  # Normaliza o vetor para ter comprimento 1

            # Cria a instância do projétil, passando os parâmetros necessários
            # (Estou assumindo que o projétil precisa de uma config, posição e direção)
            projectile = Projectile(
                self.config["projectile_cfg"], # Configuração do projétil
                self._position.x,             # Posição X inicial
                self._position.y,             # Posição Y inicial
                direction                     # Direção do movimento
            )
            return projectile