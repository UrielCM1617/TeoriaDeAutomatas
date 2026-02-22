import ply.lex as lex
import json
import datetime
import os
from collections import defaultdict

# --- CONFIGURACIÓN DEL LEXER ---
tokens = ('TIMESTAMP', 'IP', 'LOGIN_FAILED', 'COMMAND_DANGER', 'WORD')
t_ignore = ' \t'

def t_TIMESTAMP(t):
    r'\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}'
    t.value = datetime.datetime.strptime(t.value, '%Y-%m-%d %H:%M:%S')
    return t

def t_IP(t):
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'
    return t

def t_LOGIN_FAILED(t):
    r'Failed\spassword|Login\sfailed|Invalid\suser'
    return t

def t_COMMAND_DANGER(t):
    r'rm\s-rf|dd|mkfs|shutdown|sudo\s-s|chmod\s777'
    return t

def t_WORD(t):
    r'[a-zA-Z0-9:/._-]+'
    return t

def t_error(t):
    t.lexer.skip(1)

lexer = lex.lex()

class AnalizadorSeguridad:
    def __init__(self, config_path):
        # Validación de existencia del archivo de configuración
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"No se encontró el archivo: {config_path}")
            
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        self.alertas = []
        self.historial_logins = defaultdict(list)

    def analizar_linea(self, linea):
        lexer.input(linea)
        datos = {"ts": None, "ip": None, "fail": False, "cmd": None}
        for tok in lexer:
            if tok.type == 'TIMESTAMP': datos["ts"] = tok.value
            elif tok.type == 'IP': datos["ip"] = tok.value
            elif tok.type == 'LOGIN_FAILED': datos["fail"] = True
            elif tok.type == 'COMMAND_DANGER': datos["cmd"] = tok.value

        # A) Detección de Fuerza Bruta
        if datos["fail"] and datos["ip"] and datos["ts"]:
            self.historial_logins[datos["ip"]].append(datos["ts"])
            window = self.config["thresholds"]["window_seconds"]
            intentos = [t for t in self.historial_logins[datos["ip"]] 
                        if (datos["ts"] - t).total_seconds() <= window]
            if len(intentos) >= self.config["thresholds"]["max_login_attempts"]:
                self.registrar_alerta("CRITICAL", f"Fuerza bruta detectada: {datos['ip']}", datos["ts"])

        # B) IPs en Lista Negra
        if datos["ip"] in self.config["blacklist_ips"]:
            self.registrar_alerta("HIGH", f"IP en lista negra detectada: {datos['ip']}", datos["ts"])

        # C) Comandos Peligrosos
        if datos["cmd"]:
            self.registrar_alerta("CRITICAL", f"Comando peligroso detectado: {datos['cmd']}", datos["ts"])

    def registrar_alerta(self, nivel, mensaje, ts):
        self.alertas.append({"nivel": nivel, "mensaje": mensaje, "timestamp": str(ts)})
        print(f"[{nivel}] {ts}: {mensaje}")

    def procesar_log(self, ruta_log):
        if not os.path.exists(ruta_log):
            print(f"Error: El archivo de log '{ruta_log}' no existe.")
            return
        with open(ruta_log, 'r', encoding='utf-8') as f:
            for linea in f:
                self.analizar_linea(linea)

    def generar_reporte_html(self, nombre_archivo="reporte_seguridad.html"):
        conteo = {"CRITICAL": 0, "HIGH": 0}
        for a in self.alertas:
            conteo[a["nivel"]] = conteo.get(a["nivel"], 0) + 1

        html = f"""
        <html>
        <head>
            <title>Reporte de Seguridad</title>
            <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
            <style>
                body {{ font-family: 'Segoe UI', sans-serif; margin: 40px; background: #f8f9fa; }}
                .container {{ max-width: 900px; margin: auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .CRITICAL {{ background: #dc3545; color: white; padding: 3px 8px; border-radius: 4px; font-weight: bold; }}
                .HIGH {{ background: #fd7e14; color: white; padding: 3px 8px; border-radius: 4px; font-weight: bold; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
                th, td {{ padding: 12px; border-bottom: 1px solid #ddd; text-align: left; }}
                th {{ background: #212529; color: white; }}
                .chart-container {{ width: 320px; margin: 20px auto; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1> Reporte de Monitoreo de Seguridad</h1>
                <p>Análisis de archivo: <strong>seguridad.log</strong></p>
                <div class="chart-container"><canvas id="myChart"></canvas></div>
                <table>
                    <tr><th>Nivel</th><th>Fecha y Hora</th><th>Mensaje de Alerta</th></tr>
        """
        for a in self.alertas:
            html += f"<tr><td><span class='{a['nivel']}'>{a['nivel']}</span></td><td>{a['timestamp']}</td><td>{a['mensaje']}</td></tr>"
        
        html += f"""
                </table>
            </div>
            <script>
                new Chart(document.getElementById('myChart'), {{
                    type: 'pie',
                    data: {{
                        labels: ['Crítico (CRITICAL)', 'Alto (HIGH)'],
                        datasets: [{{ 
                            data: [{conteo['CRITICAL']}, {conteo['HIGH']}], 
                            backgroundColor: ['#dc3545', '#fd7e14'] 
                        }}]
                    }},
                    options: {{ plugins: {{ legend: {{ position: 'bottom' }} }} }}
                }});
            </script>
        </body></html>
        """
        with open(nombre_archivo, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"\n Reporte generado: {nombre_archivo}")

if __name__ == "__main__":
    try:
        analizador = AnalizadorSeguridad("config.json")
        # Cambio de nombre de archivo aquí:
        analizador.procesar_log("seguridad.log") 
        analizador.generar_reporte_html()
    except Exception as e:
        print(f"Error de ejecución: {e}")