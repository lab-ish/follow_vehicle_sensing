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

    #----------------------------------------------------------------------
    # feature extraction:
    #   single channel, freq domain
    def extract_feature(self, t0, v):
        time_idx, t0_offset = self.time_indices(t0, v)

        return np.array(self.sig.fft_data1[time_idx])

#==========================================================================
if __name__ == '__main__':
    pass
