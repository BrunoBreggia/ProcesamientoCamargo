from matlabStruct import create_matlabStruct
from Senial import Senial
from iterables import file_list

if __name__ == '__main__':
    Sujeto1 = create_matlabStruct('../DatosCamargo_nogc/' + file_list[1])

    # señales de pasada 1
    print(Sujeto1['S9']['header'])
    print('---------------')
    print(Sujeto1['S9']['rtoe'])
    print('---------------')
    print(Sujeto1['S9']['rankle'])

    S9 = Senial(Sujeto1['S9']['rtoe'], 'L', Sujeto1['S9']['events'],
                Sujeto1['S9']['lknee'], 'knee', 'L',
                Sujeto1['S9']['header'])

    # s2 = Senial(Sujeto1['S6']['rtoe'], 'R', Sujeto1['S2']['events'],
    #             Sujeto1['S6']['lknee'], 'knee', 'L',
    #
    #             Sujeto1['S6']['header'])
    a, b, c = S9.autosplit()

    astance = a.recortar_ciclo('stance')
    bstance = b.recortar_ciclo('stance')
    cstance = c.recortar_ciclo('stance')

    stance = astance + bstance + cstance
    stance.graficar()
    # ss = S9 + s2
    # S9.normalizar()
    # # S9.graficar()
    # a, b = S9.autosplit()
    # bswing = b.recortar_ciclo('swing')
    # bswing.scatter()
    # # a.graficar()
    # # b.graficar()

    # a.graficar()
    # astance = a.recortar_ciclo('stance')
    # anods = a.recortar_ciclo('nods')
    # bnods = b.recortar_ciclo('nods')
    # snods = anods + bnods
    # snods.graficar(opuesto=True)



