"""
macros.py — Puente xlwings entre Excel y Python.
Llama las funciones de cierres_android_tv.py desde macros VBA.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cierres_android_tv import main, fetch_data, prepare_data


def actualizar_datos():
    """Llamada desde Excel: regenera el informe completo."""
    try:
        ok = main()
        return "✅ Informe actualizado correctamente" if ok else "⚠️ Sin datos para hoy"
    except Exception as e:
        return f"❌ Error: {e}"
