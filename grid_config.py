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

#==========================================================================
class GridConfig():
    def __init__(self):
        return

    #----------------------------------------------------------------------
    def load_param_set(self, param_file):
        # パラメータ情報ファイルを読み込み
        self.param_file = self.load_class(param_file)

        # パラメータ名を取得
        self.param_names = list(self.param_file.__dict__.keys())
        self.param_names.sort()
        self.param_names = list(filter(
            lambda x: re.match(r'^[^_]', x) and (x != "constraints"),
            self.param_names
            ))

        self.param_set = {}
        for param_name in self.param_names:
            self.param_set[param_name] = self.param_file.__dict__[param_name]
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
                    help="parameter information file",
                    )
    ap.add_argument("-o", "--output", type=int, action="store",
                    default=None,
                    help="output file storing parameter combinations",
                    )
    return ap


#==========================================================================
if __name__ == '__main__':
    parser = arg_parser()
    args = parser.parse_args()

    # grid searchクラスをインスタンス化
    g = GridConfig()
    
    # パラメータ情報を読み込み
    g.load_param_set(args.param_file)
