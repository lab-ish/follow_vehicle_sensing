# -*- coding: utf-8 -*-
#
# Copyright (c) 2018-2019, Shigemi ISHIDA
# All rights reserved.
#
# DO NOT REDISTRIBUTE THIS PROGRAM NOR A PART OF THIS PROGRAM.
#

import numpy as np
from imblearn.under_sampling import RandomUnderSampler

import estimate_svm

#==========================================================================
class Estimate(estimate_svm.Estimate):

    #----------------------------------------------------------------------
    def feature_extraction(self):
        # extract TPs in vehicles
        self.vehicles.data = self.vehicles.data.loc[self.vehicles.data.detect &
                                                    self.vehicles.data.correct].reset_index(drop=True)

        # calculate features
        print("calculate features")
        self.train_matrix = self.vehicles.calc_features(
            self.vehicles.data.loc[~self.vehicles.data.is_simul &
                                   ~self.vehicles.data.is_succ
                                   ])
        self.test_matrix = self.vehicles.calc_features(
            self.vehicles.data.loc[self.vehicles.data.is_simul |
                                   self.vehicles.data.is_succ
                                   ])

        # number of classes (labels)
        self.classes = len(self.vehicles.data.type.unique())

        return

    #----------------------------------------------------------------------
    def validate(self, folds=None, repeat=1, random_state=None):
        # data
        train_x = self.train_matrix[:,:-1]
        test_x  = self.test_matrix[:,:-1]
        # label
        train_y = self.train_matrix[:,-1]
        test_y  = self.test_matrix[:,-1]

        # balance training data
        uniq, counts = np.unique(train_y, return_counts=True)
        counts[:] = np.min(counts)
        sampler1 = RandomUnderSampler(ratio=dict(zip(uniq, counts)), random_state=random_state)
        uniq, counts = np.unique(test_y, return_counts=True)
        counts[:] = np.min(counts)
        sampler2 = RandomUnderSampler(ratio=dict(zip(uniq, counts)), random_state=random_state)

        count = 0
        for rep in range(repeat):
            # resample data to balance the training/test data
            print("resample data to balance")
            train_x_resamp, train_y_resamp = sampler1.fit_sample(train_x, train_y)
            test_x_resamp, test_y_resamp   = sampler2.fit_sample(test_x, test_y)

            print("iter=%d" % count)
            score, conf_mat = self.eval(train_x_resamp, train_y_resamp,
                                        test_x_resamp,  test_y_resamp)
            self.save_result(conf_mat)
            self.save_score(score)
            count += 1

        return True

#==========================================================================
# handle arguments
def arg_parser():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("vehicle_info", type=str, action="store",
                    help="vehicle_info",
                    )
    ap.add_argument("wavfile", type=str, action="store",
                    help="vehicle sound wavfile",
                    )
    ap.add_argument("-o", "--outfile", action="store",
                    default="result.csv",
                    help="result output file name",
                    )
    ap.add_argument("-s", "--scorefile", action="store",
                    default="score.csv",
                    help="score output file name",
                    )
    ap.add_argument("-p", "--plot", action="store",
                    default=None,
                    help="confusion matrix plotting output file name",
                    )
    ap.add_argument("-r", "--repeats", type=int, action="store",
                    default=1,
                    help="number of repeats of cross-validation",
                    )
    ap.add_argument("-w", "--winsize", type=float, action="store",
                    default=2.0,
                    help="window size for each vehicle",
                    )
    ap.add_argument("-c", "--cutoff", type=float, action="store",
                    default=10e3,
                    help="LPF cutoff frequency",
                    )
    return ap

#==========================================================================
if __name__ == '__main__':
    parser = arg_parser()
    args = parser.parse_args()

    import vehicles
    import ext_feature_single

    # feature extraction class instance
    ext = ext_feature_single.ExtFeature(
        win        = args.winsize,
        cutoff     = args.cutoff,
        )
    # load sound data
    print("load sound data %s" % args.wavfile)
    ext.load_sound(args.wavfile)

    # vehicle info class instance
    veh = vehicles.Vehicles(args.vehicle_info, ext)
    print("load vehicle data %s" % args.vehicle_info)
    veh.load_data()

    # find simultaneous/successive
    veh.num_simul_successive()
    # exclude trucks
    veh.data = veh.data.loc[veh.data.type != 'truck']

    # estimation class instance
    e = Estimate(
        ext_feature = ext,
        vehicles    = veh,
        result_file = args.outfile,
        score_file  = args.scorefile,
        )
    e.feature_extraction()

    # estimate
    e.validate(repeat=args.repeats)

    # finalize results
    if args.outfile is not None:
        e.load_result(e.result_file)
        e.finalize()
        print("accuracy=%.4f" % e.final_accuracy)

        # plot confusion matrix
        if args.plot is not None:
            e.plot_confusion_matrix(args.plot)
