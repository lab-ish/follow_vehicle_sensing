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
import itertools
import subprocess

#==========================================================================
class GridConfig():
    def __init__(self, config_out=None, base=None, param_dir=None):
        self.config_out = config_out # 出力configファイル名（上書き）
        if self.config_out is None:
            self.config_out = datetime.datetime.today().strftime("config_%s.py")

        # ベースネーム
        self.save_base = base
        if self.save_base is None:
            now = datetime.datetime.today().strftime("%Y%m%d_%H%M")
            self.save_base = now

        # パラメータの組み合わせの保存先（上書き）
        if param_dir is None:
            param_dir = ""
        self.param_out = param_dir + "/" + self.save_base + "_grid.csv"

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
    def generate_combinations(self):
        # パラメータが取る値のリストを取得
        param_values = [self.param_set[x] for x in self.param_names]
        # パラメータの組み合わせを生成
        param_combs = itertools.product(*param_values)
        # 制約を満たさないものは除外
        param_combs = filter(lambda x: self.constraints(dict(zip(self.param_names, x))),
                             list(param_combs))
        return list(param_combs)

    #----------------------------------------------------------------------
    def exec_grid(self):
        param_combs = self.generate_combinations()

        # 各組み合わせで評価を実行
        num_iter = len(param_combs) - 1
        with open(self.param_out, "w") as f:
            f.write("# config_file,%s\n" % ",".join(self.param_names))
        cnt = 0
        for p in param_combs:
            print("grid %d/%d" % (cnt, num_iter))
            param = dict(zip(self.param_names, p))

            # パラメータの組み合わせでconfigを生成
            self.generate_single_config(self.config_out, param)

            # パラメータの組み合わせを記録
            with open(self.param_out, "a") as f:
                f.write(self.save_base + "_%d.py," % cnt)
                f.write(",".join(map(lambda x: str(x), p)) + "\n")

            # 実行
            try:
                out = subprocess.check_call([
                    "python3",
                    "main.py",
                    "-c", self.config_out,
                    "-b", self.save_base + "_%d" % cnt
                    ])
            except subprocess.CalledProcessError as ex:
                sys.stderr.write(ex.output + "\n")

            cnt += 1
        return

    #----------------------------------------------------------------------
    def generate_single_config(self, conffile, param):
        # 各パラメータを書き込んだconfigを生成
        with open(conffile, "w") as f:
            for k,v in param.items():
                if type(v) is str:
                    f.write('%s = "%s"\n' % (k, v.replace('"', '\\"')))
                else:
                    f.write('%s = %s\n' % (k, str(v)))
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
    ap.add_argument("-t", "--test", action="store_true",
                    help="print the number of combinations and exit",
                    )
    ap.add_argument("-p", "--param_dir", type=str, action="store",
                    default=None,
                    help="output directory of parameter combinations info",
                    )
    ap.add_argument("-c", "--config_out", type=str, action="store",
                    default=None,
                    help="output config file name (default example: config_1548849936.py)",
                    )
    ap.add_argument("-b", "--base", type=str, action="store",
                    default=None,
                    help="base name for output files (default example: 20190124_1855)",
                    )
    return ap

#==========================================================================
if __name__ == '__main__':
    parser = arg_parser()
    args = parser.parse_args()

    # grid searchクラスをインスタンス化
    g = GridConfig(args.config_out, args.base, args.param_dir)

    # パラメータ情報を読み込み
    g.load_param_set(args.param_file)

    if args.test:
        # 何パターンの組み合わせがあるのかを表示して終了
        comb = g.generate_combinations()
        print(len(comb))
    else:
        # グリッド実行
        g.exec_grid()
