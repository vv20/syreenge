import numpy
import matplotlib.pyplot as plt
from scipy.io import wavfile
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLineEdit, QPushButton, QFileDialog, QSizePolicy, QMainWindow
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

AMP_TICKS_PER_SECOND = 4000

class SyreengeKernel():
    _instance = None

    def __init__(self):
        self.sampleFileName = ""
        self.sample = numpy.zeros((1))
        self.fs = 0
        self.sampleSpecGram = numpy.zeros((1))

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SyreengeKernel, cls).__new__(cls)
        return cls._instance

    def loadSampleFile(self, sampleFileName):
        self.sampleFileName = sampleFileName
        self.fs, self.sample = wavfile.read(self.sampleFileName)
        self.sample = compressSampleChannels(self.sample)
        self.sampleSpecGram = scipy.signal.spectrogram(self.sample, self.fs)

class SyreengeApp(QMainWindow):

    def __init__(self):
        super().__init__()
        self.left = 10
        self.top = 10
        self.width = 1000
        self.height = 700
        self.title = "SYREENGE - SYnthesizer REverse ENG(E)ineering"
        self.sampleFileName = "sample.wav"
        self.fs, self.sample = wavfile.read(self.sampleFileName)
        self.sample = compressSampleChannels(self.sample)
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.sampleFileTextBox = QLineEdit(self.sampleFileName, self)
        self.selectSampleFileButton = QPushButton("Select sample file", self)
        self.sampleSpecGram = FrequencyProfilePlot(self.sample, self.fs, self)
        self.sampleFileTextBox.setReadOnly(True)
        self.sampleFileTextBox.move(20, 20)
        self.selectSampleFileButton.move(20, 50)
        self.sampleSpecGram.move(20, 80)
        self.selectSampleFileButton.clicked.connect(self.selectSampleFile)
        self.show()

    @pyqtSlot()
    def selectSampleFile(self):
        self.sampleFileName, _ = QFileDialog.getOpenFileName(self, "Select sample file")
        self.sampleFileTextBox.setText(self.sampleFileName)
        self.fs, self.sample = wavfile.read(self.sampleFileName)
        self.sample = compressSampleChannels(self.sample)
        self.sampleSpecGram.setSample(self.sample, self.fs)
        self.sampleSpecGram.plot()

class FrequencyProfilePlot(FigureCanvas):

    def __init__(self, sample, fs, parent, width=5, height=4, dpi=100):
        self.sample = sample
        self.fs = fs
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        self.plot()

    def setSample(self, sample, fs):
        self.sample = sample
        self.fs = fs

    def plot(self):
        self.axes.specgram(self.sample, Fs=self.fs)
        self.draw()

def displayAmplitude(fs, data):
    amp = data.copy()
    amp = abs(amp)
    amp = (amp[:,0] + amp[:,1]) / 2
    ampTicks = len(data) / fs * AMP_TICKS_PER_SECOND
    amp = numpy.convolve(amp, [1] * int(ampTicks))
    plt.plot(range(len(amp)), amp)
    plt.show()

def getFcyProfile(fs, data):
    powerSpectrum, fciesFound, time, imageAxis = plt.specgram(data, Fs=fs)
    plt.show()

def compressSampleChannels(sample):
    return (sample[:,0] + sample[:,1]) / 2

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = SyreengeApp()
    sys.exit(app.exec_())
#   filename = 'sample.wav'
#   fs, data = wavfile.read(filename)
#   displayFrequencyProfile(fs, data)
