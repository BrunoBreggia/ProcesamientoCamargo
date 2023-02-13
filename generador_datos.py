import numpy as np
from iterables import *
from matlabStruct import create_matlabStruct
from Senial import Senial

# variables de archivo:
n_file = 14  # 0
filename = 'sujetos/' + file_list[n_file]
toe = 'rtoe'
angle = 'rhip_addu'
ciclo = 'swing'  # puede ser 'full', 'swing', 'stance', 'nods'
norm = True


def obtener_senial():
    """
    Devuelve un objeto señal listo para ser pasada como entrada a la red neuronal mine
    que evaluara la informacion mutua entre la altura del pie y la señal de apertura angular.
    Este archivo debera ser modificado para generar señales diferentes. La funcion debra ser
    llamada desde otro script y no recibe ningun parametro.
    """

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
