# -*- coding: utf-8 -*-

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
