"""
Very simple lung cancer detection based on keras documentation.
"""
from keras import layers, models
from keras.utils.np_utils import to_categorical
import numpy as np



def test_model_dummy():
    # for a single-input model with 2 classes (binary):
    model = models.Sequential()
    model.add(layers.Dense(1, input_dim=784, activation='sigmoid'))
    model.compile(optimizer='rmsprop',
                  loss='binary_crossentropy',
                  metrics=['accuracy'])

    # generate dummy data
    data = np.random.random((1000, 784))
    labels = np.random.randint(2, size=(1000, 1))

    # train the model, iterating on the data in batches
    # of 32 samples
    fit = model.fit(data, labels, nb_epoch=10, batch_size=32)


def make_model():
    model = models.Sequential()
    model.add(layers.Convolution3D(16,1,3,3, input_shape=(1,24,128,128), activation='relu'))
    model.add(layers.Convolution3D(32,1,3,3, activation='relu'))
    model.add(layers.MaxPooling3D(pool_size=(1,2,2)))
    model.add(layers.Convolution3D(32, 1,3,3,  activation='relu'))
    model.add(layers.Convolution3D(64, 1,3,3,  activation='relu'))
    model.add(layers.MaxPooling3D(pool_size=(1,2,2)))
    model.add(layers.Convolution3D(64,1,3,3, activation='relu'))
    model.add(layers.Convolution3D(128,1,3,3, activation='relu'))
    model.add(layers.MaxPooling3D(pool_size=(1,2,2)))
    model.add(layers.Convolution3D(128,1,3,3, activation='relu'))
    model.add(layers.MaxPooling3D(pool_size=(1,2,2)))
    model.add(layers.Flatten())
    model.add(layers.Dense(512, activation='relu'))
    model.add(layers.Dropout(0.5))
    model.add(layers.Dense(2, activation='softmax'))
    model.compile(loss='categorical_crossentropy',optimizer='adadelta',
                  metrics=['accuracy'])
    model.fit(trn_x, trn_y, batch_size=24, nb_epoch=10,verbose=1,
              validation_data=(val_x, val_y))