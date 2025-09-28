import math
import random
import pygame as pg
from config import SCREEN_HEIGHT, SCREEN_WIDTH
from core import (
    State,
    GameState,
    ScoreManager,
    CollisionManager,
    ScrollerManager,
    BackgroundManager,
    load_json,
)
from .player import SkyPlayer
from .obstacles import ObstacleSpawner
from .enemies import EnemySpawner, JacareWarning, FlyBoss
from .collectibles import Coin
from .powerups import PowerUp
import random



class SkyScene:
    def __init__(self, game_state: GameState):
        self.game_state = game_state
        self.config = load_json("./config/sky.json")

        # Instanciar os gerenciadores
        self.scroll_manager = ScrollerManager(self.config["scroller_cfg"])
        self.background_manager = BackgroundManager(self.config["background_cfg"])
        self.score_manager = ScoreManager(self.config)
        self.collision_manager = CollisionManager()

        # Criar grupos de sprites
        self.all_sprites_group = pg.sprite.Group()
        self.obstacles_group = pg.sprite.Group()
        self.enemies_group = pg.sprite.Group()
        self.player_group = pg.sprite.GroupSingle()

        # Instanciar o jogador
        self.player = SkyPlayer(self.config["player_cfg"], invincible=False)
        if self.player:
            self.player_group.add(self.player)
            self.all_sprites_group.add(self.player)

        # Instanciar o spawner de obstáculos
        self.obstacle_spawner = ObstacleSpawner(self.config["obstacles_cfg"])

        # Instanciar o spawner de inimigos
        self.enemy_spawner = EnemySpawner(self.config["enemies_cfg"])

       # Instanciar o sistema de aviso e jacaré
        self.jacare_warning = JacareWarning()
        self.jacare = None
        self.jacare_spawned = False
        self.player_touched_bottom = False

        # Timer para game over após morte do jacaré
        self.death_timer = 0
        self.player_died = False

        # Sistema de coletáveis
        self.coins_group = pg.sprite.Group()
        self.powerups_group = pg.sprite.Group() 
        self.projectiles_group = pg.sprite.Group()
        self.coins_collected = 0
        self.coin_spawn_timer = 0
        self.powerup_spawn_timer = 0

        # Timers de spawn
        self.coin_spawn_interval = 4.0  # Moeda a cada 4 segundos
        self.powerup_spawn_interval = 15.0  # Power-up a cada 15 segundos

        # Boss battle system
        self.boss_timer = 0
        self.boss_interval = 30.0  # Boss a cada 30 segundos
        self.current_boss = None

    def handle_event(self, event: pg.event.Event):
        """Processa eventos do Pygame."""
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                self.game_state.change_state(State.PAUSE)
            elif not self.player.controls_locked:  # Só processa se controles não estão travados
                if event.key == pg.K_UP:
                    self.player.start_thrust()
                elif event.key == pg.K_DOWN:
                    self.player.start_dive()

        if event.type == pg.KEYUP and not self.player.controls_locked:  # Só processa se controles não estão travados
            if event.key == pg.K_UP:
                self.player.stop_thrust()
            elif event.key == pg.K_DOWN:
                self.player.stop_dive()

    def update(self, delta_time: float):
        """Atualiza o estado do cenário.

        Args:
            delta_time (float): Tempo desde o último frame em segundos
        """
        # Atualizar o scroller
        self.scroll_manager.update(delta_time)

        # Atualizar o background com base no scroller
        self.background_manager.update(self.scroll_manager.scroll_x)

        # Atualizar entidades (jogador, obstáculos e inimigos)
        self.player.update(delta_time)
        self.obstacles_group.update(delta_time)
        self.enemies_group.update(delta_time)

        # No método update, após atualizar enemies_group:
        for enemy in self.enemies_group:
            if isinstance(enemy, FlyBoss):
                projectile = enemy.update(delta_time)
                if projectile:
                    self.projectiles_group.add(projectile)
                    self.all_sprites_group.add(projectile)

        # Atualizar sistema de aviso do jacaré
        self.jacare_warning.update(self.player.position.y)

        # Verificar se player tocou a borda inferior
        if not self.player_touched_bottom and self.player.position.y >= SCREEN_HEIGHT - 10:
            self.__spawn_jacare_attack()
            self.player_touched_bottom = True

        # Atualizar jacaré se existir
        if self.jacare:
            self.jacare.update(delta_time)

            # Verificar se player morreu e dar delay para game over
        if not self.player._SkyPlayer__is_alive and not self.player_died:
            self.player_died = True
            self.death_timer = 0

        if self.player_died:
            self.death_timer += delta_time
            if self.death_timer >= 2.0:  # Espera 2 segundos após a morte
                self.game_state.change_state(State.GAME_OVER)

        # Verificar colisões (mas não com o jacaré especial)
        if not self.player.invincible and not self.player_touched_bottom:  # <- Adicione esta condição
            if self.collision_manager.check_collision(
                self.player_group, self.obstacles_group  # Player com obstáculos
            ) or self.collision_manager.check_collision(
                self.player_group, self.enemies_group  # Player com inimigos
            ):
                self.player.die()
                self.game_state.change_state(State.GAME_OVER)

        # Atualizar pontuação
        self.score_manager.update(delta_time, self.scroll_manager.current_speed)

        # Verificar as possibilidades de spawn
        self.__spawn_obstacles(delta_time)
        self.__spawn_enemies(delta_time)

        # Spawn de moedas
        self.coin_spawn_timer += delta_time
        if self.coin_spawn_timer >= self.coin_spawn_interval:
            self.coin_spawn_timer = 0
            coin = self._create_coin()
            self.coins_group.add(coin)
            self.all_sprites_group.add(coin)

        # Spawn de power-ups  
        self.powerup_spawn_timer += delta_time
        if self.powerup_spawn_timer >= self.powerup_spawn_interval:
            self.powerup_spawn_timer = 0
            powerup = self._create_powerup()
            self.powerups_group.add(powerup)
            self.all_sprites_group.add(powerup)

        # Colisão com moedas
        collected_coins = pg.sprite.spritecollide(self.player, self.coins_group, True)
        self.coins_collected += len(collected_coins)

        # Atualizar grupos
        self.coins_group.update(delta_time)
        self.powerups_group.update(delta_time)
        self.projectiles_group.update(delta_time)

        # Boss spawn
        self.boss_timer += delta_time
        if self.boss_timer >= self.boss_interval and not self.current_boss:
            self.current_boss = FlyBoss(self.config["enemies_cfg"], self.player)
            self.enemies_group.add(self.current_boss)
            self.all_sprites_group.add(self.current_boss)
            self.boss_timer = 0

    def render(self, screen: pg.Surface):
        """Renderiza o cenário."""
        # Renderizar fundo
        self.background_manager.render(screen)

        # Renderizar sprites
        self.all_sprites_group.draw(screen)

        # Renderizar linha azul do lago (mais chamativa)
        pg.draw.line(screen, (0, 150, 255), (0, SCREEN_HEIGHT - 8), (SCREEN_WIDTH, SCREEN_HEIGHT - 8), 16)
        
        # Interface melhorada
        self._render_ui(screen)
        
        # Renderizar aviso do jacaré (mais visível)
        self._render_jacare_warning(screen)

    def _render_ui(self, screen):
        """Renderiza interface melhorada"""
        # Fundo semi-transparente para a pontuação
        ui_surface = pg.Surface((300, 80), pg.SRCALPHA)
        ui_surface.fill((0, 0, 0, 128))  # Preto transparente
        screen.blit(ui_surface, (10, 10))
        
        # Pontuação estilizada
        font_big = pg.font.SysFont("Arial", 32, bold=True)
        font_small = pg.font.SysFont("Arial", 18)
        
        score_text = font_big.render(f"{self.score_manager.get_score()}m", True, (255, 255, 255))
        label_text = font_small.render("DISTÂNCIA", True, (200, 200, 200))

        # Contador de moedas
        coins_text = font_small.render(f"MOEDAS: {self.coins_collected}", True, (255, 215, 0))
        screen.blit(coins_text, (20, 70))
        
        screen.blit(label_text, (20, 20))
        screen.blit(score_text, (20, 40))

    def _render_jacare_warning(self, screen):
        """Renderiza aviso do jacaré mais visível"""
        if self.jacare_warning.visible:
            pulse = (math.sin(pg.time.get_ticks() * 0.01) + 1) / 2
            
            # Posição do aviso
            warning_pos = (int(self.jacare_warning.x), int(self.jacare_warning.y))
            
            # Círculo pulsante maior
            pg.draw.circle(screen, (255, 0, 0), warning_pos, int(20 + 5 * pulse))
            pg.draw.circle(screen, (255, 255, 0), warning_pos, 15)
            
            # Texto de aviso POSICIONADO CORRETAMENTE
            font = pg.font.SysFont("Arial", 20, bold=True)
            warning_text = font.render("PERIGO!", True, (255, 0, 0))
            # Centraliza o texto acima do círculo
            text_rect = warning_text.get_rect()
            text_rect.centerx = warning_pos[0]
            text_rect.bottom = warning_pos[1] - 30  # 30 pixels acima do círculo
            
            # Fundo semi-transparente para o texto
            bg_surface = pg.Surface((text_rect.width + 10, text_rect.height + 6), pg.SRCALPHA)
            bg_surface.fill((0, 0, 0, 180))
            screen.blit(bg_surface, (text_rect.x - 5, text_rect.y - 3))
            screen.blit(warning_text, text_rect)

    def __spawn_obstacles(self, delta_time):
        new_obstacle = self.obstacle_spawner.update(
            delta_time, self.scroll_manager.current_speed
        )

        if new_obstacle:
            self.obstacles_group.add(new_obstacle)
            self.all_sprites_group.add(new_obstacle)

    def __spawn_enemies(self, delta_time):
        new_enemy = self.enemy_spawner.update(
            delta_time, self.scroll_manager.current_speed, self.player
        )

        if new_enemy:
            self.enemies_group.add(new_enemy)
            self.all_sprites_group.add(new_enemy)

    def __spawn_jacare_attack(self):
        """Spawna o jacaré quando o player toca a borda inferior"""
        from .enemies import Jacare
        self.player.lock_controls()  # Trava controles imediatamente
        self.jacare = Jacare(self.config["enemies_cfg"], self.player)
        self.enemies_group.add(self.jacare)
        self.all_sprites_group.add(self.jacare)

    def _create_coin(self):
        """Cria uma moeda usando a classe correta"""
        return Coin()

    def _create_powerup(self):
        """Cria um power-up usando a classe correta"""
        power_types = ["shield", "speed", "magnet"]
        return PowerUp(random.choice(power_types))
