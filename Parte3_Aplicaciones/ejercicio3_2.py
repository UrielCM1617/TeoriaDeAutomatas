import re
import sys
from typing import List, Tuple

# ─────────────────────────────────────────────
#  Tipos de error
# ─────────────────────────────────────────────
class ErrorValidacion:
    def __init__(self, linea: int, mensaje: str, sugerencia: str):
        self.linea = linea
        self.mensaje = mensaje
        self.sugerencia = sugerencia

    def __str__(self):
        return (f"  [Línea {self.linea}] ERROR: {self.mensaje}\n"
                f"           SUGERENCIA: {self.sugerencia}")


# ─────────────────────────────────────────────
#  Patrones regex
# ─────────────────────────────────────────────

# INI
RE_INI_SECCION  = re.compile(r'^\[([A-Za-z_]\w*)\]$')
RE_INI_CLAVE    = re.compile(r'^([A-Za-z_]\w*)\s*=\s*(.+)$')
RE_INI_COMMENT  = re.compile(r'^;.*$')
RE_INI_EMPTY    = re.compile(r'^\s*$')

# Java Properties
RE_PROP_COMMENT = re.compile(r'^[#!].*$')
RE_PROP_KV      = re.compile(r'^([\w.\-]+)\s*[=:]\s*(.*)$')
RE_PROP_EMPTY   = re.compile(r'^\s*$')

# CSV  — validación de tipos por columna
RE_CSV_INT      = re.compile(r'^\d+$')
RE_CSV_EMAIL    = re.compile(r'^[\w.+-]+@[\w-]+\.[\w.]+$')
RE_CSV_BOOL     = re.compile(r'^(true|false|True|False|TRUE|FALSE)$')
RE_CSV_STRING   = re.compile(r'^.+$')

# Hosts
RE_HOST_IPV4    = re.compile(r'^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$')
RE_HOST_NAME    = re.compile(r'^[A-Za-z0-9]([A-Za-z0-9\-]*[A-Za-z0-9])?(\.[A-Za-z0-9]([A-Za-z0-9\-]*[A-Za-z0-9])?)*$')
RE_HOST_COMMENT = re.compile(r'^#.*$')
RE_HOST_EMPTY   = re.compile(r'^\s*$')


# ─────────────────────────────────────────────
#  Validadores
# ─────────────────────────────────────────────

def validar_ini(lineas: List[str]) -> List[ErrorValidacion]:
    errores = []
    tiene_seccion = False

    for i, linea in enumerate(lineas, 1):
        l = linea.rstrip('\n')
        if RE_INI_EMPTY.match(l) or RE_INI_COMMENT.match(l):
            continue
        if RE_INI_SECCION.match(l):
            tiene_seccion = True
            continue
        if RE_INI_CLAVE.match(l):
            if not tiene_seccion:
                errores.append(ErrorValidacion(
                    i, f"Clave fuera de sección: '{l}'",
                    "Agrega una sección antes, ej: [general]"))
            continue
        # Línea inválida
        errores.append(ErrorValidacion(
            i, f"Sintaxis no reconocida: '{l}'",
            "Usa [seccion], clave = valor, o ; comentario"))

    return errores


def validar_properties(lineas: List[str]) -> List[ErrorValidacion]:
    errores = []

    for i, linea in enumerate(lineas, 1):
        l = linea.rstrip('\n')
        if RE_PROP_EMPTY.match(l) or RE_PROP_COMMENT.match(l):
            continue
        if RE_PROP_KV.match(l):
            continue
        errores.append(ErrorValidacion(
            i, f"Propiedad inválida: '{l}'",
            "Formato: propiedad.nombre = valor  o  propiedad.nombre: valor"))

    return errores


def validar_csv(lineas: List[str]) -> List[ErrorValidacion]:
    """
    Infiere tipos de columna desde la primera fila de datos
    y valida el resto según esos tipos.
    Tipos soportados: int, email, bool, string (fallback)
    """
    errores = []
    if not lineas:
        return errores

    cabecera = lineas[0].rstrip('\n').split(',')
    num_cols = len(cabecera)

    # Inferir tipos con la segunda fila (si existe)
    tipos = ['string'] * num_cols
    if len(lineas) > 1:
        primera_fila = lineas[1].rstrip('\n').split(',')
        for j, valor in enumerate(primera_fila):
            if RE_CSV_INT.match(valor):
                tipos[j] = 'int'
            elif RE_CSV_EMAIL.match(valor):
                tipos[j] = 'email'
            elif RE_CSV_BOOL.match(valor):
                tipos[j] = 'bool'
            else:
                tipos[j] = 'string'

    VALIDADORES = {
        'int':    (RE_CSV_INT,    "entero (ej: 25)"),
        'email':  (RE_CSV_EMAIL,  "email válido (ej: user@mail.com)"),
        'bool':   (RE_CSV_BOOL,   "booleano (true/false)"),
        'string': (RE_CSV_STRING, "cadena no vacía"),
    }

    for i, linea in enumerate(lineas[1:], 2):
        l = linea.rstrip('\n')
        if not l:
            continue
        campos = l.split(',')
        if len(campos) != num_cols:
            errores.append(ErrorValidacion(
                i, f"Se esperaban {num_cols} columnas, se encontraron {len(campos)}",
                f"La cabecera define: {', '.join(cabecera)}"))
            continue
        for j, (campo, tipo) in enumerate(zip(campos, tipos)):
            patron, descripcion = VALIDADORES[tipo]
            if not patron.match(campo):
                errores.append(ErrorValidacion(
                    i, f"Columna '{cabecera[j]}' (col {j+1}): '{campo}' no es {tipo}",
                    f"Se esperaba {descripcion}"))

    return errores


