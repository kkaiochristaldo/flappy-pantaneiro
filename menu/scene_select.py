import pygame as pg
import json
from core import State, GameState, BaseMenu

# =========== adicionado para joystick
pg.joystick.init()

if pg.joystick.get_count() > 0:
    joystick = pg.joystick.Joystick(0)
    joystick.init()
else:
    joystick = None
# ====================================

class SceneSelectMenu(BaseMenu):
    def __init__(self, game_state: GameState):
        super().__init__(game_state)

        # Fundo do menu
        self.background_image = pg.image.load("assets/images/menus/SelectedGame/fundo_selectedGame_sheet.png").convert_alpha()
        self.background_rect = self.background_image.get_rect(center=(
            self._game_state.screen.get_width() // 2,
            self._game_state.screen.get_height() // 2
        ))

        # Spritesheet e JSON dos botões
        self.button_sheet = pg.image.load("assets/images/menus/SelectedGame/selectedGame_sheet.png").convert_alpha()
        with open("assets/images/menus/SelectedGame/selectedGame.json", 'r') as f:
            self.button_data = json.load(f)

        self.button_sprites = self._load_button_sprites()

        # Botões do menu
        self._options = [
            (" ", lambda: self.__select_scene(1)),
            (" ", lambda: self.__select_scene(2)),
            (" ", lambda: self.__select_scene(3)),
        ]
        self._create_buttons_with_sprites()

        # Sons
        self.sound_selected = pg.mixer.Sound("songs/menus/selected.mp3")   # Som de confirmar
        self.sound_navigate = pg.mixer.Sound("songs/menus/choice.mp3")   # Som de navegar

    def _load_button_sprites(self):
        sprites = {}
        for anim_data in self.button_data.get("animations", []):
            name = anim_data["name"]
            frames = []
            for rect in anim_data["frames_rect"]:
                x, y, w, h = rect
                frame = pg.Surface((w, h), pg.SRCALPHA)
                frame.blit(self.button_sheet, (0, 0), (x, y, w, h))

                target_size = self.button_data.get("target_size")
                if target_size:
                    frame = pg.transform.scale(frame, target_size)
                frames.append(frame)
            sprites[name] = frames[0] if frames else None
        return sprites

    def _create_buttons_with_sprites(self):
        screen_center_x = self._game_state.screen.get_width() // 2
        start_y = 340
        spacing = 120

        self._custom_buttons = []
        for i, (text, function) in enumerate(self._options):
            normal_key = f"button{i+1}"
            selected_key = f"buttonSelected{i+1}"

            sprite = self.button_sprites.get(normal_key)
            if sprite:
                rect = sprite.get_rect(center=(screen_center_x, start_y + i * spacing))
                self._custom_buttons.append({
                    'text': text,
                    'function': function,
                    'rect': rect,
                    'selected': False,
                    'normal_sprite_key': normal_key,
                    'selected_sprite_key': selected_key
                })
            else:
                print(f"[SelectedGameMenu] Sprite '{normal_key}' não encontrada para o botão {text}")

        if self._custom_buttons:
            self._custom_buttons[0]['selected'] = True

    @property
    def _current_button(self):
        for btn in self._custom_buttons:
            if btn['selected']:
                return btn
        return None

    def _select_option(self):
        current = self._current_button
        if current:
            current['function']()

    def _move_selection(self, direction):
        if not self._custom_buttons:
            return

        idx = -1
        for i, btn in enumerate(self._custom_buttons):
            if btn['selected']:
                idx = i
                btn['selected'] = False
                break

        if idx != -1:
            new_idx = (idx + direction) % len(self._custom_buttons)
            self._custom_buttons[new_idx]['selected'] = True
            # toca o som de navegação
            self.sound_navigate.play()

    def __select_scene(self, scene_number):
        if scene_number == 1:
            self.sound_selected.play()
            self._game_state.change_state(State.PLAYING, "forest")
        elif scene_number == 2:
            self.sound_selected.play()
            self._game_state.change_state(State.PLAYING, "water")
        elif scene_number == 3:
            self.sound_selected.play()
            self._game_state.change_state(State.PLAYING, "sky")

    def handle_event(self, event):
        # Teclado
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_DOWN:
                self._move_selection(1)
            elif event.key == pg.K_UP:
                self._move_selection(-1)
            elif event.key == pg.K_RETURN:
                self._select_option()

        # Joystick
        if joystick is not None:
            if event.type == pg.JOYHATMOTION:
                hat_x, hat_y = event.value
                if hat_y == 1:
                    self._move_selection(-1)
                elif hat_y == -1:
                    self._move_selection(1)
            elif event.type == pg.JOYBUTTONDOWN:
                self._select_option()

    def update(self, delta_time=None):
        pass

    def render(self, screen):
        # Fundo
        screen.blit(self.background_image, self.background_rect)

        # Botões
        for btn in self._custom_buttons:
            sprite = self.button_sprites.get(btn['selected_sprite_key'] if btn['selected'] else btn['normal_sprite_key'])
            if sprite:
                screen.blit(sprite, btn['rect'])
