.. -*- coding: utf-8; -*-

====================================================================
 サウンドマップで得られた方向の音を解析して車種判別するプロジェクト
====================================================================

サウンドマップ上のSカーブを利用するとマイクロフォンから見た車両方向が分かる。
本プロジェクトではSカーブから得た方向の音を足し合わせた上で解析することで車両種別判定の精度を向上させる。

Required Libraries
==================

* numpy

Submodules
==========

* sound_map: サウンドマップを描く。
* ransac_detect: RANSACを用いてS字カーブを検出する。

Usage
=====

Copyright, License
==================

Copyright (c) 2018, Shigemi ISHIDA

**DO NOT REDISTRIBUTE THIS PROGRAM NOR A PART OF THIS PROGRAM.**
