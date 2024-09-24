# -*- coding: utf-8 -*-
# 
# Copyright (c) 2018-2024, Masahiko MIYAZAKI, Shigemi ISHIDA
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
# requires python >= ver.3.5
# 

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import importlib

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
    def plot_confusion_matrix(self, plot_file=None, fontsize=14, type_ids=None, percentile=False):
        fig = plt.figure()

        if plot_file is not None:
            # ファイル出力のときはプロットの調整
            # plt.rcParams['font.family'] = 'Times'           # 全体のフォント
            plt.rcParams['font.size'] = fontsize            # フォントサイズ
            # plt.rcParams['axes.linewidth'] = 1              # 軸の太さ
            fig.subplots_adjust(bottom = 0.15)              # 下の余白を増やす

            if os.path.splitext(plot_file)[1] == ".eps":
                # EPS出力のためのおまじない
                plt.rcParams['ps.useafm'] = True
                plt.rcParams['pdf.use14corefonts'] = True
                plt.rcParams['text.usetex'] = True

        labels = "auto"
        if type_ids is not None:
            labels = np.array(sorted(type_ids.items()))[:,1]

        if percentile:
            label_sums = self.final_conf_matrix.sum(axis=1)
            label_sums = np.tile(label_sums, [self.classes, 1]).T
            final_conf_matrix = self.final_conf_matrix / label_sums * 1e2
            fmt = ".2f"
        else:
            final_conf_matrix = self.final_conf_matrix
            fmt = "d"

        sns.heatmap(final_conf_matrix,
                    cmap="Blues",
                    annot=True,
                    fmt=fmt,
                    cbar=False,
                    xticklabels=labels,
                    yticklabels=labels,
                    )
        plt.xlabel('Estimated Type')
        plt.ylabel('Actual Type')

        if plot_file is None:
            plt.show()
        else:
            plt.savefig(plot_file)

        plt.close()
        return final_conf_matrix

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
    ap.add_argument("-n", "--no_plot", action="store_true",
                    help="no plot output",
                    )
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
    ap.add_argument("-c", "--conf_file", type=str, action="store",
                    default=None,
                    help="config file name to load type/type_id association",
                    )
    ap.add_argument("-r", "--percentile", action="store_true",
                    help="Plot percentile form",
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

#==========================================================================
if __name__ == '__main__':
    parser = arg_parser()
    args = parser.parse_args()

    # 設定ファイルが指定されている場合は読み込み
    type_ids = None
    if args.conf_file is not None:
        config = load_class(args.conf_file)
        if 'vehicle_types' in vars(config).keys():
            type_ids = config.vehicle_types

    c = ConfMatPlotting()

    # 結果を読み込み
    c.load_result(args.result_file)

    # 最終結果を計算
    c.finalize()

    # confusion matrixをプロットして保存
    if not args.no_plot:
        if args.plot is not None:
            if args.fontsize is not None:
                c.plot_confusion_matrix(
                    plot_file=args.plot,
                    fontsize=args.fontsize,
                    type_ids=type_ids,
                    percentile=args.percentile,
                    )
            else:
                c.plot_confusion_matrix(
                    plot_file=args.plot,
                    type_ids=type_ids,
                    percentile=args.percentile,
                    )
        else:
                c.plot_confusion_matrix(
                    type_ids=type_ids,
                    percentile=args.percentile,
                    )

    print("accuracy=%.4f" % c.final_accuracy)
