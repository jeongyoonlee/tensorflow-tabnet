from typing import List

import tensorflow as tf
from tabnet.models import TabNet


class TabNetClassifier(tf.keras.Model):
    def __init__(
        self,
        num_features: int,
        feature_dim: int,
        output_dim: int,
        n_classes: int,
        feature_columns: List = None,
        n_step: int = 1,
        n_total: int = 4,
        n_shared: int = 2,
        relaxation_factor: float = 1.5,
        sparsity_coefficient: float = 1e-5,
        bn_epsilon: float = 1e-5,
        bn_momentum: float = 0.7,
        bn_virtual_divider: int = 32,
        dp: float = None,
        **kwargs
    ):
        super(TabNetClassifier, self).__init__()
        self.sparsity_coefficient = sparsity_coefficient

        self.model = TabNet(
            feature_columns=feature_columns,
            num_features=num_features,
            feature_dim=feature_dim,
            output_dim=output_dim,
            n_step=n_step,
            relaxation_factor=relaxation_factor,
            bn_epsilon=bn_epsilon,
            bn_momentum=bn_momentum,
            bn_virtual_divider=bn_virtual_divider,
        )
        self.dp = tf.keras.layers.Dropout(dp) if dp is not None else dp
        self.head = tf.keras.layers.Dense(n_classes, activation=None, use_bias=False)

    def call(self, x, training: bool = None, alpha: float = 0.0):
        out, sparse_loss, _ = self.model(x, training=training, alpha=alpha)
        if self.dp is not None:
            out = self.dp(out, training=training)
        y = self.head(out, training=training)

        if training:
            self.add_loss(-self.sparsity_coefficient * sparse_loss)

        return y
