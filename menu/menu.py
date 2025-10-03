import pygame as pg
import json
from core import State, GameState, BaseMenu


class MainMenu(BaseMenu):
    def __init__(self, game_state: GameState):
        super().__init__(game_state)

        # Carregar a imagem de fundo do menu Main diretamente
        self.background_image = pg.image.load("assets/images/menus/Main/fundo_main_sheet.png").convert_alpha()
        self.background_rect = self.background_image.get_rect(center=(self._game_state.screen.get_width() // 2,
                                                                     self._game_state.screen.get_height() // 2))

        # Carregar spritesheet e JSON para os botões diretamente
        self.button_sheet = pg.image.load("assets/images/menus/Main/main_sheet.png").convert_alpha()
        with open("assets/images/menus/Main/main.json", 'r') as f:
            self.button_data = json.load(f)

        # Extrair os sprites dos botões (normal e selecionado)
        self.button_sprites = self._load_button_sprites()

        # Opções do menu (sem texto, só sprites)
        self._options = [
            ("", self.__select_scene),
            ("", self.__view_high_scores),
            ("", self.__end_game),
        ]
        self._create_buttons_with_sprites()

        # Sons
        self.sound_selected = pg.mixer.Sound("songs/menus/selected.mp3")  # Efeito ao confirmar
        self.sound_choice = pg.mixer.Sound("songs/menus/choice.mp3")      # Efeito ao navegar

    def _load_button_sprites(self):
        sprites = {}
        for anim_data in self.button_data.get("animations", []):
            anim_name = anim_data["name"]
            frames = []
            for frame_rect in anim_data["frames_rect"]:
                x, y, w, h = frame_rect
                frame = pg.Surface((w, h), pg.SRCALPHA)
                frame.blit(self.button_sheet, (0, 0), (x, y, w, h))

                target_size = self.button_data.get("target_size")
                if target_size:
                    frame = pg.transform.scale(frame, target_size)
                frames.append(frame)

            sprites[anim_name] = frames[0] if frames else None
        return sprites

    def _create_buttons_with_sprites(self):
        if self._options:
            screen_center_x = self._game_state.screen.get_width() // 2
            start_y = 360  # Posição Y inicial para o primeiro botão
            spacing = 120  # Espaçamento entre os botões

            self._custom_buttons = []
            for i, (text, function) in enumerate(self._options):
                normal_sprite_name = f"button{i+1}"
                selected_sprite_name = f"buttonSelected{i+1}"

                button_sprite_normal = self.button_sprites.get(normal_sprite_name)
                if button_sprite_normal:
                    button_rect = button_sprite_normal.get_rect(center=(screen_center_x, start_y + i * spacing))
                    self._custom_buttons.append({
                        'text': text,
                        'function': function,
                        'rect': button_rect,
                        'selected': False,
                        'normal_sprite_key': normal_sprite_name,
                        'selected_sprite_key': selected_sprite_name
                    })
                else:
                    print(f"[MainMenu] Sprite '{normal_sprite_name}' não encontrada")

            if self._custom_buttons:
                self._custom_buttons[0]['selected'] = True

    @property
    def _current_button(self):
        for btn in self._custom_buttons:
            if btn['selected']:
                return btn
        return None

    def _select_option(self):
        current_btn = self._current_button
        if current_btn:
            self.sound_selected.play()  # toca quando confirma
            current_btn['function']()

    def _move_selection(self, direction):
        if not self._custom_buttons:
            return

        current_idx = -1
        for i, btn in enumerate(self._custom_buttons):
            if btn['selected']:
                current_idx = i
                btn['selected'] = False
                break

        if current_idx != -1:
            new_idx = (current_idx + direction) % len(self._custom_buttons)
            self._custom_buttons[new_idx]['selected'] = True
            self.sound_choice.play()  # toca quando muda de botão

    def __select_scene(self):
        self._game_state.change_state(State.SCENE_SELECT)

    def __view_high_scores(self):
        self._game_state.change_state(State.HIGH_SCORES)

    def __end_game(self):
        self._game_state.change_state(State.FINISH)

    def update(self, delta_time=None):
        pass  # lógica de atualização se necessário

    def render(self, screen):
        screen.blit(self.background_image, self.background_rect)

        # Renderiza os botões apenas com os sprites
        for btn_data in self._custom_buttons:
            sprite_to_draw = (
                self.button_sprites.get(btn_data['selected_sprite_key'])
                if btn_data['selected']
                else self.button_sprites.get(btn_data['normal_sprite_key'])
            )
            if sprite_to_draw:
                screen.blit(sprite_to_draw, btn_data['rect'])

    def handle_event(self, event):
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_DOWN:
                self._move_selection(1)
            elif event.key == pg.K_UP:
                self._move_selection(-1)
            elif event.key == pg.K_RETURN:
                self._select_option()
