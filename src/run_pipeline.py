"""
Orquestador del pipeline.
------------------------------------------------------------
Corre las etapas en orden y se detiene en la primera que falle, reportando
cual fue. No re-implementa logica: solo encadena scripts que ya funcionan
por separado.

Ejecutar:  python src/run_pipeline.py
"""

import subprocess
import sys
from pathlib import Path

DIR_SRC = Path(__file__).resolve().parent

ETAPAS = [
    "01_ingesta.py",
    "02_codificacion.py",
    "03_integridad.py",
    "04_features_crudas.py",
    "05_limpieza_texto.py",
    "06_tokenizacion.py",
    "07_stemming.py",
    "08_particion.py",
]


def main():
    print("#" * 70)
    print(f"# Pipeline de preprocesamiento — {len(ETAPAS)} etapas")
    print("#" * 70)

    for numero, etapa in enumerate(ETAPAS, start=1):
        print(f"\n>>> [{numero}/{len(ETAPAS)}] {etapa}")
        resultado = subprocess.run([sys.executable, str(DIR_SRC / etapa)])
        if resultado.returncode != 0:
            print(f"\n[FALLO]    el pipeline se detuvo en {etapa} "
                  f"(codigo {resultado.returncode})")
            sys.exit(resultado.returncode)

    print("\n" + "#" * 70)
    print("# Pipeline completo. train_modelado.csv y test_modelado.csv listos en data/processed/")
    print("#" * 70)


main()
