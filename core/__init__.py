"""
Módulo core - Contém componentes centrais compartilhados por todos os cenários.
"""

from .game_state import State, GameState
from .button import Button
from .font_manager import FontManager
from .base_menu import BaseMenu
from .score_manager import ScoreManager
from .utils import load_json, load_image
from .entity import Entity
from .entity_factory import EntityFactory
from .collision_manager import CollisionManager
from .scroller_manager import ScrollerManager
from .background_manager import BackgroundManager
