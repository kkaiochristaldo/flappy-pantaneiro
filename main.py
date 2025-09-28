import pygame as pg

# Importar configurações
from config import FPS, SCREEN_WIDTH, SCREEN_HEIGHT # Será alterado
from core import GameState

def main():
    """Função principal do jogo."""
    # Inicialização do Pygame
    pg.init()
    pg.display.set_caption("Flappy Pantaneiro")

    # Criar a janela do jogo
    screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pg.time.Clock()

    # Criar gerenciador de estados
    game_state = GameState(screen)

    # Loop principal do jogo
    running = True
    while running:
        # Gerenciar eventos
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False

            # Passar eventos para o estado atual
            running = game_state.handle_event(event)

        # Atualizar o estado atual
        game_state.update()

        # Limpar a tela
        screen.fill((0, 0, 0))
        game_state.render(screen)

        # Atualizar a tela
        pg.display.flip()

        # Controlar FPS
        clock.tick(FPS)

    # Encerrar o Pygame
    pg.quit()


if __name__ == "__main__":
    main()
