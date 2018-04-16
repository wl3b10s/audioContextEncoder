import tensorflow as tf

__author__ = 'Andres'


class Architecture(object):
    def __init__(self):
        self._input = tf.placeholder(tf.float32, shape=self.inputShape(), name='input_data')
        self._output = self._network(self._input)
        self._target = tf.placeholder(tf.float32, shape=self._output.shape, name='target_data')
        self._lossSummaries = []
        self._loss = self._lossGraph()

    def input(self):
        return self._input

    def target(self):
        return self._target

    def loss(self):
        return self._loss

    def lossSummaries(self):
        return self._lossSummaries

    def _preprocessData(self, data):
        return data

    def _postprocessData(self, data):
        return data

    def _lossGraph(self):
        raise NotImplementedError("Subclass Responsibility")

    def _network(self, data):
        raise NotImplementedError("Subclass Responsibility")

    def inputShape(self):
        raise NotImplementedError("Subclass Responsibility")

    def _targetShape(self):
        raise NotImplementedError("Subclass Responsibility")
