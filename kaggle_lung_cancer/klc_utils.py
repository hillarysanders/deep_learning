import numpy as np
import config, utils
"""
Utils functions that are specific to this pipeline (kaggle lung cancer project)
"""


def housefield_value_to_label(value):
    diff = value - config.housefield_unit_buckets.min_value
    diff = diff[diff>0]
    label = diff.idxmin()
    return label


def housefield_value_to_color(value):
    return config.housefield_unit_buckets.color[housefield_value_to_label(value)]


def housefield_value_to_rgb(value):
    # todo replace > near -2000
    if value < -2000:
        value = 0
    if value > 1000:
        value = 1000
    value = (value + 2000) /3000
    label = housefield_value_to_label(value)
    return [config.housefield_unit_buckets.r[label]/255.,
            config.housefield_unit_buckets.g[label]/255.,
            config.housefield_unit_buckets.b[label]/255.]


def ct_slice_to_3d_rgb_array(slice):
    # starts off as e.g. 355x355 housefield unit values
    # replace values with actual colors:
    return np.array([[housefield_value_to_rgb(value) for value in col] for col in slice])
