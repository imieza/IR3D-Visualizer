import itertools
import threading

import matplotlib.pyplot as plt
import numpy
from matplotlib.lines import Line2D

from detect_peaks import detect_peaks

info = numpy.load('infoSelector.npy').item()
audio = numpy.load('original_data.npy')[0]

number_of_windows = info['number_of_windows']
time_window = info['time_window']
data = info['data'][0, :]
fs = info['fs']

possible_direct = detect_peaks(data, mph=.9)
direct = possible_direct[numpy.argmax(data[possible_direct])]  # max value of the all possible direct
index_of_peaks = detect_peaks(data, mph=-300, mpd=time_window * fs / 2000)
index_of_peaks = (index_of_peaks[numpy.argsort(data[index_of_peaks])])
index_of_peaks = index_of_peaks[::-1][0:7] - 1
index_of_peaks = numpy.insert(index_of_peaks, 0, direct)
index_of_peaks.sort()

windows = [range(peak - 22, peak + 22) for peak in index_of_peaks]
distance = 5

lines = []

fig = plt.figure()
def plot(sig, peaks, selected):
    global lines
    lines=[]
    plt.clf()
    plt.plot(sig)
    sig = numpy.array(sig)
    for peaks_set in peaks:
        line, = plt.plot(peaks_set, sig[peaks_set], 'g', picker=7)
        lines.append(line)
    plt.plot(peaks[selected], sig[peaks[selected]], 'r',  linewidth=3.0)
    plt.xlim(peaks[0][0]-200, peaks[-1][-1]+200)

def onpick1(event):
    thisline = event.artist
    if isinstance(thisline , Line2D):
       selected = [str(line) for line in lines].index(str(thisline))
       plot(audio, windows, selected)
       plt.draw()



fig.canvas.mpl_connect('pick_event', onpick1)
plot(audio, windows, 0)
plt.show()
