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
class ExtFeature():
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
    def agg_feature_matrix(self, feature_matrix, winsize=10, cutoff=3e3):
        # moving average window
        ma_win = np.ones(winsize) / winsize

        # limit frequency range
        cutoff_len = int(np.round(self.sig.samp_rate / 2 / cutoff)) + 1
        feature_matrix = feature_matrix[:,0:cutoff_len]

        # matrix for storing results
        ret = np.empty([feature_matrix.shape[0]-winsize+1, feature_matrix.shape[1]], dtype=np.complex)
        # moving average for each column (freq) of feature_matrix
        for i in range(feature_matrix.shape[1]):
            ret[:,i] = np.convolve(np.real(feature_matrix[:,i]), ma_win, mode='valid') + np.convolve(np.imag(feature_matrix[:,i]), ma_win, mode='valid')*1j

        return ret

    #----------------------------------------------------------------------
    # feature extraction method 1: shift and merge in freq domain
    def feature_shift_fft(self, t0, v):
        time_idx, t0_offset = self.time_indices(t0, v)
        # calculate sound delay at each time index
        sound_delay = self.model(time_idx*self.samp_int, np.array([v, t0_offset*self.samp_int]))

        # shift back back left channel and merge in freq domain
        fft_merged = self.sig.shift_merge_fft(-sound_delay, time_idx[0])

        return fft_merged

    #----------------------------------------------------------------------
    # feature extraction method 2: single channel, freq domain
    def feature_single_fft(self, t0, v):
        time_idx, t0_offset = self.time_indices(t0, v)

        return np.array(self.sig.fft_data1[time_idx])

#==========================================================================
if __name__ == '__main__':
    pass
