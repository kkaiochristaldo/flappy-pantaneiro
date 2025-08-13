import random
from typing import Type, Callable, Any


class EntityFactory:
    """Classe base para todos os obstáculos."""

    def __init__(self):
        self.__entries: list[tuple[Callable[..., Any], float]] = []

    def register(self, entity_cls: Type, weight=1.0):
        self.__entries.append(
            (entity_cls, weight)
        )  # Tupla (entidade, probabilidade de spawn)

    def create_random(self, *args, **kwargs):
        """zip(*...): Separar a lista de tuplas

        Ex: [(Entidade1, 70), (Entidade2, 30)]

        classes = (Entidade1, Entidade2)
        weights = (70, 30)
        """
        classes, weights = zip(*self.__entries)
        entity_classes = random.choices(classes, weights=weights, k=len(self.__entries))
        entity_cls = random.choice(entity_classes)
        return entity_cls(*args, **kwargs)
