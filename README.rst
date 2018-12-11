.. -*- coding: utf-8; -*-

====================================================================
 サウンドマップで得られた方向の音を解析して車種判別するプロジェクト
====================================================================

サウンドマップ上のSカーブを利用するとマイクロフォンから見た車両方向が分かる。
本プロジェクトではSカーブから得た方向の音を足し合わせた上で解析することで車両種別判定の精度を向上させる。

Required Libraries
==================

* numpy
* scipy
* matplotlib (for testing sound_shift_fft)

Submodules
==========

* soundmap: サウンドマップを描くためのモジュール。

Usage
=====

Copyright, License
==================

Copyright (c) 2018, Shigemi ISHIDA

**DO NOT REDISTRIBUTE THIS PROGRAM NOR A PART OF THIS PROGRAM.**
