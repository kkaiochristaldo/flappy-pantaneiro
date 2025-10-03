import pygame as pg
from config import FPS
from core import GameState
import sys

def main():
    """Função principal do jogo."""
    pg.init()
    pg.mixer.init()  # Inicializa o mixer de som
    pg.display.set_caption("Flappy Pantaneiro")

    # 1. Defina a resolução para a qual seu jogo foi projetado.
    # Esta será sua "tela virtual".
    VIRTUAL_WIDTH, VIRTUAL_HEIGHT = 1080, 700

    # Carrega a música de fundo
    pg.mixer.music.load("songs/menus/trilha_sonora.mp3")

    # Reproduz (loops=-1 significa repetir infinitamente)
    pg.mixer.music.play(loops=-1)

    # 2. Crie a tela real em modo tela cheia para detectar o tamanho do monitor.
    screen = pg.display.set_mode((0, 0), pg.FULLSCREEN)
    REAL_WIDTH, REAL_HEIGHT = screen.get_size()

    # 3. Crie a superfície virtual onde TODO o jogo será desenhado.
    game_surface = pg.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT))

    # 4. Calcule a escala para manter a proporção (letterboxing).
    scale_ratio = min(REAL_WIDTH / VIRTUAL_WIDTH, REAL_HEIGHT / VIRTUAL_HEIGHT)
    scaled_width = int(VIRTUAL_WIDTH * scale_ratio)
    scaled_height = int(VIRTUAL_HEIGHT * scale_ratio)
    
    offset_x = (REAL_WIDTH - scaled_width) // 2
    offset_y = (REAL_HEIGHT - scaled_height) // 2

    clock = pg.time.Clock()

    game_state = GameState(game_surface)

    running = True
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                running = False
            running = game_state.handle_event(event)

        game_state.update()

        game_state.render(game_surface) # O método render agora desenha em 'game_surface'.

        scaled_surface = pg.transform.smoothscale(game_surface, (scaled_width, scaled_height))
        
        screen.fill((0, 0, 0)) # Fundo preto para as "barras"
        screen.blit(scaled_surface, (offset_x, offset_y))

        pg.display.flip()
        clock.tick(FPS)

    pg.quit()
    sys.exit()

if __name__ == "__main__":
    main()