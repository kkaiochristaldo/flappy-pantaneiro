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
        
        self.powerups_group = pg.sprite.Group() 
        self.active_powerups = []  # Lista de power-ups ativos
        self.projectiles_group = pg.sprite.Group()
        
        self.powerup_spawn_timer = 0

        # Timers de spawn
        self.powerup_spawn_interval = 15.0  # Power-up a cada 15 segundos

        # Boss battle system
        self.boss_timer = 0
        self.boss_interval = 30.0  # Boss a cada 30 segundos
        self.current_boss = None

        self.boss_active = False
        self.boss_appeared_once = False  # Para controlar aparição do drone

        self.shield_effect_timer = 0

    def handle_event(self, event: pg.event.Event):
        """Processa eventos do Pygame.

        Args:
            event (pg.event.Event): Evento a ser processado
        """
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_UP:
                self.player.start_thrust()
            elif event.key == pg.K_DOWN:
                self.player.start_dive()
            elif event.key == pg.K_ESCAPE:
                self.game_state.change_state(State.PAUSE)

        # --- Eventos de Tecla Solta ---
        elif event.type == pg.KEYUP:
            if event.key == pg.K_UP:
                self.player.stop_thrust()
            elif event.key == pg.K_DOWN:
                self.player.stop_dive()

        # =========== adicionado para joystick

        elif event.type == pg.JOYAXISMOTION:
        # Eixo 1 é geralmente o eixo vertical do analógico esquerdo
            if event.axis == 1:
                # Para cima (valor negativo)
                if int(event.value) == -1:
                    self.player.start_thrust()
                    self.player.stop_dive() # Impede movimento simultâneo
                # Para baixo (valor positivo)
                elif int(event.value) == 1:
                    self.player.start_dive()
                    self.player.stop_thrust() # Impede movimento simultâneo
                # Analógico no centro (zona morta)
                else:
                    self.player.stop_thrust()
                    self.player.stop_dive()

        # --- Adicional: Pausar com o botão do Joystick ---
        elif event.type == pg.JOYBUTTONDOWN:
            # O botão 7 é geralmente o "Start" ou "Options"
            if event.button == 8:
                self.game_state.change_state(State.PAUSE)
                
        # =========================================

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


        # Spawn de power-ups  
        self.powerup_spawn_timer += delta_time
        if self.powerup_spawn_timer >= self.powerup_spawn_interval:
            self.powerup_spawn_timer = 0
            powerup = self._create_powerup()
            self.powerups_group.add(powerup)
            self.all_sprites_group.add(powerup)


        self.powerups_group.update(delta_time)
        self.projectiles_group.update(delta_time)

        # --- COLISÃO PROJÉTIL <-> PLAYER ---
        if not self.player.invincible:
            if pg.sprite.spritecollide(self.player, self.projectiles_group, True, pg.sprite.collide_mask):
                self.player.die()
                self.game_state.change_state(State.GAME_OVER)

        self.boss_timer += delta_time

        # Boss spawn
        if self.boss_timer >= self.boss_interval and not self.current_boss and not self.boss_active:
            self.current_boss = FlyBoss(self.config["enemies_cfg"], self.player)
            self.enemies_group.add(self.current_boss)
            self.all_sprites_group.add(self.current_boss)
            self.boss_timer = 0
            self.boss_active = True
            self.boss_appeared_once = True

        # Verifica se boss ainda existe (pode ter morrido por colisão ou saído)
        if self.current_boss and self.current_boss not in self.enemies_group:
            self.current_boss = None
            self.boss_active = False

        collected_powerups = pg.sprite.spritecollide(self.player, self.powerups_group, True)
        for powerup in collected_powerups:
            self._activate_powerup(powerup.power_type)

        # Atualizar power-ups ativos
        for powerup_effect in self.active_powerups[:]:
            powerup_effect["timer"] -= delta_time
            if powerup_effect["timer"] <= 0:
                self._deactivate_powerup(powerup_effect)
                self.active_powerups.remove(powerup_effect)

    def _activate_powerup(self, power_type):
        """Ativa efeito do power-up"""
        if power_type == "shield":
            self.player.invincible = True
            self.active_powerups.append({"type": "shield", "timer": 5.0})
        elif power_type == "speed":
            # CORREÇÃO FINAL: Modificar a velocidade inicial
            self.scroll_manager._initial_speed *= 0.5
            self.active_powerups.append({"type": "speed", "timer": 5.0})
        elif power_type == "shoot":
            for sprite in list(self.obstacles_group) + list(self.enemies_group):
                if not isinstance(sprite, FlyBoss):
                    sprite.kill()

    def _deactivate_powerup(self, powerup_effect):
        """Desativa efeito quando expira"""
        if powerup_effect["type"] == "shield":
            self.player.invincible = False
        elif powerup_effect["type"] == "speed":
            # CORREÇÃO FINAL: Restaurar a velocidade inicial
            self.scroll_manager._initial_speed *= 2.0

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

        self._render_shield_effect(screen)

        self._render_boss_telegraph(screen)

    def _render_ui(self, screen):
        """Renderiza interface melhorada"""
        ui_surface = pg.Surface((300, 100), pg.SRCALPHA)  # Aumentei altura
        ui_surface.fill((0, 0, 0, 128))
        screen.blit(ui_surface, (10, 10))
        
        font_big = pg.font.SysFont("Arial", 32, bold=True)
        font_small = pg.font.SysFont("Arial", 18)
        
        score_text = font_big.render(f"{self.score_manager.get_score()}m", True, (255, 255, 255))
        label_text = font_small.render("DISTÂNCIA", True, (200, 200, 200))
        
        screen.blit(label_text, (20, 20))
        screen.blit(score_text, (20, 40))
        
    def _render_jacare_warning(self, screen):
        if self.jacare_warning.visible:
            pulse = (math.sin(pg.time.get_ticks() * 0.01) + 1) / 2
            
            # Posição ajustada - mais longe da borda
            warning_pos = (SCREEN_WIDTH - 80, int(self.jacare_warning.y))  # Muda de x para posição fixa
            
            # Círculo pulsante
            pg.draw.circle(screen, (255, 0, 0), warning_pos, int(20 + 5 * pulse))
            pg.draw.circle(screen, (255, 255, 0), warning_pos, 15)
            
            # Texto centralizado acima do círculo
            font = pg.font.SysFont("Arial", 20, bold=True)
            warning_text = font.render("PERIGO!", True, (255, 0, 0))
            text_rect = warning_text.get_rect()
            text_rect.centerx = warning_pos[0]
            text_rect.bottom = warning_pos[1] - 30
            
            # Fundo para o texto
            bg_surface = pg.Surface((text_rect.width + 10, text_rect.height + 6), pg.SRCALPHA)
            bg_surface.fill((0, 0, 0, 180))
            screen.blit(bg_surface, (text_rect.x - 5, text_rect.y - 3))
            screen.blit(warning_text, text_rect)
    
    def _render_shield_effect(self, screen):
        """Renderiza efeito visual do escudo"""
        has_shield = any(p["type"] == "shield" for p in self.active_powerups)
        
        if has_shield:
            self.shield_effect_timer += 0.05
            # Escudo pulsante azul
            radius = int(40 + 5 * math.sin(self.shield_effect_timer))
            shield_surface = pg.Surface((radius * 2, radius * 2), pg.SRCALPHA)
            
            # Círculo com transparência
            pg.draw.circle(shield_surface, (100, 150, 255, 100), (radius, radius), radius, 3)
            pg.draw.circle(shield_surface, (150, 200, 255, 50), (radius, radius), radius - 5, 2)
            
            pos = (int(self.player.position.x - radius), int(self.player.position.y - radius))
            screen.blit(shield_surface, pos)

    def _render_boss_telegraph(self, screen):
        """Renderiza aviso visual quando boss vai atacar"""
        if self.current_boss and hasattr(self.current_boss, 'is_telegraphing') and self.current_boss.is_telegraphing:
            # Linha vermelha piscante do boss até o player
            alpha = int(128 + 127 * abs(math.sin(pg.time.get_ticks() * 0.01)))
            boss_pos = (int(self.current_boss._position.x), int(self.current_boss._position.y))
            player_pos = (int(self.player.position.x), int(self.player.position.y))
            
            # Superfície temporária para linha com transparência
            line_surface = pg.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pg.SRCALPHA)
            pg.draw.line(line_surface, (255, 0, 0, alpha), boss_pos, player_pos, 3)
            screen.blit(line_surface, (0, 0))

    def __spawn_obstacles(self, delta_time):
        if self.boss_active:
            return
        
        new_obstacle = self.obstacle_spawner.update(
            delta_time, self.scroll_manager.current_speed
        )

        if new_obstacle:
            self.obstacles_group.add(new_obstacle)
            self.all_sprites_group.add(new_obstacle)

    def __spawn_enemies(self, delta_time):
        # Não spawna inimigos durante boss battle
        if self.boss_active:
            return
            
        new_enemy = self.enemy_spawner.update(
            delta_time, self.scroll_manager.current_speed, self.player, self.boss_appeared_once
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
        power_types = ["shield", "speed", "shoot"]  # Mudou magnet para shoot
        return PowerUp(random.choice(power_types))
