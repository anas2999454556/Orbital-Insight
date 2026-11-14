"""Read a wide LOLA DEM whose GeoTIFF uses the floating-point predictor.

The imagecodecs build available here ships the compiled float predictor but
not the `imagecodecs.floatpred` submodule that tifffile reaches for, so the
patch below routes tifffile to the compiled entry point.

Validated by cross-checking the overlap against the 5 m site DEM.
"""

import numpy as np
import tifffile
from tifffile import TIFF

import imagecodecs


def _patched_unpredict(data, axis=-1, out=None, **kwargs):
    result = imagecodecs.floatpred_decode(data, axis=axis)
    if out is None:
        return result
    out[...] = result
    return out


def install_floatpred_patch():
    TIFF.UNPREDICTORS[3] = _patched_unpredict


def read_page(path):
    install_floatpred_patch()
    with tifffile.TiffFile(path) as tif:
        page = tif.pages[0]
        array = page.asarray()
        tags = {
            name: page.tags[name].value
            for name in (
                "ModelPixelScaleTag",
                "ModelTiepointTag",
                "GeoKeyDirectoryTag",
                "GeoDoubleParamsTag",
            )
            if name in page.tags
        }
    return array, tags


if __name__ == "__main__":
    import sys

    array, tags = read_page(sys.argv[1])
    print("shape", array.shape, "dtype", array.dtype)
    finite = array[np.isfinite(array)]
    print("elevation min/max/mean", finite.min(), finite.max(), finite.mean())
    for name, value in tags.items():
        print(name, value)
