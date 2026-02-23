%{
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <dirent.h>
#include <sys/stat.h>

#define MAX_LINEA 1024
#define COLOR_ROJO "\033[1;31m"
#define COLOR_RESET "\033[0m"

char patron_busqueda[256];
int num_linea = 0;
int coincidencias = 0;
int contexto = 0;
int ultima_linea_impresa = 0;

typedef struct {
    int num_linea;
    char texto[MAX_LINEA];
} Linea;

Linea buffer_contexto[100]; 
int pos_buffer = 0;
int lineas_en_buffer = 0;

void mostrar_coincidencia(int num, char *linea);
void agregar_a_buffer(int num, char *linea);
void buscar_en_archivo(const char *path);
void buscar_en_directorio(const char *nombre_dir);
%}

%%

.* {
    num_linea++;
    char linea_actual[MAX_LINEA];
    // Limpiamos el buffer local antes de copiar
    memset(linea_actual, 0, MAX_LINEA);
    strncpy(linea_actual, yytext, MAX_LINEA - 1);

    if (strstr(linea_actual, patron_busqueda)) {
        coincidencias++;

        // 1. Mostrar contexto previo
        int lineas_a_mostrar = (lineas_en_buffer < contexto) ? lineas_en_buffer : contexto;
        int indice_inicio = (pos_buffer - lineas_a_mostrar + 100) % 100;
        
        for(int i = 0; i < lineas_a_mostrar; i++) {
            int idx = (indice_inicio + i) % 100;
            if (buffer_contexto[idx].num_linea > ultima_linea_impresa) {
                printf("  %d: %s\n", buffer_contexto[idx].num_linea, buffer_contexto[idx].texto);
                ultima_linea_impresa = buffer_contexto[idx].num_linea;
            }
        }

        // 2. Mostrar la coincidencia
        mostrar_coincidencia(num_linea, linea_actual);
        ultima_linea_impresa = num_linea;
    }
    
    agregar_a_buffer(num_linea, linea_actual);
}

\n { /* Ignorar el salto de línea para que no ensucie el buffer */ }

<<EOF>> { return 0; }

%%

int yywrap() { return 1; }

void mostrar_coincidencia(int num, char *linea) {
    char *pos = strstr(linea, patron_busqueda);
    if (pos) {
        printf("%d: ", num);
        fwrite(linea, 1, pos - linea, stdout);
        printf("%s%s%s", COLOR_ROJO, patron_busqueda, COLOR_RESET);
        printf("%s\n", pos + strlen(patron_busqueda));
    }
}

void agregar_a_buffer(int num, char *linea) {
    buffer_contexto[pos_buffer].num_linea = num;
    strncpy(buffer_contexto[pos_buffer].texto, linea, MAX_LINEA - 1);
    pos_buffer = (pos_buffer + 1) % 100;
    if (lineas_en_buffer < 100) lineas_en_buffer++;
}

void buscar_en_archivo(const char *path) {
    FILE *f = fopen(path, "r");
    if (!f) return;
    
    num_linea = 0;
    lineas_en_buffer = 0;
    pos_buffer = 0;
    ultima_linea_impresa = 0;
    
    printf("\n--- Archivo: %s ---\n", path);
    yyrestart(f); // Es mejor usar yyrestart para limpiar el estado del scanner
    yylex();
    fclose(f);
}

void buscar_en_directorio(const char *nombre_dir) {
    struct dirent *entry;
    DIR *dp = opendir(nombre_dir);
    if (!dp) return;

    while ((entry = readdir(dp))) {
        if (strcmp(entry->d_name, ".") == 0 || strcmp(entry->d_name, "..") == 0)
            continue;

        char path[1024];
        snprintf(path, sizeof(path), "%s/%s", nombre_dir, entry->d_name);
        struct stat st;
        if (stat(path, &st) == 0) {
            if (S_ISDIR(st.st_mode)) buscar_en_directorio(path);
            else buscar_en_archivo(path);
        }
    }
    closedir(dp);
}

int main(int argc, char *argv[]) {
    if (argc < 3) {
        fprintf(stderr, "Uso: %s <patron> <archivo/dir> [-C num]\n", argv[0]);
        return 1;
    }

    strncpy(patron_busqueda, argv[1], 255);
    contexto = 0;

    for (int i = 1; i < argc; i++) {
        if (strcmp(argv[i], "-C") == 0 && i + 1 < argc) {
            contexto = atoi(argv[i+1]);
        }
    }

    struct stat st;
    if (stat(argv[2], &st) == 0) {
        if (S_ISDIR(st.st_mode)) buscar_en_directorio(argv[2]);
        else buscar_en_archivo(argv[2]);
    }

    printf("\n--- Estadísticas ---\n");
    printf("Coincidencias totales: %d\n", coincidencias);
    return 0;
}