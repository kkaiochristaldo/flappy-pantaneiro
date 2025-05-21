# 🛠️ README Interno – Projeto Flappy Pantaneiro

## 🎯 Objetivo do Projeto

Desenvolver um jogo estilo Flappy Bird com **três mapas distintos**:
- 🌤️ **Céu**
- 🌳 **Terra**
- 🌊 **Água**

Cada bioma será desenvolvido por um time específico. O jogo contará com um **menu inicial** e uma **versão final integrada** que reúne os três mapas.

---

## 🌿 Branches Atuais

- `dev-sky` — desenvolvimento do cenário Céu
- `dev-earth` — desenvolvimento do cenário Terra
- `dev-water` — desenvolvimento do cenário Água
- `menu` — desenvolvimento da tela inicial e navegação entre mapas
- `main` — branch principal com a integração dos mapas, menu e funcionalidades gerais

---

## 🚧 Fluxo de Trabalho com Git

Trabalharemos com acesso direto para todos como colaboradores no repositório.

1. Cada time deve trabalhar **somente na sua branch** (`dev-sky`, `dev-earth` ou `dev-water`).
2. Faça commits pequenos e frequentes, sempre com mensagens claras.
3. Utilize o padrão para mensagens de commit (em português): [padrões de commits](https://github.com/iuricode/padroes-de-commits).
4. Antes de começar o dia, atualize sua branch local com `git pull origin <sua-branch>`.
5. Faça `push` apenas ao finalizar as tarefas do dia.
6. Após concluir uma funcionalidade ou etapa, envie o código com `git push` para sua branch.
7. Quando o cenário do seu time estiver finalizado, informe para realizarmos o **merge controlado na branch `main`**.
8. Sempre converse com seu time, adicione comentarios(em português), deixe o seu código o mais simples possível.
9. Cada time deve criar um arquivo.md ou algum tipo de documento para escrever as ideias que estão desenvolvendo.

---

## 🎯 Principais Comandos Git

| Comando                                 | Descrição                                                  |
|----------------------------------------|------------------------------------------------------------|
| `git branch`                           | Lista todas as branches locais                              |
| `git checkout <nome-branch>`           | Troca para a branch especificada                            |
| `git add <arquivos>`                    | Adiciona arquivos à área de stage para commit              |
| `git commit -m "mensagem"`              | Cria um commit com a mensagem informada                     |
| `git status`                           | Exibe os arquivos modificados e o estado do repositório    |
| `git log --oneline`                    | Mostra o histórico resumido de commits                      |
| `git pull origin <nome-branch>`        | Atualiza sua branch local com as alterações da branch remota|
| `git push origin <nome-branch>`        | Envia suas alterações locais para a branch remota          |
| `git cherry-pick <hash-do-commit>`     | Aplica um commit específico de outra branch na atual       |

---

## 📁 Organização de Pastas
```
flappy-pantaneiro/
│
├── assets/                     # Recursos visuais, sons, fontes etc.
│   ├── images/                                                      
│   │   ├── sky/                # Imagens para cenário Céu
│   │   ├── earth/              # Imagens para cenário Terra
│   │   └── water/              # Imagens para cenário Água
│   ├── sounds/                 # Sons do jogo
│   └── fonts/                  # Fontes para textos e HUD
│
├── src/                       # Código fonte
│   ├── menu/                  # Código do menu inicial
│   │   ├── __init__.py
│   │   └── menu.py
│   │
│   ├── sky/                   # Código específico do cenário Céu
│   │   ├── __init__.py
│   │   └── sky_level.py
│   │
│   ├── earth/                 # Código específico do cenário Terra
│   │   ├── __init__.py
│   │   └── earth_level.py
│   │
│   ├── water/                 # Código específico do cenário Água
│   │   ├── __init__.py
│   │   └── water_level.py
│   │
│   ├── game.py                # Controle do jogo (loop principal, troca de cenas)
│   └── settings.py            # Configurações globais (resolução, FPS, etc.)
│
├── main.py                    # Arquivo principal para iniciar o jogo
├── requirements.txt           # Dependências do projeto (ex: pygame)
└── README.md                  # Documentação do projeto
```
---

## 👥 Times

| Time        | Integrantes           | Branch        |
|-------------|------------------------|----------------|
| **Sky**     | [Ana], [Caio], [Sizenando] | `dev-sky`      |
| **Earth**   | [Gabriel], [Henrique], [Luana] | `dev-earth`    |
| **Water**   | [Barbara], [Guilherme], [Kaio] | `dev-water`    |
| **Menu**    | (definir responsáveis)   | `menu`         |
| **Main**    | [Henrique], [Kaio]       | `main`         |