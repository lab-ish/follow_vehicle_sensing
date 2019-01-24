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

OUTDIR="results"

#======================================================================
# 引数処理
def arg_parser():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("-c", "--conffile", type=str, action="store",
                    default="config.py",
                    help="config file",
                    )
    return ap

#----------------------------------------------------------------------
# 推定用クラスを読み込み
def load_est_class(class_file):
    # classファイルのをimport pathに追加
    base_path = os.path.dirname(class_file)
    base_file, base_ext = os.path.splitext(os.path.basename(class_file))
    sys.path.append(base_path)
    base_name = base_file.split("_")[:2]

    return importlib.import_module(base_file)

#======================================================================
if __name__ == '__main__':
    parser = arg_parser()
    args = parser.parse_args()

    if not os.path.exists(OUTDIR):
        os.makedirs(OUTDIR)

    # 現在時刻を取得し、データファイルのベースとする
    now = datetime.datetime.today().strftime("%Y%m%d_%H%M")
    save_base = OUTDIR + "/" + now

    # 設定ファイルのパスをimport pathに追加
    base_path = os.path.dirname(args.conffile)
    base_file, base_ext = os.path.splitext(os.path.basename(args.conffile))
    sys.path.append(base_path)

    try:
        config = importlib.import_module(base_file)
    except ImportError:
        sys.stderr.write('Error: Ignore missing config file "' + args.conffile + '"\n')
        sys.exit(1)

    print(args.conffile + " saved as " + save_base + "_config.py")

    # 設定ファイルをコピーしておく
    shutil.copy(args.conffile, save_base + "_config.py")

    #--------------------------------------------------
    # 推定クラスを読み込み
    est_class = load_est_class(config.est_class)

    # 推定クラスをインスタンス化
    e = est_class.Estimate(ext_feature_class=config.ext_feature_class,
                           result_file="%s_result.csv" % (save_base),
                           score_file="%s_score.csv" % (save_base),
                           winsize=config.winsize,
                           cutoff=config.cutoff,
                           )

    # データ読み込み
    e.load_data(config.vehicle_info, config.wavfile)

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
        e.plot_confusion_matrix(plotfile)
