/* Archivo de prueba para el ejercicio 2_2
   Este bloque de comentarios debe desaparecer
*/

#include <stdio.h>

// Este comentario de una sola línea también debe ser eliminado
int variable_global_importante = 100;

void mi_funcion_de_prueba(int valor_recibido) {
    int contador_de_iteraciones = 0;
    
    /* Comentario interno 
       que ocupa varias lineas */
    for(int i_indice = 0; i_indice < valor_recibido; i_indice++) {
        printf("El valor de la_variable es: %d\n", i_indice);
        contador_de_iteraciones++;
    }
}

int main() {
    int resultado_final_calculado = 0;
    char nombre_de_usuario[] = "Admin";

    mi_funcion_de_prueba(10); // Llamada con snake_case

    return 0;
}