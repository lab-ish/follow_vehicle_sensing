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
    def model_func(self, t_diff, v):
        if type(v) is not np.ndarray:
            return ( np.sqrt( (v*t_diff + self.D/2)**2 + self.L**2 )
                        - np.sqrt( (v*t_diff - self.D/2)**2 + self.L**2 ) ) / self.c

        vt = t_diff * np.tile(v, [len(t), 1]).T
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
        # # time adjusted to FFT sampling timing
        # t0_adjust = t0_offset * self.samp_int

        # limit the range of time
        time_idx += t0_offset
        time_idx = time_idx[(time_idx >= 0) & (time_idx < self.sig.fft_data1.shape[0])]

        return (time_idx, time_delta, t0_offset)
        
    #----------------------------------------------------------------------
    # feature extraction method 1: shift and merge in freq domain
    def feature_shift_fft(self, t0, v):
        time_idx, time_delta, t0_offset = self.time_indices(t0, v)
        # calculate sound delay at each time index
        sound_delay = self.model(time_delta, v)

        return sound_delay

#==========================================================================
if __name__ == '__main__':
    pass
