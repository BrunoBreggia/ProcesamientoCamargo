import numpy as np
from iterables import *
from matlabStruct import create_matlabStruct
from Senial import Senial
import matplotlib.pyplot as plt
from itertools import product


def obtener_senial(filename, toe, angle, ciclo, norm):
    """
    Devuelve un objeto señal listo para ser pasada como entrada a la red neuronal mine
    que evaluara la informacion mutua entre la altura del pie y la señal de apertura angular.
    Este archivo debera ser modificado para generar señales diferentes. La funcion debera ser
    llamada desde otro script y no recibe ningun parametro.

    :param
    filename [str]
        Nombre del archivo mat con información de la señal a levantar
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
            # agregar if aqui
            if ciclo == 'full':
                seniales.append(part)
            elif ciclo == 'swing':
                swing = part.recortar_ciclo('swing')
                seniales.append(swing)
            elif ciclo == 'stance':
                stance = part.recortar_ciclo('stance')
                seniales.append(stance)
            elif ciclo == 'nods':
                nods = part.recortar_ciclo('nods')
                seniales.append(nods)
            # seniales.append(part)

    completa = np.sum(seniales)  # concatenacion
    # if norm: completa.normalizar()
    #
    # definitivo = None
    #
    # if ciclo == 'full':
    #     definitivo = completa
    # elif ciclo == 'swing':
    #     particiones = completa.autosplit()
    #     swing = particiones[0].recortar_ciclo('swing')
    #     for part in particiones[1:]:
    #         swing += part.recortar_ciclo('swing')
    #     definitivo = swing
    # elif ciclo == 'stance':
    #     particiones = completa.autosplit()
    #     stance = particiones[0].recortar_ciclo('stance')
    #     for part in particiones[1:]:
    #         stance += part.recortar_ciclo('stance')
    #     definitivo = stance
    # elif ciclo == 'nods':
    #     particiones = completa.autosplit()
    #     nods = particiones[0].recortar_ciclo('nods')
    #     for part in particiones[1:]:
    #         nods += part.recortar_ciclo('nods')
    #     definitivo = nods

    # la señal a procesar esta en la variable 'definitivo'
    return completa  # definitivo


if __name__ == "__main__":
    n_file = 0
    filename = '../DatosCamargo_nogc/' + file_list[n_file]

    plt.rcParams.update({'font.size': 14})

    for (toe, angle) in product(toe_side, angles_tested):
        plt.rcParams["figure.figsize"] = (7, 7)  # values in inches
        plt.figure()
        signal1 = obtener_senial(filename, toe, angle, 'swing', False)
        signal2 = obtener_senial(filename, toe, angle, 'stance', False)
        signal3 = obtener_senial(filename, toe, angle, 'nods', False)
        min_height = min(signal1.foot_height)

        # plt.plot(signal1.time, signal1.angle, "r")
        # signal1.graficar()

        plt.scatter(signal1.angle,
                    signal1.foot_height - min_height,
                    s=3, color='b', label='vuelo')
        plt.scatter(signal2.angle,
                    signal2.foot_height - min_height,
                    s=3, color='orange', label='apoyo doble inicial')
        plt.scatter(signal3.angle,
                    signal3.foot_height - min_height,
                    s=3, color='r', label='nods')

        # z = np.polyfit(signal2.angle, signal2.foot_height, 1)
        # p = np.poly1d(z)
        # plt.plot(signal2.angle, p(signal2.angle), "k")

        plt.legend(loc='best')
        plt.ylabel(f'Altura de pie {"derecho" if signal1.foot_side == "R" else "izquierdo"} [mm]')
        plt.xlabel(f'Ángulo de {angles_translated[signal1.angle_description]} {"derecho" if signal1.angle_side == "R" else "izquierdo"} [grados]')
        plt.grid()
        plt.savefig(f'../Documento Final/apendice/{toe}-{angle}.png', bbox_inches='tight')
        plt.close()
