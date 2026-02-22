import re

class CifradorROT:
    def __init__(self, n=13):
        self.n = n
        # Lista de expresiones regulares para proteger (Punto b)
        self.patrones_regex = [
            r'https?://\S+',                   # URLs con http/https
            r'www\.\S+',                        # URLs con www
            r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', # Emails
            r'\(\d{3}\) \d{3}-\d{4}',           # Teléfonos (XXX) XXX-XXXX
            r'\d{2}/\d{2}/\d{4}',               # Fechas DD/MM/YYYY
            r'\d{4}-\d{2}-\d{2}'                # Fechas YYYY-MM-DD
        ]

    def cifrar_caracter(self, char, n_actual):
        """Aplica la rotación solo a letras, preservando mayúsculas/minúsculas"""
        if 'a' <= char <= 'z':
            # (Orden en abecedario + rotación) % 26
            return chr((ord(char) - ord('a') + n_actual) % 26 + ord('a'))
        elif 'A' <= char <= 'Z':
            return chr((ord(char) - ord('A') + n_actual) % 26 + ord('A'))
        return char # No cifra dígitos ni símbolos

    def procesar_texto(self, texto, n_actual):
        """Lógica central: Protege patrones, cifra el resto y restaura"""
        # 1. Identificar y extraer todo lo que DEBE protegerse
        protegidos = []
        
        # Unimos todos los patrones en uno solo usando OR (|)
        regex_total = "|".join(f"({p})" for p in self.patrones_regex)
        
        def guardar_y_marcar(match):
            protegidos.append(match.group(0))
            return f"__PROT_{len(protegidos)-1}__"

        # Marcamos el texto: "hola juan@mail.com" -> "hola __PROT_0__"
        texto_marcado = re.sub(regex_total, guardar_y_marcar, texto)

        # 2. Cifrar el texto que quedó (el que tiene los marcadores)
        lista_cifrada = [self.cifrar_caracter(c, n_actual) for c in texto_marcado]
        texto_cifrado = "".join(lista_cifrada)

        # 3. Restaurar los protegidos
        # Nota: Los marcadores "__PROT_X__" ahora pueden estar cifrados si N != 0
        # Pero como los marcadores usan guiones bajos y números (que no se cifran),
        # solo rotan las letras 'PROT'. Los buscaremos con cuidado.
        
        def restaurar(match):
            indice = int(match.group(1))
            return protegidos[indice]

        # Buscamos el marcador cifrado (PROT rotado n veces)
        marcador_busqueda = "".join([self.cifrar_caracter(c, n_actual) for c in "PROT"])
        patron_restaurar = fr'__{marcador_busqueda}_(\d+)__'
        
        return re.sub(patron_restaurar, restaurar, texto_cifrado)

    def cifrar_texto(self, texto):
        return self.procesar_texto(texto, self.n)

    def descifrar_texto(self, texto):
        # Descifrar es simplemente rotar en dirección opuesta (26 - N)
        return self.procesar_texto(texto, 26 - self.n)

    def cifrar_archivo(self, entrada, salida):
        try:
            with open(entrada, 'r', encoding='utf-8') as f:
                texto = f.read()
            resultado = self.cifrar_texto(texto)
            with open(salida, 'w', encoding='utf-8') as f:
                f.write(resultado)
            print(f"Archivo cifrado con éxito: {salida}")
        except FileNotFoundError:
            print(f"Error: No se encontró el archivo {entrada}")

    def descifrar_archivo(self, entrada, salida):
        try:
            with open(entrada, 'r', encoding='utf-8') as f:
                texto = f.read()
            resultado = self.descifrar_texto(texto)
            with open(salida, 'w', encoding='utf-8') as f:
                f.write(resultado)
            print(f"Archivo descifrado con éxito: {salida}")
        except FileNotFoundError:
            print(f"Error: No se encontró el archivo {entrada}")

# --- Ejemplo de Ejecución ---
if __name__ == "__main__":
    # Creamos un archivo de prueba 
    with open("entrada.txt", "w", encoding="utf-8") as f:
        f.write("Contacto: Uriel@email.com\n")
        f.write("Telefono: (555) 123-4567\n")
        f.write("Fecha: 13/12/2002\n")
        f.write("Visita: https://ejemplo.com\n\n")
        f.write("Este es un mensaje, no lo leas.")

    cifrador = CifradorROT(n=13)
    cifrador.cifrar_archivo("entrada.txt", "cifrado_rot13.txt")
    cifrador.descifrar_archivo("cifrado_rot13.txt", "descifrado.txt")