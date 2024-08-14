from iterables import *
from Senial import Senial
import matplotlib.pyplot as plt
from generador_datos import obtener_senial
import pandas as pd

"""
Graficas de dispersion x4
"""


def imagen_x4(data_filename, chosen_angle, to_file=False):
    plt.rcParams.update({'font.size': 12})
    plt.rcParams["figure.figsize"] = (10, 8.19)  # values in inches

    fig, axs = plt.subplots(2, 2)

    plt.subplots_adjust(left=0.1,
                        bottom=0.1,
                        right=0.95,
                        top=0.95,
                        wspace=0.4,
                        hspace=0.2)

    i, j = 0, 0
    pairs = [("ltoe", "l"+chosen_angle), ("rtoe", "r"+chosen_angle),
             ("rtoe", "l"+chosen_angle), ("ltoe", "r"+chosen_angle)]

    for (toe, angle) in pairs:
        signal1 = obtener_senial(data_filename, toe, angle, 'swing', False)
        signal2 = obtener_senial(data_filename, toe, angle, 'stance', False)
        signal3 = obtener_senial(data_filename, toe, angle, 'nods', False)
        min_height = min(signal1.foot_height)

        ax = axs[i][j]

        ax.scatter(signal1.angle,
                   signal1.foot_height - min_height,
                   s=3, color='b', label='vuelo')
        ax.scatter(signal2.angle,
                   signal2.foot_height - min_height,
                   s=3, color='orange', label='1er apoyo doble')
        ax.scatter(signal3.angle,
                   signal3.foot_height - min_height,
                   s=3, color='r', label='nods')

        if (i, j) == (0, 1):
            ax.legend(loc='best')

        ax.set(ylabel=f'Altura de pie {"derecho" if signal1.foot_side == "R" else "izquierdo"} [mm]')
        if i == 1:
            name = angles_translated[signal1.angle_description].title()
            ax.set(xlabel=f'{name} {"derech"+name[-1] if signal1.angle_side == "R" else "izquierd"+name[-1]} [grados]')
        ax.grid()

        # Actualizo indices
        i, j = (i, j + 1) if j != 1 else (i + 1, 0)

    if to_file:
        plt.savefig(to_file)
        plt.close()
    else:
        plt.show()


def imagenes_comparacion(infile, ciclo, outfile=False):
    plt.rcParams.update({'font.size': 12})
    plt.rcParams["figure.figsize"] = (15, 8.19)  # values in inches

    fig, axs = plt.subplots(2, 6)

    plt.subplots_adjust(left=0.1,
                        bottom=0.1,
                        right=0.95,
                        top=0.95,
                        wspace=0.1,
                        hspace=0.2)

    angles = ["ankle", "knee", "hip_flex", "hip_rot", "hip_addu", "subt"]
    if ciclo == "swing":
        color = "b"
    elif ciclo == "stance":
        color = "r"
    elif ciclo == "nods":
        color = "orange"
    else:
        color = "purple"

    # im tags
    df = pd.read_csv("../Statistical_analysis/sim06_medianas_realizaciones_nuevo.csv")

    # ipsilaterales
    for index, ax in enumerate(axs.flatten()):
        angle = angles[index]
        signal = obtener_senial(infile, "rtoe", "r" + angle, ciclo, False)   # R-R
        # signal += obtener_senial(infile, "ltoe", "l" + angle, ciclo, False)  # L-L
        im = df[(df["ciclo"] == ciclo) &
                (df["angulo"] == angle.replace("_", "-")) &
                (df["lateral"] == "ipsilateral")
                ]["mediana"].mean()

        ax.grid()
        min_height = min(signal.foot_height)
        ax.scatter(signal.angle,
                   signal.foot_height - min_height,
                   s=2, color=color, label=ciclo)

        ax.set_ylim([-10, 120])
        ax.set(title=f'IM:{im:.3}')
        if index == 0:
            ax.set(ylabel=f'Altura de pie ipsilateral [mm]')
        else:
            ax.set(yticklabels=[])
        if index == 5:
            break

    # contralaterales
    for index, ax in enumerate(axs.flatten()):
        if index <= 5:
            continue
        angle = angles[index % 6]
        signal = obtener_senial(infile, "ltoe", "r" + angle, ciclo, False)   # L-R
        # signal += obtener_senial(infile, "rtoe", "l" + angle, ciclo, False)  # R-L
        im = df[(df["ciclo"] == ciclo) &
                (df["angulo"] == angle.replace("_", "-")) &
                (df["lateral"] == "contralateral")
                ]["mediana"].mean()

        if index == 6:
            ax.set(ylabel=f'Altura pie contralateral [mm]')
        else:
            ax.set(yticklabels=[])
        ax.set_ylim([-10, 120])
        ax.set(xlabel=f'{angles[index % 6]} [°]')
        ax.grid()
        min_height = min(signal.foot_height)
        ax.scatter(signal.angle,
                   signal.foot_height - min_height,
                   s=2, color=color, label=ciclo)
        ax.set(title=f'IM:{im:.3}')
        # if index == 11:
        #     plt.legend(loc="best")

    if outfile:
        plt.savefig(outfile)
        plt.close()
    else:
        plt.show()


if __name__ == "__main__":

    n_file = 0  # Sujeto 06
    filename = '../DatosCamargo_nogc/' + file_list[n_file]

    # imagen_x4(filename, "knee")

    # for angle in [i[1:] for i in angles_tested]:
    #     output_file = f'../Documento Final/apendice2/{angle}.png'
    #     imagen_x4(filename, angle, output_file)

    # for ciclo in ["swing", "stance", "nods", "full"]:
    #     out_file = f"imagenes_comparacion_{ciclo}.pdf"
    #     imagenes_comparacion(filename, ciclo, out_file)

    imagenes_comparacion(filename, "full")
