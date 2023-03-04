import sys
from pathlib import Path


base_dir = Path(__file__).parent.parent
sys.path.append(str(base_dir.joinpath("rplugin/python3/ai-assistant")))
