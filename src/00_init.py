"""
Etapa 0 del pipeline: SETUP DEL ENTORNO
------------------------------------------------------------
Una sola responsabilidad: dejar el entorno listo para correr el pipeline.

  Hace: - crea el entorno virtual .venv/ si no existe
        - instala requirements.txt dentro de ese entorno
        - descarga los corpus de NLTK que usa la etapa 06 (stopwords, wordnet)

Se ejecuta con el python del sistema, NO con el del venv:

    python src/00_init.py
"""

import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DIR_VENV = RAIZ / ".venv"
RUTA_REQUIREMENTS = RAIZ / "requirements.txt"

# Corpus de NLTK que necesita la etapa de tokenizacion.
CORPUS_NLTK = ["stopwords", "wordnet", "omw-1.4"]


def python_del_venv():
    """Ruta al interprete dentro del venv, segun el sistema operativo."""
    if sys.platform == "win32":
        return DIR_VENV / "Scripts" / "python.exe"
    return DIR_VENV / "bin" / "python"


def main():
    print("=" * 70)
    print("Etapa 0: setup del entorno")
    print("=" * 70)

    if DIR_VENV.exists():
        print(f"[ok]       el entorno ya existe en {DIR_VENV.name}/")
    else:
        print(f"[creando]  entorno virtual en {DIR_VENV.name}/")
        subprocess.run([sys.executable, "-m", "venv", str(DIR_VENV)], check=True)

    py = python_del_venv()

    print("[instalando] dependencias de requirements.txt")
    subprocess.run([str(py), "-m", "pip", "install", "--quiet", "--upgrade", "pip"], check=True)
    subprocess.run([str(py), "-m", "pip", "install", "--quiet", "-r", str(RUTA_REQUIREMENTS)],
                   check=True)

    print(f"[instalando] corpus de NLTK: {', '.join(CORPUS_NLTK)}")
    codigo = "import nltk;" + "".join(f"nltk.download('{c}', quiet=True);" for c in CORPUS_NLTK)
    subprocess.run([str(py), "-c", codigo], check=True)

    activar = ".venv\\Scripts\\activate" if sys.platform == "win32" else "source .venv/bin/activate"
    print("\n[ok]       entorno listo. Ahora:")
    print(f"             {activar}")
    print("             python src/run_pipeline.py")


main()
