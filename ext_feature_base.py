# -*- coding: utf-8 -*-
#
# Copyright (c) 2018, Shigemi ISHIDA
# All rights reserved.
#
# DO NOT REDISTRIBUTE THIS PROGRAM NOR A PART OF THIS PROGRAM.
#

import numpy as np

from sound_shift_fft import SoundShiftFFT
from soundmap.wave_data import WaveData

#==========================================================================
class ExtFeatureBase():
    def __init__(self, wavfile, win=4.0, D=0.5, L=2.0):
        self.wavfile = wavfile  # vehicle sound .wav file
        self.win     = win      # window size in second
        self.D       = D        # mic separation
        self.L       = L        # distance between road the mic

        self.c       = 340.0           # sound speed in air
        self.model   = self.model_func # soundmap model function
        return

    #----------------------------------------------------------------------
    def load_sound(self):
        # load wav file
        wav = WaveData(self.wavfile, decimate=False)

        # FFT
        self.sig = SoundShiftFFT(np.array(wav.left),
                                 np.array(wav.right),
                                 wav.sample_rate,
                                 )
        self.sig.fft_all()
        del wav

        # FFT sampling interval
        self.samp_int = self.sig.shift / self.sig.samp_rate
        # window size in FFT samples
        self.winlen = int(self.win / self.samp_int)
        return

    #----------------------------------------------------------------------
    # default S-curve model
    def model_func(self, t, param):
        if len(param.shape) == 1:
            v  = param[0]
            t0 = param[1]
            return ( np.sqrt( (v*(t-t0) + self.D/2)**2 + self.L**2 )
                        - np.sqrt( (v*(t-t0) - self.D/2)**2 + self.L**2 ) ) / self.c

        v  = param[:,0]
        t0 = param[:,1]
        vt = (np.tile(t, [len(v), 1]) - np.tile(t0, [len(t), 1]).T) * np.tile(v, [len(t), 1]).T
        return ( np.sqrt((vt+self.D/2)**2 + self.L**2)
                - np.sqrt((vt-self.D/2)**2 + self.L**2) ) / self.c

    #----------------------------------------------------------------------
    def time_indices(self, t0, v):
        # time index
        time_idx = np.arange(-int(self.winlen/2), int(self.winlen/2))
        # time delta from t0
        time_delta = time_idx * self.samp_int
        # find the nearest FFT offset to time t0
        t0_offset = int(np.round(t0 / self.samp_int))

        # limit the range of time
        time_idx += t0_offset
        time_idx = time_idx[(time_idx >= 0) & (time_idx < self.sig.fft_data1.shape[0])]

        return (time_idx, t0_offset)

    #----------------------------------------------------------------------
    def feature(self, t0, v, winsize=10, cutoff=3e3, slide=True):
        # derive feature matrix
        feature_matrix = self.extract_feature(t0, v)

        # limit frequency range (also exclude DC)
        if cutoff is not None:
            cutoff_len = int(np.round(self.sig.samp_rate / 2 / cutoff))
            feature_matrix = feature_matrix[:,1:cutoff_len+1]

        # sliding window?
        if slide:
            # matrix for storing results
            ret = np.empty([feature_matrix.shape[0]-winsize+1, feature_matrix.shape[1]],
                           dtype=np.complex)
            # moving average window
            ma_win = np.ones(winsize) / winsize
            # moving average for each column (freq) of feature_matrix
            for i in range(feature_matrix.shape[1]):
                ret[:,i] = np.convolve(np.real(feature_matrix[:,i]), ma_win, mode='valid') \
                  + np.convolve(np.imag(feature_matrix[:,i]), ma_win, mode='valid')*1j
        else:
            # divide each freq component in winsize and average
            # cut the last part of residuals
            cut = feature_matrix.shape[0] % winsize
            if cut != 0:
                feature_matrix = feature_matrix[0:-cut,:]
            # average the each divided data
            ret = np.mean(feature_matrix.reshape(-1,winsize,feature_matrix.shape[1]),
                          axis=1)

        # calculate amplitude/phase difference
        diff = ret[0:-1,:] / ret[1:,:]

        return np.c_[np.abs(diff), np.angle(diff)]

    #----------------------------------------------------------------------
    def extract_feature(self, t0, v):
        return np.empty([self.winlen, self.win])

#==========================================================================
if __name__ == '__main__':
    pass
