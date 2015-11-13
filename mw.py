# -*- coding: utf-8 -*-

#   Copyright (C) 2015 Samuele Carcagno <sam.carcagno@gmail.com>
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
        self.intervals_db = pd.read_csv("intervals_database.csv", sep=";")
        # self.rootNotes = np.array([110, 130.81, 185])
        # self.intervalsCents = np.array([100,
        #                                500,
        #                                600,
        #                                700,
        #                                800,
        #                                1100])
        self.rootNotes = np.array([110, 185])
        self.intervalsCents = np.array([200,
                                      
                                      
                                       700
                                      
                                       ])
        self.nPracticeTrialsXStim = 1
        self.nTrialsXStim = 2
        self.nTrials = len(self.rootNotes)*len(self.intervalsCents)*(self.nTrialsXStim+self.nPracticeTrialsXStim)
        
        practiceTrials = []
        mainTrials = []
        for rootNote in self.rootNotes:
            for intervalCents in self.intervalsCents:
                for n in range(self.nPracticeTrialsXStim):
                    practiceTrials.append((rootNote, intervalCents))
                for n in range(self.nTrialsXStim):
                    mainTrials.append((rootNote, intervalCents))

        random.shuffle(practiceTrials)
        random.shuffle(mainTrials)
        self.trialList = []
        self.trialList.extend(practiceTrials)
        self.trialList.extend(mainTrials)


        
        self.diadDur = 1980
        self.diadRamps = 10
        self.diadTotLev = 80
        self.diadFilterType = "lowpass"
        self.diadFilterCutoffs = (2500,)
        self.diadLowHarm = 1
        self.diadHighHarm = 50
        self.diadNote1Chan = "Both"
        self.diadNote2Chan = "Both"
        self.fs = 48000
        self.maxLevel = 100
        self.noise1SL = -200
        self.noise1LowFreq = 0
        self.noise1HighFreq = 2000
        self.noise1Type = "Pink"
        self.noise2SL = -200#50
        self.noise2LowFreq = 4000
        self.noise2HighFreq = 8000
        self.noise2Type = "Pink"
        self.preTrialNoiseLowFreq = 0
        self.preTrialNoiseHighFreq = 8000
        self.preTrialNoiseDur = 2#980
        self.preTrialNoiseRamps = 10
        self.preTrialNoiseSL = -200#40
        self.preTrialNoiseType = "Pink"
        self.preTrialNoiseChannel = "Both"
        self.preTrialNoiseDiadISI = 10#500
        self.noiseChannel = "Both"

      

        #self.menubar = self.menuBar()
        #self.fileMenu = self.menubar.addMenu(self.tr('&File'))
        
        #self.editMenu = self.menubar.addMenu(self.tr('&Edit'))
        #self.editListenerIDAction = QAction(self.tr('Listener ID'), self)
        #self.editMenu.addAction(self.editListenerIDAction)
        #self.editListenerIDAction.triggered.connect(self.onEditListenerID)

        
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

        self.overallRatingSliderValue = QLabel(self.tr(""), self)
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
            self.statusButton.setText(self.tr("Running"))
            QApplication.processEvents()
        if self.currentTrial <= self.nTrials :
            self.doTrial()
        else:
            self.statusButton.setText(self.tr("Finished"))
     
            
    def doTrial(self):
        self.statusButton.setText(self.tr("Running"))
        QApplication.processEvents()

        try:
            intervalName = self.intervals_db["name"][self.intervals_db["cents"] == self.trialList[self.currentTrial-1][1]].values[0]
        except:
            intervalName = str(self.trialList[self.currentTrial-1][1])
        print(intervalName)

        preTrialNoise = broadbandNoise(spectrumLevel=self.preTrialNoiseSL,
                                       duration=self.preTrialNoiseDur,
                                       ramp=self.preTrialNoiseRamps, channel=self.preTrialNoiseChannel,
                                       fs=self.fs, maxLevel=self.maxLevel)
        if self.preTrialNoiseType == "Pink":
            preTrialNoise = makePink(preTrialNoise, self.fs)

        preTrialNoise = fir2Filter2(preTrialNoise, filterType="bandpass", nTaps=256, cutoffs=(self.preTrialNoiseLowFreq, self.preTrialNoiseHighFreq), transitionWidth=0.2, fs=self.fs)
            
        diad = makeDiad(self.trialList[self.currentTrial-1][0], self.trialList[self.currentTrial-1][1],
                       filterType=self.diadFilterType,
                       filterCutoffs=self.diadFilterCutoffs,
                       lowHarm=self.diadLowHarm, highHarm=self.diadHighHarm,
                       diadTotLev=self.diadTotLev, duration=self.diadDur,
                       ramp=self.diadRamps, note1Channel=self.diadNote1Chan,
                       note2Channel=self.diadNote2Chan, fs=self.fs,
                       maxLevel=self.maxLevel)

        noise1 = broadbandNoise(spectrumLevel=self.noise1SL,
                                       duration=self.diadDur,
                                       ramp=self.diadRamps*6, channel=self.noiseChannel,
                                       fs=self.fs, maxLevel=self.maxLevel)
        if self.noise1Type == "Pink":
            noise1 = makePink(noise1, self.fs)
        noise1 = fir2Filter2(noise1, filterType="bandpass", nTaps=256,
                             cutoffs=(self.noise1LowFreq, self.noise1HighFreq),
                             transitionWidth=0.2, fs=self.fs)
        noise1 = noise1[0:diad.shape[0],:]
        noise1 = gate(self.diadRamps, noise1, self.fs)
        
        noise2 = broadbandNoise(spectrumLevel=self.noise2SL,
                                duration=self.diadDur,
                                ramp=self.diadRamps*6, channel=self.noiseChannel,
                                fs=self.fs, maxLevel=self.maxLevel)
        if self.noise2Type == "Pink":
            noise2 = makePink(noise2, self.fs)
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
        rootNote = str(self.trialList[self.currentTrial-2][0])

        if self.currentTrial-1 <= len(self.rootNotes)*len(self.intervalsCents)*self.nPracticeTrialsXStim:
            trialMode = "practice"
        else:
            trialMode = "main"
        self.thisPageFile.write(self.listenerID + ';')
        self.thisPageFile.write(rootNote + ';')
        self.thisPageFile.write(intervalName + ';')
        self.thisPageFile.write(trialMode + ';')
        self.thisPageFile.write(self.overallRatingSliderValue.text() + '\n')
        self.thisPageFile.flush()
        self.overallRatingSlider.setValue(0)
        self.overallRatingSliderValue.setText("")


    def sliderChanged(self, value):
        self.overallRatingSliderValue.setText(str(round(value,1)))
        if self.currentTrial > 1 and self.statusButton.text() != self.tr("Finished"):
            self.statusButton.setText(self.tr("Next"))

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
            self.thisPageFile.write("listener;root_note;interval;trial_type;rating\n")

            self.setupListenerButton.hide()
            self.statusButton.show()
        else:
            return
