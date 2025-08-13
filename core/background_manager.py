import pygame as pg
from .asset_loader import BackgroundLayerLoader


class BackgroundManager:
    """
    Gerencia e renderiza as camadas de background, com suporte a paralaxe.
    """

    def __init__(self, background_cfg: dict):
        """
        Inicializa o background com camadas pré-carregadas.

        Args:
            layers (list[BackgroundLayer]): Lista de camadas de background já carregadas.
            background_cfg (dict): Dicionário de configuração para fallbacks e parallax.
        """
        self._layers = []
        self._fallback_color: tuple[int, int, int]

        # Carregar as camadas a partir da configuração
        self._load_layers(background_cfg)

        if not self._layers:
            self._fallback_color = background_cfg.get("fallback_color", (0, 0, 0))

    def _load_layers(self, config: dict):
        """
        Carrega as camadas do spritesheet definido na configuração.
        Em caso de falha, não faz nada, permitindo que o fallback seja usado.
        """
        spritesheet_cfg = config.get("spritesheet", {})
        if spritesheet_cfg:
            try:
                loader = BackgroundLayerLoader(
                    spritesheet_cfg["image"], spritesheet_cfg["data"]
                )
                self._layers = loader.load()

            except Exception as e:
                print(f"[Background] Erro ao carregar background: {e}. Usando fallback")
                self._layers = []

    def update(self, global_scroll_x=0.0):
        """
        Atualiza a posição de rolagem das camadas se o paralaxe estiver ativo.

        Args:
            global_scroll_x (float): O deslocamento global do cenário.
        """
        for layer in self._layers:
            layer.update(global_scroll_x)

    def render(self, screen: pg.Surface):
        """
        Renderiza as camadas na tela.

        Args:
            screen (pg.Surface): A superfície da tela onde o background será desenhado.
        """
        if self._layers:
            for layer in self._layers:
                layer.render(screen)
        else:
            screen.fill(self._fallback_color)
