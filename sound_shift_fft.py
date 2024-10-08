# -*- coding: utf-8 -*-
# 
# Copyright (c) 2018-2024, Shigemi ISHIDA
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 3. Neither the name of the Institute nor the names of its contributors
#    may be used to endorse or promote products derived from this software
#    without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE INSTITUTE AND CONTRIBUTORS ``AS IS'' AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE INSTITUTE OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.
# 

import numpy as np
from soundmap.signal_process import SignalProcess

#==========================================================================
class SoundShiftFFT(SignalProcess):
    # winsize: FFT windowサイズ
    # shift  : FFT windowをシフトするサイズ
    def __init__(self, data1, data2, # wave_data instance for left and right
                 samp_rate=48e3,     # sampling rate [Hz]
                 winsize=512,        # FFT window size [samples]
                 shift=128,          # FFT window shift size [samples]
                 ):
        super(SoundShiftFFT, self).__init__(data1, data2, samp_rate, winsize, shift)

        self.samp_rate = samp_rate
        self.folds = int(self.folds)
        self.max_offset = self.data1.shape[0] - self.folds

        return

    #----------------------------------------------------------------------
    def fft_all(self):
        # データをずらして並べた行列を作成 for FFT
        # self.folds = 4で入力データが
        # array([[ 0,  1,  2,  3,  4],
        #        [ 5,  6,  7,  8,  9],
        #        [10, 11, 12, 13, 14],
        #        [15, 16, 17, 18, 19],
        #        [20, 21, 22, 23, 24],
        #        ...
        # のとき，こんなような行列shift_dataを作る
        # array([[   0,    1,    2, ...,   17,   18,   19],
        #        [   5,    6,    7, ...,   22,   23,   24],
        #        [  10,   11,   12, ...,   27,   28,   29],
        #        ...
        shift_data1 = np.empty([self.folds,
                                self.max_offset,
                                self.shift],
                               dtype=np.float)
        shift_data2 = np.empty(shift_data1.shape, dtype=np.float)
        for cnt in range(self.folds):
            shift_data1[cnt,:,:] = self.data1[cnt:-self.folds+cnt,:]
            shift_data2[cnt,:,:] = self.data2[cnt:-self.folds+cnt,:]
        shift_data1 = shift_data1.transpose([1,0,2]).reshape(-1, self.winsize)
        shift_data2 = shift_data2.transpose([1,0,2]).reshape(-1, self.winsize)

        # 窓関数
        win = np.tile(np.hamming(self.winsize), [shift_data1.shape[0], 1])

        # それぞれの行をFFT
        self.fft_data1 = np.fft.rfft(win * shift_data1)
        self.fft_data2 = np.fft.rfft(win * shift_data2)

        return

    #----------------------------------------------------------------------
    def shift_merge_fft(self,
                        time_deltas,    # 時間差 [s] (data2を基準としてdata1をどれくらいずらすか
                                        # 各FFT offsetにおける時間差を並べたnp.arrayとすること
                        offset=0,       # 参照するデータの開始位置 (FFT sampleで)
                        ):
        samp_len = len(time_deltas)
        
        # shift量 (時間sample)
        m = np.array(time_deltas * self.samp_rate, dtype=np.int)

        # 各周波数ステップでshift量を計算
        # まずはexpの肩を計算 -j2\pi m / N
        exps = np.tile(-2j*np.pi*m/self.winsize, [self.fft_data1.shape[1],1]).T
        # kをかけて -j2\pi k m / Nにする
        exps *= np.tile(np.fft.rfftfreq(self.winsize, 1/self.winsize), [samp_len,1])
        # phase shiftを計算
        phase_shifts = np.exp(exps)

        merged_fft = self.fft_data1[offset:offset+samp_len,:]*phase_shifts + self.fft_data2[offset:offset+samp_len]

        return merged_fft

#==========================================================================
if __name__ == '__main__':
    import matplotlib.pyplot as plt

    samp_freq = 48e3
    freq = 1e3

    t = np.arange(2**10+4) / samp_freq
    data1 = np.sin(2*np.pi*freq*t)
    data2 = np.sin(2*np.pi*freq*(t+0.2e-3))

    s = SoundShiftFFT(data1, data1)
    s.fft_all()
    time_deltas = np.array([-0.4e-3, 0.2e-3, 0.4e-3, -0.3e-3])
    merge_fft = s.shift_merge_fft(time_deltas)

    fig = plt.figure()
    plt.subplot(2,1,1)
    for cnt in range(len(time_deltas)):
        plt.plot(np.real(np.fft.irfft(merge_fft[cnt])), label="%.2f" % (time_deltas[cnt]*1e3))
    plt.legend(loc="lower right")
    plt.ylim([-2,2])

    plt.subplot(2,1,2)
    plt.plot((data1 + data2)[:s.winsize])
    plt.ylim([-2,2])
    
    plt.show()
    plt.close()
