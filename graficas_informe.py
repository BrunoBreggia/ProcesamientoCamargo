import numpy as np
from sklearn.linear_model import LinearRegression
from iterables import *
from Senial import Senial
import matplotlib.pyplot as plt
from generador_datos import obtener_senial
import scipy.stats as stats

"""
Grafica con la evolucion temporal de las articulaciones consideradas en el proyecto.
"""

n_file = 0
filename = '../DatosCamargo_nogc/' + file_list[n_file]
plt.rcParams.update({'font.size': 14})
cycles = {}
toe = 'rtoe'
angles = [angle for angle in angles_tested if angle[0] == 'r']
descripcion = {
    'rankle': ["tobillo", "limite dorsi(+)/plantarflexión(-)", "(f)"],
    'rsubt': ["subtalar", "limite inversión(+)/eversión(-)", "(e)"],
    'rknee': ["rodilla", "limite extensión(+)/flexión(-)", "(d)"],
    'rhip_addu': ["cadera (plano frontal)", "limite aducción(+)/abducción(-)", "(c)"],
    'rhip_flex': ["cadera (plano sagital)", "limite flexión(+)/extensión(-)", "(b)"],
    'rhip_rot': ["cadera (plano horizontal)", "limite rotación interna(+)/externa(-)", "(a)"],
}

for angle in angles:
    signal = obtener_senial(filename, toe, angle, 'full', False)
    ini, fin = np.int16(signal.events['RHS'][0:2, 1])
    toff = int(signal.events['RTO'][0, 1] - ini)
    # print(ini, fin)
    contenido = signal.angle[ini:fin]
    # if angle in ["rhip_addu", "rknee"]:
    #     contenido *= -1
    cycles[angle] = contenido, toff

fig, axs = plt.subplots(3, 2)
# set the spacing between subplots
# plt.subplot_tool()

# fig.suptitle('Angulos articulares durante un ciclo de marcha')

i, j = 0, 0
for angle_name, (angle_signal, toff) in reversed(cycles.items()):
    percentage = np.linspace(0, 100, len(angle_signal))
    axs[i][j].plot(percentage, angle_signal)
    axs[i][j].set(xlabel=descripcion[angle_name][2], ylabel='Apertura [°]')
    axs[i][j].grid()
    if (margin := max(angle_signal)) < 0:
        axs[i][j].hlines(-margin/2, 0, 100, 'w', '--')
    axs[i][j].axhline(0, color='k', linestyle='-', label=descripcion[angle_name][1])
    axs[i][j].axvline(0, color="green", linestyle="--")
    axs[i][j].axvline(100, color="green", linestyle="--")
    axs[i][j].axvline(percentage[toff], color="red", linestyle="--")
    axs[i][j].legend(loc='best', prop={'size': 12})
    j += 1
    if j == 2:
        j = 0
        i += 1

fig.tight_layout(pad=0.05)
# plt.plot(ciclo)
plt.show()

"""
Grafica con la evolucion temporal solamente de las articulación de la rodilla
"""

n_file = 0
filename = '../DatosCamargo_nogc/' + file_list[n_file]
plt.rcParams.update({'font.size': 14})
plt.rcParams["figure.figsize"] = (10, 5)  # values in inches

signal = obtener_senial(filename, 'rtoe', 'rknee', 'full', False)
ini, fin = np.int16(signal.events['RHS'][0:2, 1])
toff = int(signal.events['RTO'][0, 1] - ini)

plt.figure()
plt.grid()
cycle = signal.angle[ini:fin]
percentage = np.linspace(0, 100, len(cycle))
plt.plot(percentage, cycle)
plt.xlabel("Porcentaje de ciclo de marcha [%]")
plt.ylabel("Apertura angular [°]")

plt.axvline(0, color="green", linestyle="--")
plt.axvline(100, color="green", linestyle="--")
plt.axvline(percentage[toff], color="red", linestyle="--")
plt.tight_layout()
plt.show()

"""
Grafica con la evolucion temporal de la altura del pie (derecho).
"""

print(type(signal.foot_height))
ini, fin = np.int16(signal.events['RHS'][2:4, 1])
toff = int(signal.events['RTO'][2, 1] - ini)

