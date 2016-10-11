"""shape_match_model_int_patch2
    Here the saved model shall be loaded and fit to matlab data
"""

# import numpy as np
import pickle
import os
import sys

from keras.models import load_model
from scipy.io import loadmat, savemat


src = sys.argv[1]
# src = '/home/nripesh/Dropbox/research_matlab/feature_tracking/shortest_paths/shortest_paths_3d/nbor_shp_data/'

if os.path.isfile(src + '/nbor_int_all_1.mat'):
    # only load if .mat file is found
    intensity_model = load_model('shape_match_model_int_patch.h5')

    no_of_files = int(sys.argv[2])
    print('processing total of: ' + str(no_of_files) + ' files.')

    for i in range(no_of_files):
        shape_data = loadmat(src+'/nbor_int_all_' + str(i+1) + '.mat')
        x_data = shape_data.get('nbor_int_all').astype('float32')
        x_data = x_data.reshape([x_data.shape[0], x_data.shape[1], 1, x_data.shape[2], x_data.shape[3],
                                 x_data.shape[4]])

        model_pred = intensity_model.predict([x_data[:, 0], x_data[:, 1]])

        x_out = {"pair_cost": model_pred}
        savemat(src+'/nbors_cost_' + str(i+1) + '.mat', x_out)
        print('match cost generated for frame: ' + str(i+1))
else:
    print('nbor_int_all_1.mat not found')
