%{
#include <stdio.h>
#include <string.h>

/* Activamos el contador de líneas de Flex */
extern int yylineno;

int complejidad = 1; 
int profundidad = 0;
int max_profundidad = 0;
int lineas_codigo = 0;
int lineas_comentario = 0;
int longitud_actual = 0;
int lineas_largas = 0;

/* Control de funciones largas */
int inicio_funcion = 0;
int en_funcion = 0;

typedef struct {
    char nombre[256];
    int longitud;
} Identificador;

Identificador identificadores[1000];
int num_identificadores = 0;

void agregar_identificador(char *nombre);
void detectar_code_smell(char *tipo, int linea, char *detalle);
%}

/* Opción para llevar el conteo de líneas automático */
%option yylineno

%x COMENTARIO

/* Definiciones precisas */
PALABRA_CLAVE  (if|else|while|for|switch|case|return)
OPERADOR_LOGICO (&&|"||")
IDENTIFICADOR  [a-zA-Z_][a-zA-Z0-9_]*

%%

"#".* { /* Ignorar directivas de preprocesador como #include <stdio.h> */ }

{PALABRA_CLAVE} { 
    complejidad++; 
}

{OPERADOR_LOGICO} { complejidad++; }

"{" {
    profundidad++;
    if (profundidad > max_profundidad) max_profundidad = profundidad;
    
    /* Si abrimos llave en nivel 1, probablemente inicia una función */
    if (profundidad == 1) {
        inicio_funcion = yylineno;
        en_funcion = 1;
    }
}

"}" { 
    if (profundidad == 1 && en_funcion) {
        int duracion = yylineno - inicio_funcion;
        if (duracion > 50) {
            detectar_code_smell("FUNCION_LARGA", inicio_funcion, "Más de 50 líneas");
        }
        en_funcion = 0;
    }
    profundidad--; 
}

{IDENTIFICADOR} { 
    agregar_identificador(yytext); 
}

"//".* { lineas_comentario++; }

"/*"            { BEGIN(COMENTARIO); }
<COMENTARIO>"*/" { lineas_comentario++; BEGIN(INITIAL); }
<COMENTARIO>\n   { lineas_comentario++; }
<COMENTARIO>.    { }

\n {
    lineas_codigo++;
    if (longitud_actual > 80) {
        lineas_largas++;
        detectar_code_smell("LINEA_LARGA", yylineno, NULL);
    }
    longitud_actual = 0;
}

[ \t] { longitud_actual++; } /* Contar espacios para longitud de línea */

. { longitud_actual++; }

%%

int yywrap() { return 1; }

void agregar_identificador(char *nombre) {
    /* Evitar que palabras clave se cuenten como identificadores */
    if (strcmp(nombre, "if") == 0 || strcmp(nombre, "else") == 0 || 
        strcmp(nombre, "while") == 0 || strcmp(nombre, "for") == 0 ||
        strcmp(nombre, "int") == 0 || strcmp(nombre, "void") == 0 ||
        strcmp(nombre, "return") == 0 || strcmp(nombre, "char") == 0) {
        return;
    }

    if (num_identificadores < 1000) {
        strncpy(identificadores[num_identificadores].nombre, nombre, 255);
        identificadores[num_identificadores].longitud = strlen(nombre);
        
        /* Detección de variables de una letra */
        if (strlen(nombre) == 1 && 
            nombre[0] != 'i' && nombre[0] != 'j' && nombre[0] != 'k') {
            detectar_code_smell("VAR_UNA_LETRA", yylineno, nombre);
        }
        num_identificadores++;
    }
}

void detectar_code_smell(char *tipo, int linea, char *detalle) {
    printf("CODE SMELL [%s] en línea %d", tipo, linea);
    if (detalle) printf(": %s", detalle);
    printf("\n");
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Uso: %s <archivo.c>\n", argv[0]);
        return 1;
    }

    FILE *archivo = fopen(argv[1], "r");
    if (!archivo) {
        perror("Error");
        return 1;
    }

    yyin = archivo;
    yylex();
    fclose(archivo);

    float ratio = (lineas_codigo > 0) ? (float)lineas_comentario / lineas_codigo : 0;
    float promedio_id = 0;
    for (int i = 0; i < num_identificadores; i++) {
        promedio_id += identificadores[i].longitud;
    }
    if (num_identificadores > 0) promedio_id /= num_identificadores;

    printf("\n=== Métricas de Complejidad ===\n");
    printf("Complejidad ciclomática: %d\n", complejidad);
    printf("Profundidad máxima de anidamiento: %d\n", max_profundidad);
    printf("Líneas de código: %d\n", lineas_codigo);
    printf("Líneas de comentarios: %d\n", lineas_comentario);
    printf("Ratio código/comentarios: %.2f%%\n", ratio * 100);
    printf("Longitud promedio de identificadores: %.2f\n", promedio_id);
    printf("Líneas largas (>80 chars): %d\n", lineas_largas);

    printf("\n=== Evaluación ===\n");
    if (complejidad > 10) printf("- Complejidad alta: considerar refactorizar\n");
    if (max_profundidad > 4) printf("- Anidamiento profundo: simplificar lógica\n");
    if (ratio < 0.1) printf("- Pocos comentarios: mejorar documentación\n");

    return 0;
}