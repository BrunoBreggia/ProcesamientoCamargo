import numpy as np
from iterables import *
from matlabStruct import create_matlabStruct
from Senial import Senial

# variables de archivo:
# n_file = 0  # 14
# filename = 'sujetos/' + file_list[n_file]
# toe = 'rtoe'
# angle = 'rhip_addu'
# ciclo = 'swing'  # puede ser 'full', 'swing', 'stance', 'nods'
# norm = True


def obtener_senial(n_file, toe, angle, ciclo, norm):
    """
    Devuelve un objeto señal listo para ser pasada como entrada a la red neuronal mine
    que evaluara la informacion mutua entre la altura del pie y la señal de apertura angular.
    Este archivo debera ser modificado para generar señales diferentes. La funcion debra ser
    llamada desde otro script y no recibe ningun parametro.

    :param
    n_file [int]
        Numero del archivo de la simulacion (de 0 a 21)
    toe [str]: "rtoe", "ltoe"
        Cual pie analizar
    angle [str]: "rankle" (entre otros)
        Cual angulo analizar (los nombres estan en el archivo de iterables)
    ciclo [str]: "full", "swing", "stance", "nods"
        Tipo de ciclo de marcha a considerar en la señal
    norm [bool]
        Bandera para normalizar la señal. La normalización es estadística,
        y se realiza en función del ciclo full. Luego se recorta, si es solicitado.
    """

    filename = 'sujetos/' + file_list[n_file]

    # pre-procesamiento:
    Sujeto = create_matlabStruct(filename)
    trials = [field for field in Sujeto.keys() if field[0] == 'S']
    seniales = []

    for n in trials:
        pasada = Senial(Sujeto[n][toe], toe[0].upper(), Sujeto[n]['events'],
                        Sujeto[n][angle], angle[1:], angle[0].upper(),
                        Sujeto[n]['header'])
        for part in pasada.autosplit():
            part.remover_nan()
            seniales.append(part)

    completa = np.sum(seniales)  # concatenacion
    if norm: completa.normalizar()

    if ciclo == 'full':
        definitivo = completa
    elif ciclo == 'swing':
        particiones = completa.autosplit()
        swing = particiones[0].recortar_ciclo('swing')
        for part in particiones[1:]:
            swing += part.recortar_ciclo('swing')
        definitivo = swing
    elif ciclo == 'stance':
        particiones = completa.autosplit()
        stance = particiones[0].recortar_ciclo('stance')
        for part in particiones[1:]:
            stance += part.recortar_ciclo('stance')
        definitivo = stance
    elif ciclo == 'nods':
        particiones = completa.autosplit()
        nods = particiones[0].recortar_ciclo('nods')
        for part in particiones[1:]:
            nods += part.recortar_ciclo('nods')
        definitivo = nods

    # la señal a procesar esta en la variable 'definitivo'
    return definitivo
