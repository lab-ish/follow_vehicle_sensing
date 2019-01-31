.. -*- coding: utf-8; -*-

====================================================================
 サウンドマップで得られた方向の音を解析して車種判別するプロジェクト
====================================================================

サウンドマップ上のSカーブを利用するとマイクロフォンから見た車両方向が分かる。
本プロジェクトではSカーブから得た方向の音を足し合わせた上で解析することで車両種別判定の精度を向上させる。

Required Libraries
==================

* wave
* numpy
* scipy
* matplotlib
* seaborn
* scikit-learn
* imblearn

Submodules
==========

* soundmap: サウンドマップを描くためのモジュール。

Usage
=====

推定
----

``config_template.py`` をコピーして変更を加えた設定ファイルを作成する。
作成した設定ファイルを ``-c`` オプションの引数として ``main.py`` を実行する。

.. code-block:: bash

   % python3 main.py -c conf.py

オプション引数を省略した場合は ``config.py`` が指定されたたものとする。

実行が完了すると ``main.py`` の ``OUTDIR`` で指定されたディレクトリを出力ディレクトリとして以下が作成される。

* 設定ファイルのコピー（例: ``20181125_1620_config.py``: 日時の付いたファイル名としてコピー）
* 出力

  * confusion matrixファイル (例 ``20181125_1620_result.csv``): confusion matrixをreshape(1,-1)したものが各試行各行にして格納。
  * トレーニングscoreファイル（例 ``20181125_1620_score.csv``): トレーニングデータでの推定結果スコアを各試行各行に格納。

Confusion Matrixの描画
----------------------

confusion matrixのプロットは ``conf_matrix_plotting.py`` を使用して描く。
引数に上記のconfusion matrixファイルを指定する。

.. code-block:: bash

   % python3 conf_mat_plotting.py results/20181125_1620_result.csv

ファイルに出力する場合は ``-p`` オプションを使う。

.. code-block:: bash

   % python3 conf_mat_plotting.py -p test.eps results/20181125_1620_result.csv

設定ファイルをオプションで指定すると車両種別をラベルで描くことができる。

.. code-block:: bash

   % python3 conf_mat_plotting.py -p test.eps -c results/20190131_0749_config.py results/20190131_0749_result.csv

パラメータを振っての実行（Grid Search）
=======================================

パラメータを振って実行する場合には、各パラメータの組み合わせを記述したファイルから設定を生成してからシェルスクリプトで繰り返し実行する。

まず、 ``grid_template.py`` のコピーを編集して各パラメータの組み合わせを記述する。
パラメータの取り得る値をリストとして記述し、パラメータの組み合わせが満たさなければいけない条件を関数 ``constraints( )`` に記述する。
ここでは ``grid.py`` に記述したものとする。

次に、 ``grid_config.py`` を使って設定ファイル群を生成する。
設定ファイル群はデフォルトでは ``conf/`` ディレクトリに作成される。
出力先は ``-c`` オプションで変更できる。

.. code-block:: bash

   % python3 grid_config.py -p conf/params.csv grid.py

なお、パラメータの組み合わせが何パターンとなるのかは ``-t`` オプションで確認できる。
``-t`` オプションが指定されていれば設定ファイル群は生成されない。

.. code-block:: bash

   % python3 grid_config.py -t grid.py
   192

最後に、パラメータの組み合わせを記述したパラメータ情報ファイルを指定して ``grid.sh`` を実行する。

.. code-block:: bash

   % ./grid.sh conf/params.csv

パラメータ情報ファイルは実行時に日付が付加されてコピーされる（\ ``results/20190130_2230_params.csv``\ など）。

解析
----

``grid_summary.py`` を使って解析する。
``-o`` オプションで解析結果をCSVファイルに保存することはできるが、ipythonを使って実行してpandas DataFrameで保持することをオススメする。

.. code-block:: python

   ipython >>> %run grid_summary.py results_msp/20190130_2230_params.csv
   ipython >>> sorted_param

Copyright, License
==================

Copyright (c) 2018, Shigemi ISHIDA

**DO NOT REDISTRIBUTE THIS PROGRAM NOR A PART OF THIS PROGRAM.**
