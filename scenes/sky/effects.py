from core import Entity

class Effect(Entity):
    def __init__(self, effect_cfg: dict, x: int, y: int, animation_name: str):
        super().__init__(effect_cfg, x, y)
        self.set_animation(animation_name)

    def update(self, delta_time: float):
        super().update(delta_time)
        # A animação é "loop=false", então _animation_finished será True quando terminar
        if self._animation_finished:
            self.kill()