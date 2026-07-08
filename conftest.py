import pathlib
import sys

# Permite `pytest` sin exportar PYTHONPATH: expone el paquete `app` (backend/).
sys.path.insert(0, str(pathlib.Path(__file__).parent / "backend"))
