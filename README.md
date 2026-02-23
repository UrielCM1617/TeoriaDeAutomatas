#  Tarea 3: Expresiones Regulares  

**Alumno:** Uriel Castillo Martínez  
**Matrícula:** 2223068846  

---

##  Requisitos  
Para ejecutar los programas es necesario contar con:  
- **Python**  
- **Flex 2.6 en adelante. En caso de usar windows**
- **PYL (Python Lex-Yacc)**  
- **GCC** (para compilar programas con Flex)  

---

##  Parte 1: Regex en Python  
Esta sección no requiere compilación, los programas se ejecutan directamente desde la terminal.  

###  Ejecución de los ejercicios  
Cada script puede ejecutarse con el siguiente comando:  

    python ejercicio1_1.py
    python ejercicio1_2.py
    python ejercicio1_3.py
    python ejercicio1_4.py

Para el ejercicio1_2 se hizo uso de un 'sistema.log'. Se hizo de manera manual para comprobar el uso del programa 

---

## Parte 2: Flex en C
Para ejecutar tosos los scripts es necesario estar en la carpeta \Parte2_Flex

### Ejecucion de los ejercicios
Es requerido tener instaldo Flex, en caso de usar Linux o Mac, no es necesario hacer cambios

#### Ejercicio 2_1
Escribir desde la terminal:

    make run EJ=2_1 FILE=pruebas/prueba2_1.txt

#### Ejercicio2_2
Escribir desde la terminal:

    make run EJ=2_2 FILE=pruebas/prueba2_2.c

#### Ejercicio2_3
Escribir desde la terminal:

    make run EJ=2_3 PATRON="int" FILE=pruebas/prueba2_3.c

### Ejercicio2_4
Escribir desde la termianl:

    make run EJ=2_4 FILE=pruebas/prueba2_4.c
## Notas Importantes

- **Estructura de salida:** Todos los resultados de la parte 2 "Flex" se almacenan automáticamente en la carpeta `salidas/` para mantener el espacio de trabajo organizado.
- **Reporte de líneas:** Se utiliza `%option yylineno` en los analizadores de la Parte 2 para reportar con precisión la línea exacta en alertas de *code smells*.
- **Gestión de argumentos:** El `Makefile` maneja dinámicamente los parámetros requeridos por cada ejercicio (patrones, archivos de entrada y salida) de forma transparente para el usuario.

---

## Parte 3: En aplicacipones Flex +


### Ejecucion de los ejercicios Asegurarse de estar en /Parte3_Aplicaciones
Antes de ejecutar el programa debemos de usar:
    
    pip install ply

De esta manera haremos uso de de la libreria Flex.
En este primer ejercicio se crearon 'config.json' y 'seguridad.log' los cuales usaremos
para simular el escenario que se propuso para la practica. Una vez que se ejecute se creara
el script 'reporte_seguridad.html'

#### ejercicio3_1
Solo es necesario tener instalado el ply que se menciono en el punto anterior y solo ejecutamos en la terminal:
    
    python python ejercicio3_1.py

#### ejercicio3_1
Solo es necesario tener instalado el ply que se menciono en el punto anterior y solo ejecutamos en la terminal:
    
    python python ejercicio3_1.py