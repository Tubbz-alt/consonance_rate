# -*- coding: utf-8 -*-

#   Copyright (C) 2015-2016 Samuele Carcagno <sam.carcagno@gmail.com>
#   This file is part of consonance_rate

#    consonance_rate is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    consonance_rate is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with consonance_rate.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import nested_scopes, generators, division, absolute_import, with_statement, print_function, unicode_literals
import os, random, time
import PyQt4.Qwt5 as Qwt
import numpy as np
import pandas as pd

from sndlib import*
from wavpy import*
from utils import*
from pyqtver import*


if pyqtversion == 4:
    from PyQt4 import QtCore, QtGui
    from PyQt4.QtCore import Qt, QEvent
    from PyQt4.QtGui import QApplication, QAction, QCheckBox, QComboBox, QDesktopServices, QDesktopWidget, QDoubleValidator, QFrame, QFileDialog, QFont, QGridLayout, QHBoxLayout, QIcon, QInputDialog, QIntValidator, QLabel, QLayout, QLineEdit, QMainWindow, QMessageBox, QProgressBar, QScrollArea, QSizePolicy, QSlider, QSpacerItem, QSplitter, QPushButton, QTextEdit, QVBoxLayout, QWhatsThis, QWidget
    QFileDialog.getOpenFileName = QFileDialog.getOpenFileNameAndFilter
    QFileDialog.getOpenFileNames = QFileDialog.getOpenFileNamesAndFilter
    QFileDialog.getSaveFileName = QFileDialog.getSaveFileNameAndFilter
    QtCore.Signal = QtCore.pyqtSignal
    QtCore.Slot = QtCore.pyqtSlot
# elif pyqtversion == -4:
#     import PySide
#     from PySide import QtCore, QtGui
#     from PySide.QtCore import Qt, QEvent
#     from PySide.QtGui import QAction, QCheckBox, QComboBox, QDesktopServices, QDesktopWidget, QDoubleValidator, QFrame, QFileDialog, QGridLayout, QHBoxLayout, QIcon, QIntValidator, QLabel, QLayout, QLineEdit, QMainWindow, QMessageBox, QScrollArea, QSizePolicy, QSlider, QSpacerItem, QSplitter, QPushButton, QVBoxLayout, QWhatsThis, QWidget
# elif pyqtversion == 5:
#     from PyQt5 import QtCore, QtGui
#     from PyQt5.QtCore import Qt, QEvent
#     from PyQt5.QtWidgets import QAction, QCheckBox, QComboBox, QDesktopWidget, QFrame, QFileDialog, QGridLayout, QHBoxLayout, QLabel, QLayout, QLineEdit, QMainWindow, QMessageBox, QScrollArea, QSizePolicy, QSlider, QSpacerItem, QSplitter, QPushButton, QVBoxLayout, QWhatsThis, QWidget
#     from PyQt5.QtGui import QDesktopServices, QDoubleValidator, QIcon, QIntValidator
#     QtCore.Signal = QtCore.pyqtSignal
#     QtCore.Slot = QtCore.pyqtSlot

phonesCalFile = os.path.expanduser("~") +'/.config/consonance_rate/phonesCal.txt'

if os.path.exists(os.path.expanduser("~") +'/.config/') == False:
    os.mkdir(os.path.expanduser("~") +'/.config/')
if os.path.exists(os.path.expanduser("~") +'/.config/consonance_rate/') == False:
    os.mkdir(os.path.expanduser("~") +'/.config/consonance_rate/')
if os.path.exists(phonesCalFile) == False:
    fHandle = open(phonesCalFile, 'w')
    fHandle.write("101")
    fHandle.close()

