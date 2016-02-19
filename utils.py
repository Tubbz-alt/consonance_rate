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
import copy
import numpy as np
from sndlib import*



def fir2Filter2(snd, filterType, nTaps, cutoffs, transitionWidth, fs):
    # """
    # Get the coefficients of a FIR filter. This function is used internally by eegutils.

    # Parameters
    # ----------
    # fs : int
    #     The EEG recording sampling rate.
    # filterType : str {'lowpass', 'highpass', 'bandpass'}
    #     The filter type.
    # nTaps : int
    #     The number of filter taps.
    # cutoffs : array of floats
    #     The filter cutoffs. If 'filterType' is 'lowpass' or 'highpass'
    #     the 'cutoffs' array should contain a single value. If 'filterType'
    #     is bandpass the 'cutoffs' array should contain the lower and
    #     the upper cutoffs in increasing order.
    # transitionWidth : float
    #     The width of the filter transition region, normalized between 0-1.
    #     For a lower cutoff the nominal transition region will go from
    #     `(1-transitionWidth)*cutoff` to `cutoff`. For a higher cutoff
    #     the nominal transition region will go from cutoff to
    #     `(1+transitionWidth)*cutoff`.

    # Returns
    # ---------
    # filterCoeff : array of floats
    #     The filter coefficients. 
        
    # Examples
    # ----------
    # >>> getFilterCoefficients(fs=2048, filterType='highpass', nTaps=512, cutoffs=[30], transitionWidth=0.2)

    # """
    if filterType == "bandpass":
        if cutoffs[0] == 0:
            filterType = "lowpass"
            cutoffs = (cutoffs[1],)
            
    if filterType == "lowpass":
        f3 = cutoffs[0]
        f4 = cutoffs[0] * (1+transitionWidth)
        f3 = (f3*2) / fs
        f4 = (f4*2) / fs
        f = [0, f3, f4, 1]
        m = [1, 1, 0.00003, 0]
    elif filterType == "highpass":
        f1 = cutoffs[0] * (1-transitionWidth)
        f2 = cutoffs[0]
        f1 = (f1*2) / fs
        f2 = (f2*2) / fs
        f = [0, f1, f2, 0.999999, 1] #high pass
        m = [0, 0.00003, 1, 1, 0]
    elif filterType == "bandpass":
        f1 = cutoffs[0] * (1-transitionWidth)
        f2 = cutoffs[0]
        f3 = cutoffs[1]
        f4 = cutoffs[1] * (1+transitionWidth)
        f1 = (f1*2) / fs
        f2 = (f2*2) / fs
        f3 = (f3*2) / fs
        f4 = (f4*2) / fs
        f = [0, f1, f2, ((f2+f3)/2), f3, f4, 1]
        m = [0, 0.00003, 1, 1, 1, 0.00003, 0]
    b = firwin2(nTaps,f,m)

    x = copy.copy(snd)
    x[:, 0] = convolve(snd[:,0], b, 1)
    x[:, 1] = convolve(snd[:,1], b, 1)
    
    return x

def makeDiad(rootNote, intervalCents, filterType="lowpass", filterCutoffs=(2500), lowHarm=1, highHarm=100, diadTotLev=80, duration=1980, ramp=10, note1Channel="Both", note2Channel="Both", fs=48000, maxLevel=101):

    F0Note1 = rootNote
    F0Note2 = rootNote*2**(intervalCents/1200)
    nyquist = fs/2
    if filterType == "lowpass":
        bandwidth = filterCutoffs[0]
    elif filterType == "highpass":
        bandwidth = nyquist - filterCutoffs[0]
    elif filterType == "bandpass":
        bandwidth = np.min(filterCutoffs[1], nyquist) - filterCutoffs[0]
        
    nHarmsNote1 = bandwidth/F0Note1
    nHarmsNote2 = bandwidth/F0Note2
    nHarmsTot = nHarmsNote1 + nHarmsNote2
    harmLev = diadTotLev - 10*log10(nHarmsTot)
    note1 = complexTone(F0=F0Note1, harmPhase="Sine", lowHarm=lowHarm, highHarm=highHarm,
                        stretch=0, level=harmLev, duration=duration, ramp=ramp,
                        channel=note1Channel, fs=fs, maxLevel=maxLevel)
    note2 = complexTone(F0=F0Note2, harmPhase="Sine", lowHarm=lowHarm, highHarm=highHarm,
                        stretch=0, level=harmLev, duration=duration, ramp=ramp,
                        channel=note2Channel, fs=fs, maxLevel=maxLevel)
    
    diad = note1+note2
    diad = fir2Filter2(diad, filterType, 256, filterCutoffs, 0.2, fs)
    
    return diad
