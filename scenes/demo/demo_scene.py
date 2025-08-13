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
from .demo_player import DemoPlayer
from .demo_obstacles import DemoObstacleSpawner
from .demo_enemies import DemoEnemySpawner


class DemoScene:
    def __init__(self, game_state: GameState):
        self.game_state = game_state
        self.config = load_json("./config/demo.json")

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
        self.player = DemoPlayer(self.config["player_cfg"], invincible=False)
        if self.player:
            self.player_group.add(self.player)
            self.all_sprites_group.add(self.player)

        # Instanciar o spawner de obstáculos
        self.obstacle_spawner = DemoObstacleSpawner(self.config["obstacles_cfg"])

        # Instanciar o spawner de inimigos
        self.enemy_spawner = DemoEnemySpawner(self.config["enemies_cfg"])

    def handle_event(self, event: pg.event.Event):
        """Processa eventos do Pygame.

        Args:
            event (pg.event.Event): Evento a ser processado
        """
        if event.type == pg.KEYDOWN:
            # Se a SETA PARA CIMA for pressionada
            if event.key == pg.K_UP:
                self.player.start_thrust()

            # Se a SETA PARA BAIXO for pressionada
            if event.key == pg.K_DOWN:
                self.player.start_dive()
            elif event.key == pg.K_ESCAPE:
                self.game_state.change_state(State.PAUSE)

        if event.type == pg.KEYUP:
            # Se a SETA PARA CIMA for solta
            if event.key == pg.K_UP:
                self.player.stop_thrust()

            # Se a SETA PARA BAIXO for solta
            if event.key == pg.K_DOWN:
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
        self.__spawn_obstacles(delta_time)
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
            f"Pontuação: {self.score_manager.get_score()}", True, (255, 255, 255)
        )
        screen.blit(score_text, (10, 10))

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
