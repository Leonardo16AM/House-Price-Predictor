import pandas as pd
from keras.models import load_model


def keras_predict(feats):
    # return 1000000
    model = load_model("models/keras_68_65.h5")
    return model.predict(feats)
