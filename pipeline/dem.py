"""LOLA GeoTIFF grid reader (pure Python, no GDAL)."""

import math
import zlib

import numpy as np
import tifffile


def _unpredict_float(raw, rows, cols, itemsize=4):
    """Reverse the TIFF floating-point predictor on raw bytes.

    The TIFF horizontal predictor differences every byte of a sample except
    the least significant one, which is left unchanged. Accumulation is
    modulo 256, so it is done on the raw byte lanes.
    """
    data = np.frombuffer(raw, dtype=np.uint8).reshape(rows, cols * itemsize)
    out = data.copy()
    for lane in range(itemsize - 1):
        column = np.ascontiguousarray(out[:, lane::itemsize])
        np.cumsum(column, axis=1, dtype=np.uint8, out=column)
        out[:, lane::itemsize] = column
    return out.tobytes()


def _read_tiled_floatpred(tif, page):
    """Decode a tiled, deflate-compressed, float-predicted GeoTIFF."""
    width, height = page.width, page.height
    tile_w, tile_h = page.tilewidth, page.tilelength
    across = (width + tile_w - 1) // tile_w
    dtype = np.dtype("<f4" if tif.byteorder == "II" else ">f4")

    array = np.empty((height, width), dtype=np.float32)
    handle = tif.filehandle
    for index, (offset, count) in enumerate(zip(page.dataoffsets, page.databytecounts)):
        handle.seek(offset)
        raw = zlib.decompress(handle.read(count))
        tile_row, tile_col = divmod(index, across)
        rows = min(tile_h, height - tile_row * tile_h)
        cols = min(tile_w, width - tile_col * tile_w)
        if raw.__len__() == tile_h * tile_w * 4:
            block = np.frombuffer(
                _unpredict_float(raw, tile_h, tile_w), dtype=dtype
            ).reshape(tile_h, tile_w)
            block = block[:rows, :cols]
        else:
            block = np.frombuffer(
                _unpredict_float(raw, rows, cols), dtype=dtype
            ).reshape(rows, cols)
        array[
            tile_row * tile_h : tile_row * tile_h + rows,
            tile_col * tile_w : tile_col * tile_w + cols,
        ] = block
    return array


class DemGrid:
    """A polar stereographic DEM with a linear raster-to-model mapping.

    Pixel (col, row) centre maps to model coordinates:
        x = origin_x + (col + 0.5) * scale_x
        y = origin_y - (row + 0.5) * scale_y
    """

    def __init__(self, path):
        with tifffile.TiffFile(path) as tif:
            page = tif.pages[0]
            try:
                self.array = page.asarray()
            except ValueError:
                # The float predictor needs the imagecodecs submodule that is
                # not shipped in this build; decode it here instead.
                self.array = _read_tiled_floatpred(tif, page)
            scale = page.tags["ModelPixelScaleTag"].value
            tiepoint = page.tags["ModelTiepointTag"].value

        self.scale_x = float(scale[0])
        self.scale_y = float(scale[1])
        self.origin_x = float(tiepoint[3])
        self.origin_y = float(tiepoint[4])
        self.nodata = float(page.tags["GDAL_NODATA"].value) if "GDAL_NODATA" in page.tags else math.nan

    @property
    def shape(self):
        return self.array.shape

    def xy_to_pixel(self, x, y):
        col = (x - self.origin_x) / self.scale_x - 0.5
        row = (self.origin_y - y) / self.scale_y - 0.5
        return col, row

    def pixel_to_xy(self, col, row):
        x = self.origin_x + (col + 0.5) * self.scale_x
        y = self.origin_y - (row + 0.5) * self.scale_y
        return x, y

    def elevation_at_xy(self, x, y):
        """Bilinear elevation at a model coordinate (m). NaN outside the grid."""
        col, row = self.xy_to_pixel(x, y)
        col0, row0 = int(math.floor(col)), int(math.floor(row))
        if col0 < 0 or row0 < 0 or col0 + 1 >= self.array.shape[1] or row0 + 1 >= self.array.shape[0]:
            return math.nan
        dc, dr = col - col0, row - row0
        patch = self.array[row0 : row0 + 2, col0 : col0 + 2]
        if np.isnan(patch).any():
            return math.nan
        return float(
            patch[0, 0] * (1 - dc) * (1 - dr)
            + patch[0, 1] * dc * (1 - dr)
            + patch[1, 0] * (1 - dc) * dr
            + patch[1, 1] * dc * dr
        )