class mainWin(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        screen = QDesktopWidget().screenGeometry()
        self.setGeometry(80, 100, int((1/2)*screen.width()), int((4/10)*screen.height()))
        self.main_frame = QFrame()
        self.cw = QFrame()
        self.cw.setFrameStyle(QFrame.StyledPanel|QFrame.Sunken)
        self.main_sizer = QVBoxLayout()
        self.hbox1_sizer = QHBoxLayout()
        self.setWindowTitle(self.tr("Consonance Rating"))
        ##
        self.sessionRunning = False
        self.listenerID = ""
        self.currentTrial = 1
        self.intervals_db = pd.read_csv(os.path.abspath(os.path.dirname(__file__)) + "/resources/intervals_database.csv", sep=";")
        # self.rootNotes = np.array([110, 130.81, 185])
        # self.intervalsCents = np.array([100,
        #                                500,
        #                                600,
        #                                700,
        #                                800,
        #                                1100])
        #self.rootNotes = np.array([110, 185])
        self.rootNotes = np.array([146.83,
                                   155.56,
                                   164.81,
                                   174.61,
                                   185,
                                   196,
                                   207.65,
                                   220])
        self.intervalsCents = np.array([600,
                                      
                                      
                                       700
                                      
                                       ])

        self.diadDur = 1980
        self.diadRamps = 10
        self.diadTotLev = np.array([40, 80])
        self.diadFilterType = "lowpass"
        self.diadFilterCutoffs = (2500,)
        self.diadLowHarm = 1
        self.diadHighHarm = 50
        self.diadNote1Chan = "Both"
        self.diadNote2Chan = "Both"
        self.fs = 48000
        self.maxLevel = self.getPhonesCal()
        self.noise1SL = -200
        self.noise1LowFreq = 0
        self.noise1HighFreq = 2000
        self.noise1Type = "Pink"
        self.noise2Type = "Pink"
        self.noise2SL = np.array([0, 40])
        self.noise2LowFreq = 4000
        self.noise2HighFreq = 8000
        self.noise1RefHz = 100
        self.noise2RefHz = 4000
        self.preTrialNoiseRefHz = 1000
        self.preTrialNoiseLowFreq = 20
        self.preTrialNoiseHighFreq = 8000
        self.preTrialNoiseDur = 1980
        self.preTrialNoiseRamps = 10
        self.preTrialNoiseSL = np.array([0, 40])
        self.preTrialNoiseType = "Pink"
        self.preTrialNoiseChannel = "Both"
        self.preTrialNoiseDiadISI = 500
        self.noiseChannel = "Both"

        self.nPracticeTrialsXStim = 4
        self.nTrialsXStim = 2
        self.nTrials = len(self.rootNotes)*len(self.intervalsCents)*len(self.diadTotLev)*(self.nTrialsXStim) + self.nPracticeTrialsXStim*len(self.intervalsCents)*len(self.diadTotLev)
        print(self.nTrials)
        practiceTrials = []
        mainTrials = []
        for rootNote in self.rootNotes:
            for intervalCents in self.intervalsCents:
                for n in range(self.nTrialsXStim):
                    mainTrials.append((rootNote, intervalCents, "main", self.diadTotLev[0], self.noise2SL[0], self.preTrialNoiseSL[0]))

        for intervalCents in self.intervalsCents:
            for n in range(self.nPracticeTrialsXStim):
                practiceTrials.append((random.choice(self.rootNotes), intervalCents, "practice", self.diadTotLev[0], self.noise2SL[0], self.preTrialNoiseSL[0]))

        random.shuffle(practiceTrials)
        random.shuffle(mainTrials)

        practiceTrials2 = []
        mainTrials2 = []
        for rootNote in self.rootNotes:
            for intervalCents in self.intervalsCents:
                for n in range(self.nTrialsXStim):
                    mainTrials2.append((rootNote, intervalCents, "main", self.diadTotLev[1], self.noise2SL[1], self.preTrialNoiseSL[1]))

        for intervalCents in self.intervalsCents:
            for n in range(self.nPracticeTrialsXStim):
                practiceTrials2.append((random.choice(self.rootNotes), intervalCents, "practice", self.diadTotLev[1], self.noise2SL[1], self.preTrialNoiseSL[1]))

        random.shuffle(practiceTrials2)
        random.shuffle(mainTrials2)

        #root note
        #interval cents
        #practice or main
        #dialTotLev
        #noise2SL
        #preTrialNoiseSL

        #remove some practice trials
        #practiceTrials = practiceTrials[0:4]
        #practiceTrials2 = practiceTrials2[0:4]
        
        self.trialList = []
        if random.choice([0,1]) == 0:
            self.trialList.extend(practiceTrials)
            self.trialList.extend(practiceTrials2)
        else:
            self.trialList.extend(practiceTrials2)
            self.trialList.extend(practiceTrials)
        if random.choice([0,1]) == 0:
            self.trialList.extend(mainTrials)
            self.trialList.extend(mainTrials2)
        else:
            self.trialList.extend(mainTrials2)
            self.trialList.extend(mainTrials)

        
      
        print(len(self.trialList))
        self.menubar = self.menuBar()
        self.fileMenu = self.menubar.addMenu(self.tr('-'))
        
        self.editPhonesAction = QAction(self.tr('Phones Calibration'), self)
        self.fileMenu.addAction(self.editPhonesAction)
        self.editPhonesAction.triggered.connect(self.onEditPhones)

        
        self.setupListenerButton = QPushButton(self.tr("Setup Listener"), self)
        self.setupListenerButton.clicked.connect(self.onClickSetupListenerButton)
        self.setupListenerButton.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
        # self.setupListenerButton.setToolTip(self.tr("Choose file to save results"))
        # self.setupListenerButton.setWhatsThis(self.tr("Choose where to save the result files"))
        self.setupListenerButton.setStyleSheet('font-size: 32pt; font-weight: bold')
        self.hbox1_sizer.addWidget(self.setupListenerButton)
        self.main_sizer.addLayout(self.hbox1_sizer)

        #statusButtonFont = QFont("Arial", 26);
        self.statusButton = QPushButton(self.tr("Start"), self)
        self.statusButton.clicked.connect(self.onClickStatusButton)
        self.statusButton.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
        self.main_sizer.addWidget(self.statusButton)
        #self.statusButton.setFont(statusButtonFont)
        self.statusButton.setStyleSheet('font-size: 32pt; font-weight: bold')
        self.statusButton.hide()
        self.cw.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        borderWidth = 4
        self.main_sizer.addItem(QSpacerItem(20, 60, QSizePolicy.Fixed))

        self.overallRatingSliderValue = QLabel(self.tr("0"), self)
        self.main_sizer.addWidget(self.overallRatingSliderValue)
        self.overallRatingSliderValue.setStyleSheet('font-size: 22pt; font-weight: normal')
        self.overallRatingSliderValue.setAlignment(Qt.AlignCenter)

        self.main_sizer.addItem(QSpacerItem(20,60, QSizePolicy.Fixed))
        sliderFont = QFont("Ubuntu", 18)
        self.overallRatingSlider = Qwt.QwtSlider(self, Qt.Horizontal, Qwt.QwtSlider.BottomScale)
        self.overallRatingSlider.setFont(sliderFont)
        self.overallRatingSlider.setScale(-3.0,3.0, 1)
        self.overallRatingSlider.setRange(-3.0,3.0)
        self.overallRatingSlider.valueChanged[float].connect(self.sliderChanged)
        self.overallRatingSlider.setMinimumSize(800, 20)
        self.overallRatingSlider.setBorderWidth(borderWidth)
        self.main_sizer.addWidget(self.overallRatingSlider)

        self.main_sizer.addItem(QSpacerItem(20,30, QSizePolicy.Fixed))
        self.gauge = QProgressBar(self)
        self.gauge.setRange(0, 100)
        self.main_sizer.addWidget(self.gauge)
      
        self.cw.setLayout(self.main_sizer)
    

        self.setCentralWidget(self.cw)
        self.show()

    def onClickStatusButton(self):
        if self.statusButton.text() == self.tr("Finished"):
            return
        self.sessionRunning = True
        self.statusButton.setText(self.tr("Running"))
        QApplication.processEvents()
        if self.listenerID == "":
            text, ok = QInputDialog.getText(self, "" , "Listener ID: ")
            if ok:
                self.listenerID = text
                self.statusButton.setText(self.tr("Start"))
            return

        if self.currentTrial == 1:
            self.setupListenerButton.hide()
            self.overallRatingSlider.setValue(0)
            self.overallRatingSliderValue.setText("")
           
            self.doTrial()
            return

        if self.overallRatingSliderValue.text() == "":
            ret = QMessageBox.warning(self, self.tr("Warning"),
                                      self.tr("You need to move the slider before going to the next trial.\nIf you want to assign a score of zero move the slider forth and then back to the zero position."),
                                      QMessageBox.Ok)
            return

        if self.currentTrial > 1:
            self.storeRating()
            self.gauge.setValue((self.currentTrial-1)/self.nTrials*100)
            #self.sliderChanged(0)
            self.sliderLabelReset()
            self.statusButton.setText(self.tr("Running"))
            QApplication.processEvents()
        if self.currentTrial <= self.nTrials :
            self.doTrial()
        else:
            self.statusButton.setText(self.tr("Finished"))
     
            
    def doTrial(self):
        self.statusButton.setText(self.tr("Running"))
        QApplication.processEvents()

        #root note
        rootNote = self.trialList[self.currentTrial-1][0]
        #interval cents
        intervalCents = self.trialList[self.currentTrial-1][1]
        #practice or main
        trialMode = self.trialList[self.currentTrial-1][2]
        #dialTotLev
        diadTotLev = self.trialList[self.currentTrial-1][3]
        #noise2SL
        noise2SL = self.trialList[self.currentTrial-1][4]
        #preTrialNoiseSL
        preTrialNoiseSL = self.trialList[self.currentTrial-1][5]

        try:
            intervalName = self.intervals_db["name"][self.intervals_db["cents"] == self.trialList[self.currentTrial-1][1]].values[0]
        except:
            intervalName = str(self.trialList[self.currentTrial-1][1])
        print(intervalName)

        preTrialNoise = broadbandNoise(spectrumLevel=preTrialNoiseSL,
                                       duration=self.preTrialNoiseDur,
                                       ramp=self.preTrialNoiseRamps, channel=self.preTrialNoiseChannel,
                                       fs=self.fs, maxLevel=self.maxLevel)
        if self.preTrialNoiseType == "Pink":
            preTrialNoise = makePinkRef(preTrialNoise, self.fs, self.preTrialNoiseRefHz)

        preTrialNoise = fir2Filter2(preTrialNoise, filterType="bandpass", nTaps=256, cutoffs=(self.preTrialNoiseLowFreq, self.preTrialNoiseHighFreq), transitionWidth=0.2, fs=self.fs)
            
        diad = makeDiad(rootNote, intervalCents,
                       filterType=self.diadFilterType,
                       filterCutoffs=self.diadFilterCutoffs,
                       lowHarm=self.diadLowHarm, highHarm=self.diadHighHarm,
                       diadTotLev=diadTotLev, duration=self.diadDur,
                       ramp=self.diadRamps, note1Channel=self.diadNote1Chan,
                       note2Channel=self.diadNote2Chan, fs=self.fs,
                       maxLevel=self.maxLevel)

        noise1 = broadbandNoise(spectrumLevel=self.noise1SL,
                                       duration=self.diadDur,
                                       ramp=self.diadRamps*6, channel=self.noiseChannel,
                                       fs=self.fs, maxLevel=self.maxLevel)
        if self.noise1Type == "Pink":
            noise1 = makePinkRef(noise1, self.fs, self.noise1RefHz)
        noise1 = fir2Filter2(noise1, filterType="bandpass", nTaps=256,
                             cutoffs=(self.noise1LowFreq, self.noise1HighFreq),
                             transitionWidth=0.2, fs=self.fs)
        noise1 = noise1[0:diad.shape[0],:]
        noise1 = gate(self.diadRamps, noise1, self.fs)
        
        noise2 = broadbandNoise(spectrumLevel=noise2SL,
                                duration=self.diadDur,
                                ramp=self.diadRamps*6, channel=self.noiseChannel,
                                fs=self.fs, maxLevel=self.maxLevel)
        if self.noise2Type == "Pink":
            noise2 = makePinkRef(noise2, self.fs, self.noise2RefHz)
        noise2 = fir2Filter2(noise2, filterType="bandpass", nTaps=256,
                             cutoffs=(self.noise2LowFreq, self.noise2HighFreq),
                             transitionWidth=0.2, fs=self.fs)
        noise2 = noise2[0:diad.shape[0],:]
        noise2 = gate(self.diadRamps, noise2, self.fs)

        stim = diad+noise1+noise2
        noiseDiadSilence = makeSilence(self.preTrialNoiseDiadISI)
        snd = np.concatenate((preTrialNoise, noiseDiadSilence, stim), axis=0)

        wavwrite(snd, self.fs, 32, "snd.wav")
        wavwrite(diad, self.fs, 32, "diad.wav")
        wavwrite(diad+noise1+noise2, self.fs, 32, "diad_in_noise.wav")
        sound(snd)

        self.currentTrial = self.currentTrial+1

    def storeRating(self):
        try:
            intervalName = self.intervals_db["name"][self.intervals_db["cents"] == self.trialList[self.currentTrial-2][1]].values[0]
        except:
            intervalName = str(self.trialList[self.currentTrial-2][1])
        #rootNote = str(self.trialList[self.currentTrial-2][0])

        #root note
        rootNote = self.trialList[self.currentTrial-2][0]
        #interval cents
        intervalCents = self.trialList[self.currentTrial-2][1]
        #practice or main
        trialMode = self.trialList[self.currentTrial-2][2]
        #dialTotLev
        diadTotLev = self.trialList[self.currentTrial-2][3]
        #noise2SL
        noise2SL = self.trialList[self.currentTrial-2][4]
        #preTrialNoiseSL
        preTrialNoiseSL = self.trialList[self.currentTrial-2][5]

        # if self.currentTrial-1 <= len(self.rootNotes)*len(self.intervalsCents)*self.nPracticeTrialsXStim:
        #     trialMode = "practice"
        # else:
        #     trialMode = "main"
        self.thisPageFile.write(self.listenerID + ';')
        self.thisPageFile.write(str(rootNote) + ';')
        self.thisPageFile.write(intervalName + ';')
        self.thisPageFile.write(str(intervalCents) + ';')
        self.thisPageFile.write(trialMode + ';')
        self.thisPageFile.write(str(diadTotLev) + ';')
        #self.thisPageFile.write(str(noise2SL) + ';')
        self.thisPageFile.write(self.overallRatingSliderValue.text() + '\n')
        self.thisPageFile.flush()
        self.overallRatingSlider.setValue(0)
        self.overallRatingSliderValue.setText("")
        


    def sliderChanged(self, value):
        self.overallRatingSliderValue.setText(str(round(value,1)))
        if self.currentTrial > 1 and self.statusButton.text() != self.tr("Finished"):
            self.statusButton.setText(self.tr("Next"))

    def sliderLabelReset(self):
        self.overallRatingSliderValue.setText("0")

    def onClickSetupListenerButton(self):
        text, ok = QInputDialog.getText(self, "" , "Listener ID: ")
        if ok:
            self.listenerID = text
        else:
            return
        ftow = QFileDialog.getSaveFileName(self, self.tr('Choose file to write results'), "", self.tr('All Files (*)'), "", QFileDialog.DontConfirmOverwrite)[0]
        if len(ftow) > 0:
            self.thisPagePath = ftow
            self.thisPageFile = open(self.thisPagePath, "a")
            self.thisPageFile.write("listener;root_note;interval;intervalCents;trial_type;totLev;rating\n")

            self.setupListenerButton.hide()
            self.statusButton.show()
        else:
            return

    def getPhonesCal(self):
        fHandle = open(phonesCalFile, 'r')
        currCal = float(fHandle.readline().strip())
        fHandle.close()

        return currCal

    def writePhonesCal(self, val):
        fHandle = open(phonesCalFile, 'w')
        fHandle.write(str(val))
        fHandle.close()


    def onEditPhones(self):
        currCal = self.getPhonesCal()
        val, ok = QInputDialog.getDouble(self, self.tr('Phones Calibration'), self.tr('Phones Max. Level'), currCal)
        self.writePhonesCal(val)
        self.maxLevel = val
