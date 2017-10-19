from __future__ import division
import math

import itertools
import numpy
from scipy import signal
from scipy.io import wavfile
from detect_peaks import detect_peaks
import sys

class DataProcessing(object):

    def __init__(self,Self):
        super(DataProcessing, self).__init__()
        self.Self = Self
        self.refresh_parameters()

    def refresh_parameters(self):
        self.time_window = self.Self.parameters["timeWindow"] #1
        self.number_of_windows = self.Self.parameters["number_of_windows"] #256
        self.cutoff_frequency_lowpass = self.Self.parameters["cutoff_frequency_lowpass"] #5000
        self.cutoff_frequency_hipass = self.Self.parameters["cutoff_frequency_hipass"] #5000
        self.value2truncate = self.Self.parameters["value2truncate"] #None
        self.threshold = self.Self.parameters["threshold"]

    def filtering(self, data, fs=44100):
        fs_w = fs * (2 * math.pi)
        nyq = 0.5 * fs_w
        def convertion(cutoff):
            cutoff_w = cutoff * (2 * math.pi) # desired cutoff frequency of the filter, Hz
            return cutoff_w / nyq

        self.refresh_parameters()
        low_pass_active = self.Self.ui.low_pass_active.isChecked()
        hi_pass_active = self.Self.ui.hi_pass_active.isChecked()
        low_pass_cutoff = convertion(self.cutoff_frequency_lowpass*1000)
        hi_pass_cutoff = convertion(self.cutoff_frequency_hipass*1000)

        n = 800
        if not low_pass_active and not hi_pass_active:
            return data
        elif low_pass_active and not hi_pass_active:
            b = signal.firwin(n, low_pass_cutoff, window="hamming")
        elif not low_pass_active and hi_pass_active:
            b = signal.firwin(n+1, hi_pass_cutoff, window="hamming", pass_zero=False)
        elif low_pass_active and hi_pass_active:
            b = signal.firwin(n, [hi_pass_cutoff,low_pass_cutoff], window="hamming", pass_zero=False)

        self.filterFrequency, self.filterAmplitudeResponse = signal.freqz(b)

        a = 1
        filtered_data_w = signal.filtfilt(b, a, data[0].tolist())[0]
        filtered_data_x = signal.filtfilt(b, a, data[1].tolist())[0]
        filtered_data_y = signal.filtfilt(b, a, data[2].tolist())[0]
        filtered_data_z = signal.filtfilt(b, a, data[3].tolist())[0]

        output = numpy.matrix([filtered_data_w, filtered_data_x, filtered_data_y, filtered_data_z])
        return output / output.max()

    def pressure_to_intensity_fft(self, fs, data):
        self.refresh_parameters()
        raiz2_sobre_z = math.sqrt(2) / 414
        n_window_frames = int(self.time_window * fs / 1000)
        window_numbers = range(n_window_frames // 2, len(numpy.array(data)[0]) - n_window_frames // 2)
        intensity_windows = numpy.zeros(shape=(4, len(data.tolist()[0])))
        az_el_windows = numpy.zeros(shape=(2, len(numpy.array(data)[0])))

        for window in window_numbers:
            fft_window = []
            from_index = int(window - n_window_frames / 2)
            to_index = int(window + n_window_frames / 2)
            for channel in range(4):
                fft_window.append(numpy.fft.fft(numpy.array(data)[channel][from_index:to_index]))
            ix, iy, iz = [], [], []

            for freq in range(len(fft_window[0])):
                ix.append(raiz2_sobre_z * numpy.real(fft_window[0][freq] * fft_window[1][freq]))
                iy.append(raiz2_sobre_z * numpy.real(fft_window[0][freq] * fft_window[2][freq]))
                iz.append(raiz2_sobre_z * numpy.real(fft_window[0][freq] * fft_window[3][freq]))

            sum_x = sum(ix)
            sum_y = sum(iy)
            sum_z = sum(iz)
            sum_i = (sum_x ** 2 + sum_y ** 2 + sum_z ** 2) ** .5

            intensity_windows[0,window] = sum_i
            intensity_windows[1,window] = sum_x
            intensity_windows[2,window] = sum_y
            intensity_windows[3,window] = sum_z

            az_el_windows[0, window], az_el_windows[1, window] = self.cart2sph(sum_i, sum_x, sum_y, sum_z)
        i_db = numpy.array(self.lin2db(numpy.array(intensity_windows[0, :])))
        intensity_windows /= intensity_windows.max()
        return intensity_windows, intensity_windows, az_el_windows, i_db

    def pressure_to_intensity(self, pressure):
        """Convierte valores de presion en intensidad
         :param pressure: Matriz (4x4: w,x,y,z)
         :return intensidad: Matriz(4x4: I,Ix,Iy,Iz)
         """
        self.refresh_parameters()

        Ix = numpy.array((pressure[0, :])) * numpy.array(pressure[1, :])
        Iy = numpy.array((pressure[0, :])) * numpy.array(pressure[2, :])
        Iz = numpy.array((pressure[0, :])) * numpy.array(pressure[3, :])
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
        window_numbers = range(n_window_frames // 2, len(data.tolist()[0]) - n_window_frames // 2)
        intensity_windows = numpy.zeros(shape=(4, len(data.tolist()[0])))
        az_el_windows = numpy.zeros(shape=(2, len(data.tolist()[0])))
        for window in window_numbers:
            from_index = int(window - n_window_frames / 2)
            to_index = int(window + n_window_frames / 2)
            for channel in range(4):
                intensity_windows[channel, window] = data[channel, from_index:to_index].sum()

            az_el_windows[0, window], \
            az_el_windows[1, window] = self.cart2sph(
                intensity_windows[0,window],
                intensity_windows[1,window],
                intensity_windows[2,window],
                intensity_windows[3,window]
            )
        i_db = numpy.array(self.lin2db(numpy.array(intensity_windows[0, :])))
        intensity_windows /= intensity_windows.max()
        return intensity_windows, az_el_windows, i_db

    def load_wavefile(self, file_name):
        """Function that returns an array of each channel, requiered: from scipy.io import wavfile
        :param file_name: ruta del archivo de audio
        :return audio,fs: matriz(4x4) de los canales de audio, frecuencia de sampleo
        """
        self.refresh_parameters()
        audio = []
        if len(file_name)==4:
            audio = [[w, x, y, z] for [w, x, y, z] in zip(
                wavfile.read(file_name[0], mmap=True)[1],
                wavfile.read(file_name[1], mmap=True)[1],
                wavfile.read(file_name[2], mmap=True)[1],
                wavfile.read(file_name[3], mmap=True)[1],
            )]
            fs = wavfile.read(file_name[0], mmap=True)[0]
            audio = numpy.matrix(audio)
        elif len(file_name)!=1:
            sys.stderr.write(
                'Error: You are selected ' +
                str(len(file_name)) +
                'audio files. Please select one multichannel or four mono')
            return
        else:
            fs, data = wavfile.read(file_name[0], mmap=True)
            audio = numpy.matrix(data)
        return [audio, fs]

    def truncate_value(self,audio,fs):
        import scipy.signal as signal

        self.refresh_parameters()
        if self.value2truncate:
            trucate_value_samples = int(self.value2truncate * fs /1000)
            audio = audio[:,:trucate_value_samples]
        return audio

    def lin2db(self, array):
        values_dB = []
        threshold = 96 - self.threshold
        max_val = max(array[numpy.nonzero(array)])
        for value in array:
            if value > 0:
                calc = 96 + 20 * math.log10(value / max_val)
                values_dB.append(calc) if calc > threshold else values_dB.append(threshold)
            else:
                values_dB.append(threshold)
        return values_dB

    def direct_sound_selector(self, i_db, index_of_peaks, fs):
        index_of_peaks_7 = numpy.argsort(i_db[index_of_peaks])[::-1][0:(15 if self.Self.parameters["overlapping"] == "Half overlapped" else 100)]  # Select the 25 most representative
        index_of_peaks_7.sort()  # Ordered again
        index_of_peaks_7 = [index for index in index_of_peaks_7 if i_db[index_of_peaks[index]]>0]
        index_of_direct_peaks = index_of_peaks[index_of_peaks_7[0]:index_of_peaks_7[-1]] if len(index_of_peaks_7)>1 else index_of_peaks_7 # Take all peaks between
        self.Self.calc['directSoundSelection_peaks'] = index_of_direct_peaks
        return index_of_direct_peaks

    def window_selector(self, i_db, fs):
        self.refresh_parameters()
        peaks_positions_4direct = detect_peaks(i_db, mpd=(self.time_window * fs / 2000))
        if self.Self.parameters["overlapping"] == "Half overlapped":
            peaks_positions = peaks_positions_4direct
        elif self.Self.parameters["overlapping"] == "Full overlapped":
            peaks_positions = detect_peaks(i_db)
        else:
            peaks_positions = numpy.arange(len(i_db.tolist()))

        peaks_4direct = [peak for peak in peaks_positions if peaks_positions_4direct[0] <= peak <= peaks_positions_4direct[-1]]
        direct_peak_position = self.direct_sound_selector(i_db, peaks_4direct, fs)[self.Self.parameters['directSoundSelection']]
        after_direct_peaks = peaks_positions[peaks_positions>= direct_peak_position]
        # Get the N number_of_windows of highest level
        output_peaks = after_direct_peaks[numpy.argsort(i_db[after_direct_peaks])][::-1][0:self.number_of_windows]
        output_peaks.sort()
        #index_of_peaks = numpy.insert(index_of_peaks, 0, index_of_peaks_direct)
        return output_peaks

    def normalizer(self, values):
        min_value = min(values)
        max_value = max(values) - min_value
        new_values = [(value - min_value)/max_value for value in values] if len(values)>1 else values
        return new_values

    def get_min_max(self, values):
        self.refresh_parameters()
        min_value = numpy.amin(numpy.absolute(numpy.array(values)))
        max_value = numpy.amax(numpy.absolute(numpy.array(values)))
        return min_value,max_value

    def cart2sph(self,r,x,y,z):
        az = math.atan2(y, x)
        el = math.atan2(z, math.sqrt(x*x + y*y)) if math.sqrt(x*x + y*y) != 0.0 else math.pi / 2
        return az, el

    def sph2cart(self, az_el_windows, peaks, r):
        [azimuth, elevation] = az_el_windows[:, peaks]
        x = r * numpy.cos(elevation) * numpy.cos(azimuth)
        y = r * numpy.cos(elevation) * numpy.sin(azimuth)
        z = r * numpy.sin(elevation)
        return x, y, z

    def get_center(self,xyz):
        x,y,z=xyz
        return [x.max()/(x.max()- x.min()), y.max()/(y.max()- y.min())]

    def generate_time(self, fs, data):
        self.refresh_parameters()
        return numpy.arange(len(data.tolist()[0])) / fs

    def refactoring_time(self):
        # Make time beginnings in direct sound
        self.Self.calc['time'] = self.Self.calc['time'] - self.Self.calc['time'][self.Self.calc['peaks'][0]]

    def get_audio_bformat(self, file_name):
        a_format = False
        [audio, fs] = self.load_wavefile(file_name)
        audio = self.truncate_value(audio, fs)
        audio = audio.astype(numpy.float64)
        audio = audio /audio.max()

        if a_format:audio = self.a2b_converter(audio, fs)
        else: audio = audio.getT()
        return audio, fs

    def a2b_converter(self, data, fs):
        if fs != 44100:
            number_of_samples = (data.size/fs)*44100
            FLU = signal.resample(data[:,0], number_of_samples)
            FRD = signal.resample(data[:,1], number_of_samples)
            BLD = signal.resample(data[:,2], number_of_samples)
            BRU = signal.resample(data[:,3], number_of_samples)

        else:
            FLU = numpy.squeeze(numpy.asarray(data[:, 0]))
            FRD = numpy.squeeze(numpy.asarray(data[:, 1]))
            BLD = numpy.squeeze(numpy.asarray(data[:, 2]))
            BRU = numpy.squeeze(numpy.asarray(data[:, 3]))

        data_b = [FLU + FRD + BLD + BRU,
                FLU + FRD - BLD - BRU,
                FLU - FRD + BLD - BRU,
                FLU + FRD + BLD - BRU]

        filters = [
            numpy.array(wavfile.read('FiltroW.wav', mmap=True)[1]),
            numpy.array(wavfile.read('FiltroX.wav', mmap=True)[1]),
            numpy.array(wavfile.read('FiltroW.wav', mmap=True)[1]),
            numpy.array(wavfile.read('FiltroY.wav', mmap=True)[1]),
        ]
        filters_filled = numpy.pad(filters, ((0, 0), (0, int(FLU.size - filters[0].size))),
                                   mode='constant', constant_values=0)

        signal_convolved = [signal.fftconvolve(audio_ch, data_ch)
                            for audio_ch,data_ch in itertools.izip(filters_filled,data_b)]

        return numpy.asmatrix(numpy.vstack((signal_convolved)))