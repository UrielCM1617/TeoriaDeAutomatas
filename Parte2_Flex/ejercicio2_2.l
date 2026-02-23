%{
#include <stdio.h>
#include <string.h>
#include <ctype.h>
#include <stdlib.h>

FILE *salida;
int lineas_originales = 0;
int lineas_finales = 0;
int comentarios_eliminados = 0;

char* snake_to_camel(char *snake);
%}

%x COMENTARIO_BLOQUE

/* Definiciones sin caracteres especiales */
IDENTIFICADOR [a-zA-Z_][a-zA-Z0-9_]*
ESPACIOS      [ \t]+
SALTO         \n

%%

"//".* { comentarios_eliminados++; }

"/*"                    { BEGIN(COMENTARIO_BLOQUE); comentarios_eliminados++; }
<COMENTARIO_BLOQUE>"*/" { BEGIN(INITIAL); }
<COMENTARIO_BLOQUE>.    { }
<COMENTARIO_BLOQUE>\n   { lineas_originales++; }

{IDENTIFICADOR} {
    if (strchr(yytext, '_')) {
        char *camel = snake_to_camel(yytext);
        fprintf(salida, "%s", camel);
        free(camel);
    } else {
        fprintf(salida, "%s", yytext);
    }
}

{ESPACIOS}      { fprintf(salida, " "); }

{SALTO}         { 
    lineas_originales++; 
    lineas_finales++; 
    fprintf(salida, "\n"); 
}

.               { fprintf(salida, "%s", yytext); }

%%

int yywrap() { return 1; }

char* snake_to_camel(char *snake) {
    char *camel = malloc(strlen(snake) + 1);
    if (!camel) return NULL;

    int i = 0, j = 0;
    int proxima_mayuscula = 0;

    while (snake[i]) {
        if (snake[i] == '_') {
            if (i > 0 && snake[i+1] != '\0') {
                proxima_mayuscula = 1;
            }
        } else {
            if (proxima_mayuscula) {
                camel[j++] = toupper((unsigned char)snake[i]);
                proxima_mayuscula = 0;
            } else {
                camel[j++] = snake[i];
            }
        }
        i++;
    }
    camel[j] = '\0';
    return camel;
}

int main(int argc, char *argv[]) {
    if (argc < 3) {
        fprintf(stderr, "Uso: %s <entrada> <salida>\n", argv[0]);
        return 1;
    }

    FILE *entrada = fopen(argv[1], "r");
    salida = fopen(argv[2], "w");

    if (!entrada || !salida) {
        perror("Error al abrir archivos");
        return 1;
    }

    yyin = entrada;
    yylex();

    fclose(entrada);
    fclose(salida);

    printf("=== Transformación completada ===\n");
    printf("Líneas originales: %d\n", lineas_originales);
    printf("Líneas finales: %d\n", lineas_finales);
    printf("Comentarios eliminados: %d\n", comentarios_eliminados);
    
    if (lineas_originales > 0) {
        printf("Reducción: %.1f%%\n", 
            100.0 * (lineas_originales - lineas_finales) / lineas_originales);
    }

    return 0;
}