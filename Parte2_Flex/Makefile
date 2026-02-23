CC = gcc
LEX = win_flex

# Valores por defecto
EJ ?= 2_3
TARGET = ejercicio$(EJ)
PATRON ?= int
FILE ?= pruebas/prueba$(EJ).c

all: setup $(TARGET)

setup:
	@if not exist salidas mkdir salidas
	@if not exist pruebas mkdir pruebas

$(TARGET): ejercicio$(EJ).l
	$(LEX) -o lex.yy.c ejercicio$(EJ).l
	$(CC) lex.yy.c -o $(TARGET).exe -lfl

run: all
	@echo --- Ejecutando Ejercicio $(EJ) ---
	@if "$(EJ)"=="2_4" ( \
		$(TARGET).exe $(FILE) \
	) else if "$(EJ)"=="2_1" ( \
		$(TARGET).exe $(FILE) \
	) else if "$(EJ)"=="2_2" ( \
		$(TARGET).exe $(FILE) salidas/resultado_2_2.c \
	) else if "$(EJ)"=="2_3" ( \
		$(TARGET).exe $(PATRON) $(FILE) -C 2 \
	)

clean:
	@if exist lex.yy.c del lex.yy.c
	@if exist ejercicio2_1.exe del ejercicio2_1.exe
	@if exist ejercicio2_2.exe del ejercicio2_2.exe
	@if exist ejercicio2_3.exe del ejercicio2_3.exe
	@if exist ejercicio2_4.exe del ejercicio2_4.exe
	@if exist salidas rmdir /s /q salidas