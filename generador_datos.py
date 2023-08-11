import numpy as np
from iterables import *
from matlabStruct import create_matlabStruct
from Senial import Senial


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
        print(n)
        pasada = Senial(Sujeto[n][toe], toe[0].upper(), Sujeto[n]['events'],
                        Sujeto[n][angle], angle[1:], angle[0].upper(),
                        Sujeto[n]['header'])
        for part in pasada.autosplit():
            part.remover_nan()
            # agregar if aqui
            if ciclo=='full':
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
    n_file = 1
    filename = '../DatosCamargo_nogc/' + file_list[n_file]

    signal1 = obtener_senial(filename, 'rtoe', 'rknee', 'stance', False)
    signal2 = obtener_senial(filename, 'rtoe', 'rknee', 'swing', False)
    #signal.scatter()

    import matplotlib.pyplot as plt
    plt.scatter(signal1.angle,
                signal1.foot_height,
                s=2, color='r', label='stance')
    plt.scatter(signal2.angle,
                signal2.foot_height,
                s=2, color='b', label='swing')
    plt.legend(loc='best')
    plt.ylabel(f'Height of {"right" if signal1.foot_side == "R" else "left"} toe [cm]')
    plt.xlabel(f'{"Right" if signal1.angle_side == "R" else "Left"} {signal1.angle_description} angle [degrees]')
    plt.grid()
