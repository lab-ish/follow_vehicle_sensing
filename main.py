# -*- coding: utf-8 -*-
#
# Copyright (c) 2018, Shigemi ISHIDA
# All rights reserved.
#
# DO NOT REDISTRIBUTE THIS PROGRAM NOR A PART OF THIS PROGRAM.
#

import numpy as np

from sound_shift_fft import SoundShiftFFT

#==========================================================================
# 引数処理
def arg_parser():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("infile", type=str, action="store",
                    help="infile",
                    )
    ap.add_argument("outfile", type=str, action="store",
                    nargs="?",
                    default="output.dat",
                    help="output file name",
                    )
    ap.add_argument("-t", action="store",
                    dest="test",
                    help="test parameter",
                    )
    ap.add_argument("-d", "--debug", action="store_true",
                    help="debug mode",
                    )
    ap.add_argument("-f", "--files", action="append",
                    default=[],
                    help="file names",
                    )
    ap.add_argument("-l", "--limit", action="store",
                    type=str,
                    default=None,
                    help="Limit range of analysis by time as \"[start:end]\" or \"start\"",
                    )
    ap.add_argument("offset", type=int, action="store", nargs="*",
                    default=[0],
                    help="set of offset values for plotting (default: 0)",
                    )
    return ap

#==========================================================================
if __name__ == '__main__':
    parser = arg_parser()
    args = parser.parse_args()

    print("infile = " + args.infile)
    print("outfile = " + args.outfile)
    if args.test:
        print("test =" + args.test)

    start = 0.
    end = 10
    if args.limit is not None:
        limit = args.limit.replace("[", "").replace("]", "")
        rng = limit.split(":")
        if len(rng) <= 1:
            start = float(rng[0])
            end   = start + args.step/2
        else:
            start = float(rng[0])
            end   = float(rng[1])

    t = SoundShiftFFT()
    print(t.glob_method())
    del t
