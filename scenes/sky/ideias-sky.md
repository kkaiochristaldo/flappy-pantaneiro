# Documento de Ideias - Cenário Céu (dev-sky)

## 1. Visão Geral
O cenário "Céu" é um nível de scroller infinito no estilo "Flappy Bird". O jogador controla um pássaro que deve voar através de aberturas em obstáculos para marcar pontos. A dificuldade pode aumentar progressivamente com a velocidade do jogo.

## 2. Personagem (Player)
- **Nome:** SkyPlayer (implementado em `player.py`).
- **Asset:** `assets/images/sky/passaro.png`.
- **Mecânica Principal:**
  - **Gravidade:** O pássaro está constantemente sob o efeito da gravidade, puxando-o para baixo.
  - **Flap (Pulo):** Ao pressionar a barra de espaço ou o botão do mouse, o pássaro recebe um impulso vertical para cima, combatendo a gravidade.
  - **Controle:** O único controle do jogador é o "flap". Não há movimento horizontal controlado pelo jogador.

## 3. Obstáculos
- **Nome:** SkyObstacle (implementado em `obstacles.py`).
- **Asset:** `assets/images/sky/obstaculo_nuvem.png`.
- **Mecânica:**
  - Os obstáculos são gerados em pares (um em cima, outro embaixo) com uma abertura vertical entre eles.
  - A altura dessa abertura é gerada aleatoriamente para criar desafios variados.
  - Eles surgem na direita da tela e se movem para a esquerda em uma velocidade constante.
  - Um `ObstacleManager` controla a frequência de surgimento e a remoção dos obstáculos que saem da tela.

## 4. Cenário (Background)
- **Nome:** SkyBackground (implementado em `background.py`).
- **Asset:** `assets/images/sky/background_ceu.png`.
- **Mecânica:**
  - O fundo se move continuamente da direita para a esquerda, mais lentamente que os obstáculos, para criar um efeito de paralaxe e a sensação de profundidade e movimento.
  - A imagem de fundo é repetida de forma contínua (seamless).

## 5. Pontuação (Score)
- A pontuação é incrementada em 1 para cada par de obstáculos que o jogador consegue atravessar com sucesso.
- A lógica de pontuação é implementada em `scene.py` e verifica quando um obstáculo cruza a posição horizontal do pássaro.

## 6. Fim de Jogo (Game Over)
A partida termina se uma das seguintes condições for atendida:
- O pássaro colide com um