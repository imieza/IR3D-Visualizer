from __future__ import division
import matplotlib.pyplot as plt
from scipy.io import wavfile
import numpy
import math
from scipy import signal
import numpy as np
from scipy.signal import correlate, fftconvolve


def import_signal():
    file_name_dir = 'C:\Users\W\Documents\IR3D\IRV360\Audios de prueba\Odeon\Refleccion piso + techo + trasera + lateral.Wav'
    file_name = 'C:\Users\W\Documents\IR3D\IRV360\Audios de prueba\Odeon\Directo.Wav'
    fs, data = wavfile.read(file_name)
    return fs, data

def pressure_to_intensity_fft(fs, data):
    time_window = 1
    raiz2_sobre_z = math.sqrt(2)/414
    n_window_frames = int(time_window * fs / 1000)
    window_start_index = range(n_window_frames // 2, len(data[:, 0]) - n_window_frames // 2)

    Ix, Iy, Iz, I = [], [], [], []
    Coehx, Coehy, Coehz, Coeh =  [], [], [], []
    for index in window_start_index:
        fft_window = []
        for channel in range(4):
            to_index = int(index + n_window_frames // 2)
            from_index  = int(index - n_window_frames // 2)
            fft_window.append(numpy.fft.fft(data[from_index:to_index, channel]))
        ix, iy, iz = [], [],[]
        coehx, coehy, coehz = [], [],[]

        for freq in range(len(fft_window[0])):
            ix.append(raiz2_sobre_z * numpy.real(fft_window[0][freq]*fft_window[1][freq]))
            iy.append(raiz2_sobre_z * numpy.real(fft_window[0][freq]*fft_window[2][freq]))
            iz.append(raiz2_sobre_z * numpy.real(fft_window[0][freq]*fft_window[3][freq]))
            # coehx.append(
            #     raiz2_sobre_z
            #     *
            #     numpy.real(fft_window[0][freq]*fft_window[1][freq])
            #     /
            #     math.sqrt(
            #         numpy.abs(fft_window[0][freq])**2
            #         +
            #         numpy.abs(fft_window[1][freq])**2
            #     )
            # )
            # coehx.append(raiz2_sobre_z * numpy.real(fft_window[0][freq] * fft_window[2][freq]) /
            #             math.sqrt(numpy.abs(fft_window[0][freq])**2 + numpy.abs(fft_window[2][freq])**2))
            # coehx.append(raiz2_sobre_z * numpy.real(fft_window[0][freq] * fft_window[3][freq]) /
            #             math.sqrt(numpy.abs(fft_window[0][freq])**2 + numpy.abs(fft_window[3][freq])**2))

        sum_x = sum(ix)
        sum_y = sum(iy)
        sum_z = sum(iz)

        Iy.append(sum_x)
        Ix.append(sum_y)
        Iz.append(sum_z)
        I.append((sum_x**2 + sum_y**2 + sum_z**2) ** .5)

        sum_coehx = sum(coehx)
        sum_coehy = sum(coehy)
        sum_coehz = sum(coehz)

        Coehy.append(sum_coehx)
        Coehx.append(sum_coehy)
        Coehz.append(sum_coehz)
        Coeh.append((sum_coehx ** 2 + sum_coehy ** 2 + sum_coehz ** 2) ** .5)

    return I, Ix, Iy, Iz
    #     az_el_windows[0, window] = math.atan2(intensity_windows[2, window], intensity_windows[1, window])
    #     az_el_windows[1, window] = math.asin(intensity_windows[3, window] / abs(intensity_windows[0, window]))
    # i_db = i_db / i_db.max()
    #return intensity_windows, az_el_windows, i_db


def plot(I,Ix,Iy,Iz):
    fig, (ax_I, ax_Ix, ax_Iy, ax_Iz) = plt.subplots(4, 1, sharex=True)
    ax_I.plot(I)
    ax_I.set_title('Magnitud del vector Intensidad')

    ax_Ix.plot(Ix)
    ax_Ix.set_title('Magnitud de la componente de intensidad X')

    ax_Iy.plot(Iy)
    ax_Iy.set_title('Magnitud de la componente de intensidad Y')

    ax_Iz.plot(Iz)
    ax_Iz.set_title('Magnitud de la componente de intensidad Z')
    plt.show()

plot(*pressure_to_intensity_fft(*import_signal()))

