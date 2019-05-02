# -*- coding: utf-8 -*-
#
# Copyright (c) 2018, Shigemi ISHIDA
# All rights reserved.
#
# DO NOT REDISTRIBUTE THIS PROGRAM NOR A PART OF THIS PROGRAM.
#

import os
import sys
import copy
import importlib
import re
import datetime
import itertools

#==========================================================================
class GridConfig():
    def __init__(self, config_dir, param_out):
        self.config_dir = config_dir # config出力先ディレクトリ
        self.param_out = param_out   # parameter組み合わせ情報出力先ファイル名

        self.dellist = lambda items, indexes: [item for index, item in enumerate(items) if index not in indexes]

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

        # IGNOREは問答無用で除外する
        self.param_names.remove('IGNORE')

        self.param_set = {}
        self.param_len = {}
        param_names = copy.copy(self.param_names)
        for param_name in self.param_names:
            self.param_set[param_name] = self.param_file.__dict__[param_name]
            try:
                self.param_len[param_name] = len(self.param_set[param_name])
            except:
                # remove from param_names
                param_names.remove(param_name)
        self.param_names = param_names

        # 除外パラメータのindex番号
        self.param_to_remove = []
        for param in self.param_file.IGNORE:
            self.param_to_remove.append(self.param_names.index(param))

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

        # 各組み合わせのconfigを出力
        param_names = self.dellist(self.param_names, self.param_to_remove)
        with open(self.config_dir + '/' + self.param_out, "w") as f:
            f.write("#cnt\tconf_file\t%s\n" % "\t".join(param_names))
        cnt = 0
        for p in param_combs:
            param = dict(zip(self.param_names, p))

            # パラメータの組み合わせを記録
            p_out = self.dellist(p, self.param_to_remove)
            conf_out = self.config_dir + "/%05d.py" % cnt
            with open(self.config_dir + '/' + self.param_out, "a") as f:
                f.write("%d\t%s\t" % (cnt, conf_out))
                f.write("\t".join(map(lambda x: str(x), p_out)) + "\n")

            # パラメータの組み合わせのconfigを生成
            self.generate_single_config(conf_out, param)
                
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
    ap.add_argument("-p", "--param_out", type=str, action="store",
                    default="params.tsv",
                    help="output file including parameter combinations info (default: params.tsv)",
                    )
    ap.add_argument("-c", "--conf_dir", type=str, action="store",
                    default="conf",
                    help="config output directory (default: conf)",
                    )
    return ap

#==========================================================================
if __name__ == '__main__':
    parser = arg_parser()
    args = parser.parse_args()

    # grid searchクラスをインスタンス化
    g = GridConfig(args.conf_dir, args.param_out)

    # パラメータ情報を読み込み
    g.load_param_set(args.param_file)

    if args.test:
        # 何パターンの組み合わせがあるのかを表示して終了
        comb = g.generate_combinations()
        print(len(comb))
    else:
        # config出力先がなければ作成
        if not os.path.exists(args.conf_dir):
            os.makedirs(args.conf_dir)
        # グリッド実行
        g.exec_grid()
