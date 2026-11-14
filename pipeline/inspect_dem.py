"""Print the geospatial tags of a LOLA GeoTIFF."""

import sys

import tifffile


def main(path):
    with tifffile.TiffFile(path) as tif:
        page = tif.pages[0]
        print("shape:", page.shape, "dtype:", page.dtype)
        for tag in page.tags.values():
            if tag.name in {
                "ModelPixelScaleTag",
                "ModelTiepointTag",
                "ModelTransformationTag",
                "GeoKeyDirectoryTag",
                "GeoDoubleParamsTag",
                "GeoAsciiParamsTag",
                "GDAL_NODATA",
                "ImageDescription",
                "34735",
            }:
                value = tag.value
                if isinstance(value, bytes):
                    value = value.decode("ascii", "replace")
                print(f"{tag.name}: {value}")


if __name__ == "__main__":
    main(sys.argv[1])
