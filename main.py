from matlabStruct import create_matlabStruct
from Senial import Senial
from iterables import file_list

if __name__ == '__main__':
    Sujeto1 = create_matlabStruct('sujetos/' + file_list[14])

    # señales de pasada 1
    print(Sujeto1['S6']['header'])
    print('---------------')
    print(Sujeto1['S6']['rtoe'])
    print('---------------')
    print(Sujeto1['S6']['rankle'])

    s1 = Senial(Sujeto1['S6']['rtoe'], 'R', Sujeto1['S6']['events'],
                Sujeto1['S6']['lknee'], 'knee', 'L',
                Sujeto1['S6']['header'])

    s2 = Senial(Sujeto1['S6']['rtoe'], 'R', Sujeto1['S2']['events'],
                Sujeto1['S6']['lknee'], 'knee', 'L',
                Sujeto1['S6']['header'])

    ss = s1 + s2
    s1.normalizar()
    # s1.graficar()
    a, b = s1.autosplit()
    bswing = b.recortar_ciclo('swing')
    bswing.scatter()
    # a.graficar()
    # b.graficar()

    # a.graficar()
    # astance = a.recortar_ciclo('stance')
    # anods = a.recortar_ciclo('nods')
    # bnods = b.recortar_ciclo('nods')
    # snods = anods + bnods
    # snods.graficar(opuesto=True)



