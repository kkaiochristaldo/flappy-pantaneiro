import pygame as pg
from config import SCREEN_WIDTH, SCREEN_HEIGHT
from core import State, GameState, CollisionManager, ScrollerManager, load_json
from .player import SkyPlayer
from .obstacles import ObstacleSpawner
from .enemies import EnemySpawner
from .effects import Effect
from .score import SkyScoreManager
from .danger_zone import Jacare

class SkyScene:
    def __init__(self, game_state: GameState):
        self.game_state = game_state
        self.config = load_json("./config/sky.json")

        self.scroll_manager = ScrollerManager(self.config["scroller_cfg"])
        self.collision_manager = CollisionManager()
        self.score_manager = SkyScoreManager()

        self.all_sprites = pg.sprite.Group()
        self.player_group = pg.sprite.GroupSingle()
        self.obstacles_group = pg.sprite.Group()
        self.enemies_group = pg.sprite.Group()
        self.effects_group = pg.sprite.Group()
        self.enemy_projectiles_group = pg.sprite.Group()
        self.danger_zone_group = pg.sprite.Group()

        self.player = SkyPlayer(self.config["player_cfg"])
        self.player_group.add(self.player)

        self.obstacle_spawner = ObstacleSpawner(self.config["obstacles_cfg"])
        self.enemy_spawner = EnemySpawner(self.config["enemies_cfg"])
        
        self.ability_charge=0.0; self.ability_charge_max=10.0; self.ability_duration=5.0
        self.ability_timer=0.0; self.is_ability_active=False
        self.jacare_cooldown=0; self.jacare_cooldown_max=3.0

        self.hud_font = pg.font.SysFont(None, 40)
        self.hud_ability_font = pg.font.SysFont(None, 24)

    def handle_event(self, event: pg.event.Event):
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_UP: self.player.start_thrust()
            if event.key == pg.K_ESCAPE: self.game_state.change_state(State.PAUSE)
            if event.key == pg.K_SPACE and self.ability_charge >= self.ability_charge_max:
                self.is_ability_active = True; self.ability_timer = self.ability_duration
                self.player.activate_shield(True); self.ability_charge = 0.0
        if event.type == pg.KEYUP and event.key == pg.K_UP: self.player.stop_thrust()

    def update(self, delta_time: float):
        if not self.player.is_alive: return
        self.scroll_manager.update(delta_time); self.player.update(delta_time)
        self.score_manager.update(delta_time)
        self.__update_ability(delta_time); self.__update_danger_zone(delta_time)
        self.__spawn_and_update_entities(delta_time); self.__check_collisions()

    def __update_danger_zone(self, delta_time: float):
        self.jacare_cooldown -= delta_time
        if self.player.rect.bottom > SCREEN_HEIGHT * 0.85 and self.jacare_cooldown <= 0:
            self.jacare_cooldown = self.jacare_cooldown_max
            jacare = Jacare(self.config["jacare_cfg"], self.player.rect.centerx, SCREEN_HEIGHT + 50)
            self.danger_zone_group.add(jacare); self.all_sprites.add(jacare)
            self.player.apply_repulsion()
        self.danger_zone_group.update(delta_time)

    def __spawn_and_update_entities(self, delta_time):
        scroll = self.scroll_manager.current_speed
        
        new_obs = self.obstacle_spawner.update(delta_time, scroll)
        self.obstacles_group.add(new_obs); self.all_sprites.add(new_obs)
        self.obstacles_group.update(delta_time, scroll)
        
        new_enemies = self.enemy_spawner.update(delta_time, scroll, self.player, self.enemy_projectiles_group, self.config["projectiles_cfg"])
        self.enemies_group.add(new_enemies); self.all_sprites.add(new_enemies)
        self.enemies_group.update(delta_time, scroll, self.player, self.enemy_projectiles_group, self.config["projectiles_cfg"])

        self.enemy_projectiles_group.update(delta_time)
        self.all_sprites.add(self.enemy_projectiles_group)
        self.effects_group.update(delta_time)

    def render(self, screen: pg.Surface):
        screen.fill((135, 206, 235))
        self.all_sprites.draw(screen)
        self.player.draw(screen)
        self.__render_hud(screen)

    def __render_hud(self, screen: pg.Surface):
        score_text = self.hud_font.render(f"Score: {self.score_manager.get_score()}", True, "white")
        screen.blit(score_text, (10, 10))
        bar_w, bar_h = 200, 25; bar_x, bar_y = (SCREEN_WIDTH-bar_w)/2, SCREEN_HEIGHT-bar_h-10
        ratio = min(self.ability_charge / self.ability_charge_max, 1.0); current_w = bar_w * ratio
        pg.draw.rect(screen, (50, 50, 50), (bar_x, bar_y, bar_w, bar_h))
        if ratio < 1.0:
            pg.draw.rect(screen, (0, 150, 255), (bar_x, bar_y, current_w, bar_h))
            text = self.hud_ability_font.render("RECARGA DO ESCUDO", True, "white")
        else:
            pg.draw.rect(screen, (255, 255, 0), (bar_x, bar_y, current_w, bar_h))
            text = self.hud_ability_font.render("ESCUDO PRONTO [ESPAÇO]", True, "black")
        text_rect=text.get_rect(center=(bar_x+bar_w/2, bar_y+bar_h/2)); screen.blit(text, text_rect)

    def __update_ability(self, delta_time: float):
        if self.is_ability_active:
            self.ability_timer -= delta_time
            if self.ability_timer <= 0: self.is_ability_active = False; self.player.activate_shield(False)
        elif self.ability_charge < self.ability_charge_max: self.ability_charge += delta_time

    def __check_collisions(self):
        if self.player.invincible: return
        if self.collision_manager.check_collision(self.player_group, self.enemy_projectiles_group) or \
           self.collision_manager.check_collision(self.player_group, self.obstacles_group):
            self.__game_over()
            return
        collided_enemies = pg.sprite.spritecollide(self.player, self.enemies_group, True, pg.sprite.collide_mask)
        if collided_enemies:
            for enemy in collided_enemies:
                exp = Effect(self.config["effects_cfg"], enemy.rect.centerx, enemy.rect.centery, "explosion")
                self.all_sprites.add(exp); self.effects_group.add(exp)
            self.__game_over()

    def __game_over(self):
        self.player.die(); self.scroll_manager.stop(); self.game_state.change_state(State.GAME_OVER)