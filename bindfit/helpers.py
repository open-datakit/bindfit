"""Miscellaneous fitting helper functions.

Mainly statistics calculations and data munging.
"""


import numpy as np
import numpy.matlib as ml


def ssr(residuals):
    """Calculate the sum of squares of given residuals."""
    return np.sum(np.square(residuals))


def cov(data, residuals, total=False):
    """Calculate the covariance of a fit."""
    # TODO: TEMP
    # Add axis to any single y arrays for generalised calcs
    if hasattr(residuals, "shape") and len(residuals.shape) == 1:
        residuals = residuals[np.newaxis]

    data_norm = normalise(data)

    if total:
        return np.var(residuals) / np.var(data_norm)
    else:
        return np.var(residuals, axis=1) / np.var(data_norm, axis=1)


def rms(residuals, total=False):
    """Calculate RMS errors from residuals.

    Parameters
    ----------
    residuals : array_like
        3D array of residuals corresponding to each input y

    Returns
    -------
    rms : array
        1D array of RMS values for each fitted y
    """
    # TODO: TEMP
    # Add axis to single y arrays for generalised calcs
    if hasattr(residuals, "shape") and len(residuals.shape) == 1:
        residuals = residuals[np.newaxis]

    r = np.array(residuals)
    sqr = np.square(r)

    if total:
        return np.sqrt(np.mean(sqr))
    else:
        return np.sqrt(np.mean(sqr, axis=1))


def normalise(data):
    """Normalise a 2D array of observations.

    Subtracts initial values from observed data.

    Parameters
    ----------
    data : ndarray
        N x M array of N dependent variables, M observations

    Returns
    -------
    data_norm : ndarray
        N x M array of normalised input data
    """

    # Create matrix of initial values to subtract from original matrix
    initialmat = ml.repmat(data.T[0, :], len(data.T), 1).T
    data_norm = data - initialmat
    return data_norm


def denormalise(data, data_norm):
    """Denormalise a dataset given original non-normalised input data.

    Add back initial values to the observed data.

    Parameters
    ----------
    data : ndarray
        Original non-normalised N x M array
    data_norm : ndarray
        Normalised N x M array

    Returns
    -------
    data_denorm : ndarray
        N x M array of denormalised input data_norm
    """
    # Create matrix of initial data values to add to fit
    initialmat = ml.repmat(data[:, 0][np.newaxis].T, 1, data.shape[1])
    # De-normalize normalised data (add initial values back)
    data_denorm = data_norm + initialmat
    return data_denorm


def dilute(h0, data):
    """Apply dilution factor to a dataset.

    Parameters
    ----------
    h0 : ndarray
        1D array of M observations of Host concentrations
    data : ndarray
        (ydata)
        Y x M array of non-normalised observations of dependent variables

    Returns
    -------
    y_dil : ndarray
        Y x M array of input data with dilution factor applied
    """
    y = data
    dilfac = h0 / h0[0]
    dilmat = ml.repmat(dilfac, y.shape[0], 1)
    y_dil = y * dilmat
    return y_dil


def pad_2d(items, const=None):
    """Pad a list to the specified size along second axis.

    All items in list must be lists.
    """
    # Find maximum 2nd axis size to pad to
    sizes = [len(i) for i in items]
    size = max(sizes)

    # If padding needed (sizes are not all equal)
    if size > 1 and sizes.count(sizes[0]) != len(sizes):
        padded = []
        for i in range(len(items)):
            pad = [const] * size
            pad[0 : len(items[i])] = items[i]
            padded.append(pad)
    else:
        padded = items

    return padded


def unpad_2d(items, const=None):
    """Remove padding on list applied by pad_2d."""
    # Check if passed list is a list of lists, do nothing if not

    unpadded = None
    if not any(isinstance(item, list) for item in items):
        unpadded = items
    else:
        unpadded = [
            [value for value in subitems if value is not None]
            for subitems in items
        ]
    return unpadded
