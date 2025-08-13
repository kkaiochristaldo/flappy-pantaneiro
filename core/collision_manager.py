import pygame as pg


class CollisionManager:
    """
    Centraliza a lógica de detecção de colisão pixel-perfect para o jogador.
    """

    def check_collision(
        self, player: pg.sprite.GroupSingle, other_entity_group: pg.sprite.Group
    ) -> bool:
        """
        Verifica a colisão pixel-perfect entre o jogador e o grupo de entidades.
        Remove a entidade colidida do grupo.

        Args:
            player (pg.sprite.GroupSingle): A instância do sprite do jogador.
            other_group (pg.sprite.Group): O grupo contendo as outras entidades.

        Returns:
            bool: True se houve colisão, False caso contrário.
        """
        # Usa spritecollide com a função de colisão de máscara.
        # Retorna uma lista de sprites de entidades que colidiram.
        collided_entities = pg.sprite.spritecollide(
            sprite=player.sprite,  # O sprite individual a ser verificado.
            group=other_entity_group,  # O grupo contra o qual verificar.
            dokill=True,  # True: remove a entidade do(s) grupo(s) na colisão.
            collided=pg.sprite.collide_mask,  # A função de colisão a ser usada.
        )

        # Se a lista não for vazia, houve colisão.
        return bool(collided_entities)
