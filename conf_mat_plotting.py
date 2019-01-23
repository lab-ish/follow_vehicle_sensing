# -*- coding: utf-8 -*-
# 
# Copyright (c) 2018, Masahiko MIYAZAKI, Shigemi ISHIDA, Kyushu University
# All rights reserved.
# 
# DO NOT REDISTRIBUTE THIS PROGRAM NOR A PART OF THIS PROGRAM.
# 
# requires python >= ver.3.5
# 

import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

#==========================================================================
class ConfMatPlotting():
    #----------------------------------------------------------------------
    def __init__(self):
        return

    #----------------------------------------------------------------------
    def finalize(self):
        # 各回のconfusion matrixを統合（合計）
        self.final_conf_matrix = np.sum(self.conf_matrix, axis=0)
        # test accuracyはconfusion matrixから算出
        self.final_accuracy = np.sum(np.diag(self.final_conf_matrix)) / np.sum(self.final_conf_matrix)

        return (self.final_conf_matrix, self.final_accuracy)

    #----------------------------------------------------------------------
    def plot_confusion_matrix(self, plot_file=None, fontsize=14):
        fig = plt.figure()

        if plot_file is not None:
            # ファイル出力のときはプロットの調整
            # plt.rcParams['font.family'] = 'Times'           # 全体のフォント
            plt.rcParams['font.size'] = fontsize            # フォントサイズ
            # plt.rcParams['axes.linewidth'] = 1              # 軸の太さ
            fig.subplots_adjust(bottom = 0.15)              # 下の余白を増やす

            if os.path.splitext(plot_file)[1] == "eps":
                # EPS出力のためのおまじない
                plt.rcParams['ps.useafm'] = True
                plt.rcParams['pdf.use14corefonts'] = True
                plt.rcParams['text.usetex'] = True

        sns.heatmap(self.final_conf_matrix,
                    cmap="Blues",
                    annot=True,
                    fmt="d",
                    cbar=False,
                    )
        plt.xlabel('Estimated Area')
        plt.ylabel('Actual Area')

        if plot_file is None:
            plt.show()
        else:
            plt.savefig(plot_file)

        plt.close()
        return

    #----------------------------------------------------------------------
    def load_result(self, result_file):
        conf_mat = np.loadtxt(result_file, delimiter=',', dtype=np.int)
        self.classes = int(np.sqrt(conf_mat.shape[1]))
        self.conf_matrix = conf_mat.reshape(-1, self.classes, self.classes)
        return

    #----------------------------------------------------------------------
    def load_score(self, score_file):
        self.score = np.loadtxt(score_file, delimiter=',', dtype=np.float)
        return

#==========================================================================
# 引数処理
def arg_parser():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("result_file", type=str, action="store",
                    help="result file to load",
                    )
    # ap.add_argument("-d", "--debug", action="store_true",
    #                 help="debug mode",
    #                 )
    ap.add_argument("-p", "--plot", action="store",
                    default=None,
                    help="confusion matrix plotting output file name",
                    )
    ap.add_argument("-f", "--fontsize", type=int, action="store",
                    default=None,
                    help="plot font size",
                    )
    ap.add_argument("-s", "--scorefile", type=int, action="store",
                    default=None,
                    help="load score file",
                    )
    return ap

#==========================================================================
if __name__ == '__main__':
    parser = arg_parser()
    args = parser.parse_args()

    c = ConfMatPlotting()

    # 結果を読み込み
    c.load_result(args.result_file)

    # 最終結果を計算
    c.finalize()

    # confusion matrixをプロットして保存
    if args.plot is not None:
        if args.fontsize is not None:
            c.plot_confusion_matrix(args.plot, fontsize=args.fontsize)
        else:
            c.plot_confusion_matrix(args.plot)
    else:
            c.plot_confusion_matrix()

    print("accuracy=%.4f" % c.final_accuracy)
