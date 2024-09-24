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

confusion matrixのプロットは ``conf_mat_plotting.py`` を使用して描く。
引数に上記のconfusion matrixファイルを指定する。

.. code-block:: bash

   % python3 conf_mat_plotting.py results/20181125_1620_result.csv

ファイルに出力する場合は ``-p`` オプションを使う。

.. code-block:: bash

   % python3 conf_mat_plotting.py -p test.eps results/20181125_1620_result.csv

設定ファイルをオプションで指定すると車両種別をラベルで描くことができる。

.. code-block:: bash

   % python3 conf_mat_plotting.py -p test.eps -c results/20190131_0749_config.py results/20190131_0749_result.csv

``-r`` オプションを指定するとパーセント表示でconfusion matrixを描く。

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

   % python3 grid_config.py -p conf/params.tsv grid.py

なお、パラメータの組み合わせが何パターンとなるのかは ``-t`` オプションで確認できる。
``-t`` オプションが指定されていれば設定ファイル群は生成されない。

.. code-block:: bash

   % python3 grid_config.py -t grid.py
   192

最後に、パラメータの組み合わせを記述したパラメータ情報ファイルを指定して ``grid.sh`` を実行する。

.. code-block:: bash

   % ./grid_exec.sh main.py conf/params.csv

パラメータ情報ファイルは実行時に日付が付加されてコピーされる（\ ``results/20190130_2230_params.tsv``\ など）。

解析
----

``grid_summary.py`` を使って解析する。
``-o`` オプションで解析結果をCSVファイルに保存することはできるが、ipythonを使って実行してpandas DataFrameで保持することをオススメする。

.. code-block:: python

   ipython >>> %run grid_summary.py results_msp/20190130_2230_params.csv
   ipython >>> sorted_param

Our Papers
==========

- B. Dawton, S. Ishida, Y. Hori, M. Uchino, Y. Arakawa, S. Tagashira, and A. Fukuda,
  "Initial Evaluation of Vehicle Type Identification using Roadside Stereo Microphones",
  IEEE Sensors and Applications Symposium (SAS), Kuala Lumpur, Malaysia, pp.1-6, Mar 2020.
  https://doi.org/10.1109/SAS48726.2020.9220076
- M. Uchino, B. Dawton, Y. Hori, S. Ishida, S. Tagashira, Y. Arakawa, and A. Fukuda,
  "Initial Design of Two-Stage Acoustic Vehicle Detection System for High Traffic Roads",
  International Workshop on Pervasive Computing for Vehicular Systems (PerVehicle), in conjunction with IEEE International Conference on Pervasive Computing and Communications (PerCom), Austin, TX, pp.590-595, Mar 2020.
  https://doi.org/10.1109/PerComWorkshops48775.2020.9156248
- 内野 雅人, 石田 繁巳, 田頭 茂明, 荒川 豊, 福田 晃,
  "多車線道路に対応した2段階音響車両検出システムの初期的評価",
  マルチメディア通信と分散処理ワークショップ（DPSWS2019）, pp.84-90, Nov 2019.
  http://id.nii.ac.jp/1001/00199833/
- S. Ishida, M. Uchino, C. Li, S. Tagashira, and A. Fukuda,
  "Design of Acoustic Vehicle Detector with Steady-Noise Suppression",
  IEEE International Conference on Intelligent Transportation Systems (ITSC), Auckland, New Zealand, pp.2848-2853, Oct 2019.
  https://doi.org/10.1109/ITSC.2019.8917289
- 石田 繁巳, 内野 雅人, 小池 大地, 田頭 茂明, 福田 晃,
  "路側設置ステレオマイクを用いた車両種別推定手法の初期的評価",
  情報処理学会マルチメディア, 分散, 協調とモバイルシンポジウム（DICOMO2019）, pp.1682-1687, Jul 2019.
  http://id.nii.ac.jp/1001/00202424/
- M. Uchino, S. Ishida, K. Kubo, S. Tagashira, and A. Fukuda,
  "Initial Design of Acoustic Vehicle Detector with Wind Noise Suppressor",
  International Workshop on Pervasive Computing for Vehicular Systems (PerVehicle), in conjunction with IEEE International Conference on Pervasive Computing and Communications (PerCom), Kyoto, Japan, pp.814-819, Mar 2019.
  https://doi.org/10.1109/PERCOMW.2019.8730822
- 石田 繁巳, 梶村 順平, 内野 雅人, 田頭 茂明, 福田 晃,
  "路側設置マイクロフォンを用いた逐次検出型車両検出システム",
  情報処理学会論文誌, vol.60, no.1, pp.76-86, Jan 2019.
  http://id.nii.ac.jp/1001/00193796/
- S. Ishida, J. Kajimura, M. Uchino, S. Tagashira, and A. Fukuda,
  "SAVeD: Acoustic Vehicle Detector with Speed Estimation capable of Sequential Vehicle Detection",
  IEEE International Conference on Intelligent Transportation Systems (ITSC), Maui, HI, pp.906-912, Nov 2018.
  https://doi.org/10.1109/ITSC.2018.8569727
- 石田 繁巳, 三村 晃平, 劉 嵩, 田頭 茂明, 福田 晃,
  "路側設置マイクロフォンによる車両カウントシステム",
  情報処理学会論文誌, vol.58, no.1, pp.89-98, Jan 2017.


Copyright, License
==================

This software is released under the BSD 3-clause license. See `LICENSE.txt`.

Copyright (c) 2018-2024, Masahiko MIYAZAKI, Shigemi ISHIDA

このレポジトリのコードを参照したり使用したりする場合は、関連論文をご参照の上、関連する論文を引用くださいますようお願いいたします。
