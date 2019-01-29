# -*- coding: utf-8 -*-
#
# Copyright (c) 2018, Shigemi ISHIDA
# All rights reserved.
#
# DO NOT REDISTRIBUTE THIS PROGRAM NOR A PART OF THIS PROGRAM.
#

import os
import sys
import importlib
import re
import datetime

#==========================================================================
class GridConfig():
    def __init__(self, config_out, param_out=None):
        self.config_out = config_out # 出力configファイル名（上書き）
        self.param_out = param_out   # パラメータの組み合わせの保存先（追記, Noneなら出力しない）
        return

    #----------------------------------------------------------------------
    def load_param_set(self, param_file):
        # パラメータ情報ファイルを読み込み
        self.param_file = self.load_class(param_file)
        # 制約条件チェック関数
        self.constraints = self.param_file.constraints

        # パラメータ名を取得
        self.param_names = list(self.param_file.__dict__.keys())
        self.param_names.sort()
        self.param_names = list(filter(
            lambda x: re.match(r'^[^_]', x) and (x != "constraints"),
            self.param_names
            ))

        self.param_set = {}
        self.param_len = {}
        for param_name in self.param_names:
            self.param_set[param_name] = self.param_file.__dict__[param_name]
            self.param_len[param_name] = len(self.param_set[param_name])
        return

    #----------------------------------------------------------------------
    def exec_grid(self):
        return

    #----------------------------------------------------------------------
    def generate_single_config(self, param):
        with open(self.config_out, "w") as f:
            pass

        return

    #----------------------------------------------------------------------
    # クラスファイルを読み込み
    def load_class(self, class_file):
        # classファイルのpathをimport pathに追加
        base_path = os.path.dirname(class_file)
        base_file, base_ext = os.path.splitext(os.path.basename(class_file))
        sys.path.append(base_path)
        base_name = base_file.split("_")[:2]

        return importlib.import_module(base_file)

#==========================================================================
# 引数処理
def arg_parser():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("param_file", type=str, action="store",
                    help="input file including parameter set",
                    )
    ap.add_argument("-c", "--config_out", type=str, action="store",
                    default=None,
                    help="output config file name",
                    )
    ap.add_argument("-o", "--param_out", type=str, action="store",
                    default=None,
                    help="output file name storing parameter combination set",
                    )
    return ap


#==========================================================================
if __name__ == '__main__':
    parser = arg_parser()
    args = parser.parse_args()

    # grid searchクラスをインスタンス化
    if args.config_out is None:
        args.config_out = datetime.datetime.today().strftime("config_%s.py")
    g = GridConfig(args.config_out, args.param_out)

    # パラメータ情報を読み込み
    g.load_param_set(args.param_file)
