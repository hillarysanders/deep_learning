import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.patches as mpatches
from skimage import measure, morphology
import base64
# from IPython.display import HTML
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np  # linear algebra
import pandas as pd  # data processing, CSV file I/O (e.g. pd.read_csv)
import os
import config, utils, klc_utils


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
    # p has 2 elements: 1) frequency and 2) bin start / ends.
    series = pd.Series(patient_pixels.flatten())
    freq, bins = np.histogram(series, config.housefield_unit_buckets.min_value)

    p = series.plot(kind='hist', bins=100, color='#5090cc')
    for i, rectangle in enumerate(p.patches):  # iterate over every bar
        distances = abs((rectangle.get_x() + (rectangle.get_width() * .5)) -
                        config.housefield_unit_buckets.average_value)
        closest = distances.idxmin()
        p.patches[i].set_color(config.housefield_unit_buckets.color[closest])
        p.patches[i].set_label(closest)

    handles, labels = p.get_legend_handles_labels()
    fuck_python_plotting_idx = ~pd.Series(labels).duplicated().values
    h = [handles[i] for i in range(len(handles)) if fuck_python_plotting_idx[i] == True]
    l = [labels[i] for i in range(len(labels)) if fuck_python_plotting_idx[i] == True]
    p.legend(h, l)
    plt.xlabel("Hounsfield Units (HU)")
    plt.ylabel("Frequency")
    plt.title("Cancer Status: {}".format(cancer_status))

    if save_path is not None:
        plt.savefig(save_path)
        plt.close()
    else:
        plt.show()
        plt.close()


def plot_ct_slice(patient_pixels, slice_idx=80, save_path=None, cancer_status='', color=True):
    # Show some slice in the middle
    slice = patient_pixels[slice_idx]
    if color:
        slice = klc_utils.ct_slice_to_3d_rgb_array(slice)
        p = plt.imshow(slice)
    else:
        p = plt.imshow(slice, cmap=plt.cm.gray)

    hus = config.housefield_unit_buckets
    colors = [mpatches.Patch(color=hus.color[l], label='{} ({})'.format(l, hus.average_value[l])) for l in hus]
    plt.legend(handles=colors)
    plt.title("CT Slice ({})\nCancer Status: {}".format(slice_idx, cancer_status))
    if save_path is not None:
        plt.savefig(save_path)
        plt.close()
    else:
        plt.show()


def animate_ct_scan(pixels, gifname):
    # Based on @Zombie's code
    fig = plt.figure()
    anim = plt.imshow(pixels[0], cmap=plt.cm.bone)
    def update(i):
        anim.set_array(pixels[i])
        return anim,

    a = animation.FuncAnimation(fig, update, frames=range(len(pixels)), interval=50, blit=True)
    a.save(gifname, writer='imagemagick')


# def display_gif(fname):
#     IMG_TAG = """<img src="data:image/gif;base64,{0}">"""
#     data = open(fname, "rb").read()
#     data = base64.b64encode(data)
#     return HTML(IMG_TAG.format(data))


def main():
    labels = pd.read_csv(config.input_data_dir + config.file_stage1_labels, index_col='id')
    patients = os.listdir(config.input_images_dir)
    patients.sort()
    utils.safe_mkdirs(config.processed_images_dir)
    utils.safe_mkdirs(config.plots_dir)
    for p in range(len(patients)):
        pat = patients[p]
        if pat != '.DS_Store':

            cancer_status = utils.get_patient_cancer_status(patient_id=pat, labels=labels)
            patient_proc_data_dir = config.processed_images_dir + pat + '/'

            print('Creating plots for patient {}/{}: {}'.format(p + 1, len(patients), pat))
            print('\tCancer status: {}'.format(cancer_status))
            print('\tSaving plots to {}'.format(patient_proc_data_dir))
            # load objects
            patient_data_file = patient_proc_data_dir + '{}.npy'
            # scan = np.load(file=patient_data_file.format(config.file_scan))
            pixels = np.load(file=patient_data_file.format(config.file_pixels_resampled))
            # pix = np.load(file=patient_data_file.format(config.file_pixels))
            spacing = np.load(file=patient_data_file.format(config.file_pixels_resampled_spacing))
            segmented_lungs = np.load(file=patient_data_file.format(config.file_segmented_lungs))
            segmented_lungs_fill = np.load(file=patient_data_file.format(config.file_segmented_lungs_fill))

            # now make some initial plots:
            # first make folder to store patient plots:
            plot_file = config.plots_dir + '{}' + cancer_status + '_' + pat + '.jpeg'

            dir = 'ct_scan_gif/'
            utils.safe_mkdirs(config.plots_dir + dir)
            animate_ct_scan(pixels, gifname=plot_file.format(dir).replace('.jpeg', '.gif'))

            dir = 'housefield_unit_histograms/'
            utils.safe_mkdirs(config.plots_dir + dir)
            plot_housefield_units_hist(patient_pixels=pixels,
                                       save_path=plot_file.format(dir),
                                       cancer_status=cancer_status)

            for slice in range(0, len(pixels), 30):
                for color in [True, False]:
                    colored = 'rgb' if color else 'bw'
                    dir = 'ct_slices_{}_{}/'.format(colored, slice)
                    utils.safe_mkdirs(config.plots_dir + dir)
                    if slice < len(pixels):
                        plot_ct_slice(patient_pixels=pixels,
                                      slice_idx=slice,
                                      save_path=plot_file.format(dir),
                                      cancer_status=cancer_status,
                                      color=color)

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
