# -*- coding: utf-8 -*-
#
# Copyright (c) 2018, Shigemi ISHIDA
# All rights reserved.
#
# DO NOT REDISTRIBUTE THIS PROGRAM NOR A PART OF THIS PROGRAM.
#

import re
import os
import numpy as np
import pandas as pd

import conf_mat_plotting

#==========================================================================
class GridSummary():
    def __init__(self):
        self.param_in = None    # parameter組み合わせ情報のファイル名
        self.param = None       # parameter組み合わせ情報
        self.vars = None        # 変更しているパラメータのリスト
        self.lim_param = None   # 変更しているパラメータのみの情報

        return

    #----------------------------------------------------------------------
    def load_grid(self, param_file):
        self.param_in = param_file # parameter組み合わせ情報のファイル名

        # パラメータ情報ファイルを読み込み
        self.param = pd.read_csv(param_file)
        # カラム名の最初を補正
        first_col = self.param.columns[0]
        self.param = self.param.rename(columns={first_col: re.sub('#[ ]*', '', first_col)})
        # cntをindexにする
        self.param.index = self.param.cnt
        self.param = self.param.drop(columns='cnt')

        return

    #----------------------------------------------------------------------
    def extract_vars(self):
        if self.param is None:
            return None

        # parameter組み合わせ情報の全カラム名
        cols = np.array(self.param.columns)
        # 各カラムのパターン数
        col_count = np.array([self.param.groupby(col)[col].unique().count() for col in cols])

        # 変更しているパラメータのみを抽出
        self.vars = cols[(col_count > 1).nonzero()[0]]
        self.lim_param = pd.DataFrame(self.param[self.vars])

        return self.vars

    #----------------------------------------------------------------------
    def summarize(self):
        if self.vars is None:
            return None

        base_path = os.path.dirname(self.param_in)
        base_file, base_ext = os.path.splitext(os.path.basename(self.param_in))
        base_name = "_".join(base_file.split('_')[:-1])
        max_cnt = self.lim_param[g.vars[0]].count()

        self.lim_param['accuracy'] = -1.0

        cmp = conf_mat_plotting.ConfMatPlotting()
        for cnt in range(max_cnt):
            fname = "%s/%s_%d_result.csv" % (base_path, base_name, cnt)
            cmp.load_result(fname)
            cmp.finalize()
            self.lim_param.loc[cnt, 'accuracy'] = cmp.final_accuracy

        return self.lim_param.accuracy

#==========================================================================
# 引数処理
def arg_parser():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("param_file", type=str, action="store",
                    help="parameter combinations info file",
                    )
    ap.add_argument("-o", "--output", type=str, action="store",
                    default=None,
                    help="output filename",
                    )
    return ap

#==========================================================================
if __name__ == '__main__':
    parser = arg_parser()
    args = parser.parse_args()

    # grid searchクラスをインスタンス化
    g = GridSummary()

    # パラメータ情報を読み込み
    g.load_grid(args.param_file)

    # 変更しているパラメータを抽出
    g.extract_vars()

    # 集計
    g.summarize()

    if args.output is not None:
        print("output saved in %s" % args.output)
        with open(args.output, "w") as f:
            f.write("# ")
        with open(args.output, "a") as f:
            g.lim_param.to_csv(f)
    else:
        print(g.lim_param)
