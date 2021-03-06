import tensorflow as tf
from tensorflow.contrib import slim

from network.emptyTFGraph import EmptyTfGraph
from utils.legacy.stftMagContextEncoder import StftTestContextEncoder

__author__ = 'Andres'

tf.reset_default_graph()
train_filename = '../test_w5120_g1024_h512_ex63501.tfrecords'
valid_filename = '../test_w5120_g1024_h512_ex63501.tfrecords'

window_size = 5120
gap_length = 1024
batch_size = 256

aModel = EmptyTfGraph(shapeOfInput=(batch_size, window_size), name="context encoder")

signal = aModel.output()

with tf.name_scope('Energy_Spectogram'):
    fft_frame_length = 512
    fft_frame_step = 128
    stft = tf.contrib.signal.stft(signals=signal, frame_length=fft_frame_length, frame_step=fft_frame_step)

    sides_stft = tf.stack((stft[:, :15, :], stft[:, 15+7:, :]), axis=3)

    mag_stft = tf.abs(sides_stft)    # (256, 15, 257, 2)
    aModel.setOutputTo(mag_stft)

with tf.variable_scope("Encoder"):
    filter_shapes = [(7, 89), (3, 17), (2, 6), (1, 5), (1, 3)]
    input_channels = [2, 32, 64, 128, 128]
    output_channels = [32, 64, 128, 128, 200]
    strides = [[1, 2, 2, 1], [1, 2, 3, 1], [1, 2, 3, 1], [1, 1, 2, 1], [1, 1, 1, 1]]
    names = ['First_Conv', 'Second_Conv', 'Third_Conv', 'Fourth_Conv', 'Fifth_Conv']
    aModel.addSeveralConvLayers(filter_shapes=filter_shapes, input_channels=input_channels,
                                output_channels=output_channels, strides=strides, names=names)

aModel.addReshape((batch_size, 3200))
aModel.addFullyConnectedLayer(3200, 2048, 'Fully')
aModel.addRelu()
aModel.addReshape((batch_size, 8, 8, 32))

with tf.variable_scope("Decoder"):
    filter_shapes = [(5, 5), (3, 3)]
    input_channels = [32, 64]
    output_channels = [64, 257]
    strides = [[1, 2, 2, 1]] * len(input_channels)
    names = ['First_Deconv', 'Second_Deconv']
    aModel.addSeveralDeconvLayers(filter_shapes=filter_shapes, input_channels=input_channels,
                                  output_channels=output_channels, strides=strides, names=names)

    aModel.addReshape((batch_size, 8, 257, 128))
    aModel.addDeconvLayer(filter_shape=(3, 33), input_channels=128, output_channels=7, stride=(1, 2, 2, 1),
                          name='Third_deconv')

    aModel.addReshape((batch_size, 7, 257, 32))

    aModel.addDeconvLayerWithoutNonLin(filter_shape=(5, 89), input_channels=32, output_channels=1,
                                       stride=(1, 1, 1, 1), name="Last_Deconv")
    aModel.addReshape((batch_size, 7, 257))

print(aModel.description())

model_vars = tf.trainable_variables()
slim.model_analyzer.analyze_vars(model_vars, print_info=True)

aContextEncoderNetwork = StftTestContextEncoder(model=aModel, batch_size=batch_size, stft=stft, window_size=window_size,
                                               gap_length=gap_length, learning_rate=1e-4, name='nat_mag_stft_5_')
aContextEncoderNetwork.train(train_filename, valid_filename, num_steps=1e6)
