from __future__ import division
import matplotlib.pyplot as plt
from scipy.io import wavfile
import numpy
import math
from scipy import signal
import numpy as np
from scipy.signal import correlate, fftconvolve


def _add_zeros(a, num, side='both'):
    """Add num zeros at side of array a"""
    return np.hstack([np.zeros(num)] * (side in ('both', 'left')) + [a] +
                     [np.zeros(num)] * (side in ('both', 'right')))


def xcorr(a, b, num, zero_sample=0, normalize=True, domain='freq'):
    """
    Cross-correlation of signals a and b.

    :param a,b: data
    :param num: The cross-correlation will consist of 2*num+1 samples.
        The sample with 0 lag time will be in the middle.
    :param zero_sample: Signals a and b are aligned around the middle of their
        signals.\n
        If zero_sample != 0 a will be shifted additionally to the left.
    :return: cross-correlation
    """
    if zero_sample != 0:
        a = _add_zeros(a, 2 * abs(zero_sample),
                       'left' if zero_sample > 0 else 'right')
    if normalize:
        a = a / np.max(a)
        b = b / np.max(a)
        stdev1 = (np.sum(a ** 2)) ** 0.5
        stdev2 = (np.sum(b ** 2)) ** 0.5
    else:
        stdev1 = stdev2 = 1.
    dif = len(a) - len(b) - 2 * num
    if dif > 0:
        b = _add_zeros(b, dif // 2)
    else:
        a = _add_zeros(a, -dif // 2)
    if domain == 'freq':
        c = fftconvolve(a, b[::-1], 'valid')
    else:
        c = correlate(a, b, 'valid')
    return c / stdev1 / stdev2


def plot(sig1,sig2,corr,sig1_db,corr_db):
    fig, (ax_sig1, ax_sig2, ax_corr, ax_db) = plt.subplots(4, 1, sharex=True)
    ax_sig1.plot(sig1)
    ax_sig1.set_title('Original source')
    ax_sig2.plot(sig2)
    ax_sig2.set_title('Original signal')
    direct_diff = numpy.argmax(abs(corr)) - numpy.argmax(abs(sig2))
    corr_values = numpy.arange(len(corr)) - direct_diff
    ax_corr.plot(corr_values, corr)
    ax_corr.set_title('Cross-correlated')
    ax_db.plot(sig1_db, label="Signal")
    ax_db.plot(corr_values, corr_db, label="Correlation")
    ax_db.set_title('Cross-correlated and Signal in dB')
    ax_db.legend(shadow=True)
    plt.show()


def to_db(audio, thres):
    values_dB = []
    max_val = max(audio[numpy.nonzero(audio)])
    for value in abs(audio):
        if value>0:
            calc = 96 + 20 * math.log10(value/max_val) # segun https://books.google.com.ar/books?id=0f7SBwAAQBAJ&pg=PA227&lpg=PA227&dq=formula+spl+digital&source=bl&ots=IG_RntZgg-&sig=pzWeE9PyXTvb1ZF-sp59IRYDvJ4&hl=es-419&sa=X&ved=0ahUKEwjaqM_ssprVAhUEG5AKHdshCd4Q6AEIMjAC#v=onepage&q=formula%20spl%20digital&f=false
            values_dB.append(calc) if calc > thres else values_dB.append(0)
        else:
            values_dB.append(0)
    return values_dB

file_name = 'C:\Users\W\Documents\IR3D\IRV360\Audios de prueba\Odeon\Refleccion piso + techo + trasera + lateral.Wav'
file_name_dir = 'C:\Users\W\Documents\IR3D\IRV360\Audios de prueba\Odeon\Directo.Wav'
#file_name = 'C:\Users\W\Documents\IR3D\IRV360\Audios de prueba\stpatricks_s1r1.Wav'
fs, data = wavfile.read(file_name)
audio = numpy.matrix(data)
new_audio= numpy.squeeze(numpy.asarray(audio[:, 0]))
threshold = 0


fs, data_dir = wavfile.read(file_name_dir)
audio_dir = numpy.matrix(data_dir)
new_audio_dir = numpy.squeeze(numpy.asarray(audio_dir[:, 0]))


new_audio_corr = xcorr(new_audio, new_audio_dir, 7000)

values_dB = to_db(new_audio, threshold)
values_dB_corr = to_db(new_audio_corr, threshold)
plot(new_audio_dir, new_audio, new_audio_corr, values_dB, values_dB_corr)