def _ip_valida(m: re.Match) -> bool:
    return all(0 <= int(g) <= 255 for g in m.groups())


def validar_hosts(lineas: List[str]) -> List[ErrorValidacion]:
    errores = []

    for i, linea in enumerate(lineas, 1):
        l = linea.rstrip('\n')
        if RE_HOST_EMPTY.match(l) or RE_HOST_COMMENT.match(l):
            continue

        partes = l.split()
        if len(partes) < 2:
            errores.append(ErrorValidacion(
                i, f"Línea incompleta: '{l}'",
                "Formato: <ip>   <hostname> [alias ...]"))
            continue

        ip_str = partes[0]
        m = RE_HOST_IPV4.match(ip_str)
        if not m:
            errores.append(ErrorValidacion(
                i, f"IP inválida: '{ip_str}'",
                "Usa formato IPv4, ej: 192.168.1.1"))
        elif not _ip_valida(m):
            errores.append(ErrorValidacion(
                i, f"IP fuera de rango: '{ip_str}'",
                "Cada octeto debe estar entre 0 y 255"))

        for nombre in partes[1:]:
            if not RE_HOST_NAME.match(nombre):
                errores.append(ErrorValidacion(
                    i, f"Hostname inválido: '{nombre}'",
                    "Solo letras, dígitos, guiones y puntos; no puede empezar/terminar con guión"))

    return errores


# ─────────────────────────────────────────────
#  Detección automática de formato
# ─────────────────────────────────────────────

def detectar_formato(nombre_archivo: str, lineas: List[str]) -> str:
    ext = nombre_archivo.rsplit('.', 1)[-1].lower() if '.' in nombre_archivo else ''
    if ext == 'ini':
        return 'ini'
    if ext == 'properties':
        return 'properties'
    if ext == 'csv':
        return 'csv'
    if ext in ('hosts', '') and nombre_archivo in ('hosts', '/etc/hosts'):
        return 'hosts'

    # Heurística por contenido
    for l in lineas[:10]:
        l = l.strip()
        if l.startswith('[') and l.endswith(']'):
            return 'ini'
        if re.match(r'^\d+\.\d+\.\d+\.\d+\s+\S', l):
            return 'hosts'
    if lineas and ',' in lineas[0]:
        return 'csv'
    return 'properties'


# ─────────────────────────────────────────────
#  Interfaz principal
# ─────────────────────────────────────────────

VALIDADORES_MAP = {
    'ini':        validar_ini,
    'properties': validar_properties,
    'csv':        validar_csv,
    'hosts':      validar_hosts,
}

def validar_archivo(ruta: str, formato: str = None) -> None:
    try:
        with open(ruta, 'r', encoding='utf-8') as f:
            lineas = f.readlines()
    except FileNotFoundError:
        print(f"[ERROR] Archivo no encontrado: {ruta}")
        return

    fmt = formato or detectar_formato(ruta, lineas)
    if fmt not in VALIDADORES_MAP:
        print(f"[ERROR] Formato desconocido: '{fmt}'. Opciones: {list(VALIDADORES_MAP)}")
        return

    print(f"\n{'='*55}")
    print(f"  Validando: {ruta}  (formato: {fmt.upper()})")
    print(f"{'='*55}")

    errores = VALIDADORES_MAP[fmt](lineas)

    if not errores:
        print("  ✔  Validación exitosa. Sin errores encontrados.")
    else:
        print(f"  ✖  Se encontraron {len(errores)} error(es):\n")
        for e in errores:
            print(e)
    print()


# ─────────────────────────────────────────────
#  Demo interactivo (sin archivo externo)
# ─────────────────────────────────────────────

def demo():
    import tempfile, os

    casos = {
        'ini': (
            "config.ini",
            "[seccion]\nclave = valor\n; comentario\n\nsin_seccion_al_inicio\n"
        ),
        'properties': (
            "app.properties",
            "# Comentario\npropiedad.nombre = valor\nclave_invalida!\n"
        ),
        'csv': (
            "datos.csv",
            "nombre,edad,email,activo\nJuan,25,juan@mail.com,true\nAna,abc,noesmail,si\n"
        ),
        'hosts': (
            "hosts",
            "127.0.0.1   localhost\n192.168.1.1 gateway\n999.1.1.1   bad_ip\n"
        ),
    }

    for fmt, (nombre, contenido) in casos.items():
        with tempfile.NamedTemporaryFile(mode='w', suffix='_'+nombre,
                                         delete=False, encoding='utf-8') as tmp:
            tmp.write(contenido)
            tmp_path = tmp.name
        validar_archivo(tmp_path, fmt)
        os.unlink(tmp_path)


if __name__ == '__main__':
    if len(sys.argv) >= 2:
        fmt_arg = sys.argv[2] if len(sys.argv) >= 3 else None
        validar_archivo(sys.argv[1], fmt_arg)
    else:
        print("Modo demo — ejecutando casos de prueba...\n")
        demo()