import re
from collections import Counter

def analizar_log(archivo):
    """Analiza archivo de log y extrae información relevante"""
    try:
        with open(archivo, 'r', encoding='utf-8') as f:
            contenido = f.read()
    except FileNotFoundError:
        print(f"Error: El archivo {archivo} no fue encontrado.")
        return

    # a) Extraer entradas de tipo ERROR (timestamp y mensaje)
    # Buscamos: Fecha y hora, luego [ERROR] y capturamos el resto de la línea
    patron_error = r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) \[ERROR\] (.*)$'
    errores = re.findall(patron_error, contenido, re.MULTILINE)

    # b) Extraer todas las direcciones IP
    patron_ip = r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'
    ips = re.findall(patron_ip, contenido)

    # c) Extraer rutas completas de archivos
    # Buscamos algo que empiece con / y siga con caracteres de ruta/archivo
    patron_archivo = r'(/[a-zA-Z0-9._/-]+\.[a-z]{2,4})'
    archivos = re.findall(patron_archivo, contenido)

    # d) Contar cuántos mensajes hay de cada tipo
    patron_tipo = r'\[(ERROR|INFO|WARNING)\]'
    tipos = re.findall(patron_tipo, contenido)
    contador = Counter(tipos)

    # e) Extraer todos los tiempos de ejecución en milisegundos
    patron_tiempo = r'(\d+ms)'
    tiempos = re.findall(patron_tiempo, contenido)

    # --- Mostrar resultados (Formato según Ejemplo de Salida) ---
    print(f"=== Análisis de {archivo} ===\n")

    print("ERRORES encontrados:")
    for fecha, mensaje in errores:
        print(f"  [{fecha}] {mensaje}")
    
    print("\nIPs detectadas:")
    for ip in set(ips): # Usamos set para no repetir IPs si aparecen varias veces
        print(f"  {ip}")

    print("\nArchivos mencionados:")
    for arc in archivos:
        print(f"  {arc}")

    print("\nResumen por tipo:")
    # Orden específico solicitado: ERROR, INFO, WARNING
    for t in ["ERROR", "INFO", "WARNING"]:
        print(f"  {t}: {contador.get(t, 0)}")

    print("\nTiempos de ejecución:")
    for t in tiempos:
        print(f"  {t}")

if __name__ == "__main__":
    # Asegúrate de que el archivo 'sistema.log' exista en la misma carpeta
    analizar_log("sistema.log")