import pygame as pg
import json
from core import State, GameState, BaseMenu, FontManager, Button


class GameOverMenu(BaseMenu):
    def __init__(self, game_state: GameState, scene):
        super().__init__(game_state)

        self.font_manager = FontManager()
        self.font_title = self.font_manager.load_font(None, 74)

        # Carregar a imagem de fundo do menu GameOver diretamente
        self.background_image = pg.image.load("assets/images/menus/GameOver/fundo_gameOver_sheet.png").convert_alpha()
        self.background_rect = self.background_image.get_rect(center=(self._game_state.screen.get_width() // 2, self._game_state.screen.get_height() // 2))

        # Botões normais
        self.buttons_sheet = pg.image.load("assets/images/menus/GameOver/gameOver_sheet.png").convert_alpha()
        with open("assets/images/menus/GameOver/gameOver.json", 'r') as f:
            self.buttons_data = json.load(f)

        # Quadro da distância
        self.distancia_sheet = pg.image.load("assets/images/menus/GameOver/distancia_sheet.png").convert_alpha()
        with open("assets/images/menus/GameOver/distancia.json", 'r') as f:
            self.distancia_data = json.load(f)

        # Estrair as sprites dos botões e do quadro de distância
        self.button_sprites = self._load_sprites(self.buttons_sheet, self.buttons_data)
        self.distancia_sprite = self._load_sprites(self.distancia_sheet, self.distancia_data).get("button_distancia")

        self._options = [
            ("", self.__retry_scene),
            ("", self.__return_to_menu),
        ]
        # _create_buttons agora criará uma lista interna de dicionários para os botões
        self._create_buttons_with_sprites()

        # Atualiza os scores salvos
        self.scene = scene
        self.score_manager = self.scene.score_manager
        self.score = self.score_manager.get_score()
        self.score_manager.check_high_score()

        # SONS
        self.sound_choice = pg.mixer.Sound("songs/menus/choice.mp3")  # Pré carrega o som de efeito de escolha
        self.sound_selected = pg.mixer.Sound("songs/menus/selected.mp3")  # Pré carrega o som de efeito selecionado
        # Para a música e toca o som de game over
        pg.mixer.music.stop()
        self.death_sound = pg.mixer.Sound("songs/menus/gameOver.mp3")
        self.death_sound.play()

    def _load_sprites(self, sheet, data):
        sprites = {}
        for anim_data in data.get("animations", []):
            anim_name = anim_data["name"]
            frames = []
            for frame_rect in anim_data["frames_rect"]:
                x, y, w, h = frame_rect
                frame = pg.Surface((w, h), pg.SRCALPHA)
                frame.blit(sheet, (0, 0), (x, y, w, h))
                
                target_size = data.get("target_size")
                if target_size:
                    frame = pg.transform.scale(frame, target_size)
                frames.append(frame)
            sprites[anim_name] = frames[0] if frames else None 
        return sprites

    def _create_buttons_with_sprites(self):
        if self._options:
            screen_center_x = self._game_state.screen.get_width() // 2
            start_y = 370
            spacing = 120

            # Criar uma estrutura para os botões que inclua as sprites
            self._custom_buttons = [] # Nova lista para gerenciar os botões internamente
            for i, (text, function) in enumerate(self._options):
                # Usamos o sprite 'button1' para o primeiro botão e 'button2' para o segundo
                # E 'buttonSelected1'/'buttonSelected2' para os estados selecionados
                normal_sprite_name = f"button{i+1}"
                selected_sprite_name = f"buttonSelected{i+1}"

                button_sprite_normal = self.button_sprites.get(normal_sprite_name)
                if button_sprite_normal:
                    button_rect = button_sprite_normal.get_rect(center=(screen_center_x, start_y + i * spacing))
                    self._custom_buttons.append({
                        'text': text,
                        'function': function,
                        'rect': button_rect,
                        'selected': False, # Estado de seleção para cada botão
                        'normal_sprite_key': normal_sprite_name,
                        'selected_sprite_key': selected_sprite_name
                    })
                else:
                    print(f"[GameOverMenu] Sprite '{normal_sprite_name}' não encontrada para o botão {text}")
            
            # Seleciona o primeiro botão por padrão
            if self._custom_buttons:
                self._custom_buttons[0]['selected'] = True

    @property
    def _current_button(self):
        # Retorna o botão atualmente selecionado da nossa lista customizada
        for btn in self._custom_buttons:
            if btn['selected']:
                return btn
        return None

    def _select_option(self):
        current_btn = self._current_button
        if current_btn:
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
            self.sound_choice.play()  # Toca o som de escolha sempre que muda de botão

    def __retry_scene(self):
        # toca o som de seleção primeiro
        self.sound_selected.play()
        self.death_sound.stop()  # Para o som de game over se ainda estiver tocando
        pg.mixer.music.load("songs/menus/trilha_sonora.mp3")  # Volta a tocar a trilha sonora do inicio
        pg.mixer.music.play(loops=-1)
        self._game_state.change_state(State.PLAYING, self.scene.config["scene_name"])

    def __return_to_menu(self):
        # toca o som de seleção primeiro
        self.sound_selected.play()
        self.death_sound.stop()  # Para o som de game over se ainda estiver tocando
        pg.mixer.music.load("songs/menus/trilha_sonora.mp3")  # Volta a tocar a trilha sonora do inicio
        pg.mixer.music.play(loops=-1)
        self._game_state.change_state(State.MAIN_MENU)

    def update(self, delta_time=None):
        # A lógica de seleção é tratada em handle_event e _move_selection
        pass

    def render(self, screen):
        # Desenha a imagem de fundo primeiro
        screen.blit(self.background_image, self.background_rect)

        # Renderiza o quadadro da distancia
        if self.distancia_sprite:
            rect = self.distancia_sprite.get_rect(center=(screen.get_width() // 2, 309))
            screen.blit(self.distancia_sprite, rect)

        score = self.small_font.render(f"DISTÂNCIA: {self.score}", True, (255, 200, 0))
        screen.blit(score, score.get_rect(center=(screen.get_width() // 2, 270)))

        # Renderiza os botões customizados com sprites
        for btn_data in self._custom_buttons:
            # Escolhe o sprite com base no estado de seleção do botão
            sprite_to_draw = self.button_sprites.get(btn_data['selected_sprite_key']) if btn_data['selected'] else self.button_sprites.get(btn_data['normal_sprite_key'])
            if sprite_to_draw:
                screen.blit(sprite_to_draw, btn_data['rect'])

    def handle_event(self, event):
        # Sobrescreve o handle_event da BaseMenu para usar a lógica de seleção de botões customizada
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_DOWN:
                self._move_selection(1)
            elif event.key == pg.K_UP:
                self._move_selection(-1)
            elif event.key == pg.K_RETURN:
                self._select_option()