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

Copyright, License
==================

Copyright (c) 2018, Shigemi ISHIDA

**DO NOT REDISTRIBUTE THIS PROGRAM NOR A PART OF THIS PROGRAM.**
