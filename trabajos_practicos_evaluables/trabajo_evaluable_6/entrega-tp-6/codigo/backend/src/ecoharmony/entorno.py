from pathlib import Path


def leer_env(ruta):
    """Lee un archivo .env (CLAVE=valor por linea). Si no existe devuelve un dict vacio."""
    ruta = Path(ruta)
    if not ruta.exists():
        return {}
    variables = {}
    for linea in ruta.read_text(encoding="utf-8").splitlines():
        linea = linea.strip()
        if not linea or linea.startswith("#"):
            continue
        clave, _, valor = linea.partition("=")
        variables[clave.strip()] = valor.strip()
    return variables
