import pygame as pg
from core import (
    State,
    GameState,
    ScoreManager,
    CollisionManager,
    ScrollerManager,
    BackgroundManager,
    load_json,
)
from .forest_player import ForestPlayer
from .forest_enemies import ForestEnemySpawner
from .forest_fogo import ForestFogo 

pg.joystick.init()

if pg.joystick.get_count() > 0:
    joystick = pg.joystick.Joystick(0)
    joystick.init()
else:
    joystick = None

class ForestScene:
    def __init__(self, game_state: GameState):
        self.game_state = game_state
        self.config = load_json("./config/forest.json")

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
        self.player = ForestPlayer(self.config["player_cfg"], invincible=False)
        if self.player:
            self.player_group.add(self.player)
            self.all_sprites_group.add(self.player)
        
        # Instanciar o fogo (fixo no cenário)
        self.fogo = ForestFogo(self.config["fogo_cfg"])
        self.all_sprites_group.add(self.fogo)

        # Instanciar o spawner de inimigos
        self.enemy_spawner = ForestEnemySpawner(self.config["enemies_cfg"])

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

        elif joystick != None and event.type == pg.JOYAXISMOTION:
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
        elif joystick != None and event.type == pg.JOYBUTTONDOWN:
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
        self.fogo.update(delta_time)   
        self.obstacles_group.update(delta_time)
        self.enemies_group.update(delta_time)

        # Verificar colisões
        if not self.player.invincible:
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
        self.__spawn_enemies(delta_time)

    def render(self, screen: pg.Surface):
        """Renderiza o cenário.

        Args:
            screen (pg.Surface): Superfície onde renderizar
        """
        # Renderizar fundo
        self.background_manager.render(screen)

        # Renderizar sprites
        self.all_sprites_group.draw(screen)

        # Renderizar pontuação
        font = pg.font.SysFont(None, 36)
        score_text = font.render(
            f"Distância: {self.score_manager.get_score()}", True, (255, 255, 255)
        )
        # Obter as dimensões da tela
        screen_width, screen_height = screen.get_size()

        # Calcular a posição central para o texto
        text_rect = score_text.get_rect(center=(screen_width // 1.1, 10 + score_text.get_height() // 2))

        screen.blit(score_text, text_rect.topleft)

    def __spawn_enemies(self, delta_time):
        new_enemy = self.enemy_spawner.update(
            delta_time, self.scroll_manager.current_speed, self.player
        )

        if new_enemy:
            self.enemies_group.add(new_enemy)
            self.all_sprites_group.add(new_enemy)