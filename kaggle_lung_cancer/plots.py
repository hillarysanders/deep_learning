import matplotlib.pyplot as plt
from skimage import measure, morphology
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

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
        plt.savefig(save_path.format(slice_idx))
        plt.close()
    else:
        plt.show()


