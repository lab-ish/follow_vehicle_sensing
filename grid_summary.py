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
        self.param = pd.read_csv(param_file, sep='\t')
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

    # 並べ替え
    sorted_param = g.lim_param.sort_values('accuracy')

    if args.output is not None:
        print("output saved in %s" % args.output)
        with open(args.output, "w") as f:
            f.write("# ")
        with open(args.output, "a") as f:
            sorted_param.to_csv(f)
    else:
        print(sorted_param)
