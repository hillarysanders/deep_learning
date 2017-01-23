import numpy as np  # linear algebra
import pandas as pd  # data processing, CSV file I/O (e.g. pd.read_csv)
import dicom
import os
import scipy.ndimage
from skimage import measure, morphology
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import config, utils

"""
Note: much of the code in this file is based off of the awesome Guido's Zuidhof's pre-processing tutorial
for DICOM formatted CT scans.
https://www.kaggle.com/gzuidhof/data-science-bowl-2017/full-preprocessing-tutorial
"""


# Load the scans in given folder path
def load_scan(path):
    slices = [dicom.read_file(path + '/' + s) for s in os.listdir(path)]
    slices.sort(key=lambda x: int(x.InstanceNumber))
    try:
        slice_thickness = np.abs(slices[0].ImagePositionPatient[2] - slices[1].ImagePositionPatient[2])
    except:
        slice_thickness = np.abs(slices[0].SliceLocation - slices[1].SliceLocation)

    for s in slices:
        s.SliceThickness = slice_thickness

    return slices


def get_pixels_hu(scans):
    image = np.stack([s.pixel_array for s in scans])
    # Convert to int16 (from sometimes int16),
    # should be possible as values should always be low enough (<32k)
    image = image.astype(np.int16)

    # Set outside-of-scan pixels to 0
    # The intercept is usually -1024, so air is approximately 0
    image[image == -2000] = 0

    # Convert to Hounsfield units (HU)
    intercept = scans[0].RescaleIntercept
    slope = scans[0].RescaleSlope

    if slope != 1:
        image = slope * image.astype(np.float64)
        image = image.astype(np.int16)

    image += np.int16(intercept)

    return np.array(image, dtype=np.int16)


def resample(image, scan, new_spacing=[1, 1, 1]):
    """
    A scan may have a pixel spacing of [2.5, 0.5, 0.5], which means that the distance between slices is
    2.5 millimeters. For a different scan this may be [1.5, 0.725, 0.725], this can be problematic for
    automatic analysis (e.g. using ConvNets)!
    A common method of dealing with this is resampling the full dataset to a certain isotropic resolution.
    If we choose to resample everything to 1mm1mm1mm pixels we can use 3D convnets without worrying about
    learning zoom/slice thickness invariance.
    :param image:
    :param scan:
    :param new_spacing:
    :return:
    """
    # Determine current pixel spacing
    spacing = map(float, ([scan[0].SliceThickness] + scan[0].PixelSpacing))
    spacing = np.array(list(spacing))

    resize_factor = spacing / new_spacing
    new_real_shape = image.shape * resize_factor
    new_shape = np.round(new_real_shape)
    real_resize_factor = new_shape / image.shape
    new_spacing = spacing / real_resize_factor

    image = scipy.ndimage.interpolation.zoom(image, real_resize_factor)

    return image, new_spacing


def largest_label_volume(im, bg=-1):
    vals, counts = np.unique(im, return_counts=True)

    counts = counts[vals != bg]
    vals = vals[vals != bg]

    if len(counts) > 0:
        return vals[np.argmax(counts)]
    else:
        return None


def segment_lung_mask(image, fill_lung_structures=True):
    """
    In order to reduce the problem space, we can segment the lungs (and usually some tissue around it).
    The method that me and my student colleagues developed was quite effective.
    It involves quite a few smart steps. It consists of a series of applications of region growing and morphological
     operations. In this case, we will use only connected component analysis.
    The steps:
    Threshold the image (-320 HU is a good threshold, but it doesn't matter much for this approach)
    Do connected components, determine label of air around person, fill this with 1s in the binary image
    Optionally: For every axial slice in the scan, determine the largest solid connected component
    (the body+air around the person), and set others to 0. This fills the structures in the lungs in the mask.
    Keep only the largest air pocket (the human body has other pockets of air here and there).
    :param image:
    :param fill_lung_structures:
    :return:
    """

    # not actually binary, but 1 and 2.
    # 0 is treated as background, which we do not want
    binary_image = np.array(image > -320, dtype=np.int8) + 1
    labels = measure.label(binary_image)

    # Pick the pixel in the very corner to determine which label is air.
    #   Improvement: Pick multiple background labels from around the patient
    #   More resistant to "trays" on which the patient lays cutting the air
    #   around the person in half
    background_label = labels[0, 0, 0]

    # Fill the air around the person
    binary_image[background_label == labels] = 2


    # Method of filling the lung structures (that is superior to something like
    # morphological closing)
    if fill_lung_structures:
        # For every slice we determine the largest solid structure
        for i, axial_slice in enumerate(binary_image):
            axial_slice = axial_slice - 1
            labeling = measure.label(axial_slice)
            l_max = largest_label_volume(labeling, bg=0)

            if l_max is not None:  # This slice contains some lung
                binary_image[i][labeling != l_max] = 1

    binary_image -= 1  # Make the image actual binary
    binary_image = 1 - binary_image  # Invert it, lungs are now 1

    # Remove other air pockets inside body
    labels = measure.label(binary_image, background=0)
    l_max = largest_label_volume(labels, bg=0)
    if l_max is not None:  # There are air pockets
        binary_image[labels != l_max] = 0

    return binary_image


def normalize(image, min_bound=-1000., max_bound=400.):
    image = (image - min_bound) / (max_bound - min_bound)
    image[image > 1] = 1.
    image[image < 0] = 0.
    return image


def zero_center(image, pixel_mean=.25):
    image = image - pixel_mean
    return image


def main():
    # load, pre-process, and save the CT scans, although do zero centering and normalizing later <3
    labels = pd.read_csv(config.input_data_dir + config.file_stage1_labels, index_col='id')
    patients = os.listdir(config.input_images_dir)
    patients.sort()
    utils.safe_mkdirs(config.processed_images_dir)
    for p in range(len(patients)):
        pat = patients[p]
        if pat != '.DS_Store' and p >= 1088:

            print('Patient {}/{}: {}'.format(p+1, len(patients), pat))
            scan = load_scan(config.input_images_dir + pat)
            patient_pixels = get_pixels_hu(scan)

            pix_resampled, spacing = resample(patient_pixels, scan, [1, 1, 1])
            segmented_lungs = segment_lung_mask(pix_resampled, False)
            segmented_lungs_fill = segment_lung_mask(pix_resampled, True)

            print("\tShape before resampling: {}".format(patient_pixels.shape))
            print("\tShape after resampling: {}".format(pix_resampled.shape))

            # save the processed data:
            patient_proc_data_dir = config.processed_images_dir + pat + '/'
            utils.safe_mkdirs(patient_proc_data_dir)
            # save stuff:
            # np.save(file=patient_proc_data_dir + config.file_scan, arr=scan)
            # np.save(file=patient_proc_data_dir + config.file_pixels, arr=patient_pixels)
            np.save(file=patient_proc_data_dir + config.file_pixels_resampled, arr=pix_resampled)
            np.save(file=patient_proc_data_dir + config.file_pixels_resampled_spacing, arr=spacing)
            np.save(file=patient_proc_data_dir + config.file_segmented_lungs, arr=segmented_lungs)
            np.save(file=patient_proc_data_dir + config.file_segmented_lungs_fill, arr=segmented_lungs_fill)


# 4 dimensional convolutional neural network

##############
if __name__ == '__main__':
    # about two thirds done, Patient 1088/1596: ad7e6fe9d036ed070df718f95b212a10
    main()
