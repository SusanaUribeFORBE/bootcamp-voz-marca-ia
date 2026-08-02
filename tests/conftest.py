import sys
from pathlib import Path

# Permite `from src...` sin importar cómo se invoque pytest.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
