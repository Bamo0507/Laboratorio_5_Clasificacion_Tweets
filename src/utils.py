"""
Utilidades compartidas por todas las etapas del pipeline.
------------------------------------------------------------
Hacen que cada etapa se lea igual: cargar -> validar -> transformar
-> validar -> guardar, y que el log cuente la historia de que paso.

Prefijos de log: [cargado] [guardado] [ok] [FALLO] [creando] [instalando]
"""

import sys

import pandas as pd


def banner(titulo):
    """Separador visual con el titulo de la etapa."""
    print("=" * 70)
    print(titulo)
    print("=" * 70)


def cargar(ruta, **kwargs):
    """Lee un csv y reporta lo que entro."""
    df = pd.read_csv(ruta, **kwargs)
    print(f"[cargado]  {ruta.name} -> {len(df):,} filas, {df.shape[1]} columnas")
    return df


def guardar(df, ruta):
    """Escribe el csv creando el directorio si hace falta."""
    ruta.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(ruta, index=False)
    print(f"[guardado] {ruta.name} -> {len(df):,} filas, {df.shape[1]} columnas")


def afirmar(condicion, mensaje):
    """
    Validacion fail-fast. Si no se cumple, corta el pipeline en el punto
    exacto donde se rompio el contrato en lugar de arrastrar datos malos.
    """
    if condicion:
        print(f"[ok]       {mensaje}")
    else:
        print(f"[FALLO]    {mensaje}")
        sys.exit(1)


def afirmar_columnas(df, columnas, contexto):
    """Verifica que existan todas las columnas que promete la etapa anterior."""
    faltantes = [c for c in columnas if c not in df.columns]
    afirmar(not faltantes, f"{contexto}: estan las columnas {columnas}"
                           + (f" | faltan {faltantes}" if faltantes else ""))
