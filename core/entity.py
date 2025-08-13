import pygame as pg
from .asset_loader import EntityAnimationLoader


class Entity(pg.sprite.Sprite):
    """
    Representa uma entidade genérica no jogo, como um personagem ou objeto,
    capaz de gerenciar suas próprias animações a partir de um spritesheet.
    """

    def __init__(self, entity_cfg: dict, x: int, y: int):
        """
        Inicializa a entidade.

        Args:
            entity_cfg (dict): Dicionário de configuração da entidade.
                               Deve conter informações sobre o spritesheet
                               e configurações de fallback.
            x (int): Posição inicial da entidade no eixo X.
            y (int): Posição inicial da entidade no eixo Y.
        """
        super().__init__()

        # Inicializar os atributos de estado
        self.__initialize_attributes()

        # Carregar as animações a partir da configuração
        self.__load_animations(entity_cfg)

        # Definir o estado inicial (imagem, rect, etc.)
        self.__setup_initial_state(entity_cfg, x, y)

    def __initialize_attributes(self):
        """Inicializa todos os atributos de estado da animação."""
        self._animations = {}
        self._current_animation = None
        self._current_frame = 0
        self._animation_timer = 0.0
        self._animation_speed = 0.1
        self._loop_animation = True
        self._animation_finished = False

    def __load_animations(self, config: dict):
        """
        Carrega as animações do spritesheet definido na configuração.
        Em caso de falha, não faz nada, permitindo que o fallback seja usado.
        """
        spritesheet_cfg = config.get("spritesheet", {})
        if spritesheet_cfg:
            try:
                loader = EntityAnimationLoader(
                    spritesheet_cfg["image"], spritesheet_cfg["data"]
                )
                self._animations = loader.load()

            except Exception as e:
                print(f"[Entity] Erro ao carregar spritesheet: {e}. Usando fallback.")
                self._animations = {}

    def __setup_initial_state(self, entity_cfg: dict, x: int, y: int):
        """Configura a imagem inicial, o rect e a máscara."""
        if self._animations:
            # Se houver animações, define a primeira da lista como a inicial
            first_animation_name = next(iter(self._animations))
            self.set_animation(first_animation_name)
        else:
            # Se não, cria uma imagem de fallback
            fallback_size = tuple(entity_cfg.get("fallback_size", (50, 50)))
            fallback_color = tuple(entity_cfg.get("fallback_color", (255, 0, 255)))
            self.__create_fallback_image(fallback_size, fallback_color)

        # Configura o rect e a máscara iniciais
        self.rect = self.image.get_rect(center=(x, y))
        self.mask = pg.mask.from_surface(self.image)

    def __create_fallback_image(
        self, size: tuple[int, int], color: tuple[int, int, int]
    ):
        """Cria uma imagem de superfície sólida como fallback."""
        self.image = pg.Surface(size, pg.SRCALPHA)
        self.image.fill(color)

    def __animate(self, delta_time: float):
        """Avança o quadro da animação com base no delta_time."""
        anim_data = self._animations[self._current_animation]
        frames = anim_data["frames"]

        if frames:
            self._animation_timer += delta_time

            if self._animation_timer >= self._animation_speed:
                self._animation_timer -= self._animation_speed

                next_frame_index = self._current_frame + 1

                if self._loop_animation:
                    self._current_frame = next_frame_index % len(frames)
                elif next_frame_index < len(frames):
                    self._current_frame = next_frame_index
                else:
                    self._animation_finished = True

                # Atualiza a imagem e a máscara
                self.image = frames[self._current_frame]
                self.mask = pg.mask.from_surface(self.image)

    def set_animation(self, name: str):
        """
        Define a animação atual e reinicia seu estado.

        A animação só é alterada se o nome for diferente da animação atual
        e existir na lista de animações carregadas.

        Args:
            name (str): O nome da animação a ser executada (ex: "idle", "run").
        """
        if name in self._animations and name != self._current_animation:
            self._current_animation = name
            anim_data = self._animations[name]

            # Reinicia o estado da animação
            self._loop_animation = anim_data["loop"]
            self._animation_speed = anim_data["speed"]
            self._current_frame = 0
            self._animation_timer = 0.0
            self._animation_finished = False

            # Define a imagem e máscara iniciais da nova animação
            self.image = anim_data["frames"][0]
            self.mask = pg.mask.from_surface(self.image)

    def update(self, delta_time: float):
        """
        Atualiza o estado da entidade a cada quadro.

        Args:
            delta_time (float): O tempo decorrido desde o último quadro.
        """
        if not self._animation_finished and self._current_animation:
            self.__animate(delta_time)