plt.rcParams["figure.figsize"] = (10, 5)  # values in inches
plt.figure()
plt.grid()
cycle = signal.foot_height[ini:fin]
min_height = min(cycle)
cycle -= min_height  # quito el bias
percentage = np.linspace(0, 100, len(cycle))
plt.plot(percentage, cycle)
plt.xlabel("Porcentaje del ciclo de marcha [%]")
plt.ylabel("Altura [mm]")

plt.axvline(0, color="green", linestyle="--")
plt.axvline(100, color="green", linestyle="--")
plt.axvline(percentage[toff], color="red", linestyle="--")

"""
Graficas de dispersion de rodilla x4
"""

# signal3 = obtener_senial(filename, toe, angle, 'nods', False)

fig, axs = plt.subplots(2, 2)
# fig.tight_layout(pad=0.05)

plt.subplots_adjust(left=0.1,
                    bottom=0.1,
                    right=0.95,
                    top=0.95,
                    wspace=0.4,
                    hspace=0.2)

i, j = 0, 0

angle = "knee"
# angle = "hip_rot"

pairs = [("ltoe", "l"+angle), ("rtoe", "r"+angle),
         ("rtoe", "l"+angle), ("ltoe", "r"+angle)]

for (toe, angle) in pairs:
    signal1 = obtener_senial(filename, toe, angle, 'swing', False)
    signal2 = obtener_senial(filename, toe, angle, 'stance', False)
    min_height = min(signal1.foot_height)

    ax = axs[i][j]

    ax.scatter(signal1.angle,
               signal1.foot_height - min_height,
               s=3, color='b', label='vuelo')
    ax.scatter(signal2.angle,
               signal2.foot_height - min_height,
               s=3, color='r', label='apoyo')
    # ax.scatter(signal3.angle,
    #            signal3.foot_height,
    #            s=3, color='r', label='nods')

    if (i, j) == (0, 1):
        ax.legend(loc='best')

    ax.set(ylabel=f'Altura de pie {"derecho" if signal1.foot_side == "R" else "izquierdo"} [mm]')
    if i == 1:
        name = angles_translated[signal1.angle_description].title()
        ax.set(xlabel=f'{name} {"derech"+name[-1] if signal1.angle_side == "R" else "izquierd"+name[-1]} [grados]')
    ax.grid()

    # Actualizo indices
    i, j = (i, j + 1) if j != 1 else (i + 1, 0)
# plt.savefig(f'../Documento Final/apendice2/{toe}-{angle}.png', bbox_inches='tight')
# plt.close()

plt.rcParams["figure.figsize"] = (10, 8.19)  # values in inches
plt.show()


"""
Correlacion lineal aplicado a angulo de rodilla
"""

signal = obtener_senial(filename, 'rtoe', 'rknee', 'full', False)
min_height = min(signal.foot_height)

# signal = obtener_senial(filename, 'rtoe', 'rhip_rot', 'full', False)

y = signal.foot_height - min_height
x = signal.angle
r, _ = stats.pearsonr(x, y)

model = LinearRegression()
model.fit(x.reshape((-1, 1)), y)

intercept = model.intercept_
slope = model.coef_[0]

y_pred = slope*x + intercept

plt.rcParams["figure.figsize"] = (7, 7)  # values in inches
fig = plt.figure()
ax = fig.add_subplot()
fig.subplots_adjust(top=0.85)
plt.scatter(x, y,
            color='c', marker='o', s=10)
plt.plot(x, y_pred,
         color='k')  # , label=f'r={r:.3f}')
plt.grid()

ax.text(-50, 80, '$r_{xy} = $' + str(round(r, 3)), fontsize=15)
# ax.text(-50, 70, '$m = $' + str(round(slope, 3)), fontsize=15)

# ax.text(-8, 100, '$r_{xy} = $' + str(round(r, 3)), fontsize=15)
# ax.text(-8, 90, '$m = $' + str(round(slope, 3)), fontsize=15)

plt.xlabel("Apertura de rodilla derecha [grados]")
plt.ylabel("Altura del pie derecho [mm]")
# plt.xlabel("Rotación de cadera derecha [grados]")
# plt.ylabel("Altura del pie derecho [mm]")
# plt.legend(loc='best')
plt.show()

