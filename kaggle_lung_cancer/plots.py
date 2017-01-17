import matplotlib.pyplot as plt
from skimage import measure, morphology
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np  # linear algebra
import pandas as pd  # data processing, CSV file I/O (e.g. pd.read_csv)
import os
import config, utils


# todo create or find a plot save wrapper / decorator?


def plot_3d(image, threshold=-300, save_path=None, cancer_status=''):
    # Position the scan upright,
    # so the head of the patient would be at the top facing the camera
    p = image.transpose(2, 1, 0)
    p = p[:, :, ::-1]

    verts, faces = measure.marching_cubes(p, threshold)

    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(111, projection='3d')

    # Fancy indexing: `verts[faces]` to generate a collection of triangles
    mesh = Poly3DCollection(verts[faces], alpha=0.1)
    face_color = [0.5, 0.5, 1]
    mesh.set_facecolor(face_color)
    ax.add_collection3d(mesh)

    ax.set_xlim(0, p.shape[0])
    ax.set_ylim(0, p.shape[1])
    ax.set_zlim(0, p.shape[2])
    plt.title("Cancer Status: {}".format(cancer_status))

    if save_path is not None:
        plt.savefig(save_path)
        plt.close()
    else:
        plt.show()


def plot_housefield_units_hist(patient_pixels, save_path=None, cancer_status=''):
    fig, ax = plt.subplots()
    plt.hist(patient_pixels.flatten(), bins=80, color='c')
    plt.xlabel("Hounsfield Units (HU)")
    plt.ylabel("Frequency")
    plt.title("Cancer Status: {}".format(cancer_status))
    if save_path is not None:
        plt.savefig(save_path)
        plt.close()
    else:
        plt.show()


def plot_ct_slice(patient_pixels, slice_idx=80, save_path=None, cancer_status=''):
    # Show some slice in the middle
    fig, ax = plt.subplots()
    plt.imshow(patient_pixels[slice_idx], cmap=plt.cm.gray)
    plt.title("CT Slice ({})\nCancer Status: {}".format(slice_idx, cancer_status))
    if save_path is not None:
        plt.savefig(save_path)
        plt.close()
    else:
        plt.show()


def main():
    labels = pd.read_csv(config.input_data_dir + config.file_stage1_labels, index_col='id')
    patients = os.listdir(config.input_images_dir)
    patients.sort()
    utils.safe_mkdirs(config.processed_images_dir)
    utils.safe_mkdirs(config.plots_dir)
    for pat in patients:
        if pat != '.DS_Store':

            cancer_status = utils.get_patient_cancer_status(patient_id=pat, labels=labels)
            patient_proc_data_dir = config.processed_images_dir + pat + '/'

            print('Creating plots for patient {}:'.format(pat))
            print('\tSaving plots to {}'.format(patient_proc_data_dir))
            print('\tCancer status: {}'.format(cancer_status))
            # load objects
            patient_data_file = patient_proc_data_dir + '{}.npy'
            # scan = np.load(file=patient_proc_data_dir.format(config.file_scan))
            pixels = np.load(file=patient_proc_data_dir.format(config.file_pixels_resampled))
            # pix_resampled = np.load(file=patient_proc_data_dir.format(config.file_pixels_resampled))
            # spacing = np.load(file=patient_proc_data_dir.format(config.file_pixels_resampled_spacing))
            segmented_lungs = np.load(file=patient_proc_data_dir.format(config.file_segmented_lungs))
            segmented_lungs_fill = np.load(file=patient_proc_data_dir.format(config.file_segmented_lungs_fill))

            # now make some initial plots:
            # first make folder to store patient plots:
            plot_file = config.plots_dir + '{}' + cancer_status + '_' + pat + '.jpeg'

            dir = 'housefield_unit_histograms/'
            utils.safe_mkdirs(config.plots_dir + dir)
            plot_housefield_units_hist(patient_pixels=pixels,
                                       save_path=plot_file.format(dir),
                                       cancer_status=cancer_status)

            for slice in range(0, len(pixels), 30):
                dir = 'ct_slices_{}/'.format(slice)
                utils.safe_mkdirs(config.plots_dir + dir)
                if slice < len(pixels):
                    plot_ct_slice(patient_pixels=pixels,
                                  slice_idx=slice,
                                  save_path=plot_file.format(dir),
                                  cancer_status=cancer_status)

            dir = 'segmented_lungs/'
            utils.safe_mkdirs(config.plots_dir + dir)
            plot_3d(segmented_lungs_fill - segmented_lungs, 0,
                    save_path=plot_file.format(dir),
                    cancer_status=cancer_status)

            dir = 'segmented_lungs_filled/'
            utils.safe_mkdirs(config.plots_dir + dir)
            plot_3d(segmented_lungs_fill, 0,
                    save_path=plot_file.format(dir),
                    cancer_status=cancer_status)


if __name__ == '__main__':
    # NOTE: must be run after preprocessing.py has been run at least once!
    main()
