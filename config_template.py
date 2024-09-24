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

# 出力先ディレクトリ
outdir = "result"

# 推定クラスのファイル名
est_class = "estimate_svm.py"

# 特徴量抽出クラスのファイル名
ext_feature_class = "ext_feature_shift_fft.py"
# ext_feature_class = "ext_feature_single.py"

# window size in second (float)
#   車両通過時を基準として前後合計何秒分の音を取り出すか
winsize = 2.0

# 検出された車両情報が格納されているTSVファイル名
vehicle_info = "../data/MAH00092_follow_vehicle_sensing_L2_notruck.tsv"

# 車両走行音wavファイル
wavfile = "../data/MAH00092.wav"

# 交差検証の分割数 (int)
folds = 10

# 交差検証の繰り返し数 (int)
repeats = 1

# confusion matrixのプロット出力有無
#   True:   デフォルトファイル名 (例: 20190124_1855_result.png)
#   False:  出力しない
#   文字列: その文字列をファイル名とする
plot = True

# LPFのカットオフ周波数 [Hz]
#   Noneの場合は全周波数
cutoff = 3e3

# FFT点数 (int)
fft_len = 512

# FFTシフトサイズ (int)
#   FFT点数の約数とすること
fft_shift = 128

# FFT結果に対する移動平均の長さ [sample] (int)
ma_len = 10

# FFT結果に対する移動平均のwindow移動を重ねるか
ma_overlap = True

#----------------------------------------------------------------------
# fft_shiftのチェック
if fft_len % fft_shift != 0:
    raise ValueError
