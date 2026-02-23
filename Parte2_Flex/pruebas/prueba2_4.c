#include <stdio.h>

/* Este es un comentario de bloque 
   que debería ser contado correctamente */
int funcion_compleja(int n) {
    int contador_pasos = 0;
    int z = 1; // CODE SMELL: Variable de una sola letra

    if (n > 0 && n < 100) { // Complejidad +2 (if y &&)
        for (int i = 0; i < n; i++) { // Complejidad +1, Anidamiento nivel 2
            if (i % 2 == 0) { // Complejidad +1, Anidamiento nivel 3
                while (z < 10) { // Complejidad +1, Anidamiento nivel 4
                    z++;
                    // La siguiente es una linea muy larga para activar el code smell de longitud de linea
                    printf("Esta es una salida de depuracion extremadamente larga para probar si el analizador detecta mas de ochenta caracteres en una sola linea de codigo fuente\n");
                }
            } else {
                z--;
            }
        }
    } else if (n == 0 || n > 1000) { // Complejidad +2 (else if y ||)
        printf("Valor fuera de rango\n");
    }

    return z;
}

int main() {
    // Comentario de una linea
    int resultado = funcion_compleja(10);
    return 0;
}