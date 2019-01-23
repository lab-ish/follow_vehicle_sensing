# -*- coding: utf-8 -*-
#
# Copyright (c) 2018, Shigemi ISHIDA
# All rights reserved.
#
# DO NOT REDISTRIBUTE THIS PROGRAM NOR A PART OF THIS PROGRAM.
#

import numpy as np

from ext_feature_base import ExtFeatureBase

#==========================================================================
class ExtFeature(ExtFeatureBase):
    def __init__(self, wavfile, win=4.0, D=0.5, L=2.0):
        super(ExtFeature, self).__init__(wavfile, win, D, L)
        return

    #----------------------------------------------------------------------
    # feature extraction:
    #   shift and merge in freq domain
    def extract_feature(self, t0, v):
        time_idx, t0_offset = self.time_indices(t0, v)
        # calculate sound delay at each time index
        sound_delay = self.model(time_idx*self.samp_int, np.array([v, t0_offset*self.samp_int]))

        # shift back back left channel and merge in freq domain
        fft_merged = self.sig.shift_merge_fft(-sound_delay, time_idx[0])

        return fft_merged

#==========================================================================
if __name__ == '__main__':
    pass
