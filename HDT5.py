# -*- coding: cp1252 -*-
#*****************************************************
# Fredy Espana carne: 15060
# Pedro Garcia carne: 15409
# HDT5
# El siguiente programa simula procesamiento de datos
#*****************************************************

# Se importan librerias
import simpy
import math
import random

# Definicion de variables globales
global time_TOT			# Tiempo total 
global time_PRCS		# Tiempo proceso
global time_IO			# Tiempo operaciones IO fase waiting 
global cantidad_MEM		# Memoria maxima por proceso
global cantidad_INS		# Instrucciones maximas
global capacidad_PRCS           # Intervalo
global promedio                 # Promedio de los procesos
global lista
                
# Inicializacion de variables y constantes
random_seed = 1488 	# Numero arbitrario permite generar siempre los mismos aleatorios
cantidad_PRCS = 200	# Ejecucion de X procesos
capacidad_PRCS = 10	# Intervalo
time_PRCS = 1		# Tiempo que tarda el CPU a cada proceso
time_IO = 2		# "Supuesto" de tiempo que espera para entrar a IO
cantidad_INS = 3 	# Realiza 10 instrucciones maximas 
cantidad_MEM = 20      # Cada proceso utiliza maximo de memoria 10
time_TOT = 0.0		# Se inicializa tiempo total de los procesos en 0
promedio = 0.0          # Se inicializa promedio en 0    
lista = []

# Funcion de proceso
def newProceso(env, name, unit, ram, io, mem, ins):
	init_STRT = env.now # Se inicia un nuevo proceso
	print ('El proceso %s fue creado durante las %s U.D.T' % (name, init_STRT))	# Se imprime la instruccion
	
	global time_TOT, time_PRCS, time_IO, capacidad_PRCS

	with ram.get(mem) as req:
		yield req
		init_RDY = env.now # Tiempo en que el proceso logra entrar a ready
		print ('El proceso %s ha pasado al estado ready durante las %s U.D.T.' % (name, init_RDY))

		while (ins > 0): # Se ejecutara mientras existan instrucciones en cola
			with unit.request() as req2:
				yield req2
				init_PRCS = env.now # Tiempo en que el proceso logra entrar al procesamiento
				print ('El proceso %s se ha empezado a procesar durante las %s U.D.T' % (name, init_PRCS))

				yield env.timeout(time_PRCS)
				exit_PRCS = env.now # Tiempo en que el proceso logra salir del procesamiento
				print ('El proceso %s se ha terminado de procesar durante las %s U.D.T' % (name, exit_PRCS))

				if (ins < capacidad_PRCS):
					term_PRCS = env.now # Tiempo "terminated" del proceso
					print ('El proceso %s ha finalizado durante las %s U.D.T' % (name, term_PRCS))
					term_PRCS = env.now
					temp_PRCS_time = term_PRCS - init_STRT	# Variable temporal para guardar la operacion
					lista.append(temp_PRCS_time)
					time_TOT = time_TOT + temp_PRCS_time	# Se suma a tiempo total
					ram.put(mem)	# Se regresa la memoria utilizada 
					ins = 0		# Reset

				else:
					ins -= capacidad_PRCS	# Se restan las instrucciones disponibles a instrucciones
					if (random.randint(1,2) == 1):
						with io.request() as req3:
							yield req3
							init_IO = env.now
							print ('El proceso %s ha iniciado etapa I/O durante las %s U.D.T' % (name, init_IO))

							time_Waiting_IO = random.randint(1,time_IO)
							yield env.timeout(time_Waiting_IO)
							exit_IO = env.now
							temp_PRCS_time = exit_IO - init_STRT
							lista.append(temp_PRCS_time)
							time_TOT = time_TOT + temp_PRCS_time

							print ('El proceso %s ha finalizado etapa I/O durante las %s U.D.T' % (name, exit_IO))

							

def procesamiento(env, cantidad, capacidad, unit, io, ram):
	global cantidad_INS, cantidad_MEM
	for i in range(cantidad):
		mem = random.randint(1, cantidad_MEM)						# Random para memoria del proceso
		istr = random.randint(1, cantidad_INS)						# Random para instrucciones del proceso
		nuevo_proceso = newProceso(env, ('%s' % i), unit, ram, io, mem, istr)		# Se crea un nuevo proceso
		env.process(nuevo_proceso)															
		temp_time = random.expovariate(1.0 / capacidad)
		yield env.timeout(temp_time)



env = simpy.Environment()
random.seed(random_seed)

procesador = simpy.Resource(env, capacity = 1)
ram_TOT = simpy.Container(env, capacity = 100, init = 100)
io = simpy.Resource(env, capacity = 1)
env.process(procesamiento(env, cantidad_PRCS, capacidad_PRCS, procesador, io, ram_TOT))

env.run()

# Calcular promedio
promedio = (time_TOT / cantidad_PRCS)
print ("El promedio de tiempo de proceso es: %f " % promedio)

# Calcular desviacion estandar
tmp = 0

for i in lista:
        tmp += (i-promedio)**2

desv_Estandar = (tmp/(cantidad_PRCS-1))**0.5

print "La desviacion estandar es: ", desv_Estandar


