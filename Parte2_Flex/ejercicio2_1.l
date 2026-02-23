%{
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <ctype.h>

typedef struct {
    char *palabra;
    int frecuencia;
} Palabra;

int total_palabras = 0;
int total_numeros = 0;
long suma_longitudes = 0;

Palabra diccionario[2000];
int num_distintas = 0;

char *emails[500], *urls[500], *compuestas[500];
int n_emails = 0, n_urls = 0, n_compuestas = 0;

void agregar_palabra(char *p) {
    char temp[256];
    int i;
    for(i = 0; p[i]; i++) temp[i] = tolower((unsigned char)p[i]);
    temp[i] = '\0';

    for (int j = 0; j < num_distintas; j++) {
        if (strcmp(diccionario[j].palabra, temp) == 0) {
            diccionario[j].frecuencia++;
            return;
        }
    }
    if (num_distintas < 2000) {
        diccionario[num_distintas].palabra = strdup(temp);
        diccionario[num_distintas].frecuencia = 1;
        num_distintas++;
    }
}

void guardar_u(char **lista, int *cont, char *val) {
    for (int i = 0; i < *cont; i++) {
        if (strcmp(lista[i], val) == 0) return;
    }
    if (*cont < 500) lista[(*cont)++] = strdup(val);
}
%}

LETRA       [a-zA-ZáéíóúÁÉÍÓÚñÑ]
DIGITO      [0-9]
URL_CHARS   [a-zA-Z0-9\-\.]

%%

{LETRA}+@{LETRA}+\.{LETRA}+ {
    guardar_u(emails, &n_emails, yytext);
}

(https?:\/\/|www\.){URL_CHARS}+\.[a-z]+ {
    guardar_u(urls, &n_urls, yytext);
}

{LETRA}+(-{LETRA}+)+ {
    total_palabras++;
    suma_longitudes += yyleng;
    agregar_palabra(yytext);
    guardar_u(compuestas, &n_compuestas, yytext);
}

{LETRA}+ {
    total_palabras++;
    suma_longitudes += yyleng;
    agregar_palabra(yytext);
}

{DIGITO}+ {
    total_numeros++;
}

[ \t\n\r]+ { }
.          { }

%%

int yywrap() { return 1; }

int comp(const void *a, const void *b) {
    return ((Palabra*)b)->frecuencia - ((Palabra*)a)->frecuencia;
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        printf("Falta el archivo. Uso: %s archivo.txt\n", argv[0]);
        return 1;
    }
    
    FILE *f = fopen(argv[1], "r");
    if (!f) {
        perror("No se pudo abrir el archivo");
        return 1;
    }
    
    yyin = f; 
    yylex();
    fclose(f);
    
    printf("--- RESULTADOS DEL ANALISIS ---\n\n");
    printf("Palabras totales: %d\n", total_palabras);
    printf("Numeros encontrados: %d\n", total_numeros);
    printf("Longitud promedio: %.2f\n", total_palabras ? (float)suma_longitudes/total_palabras : 0);
    
    qsort(diccionario, num_distintas, sizeof(Palabra), comp);
    printf("\nPalabras mas frecuentes:\n");
    int tope = (num_distintas < 10) ? num_distintas : 10;
    for (int i = 0; i < tope; i++)
        printf("  %d. %s (%d)\n", i+1, diccionario[i].palabra, diccionario[i].frecuencia);

    printf("\nCorreos detectados:\n");
    for(int i=0; i<n_emails; i++) printf("  - %s\n", emails[i]);

    printf("\nURLs detectadas:\n");
    for(int i=0; i<n_urls; i++) printf("  - %s\n", urls[i]);

    printf("\nPalabras con guion:\n");
    for(int i=0; i<n_compuestas; i++) printf("  - %s\n", compuestas[i]);
    
    return 0;
}