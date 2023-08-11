import numpy as np
import matplotlib.pyplot as plt


class Senial:
    """
    Clase que contiene un par de señales de registro simultáneo para su
    procesamiento conjunto, destinada a contener los datos de entrada
    de la red MINE de estimacion de informacion mutua.
    Esta clase contiene el par de señales de las cuales se pretende obtener
    la información mutua. Se encarga del preprocesamiento de los datos de
    ambas señales, sin perder su cotemporalidad.
    """

    def __init__(self, foot_height: np.ndarray, foot_side: str, events: dict,
                 angle: np.ndarray, angle_description: str, angle_side: str,
                 timestamp: np.ndarray = None):
        """
        :param foot_height[np.array]: señal de altura de pie
        :param foot_side[str]: "R" si derecho, "L" si izquierdo
        :param events[dict]: diccionario con eventos de toe-off y heel-strike
        :param angle[np.array]: señal de apertura angular
        :param angle_description[str]: que angulo es (ej "knee")
        :param angle_side[str]: "R" si derecho, "L" si izquierdo
        :param timestamp[np.array]: señal que se corresponde con indices temporales
        """

        self.foot_height = foot_height
        if foot_side not in ['R', 'L']:
            raise TypeError('Foot side must be coded as "R" or "L"')
        self.foot_side = foot_side
        self.events = events

        self.angle = angle
        self.angle_description = angle_description
        if angle_side not in ['R', 'L']:
            raise TypeError('Angle side must be coded as "R" or "L"')
        self.angle_side = angle_side

        self.timestamp = timestamp if timestamp is not None else None

    def create_empty_signal(self):
        new = Senial(foot_height=np.array([]),foot_side=self.foot_side, events=self.events,
                  angle=np.array([]), angle_description=self.angle_description, angle_side=self.angle_side,
                  timestamp=np.array([]))
        return new

    def remover_nan(self):
        # TODO: considerar el caso de tenr vario nan consecutivos dentro de la señal
        nans = np.logical_or(np.isnan(self.foot_height), np.isnan(self.angle))

        # Trim signal if there are NaNs on the ends
        while nans[0] is True:
            np.delete(self.foot_height, 0, axis=0)
            np.delete(self.angle, 0, axis=0)
            np.delete(self.timestamp, 0, axis=0)
            np.delete(nans, 0, axis=0)
            for event in self.events.keys():
                self.events[event][:, 1] -= 1
        while nans[-1] is True:
            np.delete(self.foot_height, -1, axis=0)
            np.delete(self.angle, -1, axis=0)
            np.delete(self.timestamp, -1, axis=0)
            np.delete(nans, -1, axis=0)

        # Interpolate to replace NaNs in the middle of the signal
        if np.sum(nans) > 0:
            nan_idxs = np.where(nans == True)
            for idx in nan_idxs:
                if np.isnan(self.foot_height[idx]):  # nan is in foot height signal
                    self.foot_height[idx] = self.foot_height[idx-1]/2 + self.foot_height[idx+1]/2
                else:  # nan is in angle signal
                    self.angle[idx] = self.angle[idx-1]/2 + self.angle[idx+1]/2

    def recortar_ciclo(self, ciclo):
        if ciclo == 'stance':
            return self._extraer_ciclos_stance()
        elif ciclo == 'swing':
            return self._extraer_ciclos_swing()
        elif ciclo == 'nods':
            # no double support
            return self._extraer_ciclos_nods()
        else:
            raise TypeError('Solo se aceptan las etiquetas de '
                            '"swing", "stance" y "nods" para los recortes de ciclo')

    def _extraer_ciclos_swing(self):
        """
        Devuelve otro objeto Senial con ciclos de swing consecutivos. Un ciclo swing se corresponde
        al intervalo entre un toe-off y un heel-strike del mismo pie.
        """
        if self.foot_side == 'L':
            eventos = [self.events['LTO'], self.events['LHS']]
        else:
            eventos = [self.events['RTO'], self.events['RHS']]

        split_idxs = np.empty((len(eventos[0]) + len(eventos[1]),), dtype=np.int32)

        if (eventos[0].size == 0) and (eventos[1].size == 0):
            portions = [self.create_empty_signal()]
        elif eventos[0].size == 0:
            portions = self.split([eventos[1][0][1]])[0]
        elif eventos[1].size == 0:
            portions = self.split([eventos[0][0][1]])[1]
        elif eventos[1][0][1] < eventos[0][0][1]:
            split_idxs[0::2] = eventos[1][:, 1]
            split_idxs[1::2] = eventos[0][:, 1]
            portions = self.split(split_idxs)[0::2]
        else:
            split_idxs[0::2] = eventos[0][:, 1]
            split_idxs[1::2] = eventos[1][:, 1]
            portions = self.split(split_idxs)[1::2]

        complete = portions[0]
        for i in range(1, len(portions)):
            complete += portions[i]

        return complete

    def _extraer_ciclos_stance(self):
        """
        Devuelve otro objeto Senial con ciclos de stance consecutivos. Un ciclo stance se corresponde
        al intervalo entre un heel-strike y un toe-off del mismo pie.
        """
        if self.foot_side == 'L':
            eventos = [self.events['LHS'], self.events['LTO']]
        else:
            eventos = [self.events['RHS'], self.events['RTO']]

        split_idxs = np.empty((len(eventos[0]) + len(eventos[1]),), dtype=np.int32)

        if (eventos[0].size == 0) and (eventos[1].size == 0):
            portions = [self.create_empty_signal()]
        elif eventos[0].size == 0:
            portions = self.split([eventos[1][0][1]])[0]
        elif eventos[1].size == 0:
            portions = self.split([eventos[0][0][1]])[1]
        elif eventos[1][0][1] < eventos[0][0][1]:
            split_idxs[0::2] = eventos[1][:, 1]
            split_idxs[1::2] = eventos[0][:, 1]
            portions = self.split(split_idxs)[0::2]
        else:
            split_idxs[0::2] = eventos[0][:, 1]
            split_idxs[1::2] = eventos[1][:, 1]
            portions = self.split(split_idxs)[1::2]

        # return portions
        # complete = portions[0]
        # for i in range(1, len(portions)):
        #     complete += portions[i]

        complete = np.sum(portions)

        return complete

    def _extraer_ciclos_nods(self):
        """
        Devuelve otro objeto Senial con ciclos de no double support (nods) consecutivos.
        Un ciclo nods se corresponde al intervalo entre un toe-off del pie contrario y
        un toe-off del pie bajo análisis.
        """
        if self.foot_side == 'L':
            eventos = [self.events['RTO'], self.events['LTO']]
        else:
            eventos = [self.events['LTO'], self.events['RTO']]

        split_idxs = np.empty((len(eventos[0]) + len(eventos[1]),), dtype=np.int32)

        if (eventos[0].size == 0) and (eventos[1].size == 0):
            portions = [self.create_empty_signal()]
        elif eventos[0].size == 0:
            portions = self.split([eventos[1][0][1]])[0]
        elif eventos[1].size == 0:
            portions = self.split([eventos[0][0][1]])[1]
        elif eventos[1][0][1] < eventos[0][0][1]:
            split_idxs[0::2] = eventos[1][:, 1]
            split_idxs[1::2] = eventos[0][:, 1]
            portions = self.split(split_idxs)[0::2]
        else:
            split_idxs[0::2] = eventos[0][:, 1]
            split_idxs[1::2] = eventos[1][:, 1]
            portions = self.split(split_idxs)[1::2]

        # return portions
        complete = portions[0]
        for i in range(1, len(portions)):
            complete += portions[i]

        return complete

    def __len__(self):
        return len(self.timestamp)

    def __add__(self, other):

        if self.foot_side != other.foot_side:
            raise TypeError("Incompatible signals to be merged. Signals from different foot.")
        if self.angle_description != other.angle_description:
            raise TypeError("Incompatible signals to be merged. Signals from different angles.")
        if self.angle_side != other.angle_side:
            raise TypeError("Incompatible signals to be merged. Signals from different angle side.")

        foot_height = np.concatenate((self.foot_height, other.foot_height))
        angle = np.concatenate((self.angle, other.angle))
        timestamp = np.concatenate((self.timestamp, other.timestamp))
        events = {}
        for key in self.events.keys():
            # the indexes of the events should be updated
            new_events = other.events[key].copy()
            new_events[:,1] += len(self.timestamp)
            events[key] = np.concatenate((self.events[key], new_events))

        newSignal = Senial(foot_height, self.foot_side, events,
                           angle, self.angle_description, self.angle_side,
                           timestamp)
        return newSignal

    def __iadd__(self, other):
        original_len = len(self)
        self.foot_height = np.concatenate((self.foot_height, other.foot_height))
        self.angle = np.concatenate((self.angle, other.angle))
        self.timestamp = np.concatenate((self.timestamp, other.timestamp))
        for key in self.events.keys():
            # the indexes of the events should be updated
            new_events = other.events[key].copy()
            new_events[:, 1] += original_len
            self.events[key] = np.concatenate((self.events[key], new_events))

        return self

    def graficar(self, eventos=True, opuesto=False):
        """
        Grafica las señales de altura de pie y señal angular, una bajo la otra.
        Por defecto indica las posiciones de los eventos de toe-off y heel-strike del
        pie bajo cuestion. Se puede pedir que señale los eventos del pie opuesto.
        """
        fig, axs = plt.subplots(nrows=2, sharex=True)
        fig.suptitle(f'Pie {"der" if self.foot_side=="R" else "izq"} (arriba) vs {self.angle_description} '
                     f'{"der" if self.angle_side=="R" else "izq"} (abajo)')
        axs[0].grid()
        axs[0].plot(self.foot_height)
        axs[1].grid()
        axs[1].plot(self.angle)

        # señalar eventos
        if eventos and not opuesto:
            if self.foot_side == 'L':
                eventos = [self.events['LTO'], self.events['LHS']]
            else:
                eventos = [self.events['RTO'], self.events['RHS']]
            for TO in eventos[0][:,1]:
                axs[0].axvline(x=TO, color='red', linestyle='--')
                axs[1].axvline(x=TO, color='red', linestyle='--')
            for HS in eventos[1][:,1]:
                axs[0].axvline(x=HS, color='green', linestyle='--')
                axs[1].axvline(x=HS, color='green', linestyle='--')

        if opuesto:
            if self.foot_side == 'R':
                eventos = [self.events['LTO'], self.events['LHS']]
            else:
                eventos = [self.events['RTO'], self.events['RHS']]
            for TO in eventos[0][:,1]:
                axs[0].axvline(x=TO, color='magenta', linestyle='--')
                axs[1].axvline(x=TO, color='magenta', linestyle='--')
            for HS in eventos[1][:,1]:
                axs[0].axvline(x=HS, color='blue', linestyle='--')
                axs[1].axvline(x=HS, color='blue', linestyle='--')

    def scatter(self):
        plt.scatter(self.angle,
                    self.foot_height,
                    s=2)
        plt.ylabel(f'Altura pie {"der" if self.foot_side=="R" else "izq"}')
        plt.xlabel(f'Angulo de {self.angle_description} {"der" if self.angle_side=="R" else "izq"}')
        plt.grid()

    def normalizar(self):
        """
        Vuelve cero la media de la señal y le da varianza unitaria
        """
        # normalizo altura del pie
        self.foot_height -= np.mean(self.foot_height)
        self.foot_height /= np.std(self.foot_height)
        # normalizo señal angular
        self.angle -= np.mean(self.angle)
        self.angle /= np.std(self.angle)

    def autosplit(self):
        """
        Parte la señal en puntos donde detecta que ha sido previamente particionada
        (en base a los gaps en el vector de timestamp). Esto permite procesar adecuadamente
        cada porción considerando sus respectivos eventos de TO y HS, con tamaños de paso
        constantes.
        """

        idxs = np.where(np.round(np.abs(np.diff(self.timestamp))) > 0.005)[0] + 1
        return self.split(idxs)

    def split(self, idxs):
        timestamps = np.split(self.timestamp, idxs)
        foot_heights = np.split(self.foot_height, idxs)
        angles = np.split(self.angle, idxs)

        split_events = []  # lista de diccionarios
        L1, L2, R1, R2 = [self.events['LTO'].copy(), self.events['LHS'].copy(),
                          self.events['RTO'].copy(), self.events['RHS'].copy()]
        for idx in idxs:
            (i,) = np.where(L1[:, 1] >= idx)
            LTOs, L1 = np.split(L1, (i[0],) if len(i) > 0 else (len(L1),))

            (i,) = np.where(L2[:, 1] >= idx)
            LHSs, L2 = np.split(L2, (i[0],) if len(i) > 0 else (len(L2),))

            (i,) = np.where(R1[:, 1] >= idx)
            RTOs, R1 = np.split(R1, (i[0],) if len(i) > 0 else (len(R1),))

            (i,) = np.where(R2[:, 1] >= idx)
            RHSs, R2 = np.split(R2, (i[0],) if len(i) > 0 else (len(R2),))

            split_events.append( {'LTO': LTOs, 'LHS': LHSs, 'RTO': RTOs, 'RHS': RHSs} )
        else:
            split_events.append({'LTO': L1, 'LHS': L2, 'RTO': R1, 'RHS': R2})

        delay = 0
        for i in range(1,len(split_events)):
            delay += len(timestamps[i-1])
            split_events[i]['LTO'][:,1] -= delay
            split_events[i]['LHS'][:,1] -= delay
            split_events[i]['RTO'][:,1] -= delay
            split_events[i]['RHS'][:,1] -= delay

        new_signals = []

        for i in range(len(idxs)+1):
            new_signals.append(Senial(foot_heights[i], self.foot_side, split_events[i],
                                      angles[i], self.angle_description, self.angle_side,
                                      timestamps[i]))
        return new_signals
