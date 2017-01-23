import pandas as pd
"""
Configuration values
"""


input_data_dir = 'data/'
input_images_dir = 'data/stage1/'
processed_images_dir = 'data/processed_images/'
plots_dir = 'plots/'


# input file names:
file_stage1_labels = 'stage1_labels.csv'
# file names:
file_scan = 'scan'
file_pixels = 'pixels'
file_pixels_resampled = 'pixels_resampled'
file_pixels_resampled_spacing = 'pixels_resampled_spacing'
file_segmented_lungs = 'segmented_lungs'
file_segmented_lungs_fill = 'segmented_lungs_fill'


housefield_unit_buckets = pd.DataFrame(
    dict(air=[-1000, '#5080cc', -10000, 170, 200, 240],
         lung=[-500, 'pink', -750, 238, 136, 186],
         fat=[-75, 'grey', -150, 150, 150, 150],
         water=[0, 'blue', -25, 50, 50, 250],
         # csf=[15, '#90aaff', 5],
         muscle=[25, 'red', 5, 250, 30, 30],
         blood=[37.5, 'darkred', 30, 170, 40, 40],
         liver=[50, 'green', 45, 65, 205, 130],
         soft_tissue=[200, 'yellow', 75, 220, 200, 50],
         bone=[700, 'white', 500, 245, 255, 255]),
    index=['average_value', 'color', 'min_value', 'r', 'g', 'b']
).transpose().sort_values('min_value')
