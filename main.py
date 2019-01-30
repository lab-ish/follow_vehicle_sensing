# -*- coding: utf-8 -*-
#
# Copyright (c) 2018, Shigemi ISHIDA
# All rights reserved.
#
# DO NOT REDISTRIBUTE THIS PROGRAM NOR A PART OF THIS PROGRAM.
#

import sys
import os
import numpy as np
import shutil
import importlib
import datetime

import vehicles

#======================================================================
# 引数処理
def arg_parser():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("-c", "--conffile", type=str, action="store",
                    default="config.py",
                    help="config file",
                    )
    ap.add_argument("-b", "--base", type=str, action="store",
                    default=None,
                    help="base name for output files",
                    )
    return ap

#----------------------------------------------------------------------
# クラスファイルを読み込み
def load_class(class_file):
    # classファイルのpathをimport pathに追加
    base_path = os.path.dirname(class_file)
    base_file, base_ext = os.path.splitext(os.path.basename(class_file))
    sys.path.append(base_path)
    base_name = base_file.split("_")[:2]

    return importlib.import_module(base_file)

#======================================================================
if __name__ == '__main__':
    parser = arg_parser()
    args = parser.parse_args()

    # 設定ファイル読み込み
    try:
        config = load_class(args.conffile)
    except ImportError:
        sys.stderr.write('Error: Ignore missing config file "' + args.conffile + '"\n')
        sys.exit(1)

    if not os.path.exists(config.outdir):
        os.makedirs(config.outdir)

    # 指定がなければ現在時刻を取得して出力ファイルのベースとする
    now = datetime.datetime.today().strftime("%Y%m%d_%H%M")
    if args.base is None:
        args.base = now
    save_base = config.outdir + "/" + args.base

    print(args.conffile + " saved as " + save_base + "_config.py")

    # 設定ファイルをコピーしておく
    shutil.copy(args.conffile, save_base + "_config.py")

    #--------------------------------------------------
    # 特徴量抽出クラスを読み込み
    extf_class = load_class(config.ext_feature_class)
    # 推定クラスを読み込み
    est_class  = load_class(config.est_class)

    # 特徴量抽出クラスをインスタンス化
    ext = extf_class.ExtFeature(win        = config.winsize,
                                cutoff     = config.cutoff,
                                fft_len    = config.fft_len,
                                fft_shift  = config.fft_shift,
                                ma_len     = config.ma_len,
                                ma_overlap = config.ma_overlap,
                                )
    # 車両走行音データを読み込み
    print("load sound data %s" % config.wavfile)
    ext.load_sound(config.wavfile)

    # 車両情報クラスをインスタンス化
    veh = vehicles.Vehicles(config.vehicle_info, ext)
    # 車両情報を読み込み
    print("load vehicle data %s" % config.vehicle_info)
    veh.load_data()

    # 車両種別と車両種別IDの対応を設定ファイルに追記
    with open(save_base + "_config.py", "a") as f:
        f.write("\n")
        f.write("#======================================================================\n")
        f.write("# Lines below are automatically added by main.py\n")
        f.write("vehicle_types = {\n")
        for type_id in veh.type_ids.keys():
            f.write("  %d: '%s',\n" % (type_id, veh.type_ids[type_id]))
        f.write("}\n")

    # 推定クラスをインスタンス化
    e = est_class.Estimate(ext_feature = ext,
                           vehicles    = veh,
                           result_file = "%s_result.csv" % (save_base),
                           score_file  = "%s_score.csv" % (save_base),
                           )

    # 特徴量抽出
    e.feature_extraction()

    # 推定
    e.cross_validation(folds=config.folds, repeat=config.repeats)

    # 最終結果をとりまとめ
    e.load_result(e.result_file)
    e.finalize()
    print("accuracy=%.4f" % e.final_accuracy)

    # confusion matrixをプロット
    if config.plot:
        plotfile = "%s_result.png" % (save_base)
        if type(config.plot) is str:
            plotfile = config.plot
        e.plot_confusion_matrix(plot_file=plotfile, type_ids=veh.type_ids)
