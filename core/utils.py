import pygame as pg
import json


def load_json(json_path):
    try:
        with open(json_path, mode="r", encoding="utf-8") as file:
            data = json.load(file)
            return data

    except Exception as e:
        print(f"Erro ao carregar arquivo .json: {json_path}")
        print(f"Erro: {e}")
        return {}


def load_image(path, convert_alpha=True):
    """
    Carrega uma imagem do disco.

    Args:
        path (str): Caminho para a imagem
        scale (float): Fator de escala (opcional)
        convert_alpha (bool): Se deve converter para formato com alpha

    Returns:
        pygame.Surface: Imagem carregada
    """
    try:
        if convert_alpha:
            image = pg.image.load(path).convert_alpha()
        else:
            image = pg.image.load(path).convert()

        return image
    except pg.error as e:
        print(f"Erro ao carregar imagem: {path}")
        print(f"Erro: {e}")
        surface = pg.Surface((50, 50), pg.SRCALPHA)
        surface.fill((255, 0, 255))  # Magenta para indicar erro
        return surface
