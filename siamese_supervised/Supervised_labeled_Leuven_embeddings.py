"""
    here we'll do supervised learning on canine patches, and use the resulting embedding
    the idea is that those embeddings shall be better than auto-encoder embeddings
"""

import numpy as np
from keras.layers import Input, Dense, Dropout, Convolution3D, \
    MaxPooling3D, Flatten, BatchNormalization
from keras.models import Model, Sequential
from keras.callbacks import EarlyStopping
from sklearn.metrics import confusion_matrix, accuracy_score

import matplotlib
matplotlib.use('qt4agg')
from matplotlib import pyplot as plt

from canine_labeled import loadData


# a CNN layer for intensity inputs
def create_cnn_network(input_dim):
    '''Base network to be shared (eq. to feature extraction).
    '''
    seq = Sequential()

    # conv layers
    kern_size = 3
    seq.add(Convolution3D(5, kern_size, kern_size, kern_size, input_shape=input_dim,
                          border_mode='valid', dim_ordering='th', activation='relu'))
    seq.add(Dropout(.2))
    seq.add(MaxPooling3D((2, 2, 2), dim_ordering='th'))
    seq.add(Convolution3D(15, kern_size, kern_size, kern_size,
                          border_mode='valid', dim_ordering='th', activation='relu'))
    seq.add(Convolution3D(45, kern_size, kern_size, kern_size,
                          border_mode='valid', dim_ordering='th', activation='relu'))
    seq.add(Dropout(.2))
    seq.add(Flatten())
    return seq


# create groups of 4 image sets as training and 1 as test
def create_train_test_set(src, data_stem, train_ids, test_id):
    x_tr = []
    y_tr = []
    for tid in train_ids:
        train_name = data_stem + str(tid)
        x_train, y_train = loadData.get_labeled_patches(src, train_name)
        x_tr.append(x_train)
        y_tr.append(y_train)

    x_tr_all = np.concatenate(x_tr)
    y_tr_all = np.concatenate(y_tr)

    test_name = data_stem + str(test_id)
    x_test, y_test = loadData.get_labeled_patches(src, test_name)
    return x_tr_all, y_tr_all, x_test, y_test


# load data
src = '/home/nripesh/Dropbox/research_matlab/feature_tracking/' + \
      'generating_train_data_forNNet/'
tr_id = [25, 26, 28, 29]
test_id = 27
data_stem = 'leuven_labeled_patches_'
x_train, y_train, x_test, y_test = create_train_test_set(src, data_stem, tr_id, test_id)

# encoding layer
rand_samp_inds = np.random.randint(0, x_train.shape[0], 200000)
x_train = x_train[rand_samp_inds, :, :, :, :]
y_train = y_train[rand_samp_inds, :]

input_dim = x_train.shape[1:]
input_a = Input(shape=input_dim)
base_network = create_cnn_network(input_dim)
embedding = base_network(input_a)

# save the encoder and add one dense layer/dropout after
encoder = Model(input=input_a, output=embedding)
post_encoder = Dense(50, activation='relu')(embedding)
post_encoder = Dropout(.2)(post_encoder)

# add softmax and categorical crossentropy
num_classes = y_train.shape[1]
predict_layer = Dense(num_classes, activation='softmax')(post_encoder)
model = Model(input=input_a, output=predict_layer)
model.compile(loss='categorical_crossentropy',
              optimizer='adadelta',
              metrics=['accuracy'])

batch_size = 128
epochs = 20
model.fit([x_train], y_train,
          batch_size=batch_size,
          nb_epoch=epochs,
          verbose=2,
          validation_split=.25,
          callbacks=[EarlyStopping(monitor='val_loss', patience=3)])

y_test_pred = model.predict(x_test)
y_test_pred_label = np.argmax(y_test_pred, axis=1)
y_test_label = np.argmax(y_test, axis=1)

print("accuracy is: " + str(accuracy_score(y_test_label, y_test_pred_label)))
print("confusion matrix:")
print(confusion_matrix(y_test_label, y_test_pred_label))

# save the embedder
encode_name = '/home/nripesh/PycharmProjects/Siamese/leuven_sup_encoder.h5'
encoder.save(encode_name)
