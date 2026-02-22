import re
from collections import defaultdict

class GeneradorAFND:
    def __init__(self, regex):
        self.regex = regex
        self.estados = set()
        self.transiciones = defaultdict(lambda: defaultdict(set))
        self.estado_inicial = None
        self.estados_finales = set()
        self.alfabeto = sorted(list(set(re.findall(r'[a-zA-Z0-9]', regex))))
        self.contador_estados = 0

    def nuevo_estado(self):
        estado = f"q{self.contador_estados}"
        self.contador_estados += 1
        self.estados.add(estado)
        return estado

    def validar_regex(self):
        # Soporta letras, números y los operadores: | * + ? ( )
        patron = r'^[a-zA-Z0-9|()*+?]+$'
        if not re.fullmatch(patron, self.regex): return False
        pila = []
        for c in self.regex:
            if c == '(': pila.append(c)
            elif c == ')':
                if not pila: return False
                pila.pop()
        return len(pila) == 0

    def infix_to_postfix(self, regex):
        # 1. Insertar concatenación explícita '.'
        res = ""
        for i in range(len(regex)):
            res += regex[i]
            if i + 1 < len(regex):
                c1, c2 = regex[i], regex[i+1]
                if (c1.isalnum() or c1 in '*+?)') and (c2.isalnum() or c2 == '('):
                    res += '.'
        
        # 2. Shunting-yard
        precedencia = {'*': 4, '+': 4, '?': 4, '.': 3, '|': 2}
        salida, pila = [], []
        for c in res:
            if c.isalnum(): salida.append(c)
            elif c == '(': pila.append(c)
            elif c == ')':
                while pila and pila[-1] != '(': salida.append(pila.pop())
                pila.pop()
            else:
                while pila and pila[-1] != '(' and precedencia.get(c, 0) <= precedencia.get(pila[-1], 0):
                    salida.append(pila.pop())
                pila.append(c)
        while pila: salida.append(pila.pop())
        return salida

    def generar_afnd(self):
        postfix = self.infix_to_postfix(self.regex)
        pila = []

        for simbolo in postfix:
            if simbolo.isalnum():
                ini, fin = self.nuevo_estado(), self.nuevo_estado()
                self.transiciones[ini][simbolo].add(fin)
                pila.append((ini, fin))
            elif simbolo == '*':
                a_ini, a_fin = pila.pop()
                ini, fin = self.nuevo_estado(), self.nuevo_estado()
                self.transiciones[ini]['ε'] = {a_ini, fin}
                self.transiciones[a_fin]['ε'] = {a_ini, fin}
                pila.append((ini, fin))
            elif simbolo == '+':
                a_ini, a_fin = pila.pop()
                ini, fin = self.nuevo_estado(), self.nuevo_estado()
                self.transiciones[ini]['ε'] = {a_ini}
                self.transiciones[a_fin]['ε'] = {a_ini, fin}
                pila.append((ini, fin))
            elif simbolo == '?':
                a_ini, a_fin = pila.pop()
                ini, fin = self.nuevo_estado(), self.nuevo_estado()
                self.transiciones[ini]['ε'] = {a_ini, fin}
                self.transiciones[a_fin]['ε'] = {fin}
                pila.append((ini, fin))
            elif simbolo == '|':
                (a2_i, a2_f), (a1_i, a1_f) = pila.pop(), pila.pop()
                ini, fin = self.nuevo_estado(), self.nuevo_estado()
                self.transiciones[ini]['ε'] = {a1_i, a2_i}
                self.transiciones[a1_f]['ε'] = {fin}
                self.transiciones[a2_f]['ε'] = {fin}
                pila.append((ini, fin))
            elif simbolo == '.':
                (a2_i, a2_f), (a1_i, a1_f) = pila.pop(), pila.pop()
                self.transiciones[a1_f]['ε'] = {a2_i}
                pila.append((a1_i, a2_f))

        self.estado_inicial, final = pila.pop()
        self.estados_finales.add(final)

    def mostrar_automata(self):
        print(f"\n=== Autómata para: {self.regex} ===")
        print(f"Estados: {{{', '.join(sorted(self.estados, key=lambda x: int(x[1:])))}}}")
        print(f"Alfabeto: {{{', '.join(self.alfabeto)}}}")
        print(f"Estado inicial: {self.estado_inicial}")
        print(f"Estados finales: {{{', '.join(self.estados_finales)}}}")

        # Dibujar Tabla
        cols = self.alfabeto + (['ε'] if any('ε' in d for d in self.transiciones.values()) else [])
        header = f"+----------" + "".join([f"+-----------" for _ in cols]) + "+"
        print("\nTabla de transiciones:")
        print(header)
        print(f"| Estado   " + "".join([f"| {c:<9} " for c in cols]) + "|")
        print(header)
        
        for est in sorted(self.estados, key=lambda x: int(x[1:])):
            linea = f"| {est:<8} "
            for c in cols:
                dest = self.transiciones[est].get(c, set())
                dest_str = "{" + ",".join(sorted(dest)) + "}" if dest else "{}"
                linea += f"| {dest_str:<9} "
            print(linea + "|")
        print(header)

        # Razón de No Determinismo
        tiene_epsilon = any('ε' in self.transiciones[e] for e in self.estados)
        multi_trans = any(len(self.transiciones[e][s]) > 1 for e in self.estados for s in self.transiciones[e])
        
        if tiene_epsilon or multi_trans:
            print("\nTipo de autómata: AFND (No Determinista)")
            razon = "Tiene transiciones ε" if tiene_epsilon else "Tiene múltiples destinos para un mismo símbolo"
            print(f"Razón: {razon}")
        else:
            print("\nTipo de autómata: AFD (Determinista)")

if __name__ == "__main__":
    regex_input = "(a|b)*abb"
    gen = GeneradorAFND(regex_input)
    if gen.validar_regex():
        gen.generar_afnd()
        gen.mostrar_automata()
    else:
        print("Regex inválida.")