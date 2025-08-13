class ScrollerManager:
    """
    Gerencia a rolagem automática da cena e a progressão de dificuldade contínua.
    """

    def __init__(self, scroller_cfg: dict):
        """
        Inicializa o scroller com base na configuração da cena.

        Args:
            scroller_cfg (dict): Dicionário de configuração contendo:
                                 - initial_speed
                                 - max_difficulty_multiplier
                                 - difficulty_increase_rate
        """
        # Atributos de Configuração
        self._initial_speed = scroller_cfg.get("initial_speed", 10.0)
        self._max_difficulty_multiplier = scroller_cfg.get(
            "max_difficulty_multiplier", 2.0
        )
        self._difficulty_increase_rate = scroller_cfg.get(
            "difficulty_increase_rate", 0.02
        )

        # Atributos de Estado
        self.__current_speed = self._initial_speed
        self.__difficulty_timer = 0.0
        self.__scroll_x = 0.0
        self._is_stopped = False

    @property
    def current_speed(self) -> float:
        """Getter da velocidade atual"""
        return self.__current_speed

    @property
    def scroll_x(self) -> float:
        """Getter do scroll_x"""
        return self.__scroll_x

    def update(self, delta_time):
        """
        Atualiza a rolagem e a dificuldade com base no tempo decorrido.

        Args:
            delta_time (float): O tempo em segundos desde o último quadro.
        """
        if self._is_stopped:
            return

        # A rolagem agora usa a velocidade que é atualizada constantemente
        self.__scroll_x += self.__current_speed * delta_time
        self.__difficulty_timer += delta_time

        # Atualiza a dificuldade (e consequentemente a _current_speed)
        self.__update_difficulty()

    def __update_difficulty(self):
        """
        Calcula e aplica o aumento de dificuldade com base no tempo.
        """
        # O multiplicador aumenta linearmente com o tempo
        difficulty_multiplier = (
            1.0 + self.__difficulty_timer * self._difficulty_increase_rate
        )

        # Limita o multiplicador ao valor máximo definido
        capped_multiplier = min(difficulty_multiplier, self._max_difficulty_multiplier)

        # A velocidade atual é sempre baseada na velocidade inicial * o multiplicador
        self.__current_speed = self._initial_speed * capped_multiplier

    def stop(self):
        """Para a rolagem e o cronômetro de dificuldade."""
        self._is_stopped = True

    def resume(self):
        """Retoma a rolagem."""
        self._is_stopped = False

    def reset(self):
        """Reseta o scroller para o estado inicial de uma nova partida."""
        self.__scroll_x = 0.0
        self.__difficulty_timer = 0.0
        self.__current_speed = self._initial_speed
        self.resume()
        print(
            f"[SceneScroller] Sistema resetado. Velocidade inicial: {self.__current_speed}"
        )
