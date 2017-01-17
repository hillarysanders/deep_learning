import os
import tempfile


def safe_remove(f):
    try:
        os.remove(f)
    except OSError:
        pass


def safe_mkdirs(d):
    if not os.path.isdir(d):
        try:
            os.makedirs(d)
        except OSError:
            pass


def safe_tempfile(tempdir="/tmp"):
    o, t = tempfile.mkstemp(dir=tempdir)
    os.close(o)
    return t


def file_dir(file=__file__):
    """
    :return: the absolute path to the directory that holds the current file
    """
    return os.path.dirname(os.path.realpath(file)) + '/'


def get_patient_cancer_status(patient_id, labels):
    if patient_id in labels.index:
        cancer_status = ['benign', 'cancerous'][labels.cancer[patient_id]]
    else:
        cancer_status = 'unknown'

    return cancer_status
