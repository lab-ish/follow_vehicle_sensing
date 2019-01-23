# -*- coding: utf-8 -*-
#
# Copyright (c) 2018, Shigemi ISHIDA
# All rights reserved.
#
# DO NOT REDISTRIBUTE THIS PROGRAM NOR A PART OF THIS PROGRAM.
#

import numpy as np
import pandas as pd

#==========================================================================
class Vehicles():
    def __init__(self, datafile, extract_feature=None):
        self.datafile = datafile
        self.data = None

        if extract_feature is not None:
            self.extract_feature = extract_feature.feature
        return

    #----------------------------------------------------------------------
    def load_data(self):
        self.data = pd.read_csv(self.datafile,
                                sep="\t",
                                header=0,
                                )
        # type is described by type_id instead of type name such as 'normal' and 'bike'
        self.data['type_id'] = -1
        vehicle_types = self.data.type.unique()
        for i in range(len(vehicle_types)):
            self.data.loc[self.data.type == vehicle_types[i], 'type_id'] = i

        return

    #----------------------------------------------------------------------
    def calc_feature(self, t0, v, label):
        fet = self.extract_feature(t0, v)

        lab = np.empty([fet.shape[0], 1])
        lab[:] = label

        return np.c_[fet, lab]

    #----------------------------------------------------------------------
    def calc_features(self):
        if self.extract_feature is None:
            return None

        if self.data is None:
            self.load_data()

        # calculate feature for first vehicle
        ret = self.calc_feature(self.data.iloc[0].t0,
                                self.data.iloc[0].v,
                                self.data.iloc[0].type_id)
        # retrive the length of feature_matrix
        ret_len = ret.shape[0]
        # reserve space for features
        result = np.empty([ret_len*len(self.data), ret.shape[1]])

        # store the first feature
        result[0:ret_len,:] = ret
        # calculate and store feature for remaining vehicles
        for i in range(1,len(self.data)):
            ret = self.calc_feature(self.data.iloc[i].t0,
                                    self.data.iloc[i].v,
                                    self.data.iloc[i].type_id)
            result[ret_len*i:ret_len*(i+1),:] = ret

        return result

#==========================================================================
if __name__ == '__main__':
    pass
