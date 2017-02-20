import math
import numpy
from scipy import signal
from scipy.io import wavfile

from detect_peaks import detect_peaks


class DataProcessing(object):

    def __init__(self,Self):
        super(DataProcessing, self).__init__()
        self.Self = Self
        self.refresh_parameters()

    def refresh_parameters(self):
        self.time_window = self.Self .parameters["timeWindow"] #1
        self.number_of_windows = self.Self .parameters["number_of_windows"] #256
        self.cutoff_frequency = self.Self .parameters["cutoff_frequency"] #5000
        self.value2truncate = self.Self.parameters["value2truncate"] #None

    def low_filtering(self, data, fs=44100):
        self.refresh_parameters()
        cutoff = self.cutoff_frequency  # desired cutoff frequency of the filter, Hz
        cutoff_w = cutoff * (2 * math.pi)
        fs_w = fs * (2 * math.pi)
        nyq = 0.5 * fs_w
        normal_cutoff = cutoff_w / nyq

        n = 400
        b = signal.firwin(n, cutoff=normal_cutoff, window="hamming")
        a = 1

        self.filterFrequency, self.filterAmplitudeResponse = signal.freqz(b)

        filtered_data_w = signal.filtfilt(b, a, data[0].tolist())[0]
        filtered_data_x = signal.filtfilt(b, a, data[1].tolist())[0]
        filtered_data_y = signal.filtfilt(b, a, data[2].tolist())[0]
        filtered_data_z = signal.filtfilt(b, a, data[3].tolist())[0]

        return numpy.matrix([filtered_data_w, filtered_data_x, filtered_data_y, filtered_data_z])

    def pressure_to_intensity(self, pressure):
        """Convierte valores de presion en intensidad
         :param pressure: Matriz (4x4: w,x,y,z)
         :return intensidad: Matriz(4x4: I,Ix,Iy,Iz)
         """
        self.refresh_parameters()

        Ix = numpy.array(pressure[0, :]) * numpy.array(pressure[1, :])
        Iy = numpy.array(pressure[0, :]) * numpy.array(pressure[2, :])
        Iz = numpy.array(pressure[0, :]) * numpy.array(pressure[3, :])
        I = (Ix ** 2 + Iy ** 2 + Iz ** 2) ** .5
        return numpy.matrix([I[0, :], Ix[0, :], Iy[0, :], Iz[0, :]])

    def temporal_windowing(self, data, fs):
        """ Funcion que segmenta las senales de intensidad en ventanas de tiempo y devuelve los valores de cada ventana
            :param data: matriz de valores de intensidad
            :param fs: frecuencia de sampleo
            :return intensity_windows: 4 x cantidad_de_ventanas matrices con los valores de cada ventana
            :return az_el_windows: 2 x cantidad_de_ventanas matrices con los valores de cada ventana
        """
        self.refresh_parameters()

        n_window_frames = int(self.time_window * fs / 1000)
        window_numbers = range(n_window_frames / 2, len(data.tolist()[0]) - n_window_frames / 2)
        intensity_windows = numpy.zeros(shape=(4, len(data.tolist()[0])))
        az_el_windows = numpy.zeros(shape=(2, len(data.tolist()[0])))
        i_db = numpy.zeros(shape=(1, len(data.tolist()[0])))
        for window in window_numbers:
            for index in range(4):
                intensity_windows[index, window] = (
                (data[index, window - n_window_frames / 2:window + n_window_frames / 2 - 1]).sum())
            az_el_windows[0, window] = math.atan2(intensity_windows[2, window], intensity_windows[1, window])
            az_el_windows[1, window] = math.atan2(intensity_windows[3, window], intensity_windows[0, window])
        i_db[0, :] = self.lin2db(intensity_windows[0, :])
        i_db = i_db / i_db.max()
        return intensity_windows, az_el_windows, i_db

    def load_wavefile(self, file_name):
        """Function that returns an array of each channel, requiered: from scipy.io import wavfile
        :param file_name: ruta del archivo de audio
        :return audio,fs: matriz(4x4) de los canales de audio, frecuencia de sampleo
        """
        self.refresh_parameters()

        fs, data = wavfile.read(file_name)
        audio = numpy.matrix(data)
        self.truncate_value(audio,fs)
        audio = audio.astype(numpy.float64)
        maximum = float(audio.max())
        audio = audio.getT() / maximum
        return [audio, fs]

    def truncate_value(self,audio,fs):
        self.refresh_parameters()
        if self.value2truncate:
            trucate_value_samples = int(self.value2truncate * fs /1000)
            audio = audio[:,:trucate_value_samples]
        return audio

    def lin2db(self, array):
        value_dB = []
        min_value = min(array[numpy.nonzero(array)])
        for value in array:
            if value > 0:
                value_dB.append(10 * math.log10(math.fabs(value) / min_value))
            else:
                value_dB.append(0)
        return value_dB
        self.refresh_parameters()

    def window_selector(self, data, fs):
        self.refresh_parameters()

        possible_direct = detect_peaks(data[0, :], mph=.9)
        direct = possible_direct[numpy.argmax(data[0,possible_direct])]  # max value of the all possible direct
        index_of_peaks = detect_peaks(data[0, direct:], mph=-300, mpd=self.time_window * fs / 2000) + direct - 1
        index_of_peaks = (index_of_peaks[numpy.argsort(data[0, index_of_peaks])])
        index_of_peaks = index_of_peaks[::-1][0:self.number_of_windows - 1]
        index_of_peaks = numpy.insert(index_of_peaks, 0, direct)
        index_of_peaks.sort()
        return index_of_peaks

    def normalizer(self, values, min_value=None, max_value=None):
        self.refresh_parameters()
        if min_value or max_value:
            max_value = max_value - min_value
        else:
            min_value = min(values)
            max_value = max(values) - min_value
        values_normalized = [(value - min_value)/max_value for value in values]
        return values_normalized

    def get_min_max(self, values):
        self.refresh_parameters()
        min_value = numpy.amin(numpy.absolute(numpy.array(values)))
        max_value = numpy.amax(numpy.absolute(numpy.array(values)))
        return min_value,max_value

    def get_center(self,values_normalized):

        pass


    def generate_time(self, fs, data):
        self.refresh_parameters()

        return numpy.arange(0.0, float(len(data.tolist()[0])) / fs, 1.0 / fs)