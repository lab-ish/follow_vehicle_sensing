# -*- coding: utf-8 -*-
#
# Copyright (c) 2018, Shigemi ISHIDA
# All rights reserved.
#
# DO NOT REDISTRIBUTE THIS PROGRAM NOR A PART OF THIS PROGRAM.
#

import os
import sys
import numpy as np
import importlib
from sklearn import svm
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler
from imblearn.under_sampling import RandomUnderSampler

import vehicles
import conf_mat_plotting

#==========================================================================
class Estimate(conf_mat_plotting.ConfMatPlotting):
    def __init__(self,
                 ext_feature_class="ext_feature_shift_fft", # feature extraction class file
                 result_file=None, # output filename for results
                 score_file=None,  # output filename for test score
                 winsize=None,     # window size for each vehicle
                 cutoff=None,      # cutoff frequency
                 fft_len=None,     # FFT window size
                 fft_shift=None,   # FFT shift length
                 ma_len=None,      # moving average window size
                 ):
        super(Estimate, self).__init__()
        self.result_file = result_file
        self.score_file = score_file
        self.winsize = winsize
        self.cutoff = cutoff
        self.fft_len = fft_len
        self.fft_shift = fft_shift
        self.ma_len = ma_len

        self.model = None          # machine learning model
        self.results = None        # results
        self.ext_feature = None    # feature extraction class
        self.vehicles = None       # vehicle data class
        self.classes = None        # number of classes (labels)
        # feature matrix: features, label (= vehicle type id)
        self.feature_matrix = None

        # import feature extraction class
        self.load_ext_feature_class(ext_feature_class)

        return

    #----------------------------------------------------------------------
    def load_ext_feature_class(self, class_file):
        # add feature extraction class path to the import path
        base_path = os.path.dirname(class_file)
        base_file, base_ext = os.path.splitext(os.path.basename(class_file))
        sys.path.append(base_path)
        base_name = base_file.split("_")[:2]

        # import feature extraction class
        self.ext = importlib.import_module(base_file)

        return True

    #----------------------------------------------------------------------
    def load_data(self, vehicle_file, wavfile):
        # load sound data
        print("load sound data %s" % wavfile)
        self.ext_feature = self.ext.ExtFeature(wavfile=wavfile,
                                               win=self.winsize,
                                               cutoff=self.cutoff,
                                               fft_len=self.fft_len,
                                               fft_shift=self.fft_shift,
                                               ma_len=self.ma_len,
                                               )
        self.ext_feature.load_sound()
        # load vehicle data
        print("load vehicle data %s" % vehicle_file)
        self.vehicles = vehicles.Vehicles(vehicle_file, self.ext_feature)
        self.vehicles.load_data()

        # calculate features
        print("calculate features")
        self.feature_matrix = self.vehicles.calc_features()

        # number of classes (labels)
        self.classes = len(self.vehicles.data.type.unique())

        return

    #----------------------------------------------------------------------
    def define_model(self):
        # release model
        del self.model
        # reload model
        self.model = svm.LinearSVC(loss='hinge', C=1.0, class_weight='balanced', random_state=0)

        return self.model

    #----------------------------------------------------------------------
    def eval(self, x_train, y_train, x_test, y_test):
        # recompile model
        self.define_model()

        # feature scaling
        scaler = StandardScaler()
        x_train_scaled = scaler.fit_transform(x_train)
        x_test_scaled  = scaler.transform(x_test)

        # training
        self.model.fit(x_train_scaled, y_train)
        test_score = self.model.score(x_train_scaled, y_train)

        # estimation
        y_est = self.model.predict(x_test_scaled)

        # generate confusion matrix
        conf_mat = confusion_matrix(y_test, y_est)

        return test_score, conf_mat

    #----------------------------------------------------------------------
    def cross_validation(self, folds=10, repeat=1):
        # data
        x = self.feature_matrix[:,:-1]
        # label
        y = self.feature_matrix[:,-1]

        # folded validation
        skf = StratifiedKFold(n_splits=folds, shuffle=True)

        count = 0
        for rep in range(repeat):
            # resample data to balance the training/test data
            print("resample data to balance")
            uniq, counts = np.unique(y, return_counts=True)
            counts[:] = np.min(counts)
            sampler = RandomUnderSampler(ratio=dict(zip(uniq, counts)), random_state=0)
            x_resamp, y_resamp = sampler.fit_sample(x, y)

            for train_idx, test_idx in skf.split(x_resamp, y_resamp):
                print("iter=%d" % count)
                score, conf_mat = self.eval(x_resamp[train_idx], y_resamp[train_idx],
                                            x_resamp[test_idx],  y_resamp[test_idx])
                self.save_result(conf_mat)
                self.save_score(score)
                count += 1

        return True

    #----------------------------------------------------------------------
    def save_result(self, c_mat):
        if self.result_file is None:
            return False

        with open(self.result_file, 'a') as f:
            np.savetxt(f,
                       c_mat.reshape(1,-1),
                       fmt=["%d"]*(self.classes**2),
                       delimiter=",",
                       )

        return True

    #----------------------------------------------------------------------
    def save_score(self, score):
        if self.score_file is None:
            return False

        with open(self.score_file, 'a') as f:
            np.savetxt(f,
                       np.array([score]),
                       fmt=["%f"],
                       delimiter=",",
                       )

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
    ap.add_argument("-f", "--folds", type=int, action="store",
                    default=10,
                    help="number of folding in cross-validation",
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
                    default=4.0,
                    help="window size for each vehicle",
                    )
    return ap

#==========================================================================
if __name__ == '__main__':
    parser = arg_parser()
    args = parser.parse_args()

    e = Estimate(winsize=args.winsize)

    if args.outfile is not None:
        e.result_file = args.outfile
    if args.scorefile is not None:
        e.score_file = args.scorefile

    e.load_data(args.vehicle_info, args.wavfile)
    e.cross_validation(folds=args.folds, repeat=args.repeats)

    # plot confusion matrix
    if args.plot is not None:
        if args.outfile is None:
            sys.stderr.print("No result is stored.")
        else:
            e.load_result(e.result_file)
            e.finalize()
            e.plot_confusion_matrix(args.plot)
            print("accuracy=%.4f" % e.final_accuracy)
