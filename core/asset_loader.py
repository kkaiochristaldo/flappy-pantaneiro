import pygame as pg
from .utils import load_json, load_image
from .background_layer import BackgroundLayer


class AssetLoader:
    """
    Classe base para carregar assets de uma spritesheet com um JSON associado.
    Lida com o carregamento dos arquivos, deixando a interpretação dos dados
    para as classes filhas.
    """

    def __init__(self, image_path: str, json_path: str):
        """
        Tenta carregar a imagem e o arquivo JSON.
        Lança exceções específicas em caso de falha (ex: FileNotFoundError).
        """
        try:
            self.sheet = load_image(image_path, convert_alpha=True)
            self.data = load_json(json_path)
        except Exception as e:
            print(
                f"[AssetLoader] Erro ao carregar arquivos base ({image_path}, {json_path}): {e}"
            )
            # Propaga a exceção para que o código que chamou o loader possa tratar o erro.
            raise e

    def _get_frame(self, x: int, y: int, w: int, h: int) -> pg.Surface:
        """Recorta um frame da spritesheet."""
        frame = pg.Surface((w, h), pg.SRCALPHA)
        frame.blit(self.sheet, (0, 0), (x, y, w, h))
        return frame

    def load(self):
        """
        Método abstrato que deve ser implementado pelas classes filhas.
        """
        raise NotImplementedError(
            "O método 'load' deve ser implementado na classe filha."
        )


class EntityAnimationLoader(AssetLoader):
    """
    Carrega todas as animações de uma entidade a partir da spritesheet e do JSON.
    """

    def load(self) -> dict:
        """
        Carrega e retorna um dicionário de animações.
        A configuração de 'target_size' é lida diretamente do arquivo JSON.

        Returns:
            dict: Dicionário com os frames de animação já escalados.
        """
        animations = {}
        target_size = self.data.get("target_size")

        for anim_data in self.data.get("animations", []):
            anim_name = anim_data["name"]
            sprites = []

            for frame_rect in anim_data["frames_rect"]:
                sprite = self._get_frame(*frame_rect)

                if target_size:
                    sprite = pg.transform.scale(sprite, target_size)

                sprites.append(sprite)

            animations[anim_name] = {
                "frames": sprites,
                "loop": anim_data.get("loop", True),
                "speed": anim_data.get("speed", 0.1),
            }
        return animations


class BackgroundLayerLoader(AssetLoader):
    """
    Carrega as camadas de background, criando uma lista de objetos BackgroundLayer.
    """

    def load(self) -> list[BackgroundLayer]:
        """
        Carrega as camadas do background.
        'target_size' e 'parallax_scale' são lidos do arquivo JSON.

        Returns:
            list[BackgroundLayer]: Uma lista de objetos BackgroundLayer prontos para uso.
        """
        layers = []
        target_size = self.data.get("target_size")

        for layer_def in self.data.get("layers", []):
            frame_rect = layer_def["frame_rect"]
            # Lê a escala de paralaxe de dentro da definição da camada
            parallax_scale = layer_def.get("parallax_scale", 1.0)

            layer_image = self._get_frame(*frame_rect)

            if target_size:
                layer_image = pg.transform.scale(layer_image, target_size)

            # Cria a instância de BackgroundLayer com a camada e escala
            bg_layer = BackgroundLayer(layer_image, parallax_scale=parallax_scale)
            layers.append(bg_layer)
        return layers
