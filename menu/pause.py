import pygame as pg
import json
from core import State, GameState, BaseMenu


class PauseMenu(BaseMenu):
    def __init__(self, game_state: GameState):
        super().__init__(game_state)

        # Carregar a imagem de fundo do menu Pause
        self.background_image = pg.image.load("assets/images/menus/Pause/fundo_pause_sheet.png").convert_alpha()
        self.background_rect = self.background_image.get_rect(center=(
            self._game_state.screen.get_width() // 2,
            self._game_state.screen.get_height() // 2
        ))

        # Carregar spritesheet e JSON dos botões
        self.button_sheet = pg.image.load("assets/images/menus/Pause/pause_sheet.png").convert_alpha()
        with open("assets/images/menus/Pause/pause.json", 'r') as f:
            self.button_data = json.load(f)

        # Extrair sprites dos botões
        self.button_sprites = self._load_button_sprites()

        # Opções do menu
        self._options = [
            ("", self.__resume_game),
            ("", self.__return_to_menu),
        ]
        self._create_buttons_with_sprites()

        # Sons
        self.sound_selected = pg.mixer.Sound("songs/menus/selected.mp3")  # som de confirmação
        self.sound_choice = pg.mixer.Sound("songs/menus/choice.mp3")      # som de navegação

        pg.mixer.music.pause()   # música pausa ao abrir o Pause

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
        if not self._options:
            return

        screen_center_x = self._game_state.screen.get_width() // 2
        start_y = 350
        spacing = 120

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
                print(f"[PauseMenu] Sprite '{normal_sprite_name}' não encontrada para o botão {text}")

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
            self.sound_selected.play()  # toca som ao confirmar
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
            self.sound_choice.play()  # toca som ao navegar

    def __resume_game(self):
        self.sound_selected.play()
        pg.mixer.music.unpause()  # música continua ao voltar o jogo
        self._game_state.change_state(State.PLAYING)

    def __return_to_menu(self):
        self.sound_selected.play()
        pg.mixer.music.load("songs/menus/trilha_sonora.mp3")
        pg.mixer.music.play(loops=-1)  # reinicia a música
        self._game_state.change_state(State.MAIN_MENU)

    def update(self, delta_time=None):
        pass

    def render(self, screen):
        # Desenha o fundo
        screen.blit(self.background_image, self.background_rect)

        # Renderiza os botões
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
