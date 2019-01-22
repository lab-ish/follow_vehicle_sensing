# -*- coding: utf-8 -*-
#
# Copyright (c) 2018, Shigemi ISHIDA
# All rights reserved.
#
# DO NOT REDISTRIBUTE THIS PROGRAM NOR A PART OF THIS PROGRAM.
#

import pandas as pd

#==========================================================================
class Vehicles():
    def __init__(self, datafile, extract_feature=None):
        self.datafile = datafile
        if extract_feature is not None:
            self.extract_feature = extract_feature
        return

    #----------------------------------------------------------------------
    def load_data(self):
        self.data = pd.read_csv(self.datafile,
                                sep="\t",
                                header=0,
                                )
        return

#==========================================================================
if __name__ == '__main__':
    pass
