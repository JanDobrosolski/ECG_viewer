import tensorflow as tf

class ConditionalActivationLayer(tf.keras.layers.Layer):

    def __init__(self, f1, f2, **kwargs):
        super(ConditionalActivationLayer, self).__init__(**kwargs)
        self.f1 = f1
        self.f2 = f2

    def get_config(self):
        config = super().get_config()
        config.update({
            'f1': self.f1,
            'f2': self.f2
        })
        return config

    def call(self, inputs):
        x = inputs
        x = self.f1(x)
        condition = tf.greater(x, 0.5)
        return tf.where(condition, self.f2(inputs), tf.zeros_like(x))

def load_E2E_Model(model_path):
    custom_objects = {"ConditionalActivationLayer": ConditionalActivationLayer}
    model = tf.keras.models.load_model(model_path, custom_objects=custom_objects)
    return model
