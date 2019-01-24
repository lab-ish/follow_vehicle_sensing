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
    def __init__(self, wavfile, win=4.0, cutoff=None, fft_len=512, fft_shift=128, D=0.5, L=2.0):
        self.wavfile = wavfile  # vehicle sound .wav file
        self.win     = win      # window size in second
        self.cutoff  = cutoff   # LPF cutoff frequency
        self.fft_len = fft_len  # FFT window size
        self.fft_shift = fft_shift # FFT shift length
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
                                 self.fft_len,
                                 self.fft_shift,
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
    def feature(self, t0, v, winsize=10, slide=True):
        # derive feature matrix
        features = self.extract_feature(t0, v)

        # limit frequency range (also exclude DC)
        if self.cutoff is not None:
            cutoff_len = int(np.round(self.sig.winsize * self.cutoff / self.sig.samp_rate))
            features = features[:,1:cutoff_len+1]

        # sliding window?
        if slide:
            # matrix for storing results
            ret = np.empty([features.shape[0]-winsize+1, features.shape[1]],
                           dtype=np.complex)
            # moving average window
            ma_win = np.ones(winsize) / winsize
            # moving average for each column (freq) of features
            for i in range(features.shape[1]):
                ret[:,i] = np.convolve(np.real(features[:,i]), ma_win, mode='valid') \
                  + np.convolve(np.imag(features[:,i]), ma_win, mode='valid')*1j
        else:
            # divide each freq component in winsize and average
            # cut the last part of residuals
            cut = features.shape[0] % winsize
            if cut != 0:
                features = features[0:-cut,:]
            # average the each divided data
            ret = np.mean(features.reshape(-1,winsize,features.shape[1]),
                          axis=1)

        # split amplitude and phase
        #   phase is more divided into sin/cos to consider phase rotation
        amp   = np.abs(ret)
        phase = np.exp(np.angle(ret)*1j)
        return amp

    #----------------------------------------------------------------------
    def extract_feature(self, t0, v):
        return np.empty([self.winlen, self.win])

#==========================================================================
if __name__ == '__main__':
    pass
