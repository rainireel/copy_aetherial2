# Export key symbols for convenience when importing from game package
from .audio import init_mixer, load_sfx, load_music, play, start_ambient_loop # noqa: F401
from .save import load_progress, save_progress # noqa: F401
from .levels import LEVELS, LevelInfo # noqa: F401
from .star import StarHUD # noqa: F401