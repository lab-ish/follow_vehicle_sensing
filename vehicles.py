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
                                index_col=0,
                                )
        # type is described by type_id instead of type name such as 'normal' and 'bike'
        self.data['type_id'] = -1
        vehicle_types = self.data.type.unique()
        self.type_ids = dict(zip(range(len(vehicle_types)), vehicle_types))
        for type_id in self.type_ids.keys():
            self.data.loc[self.data.type == self.type_ids[type_id], 'type_id'] = type_id

        # ordery by t0 (passing time)
        self.data = self.data.sort_values('t0').reset_index(drop=True)
        return

    #--------------------------------------------------
    def num_simul_successive(self, simul_range=2):
        diff = np.diff(self.data.t0)
        self.data['diff_pos'] = np.append(diff, np.inf)
        self.data['diff_pre'] = np.insert(diff, 0, np.inf)
        self.data['diff_closer'] = np.min(self.data[['diff_pos', 'diff_pre']], axis=1)

        dirs = np.array(self.data.dir)
        self.data['dir_pos'] = np.append(dirs[1:], np.nan)
        self.data['dir_pre'] = np.insert(dirs[:-1], 0, np.nan)
        self.data['dir_closer'] = self.data.apply(
            lambda x: x.dir_pos if x.diff_pos < x.diff_pre else x.dir_pre,
            axis=1)

        # extract simul or successive
        self.data['is_simul'] = False
        self.data['is_succ']  = False
        self.data.loc[(self.data.diff_closer < simul_range) & (self.data.dir == self.data.dir_closer), 'is_simul'] = True
        self.data.loc[(self.data.diff_closer < simul_range) & (self.data.dir != self.data.dir_closer), 'is_succ'] = True

        # drop unnecessary columns
        self.data = self.data.drop(['diff_pos', 'diff_pre', 'diff_closer', 'dir_pos', 'dir_pre', 'dir_closer'], axis=1)

        ret = {}
        ret['simul'] = self.data.is_simul.sum()
        ret['succ']  = self.data.is_succ.sum()

        return ret

    #----------------------------------------------------------------------
    def calc_feature(self, t0, v, label):
        fet = self.extract_feature(t0, v)

        lab = np.empty([fet.shape[0], 1])
        lab[:] = label

        return np.c_[fet, lab]

    #----------------------------------------------------------------------
    def calc_features(self, data=None):
        if self.extract_feature is None:
            return None

        if self.data is None:
            self.load_data()

        if data is None:
            data = self.data

        # calculate feature for first vehicle
        ret = self.calc_feature(data.iloc[0].t0,
                                data.iloc[0].v,
                                data.iloc[0].type_id)
        # retrive the length of feature_matrix
        ret_len = ret.shape[0]
        # reserve space for features
        result = np.empty([ret_len*len(data), ret.shape[1]])

        # store the first feature
        result[0:ret_len,:] = ret
        # calculate and store feature for remaining vehicles
        for i in range(1,len(data)):
            ret = self.calc_feature(data.iloc[i].t0,
                                    data.iloc[i].v,
                                    data.iloc[i].type_id)
            result[ret_len*i:ret_len*(i+1),:] = ret

        return result

#==========================================================================
if __name__ == '__main__':
    pass
