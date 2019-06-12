import os, glob
from osgeo import gdal, gdal_array
import pandas as pd
import numpy as np
import logging

"""
RASTER utilities
Author:     Nicolas EKICIER
Release:    V1.1    06/2019
        - Some changes
        - Add makemask function
            V1.O    02/2019
        - Initialization
"""

def gdal2array(filepath, sensor='S2'):
    """
    Read and transform a raster to array
    :param filepath:    - path of file
                        - folder => only one final product per folder
                            Example : .SAFE from S2
    :param sensor:      {'S2', 'LS8'}
    :return:            array of raster, projection, dimensions
    """
    def read(input):
        # Open the file:
        raster = gdal.Open(input)
        # Projection
        proj = raster.GetProjection()
        # Dimensions
        rwidth = raster.RasterXSize
        rheight = raster.RasterYSize
        # Number of bands
        numbands = raster.RasterCount
        # Metadata for the raster dataset
        meta = raster.GetMetadata()
        # Read raster data as numeric array from file
        rasterArray = gdal_array.LoadFile(input)
        return rasterArray, proj, (rwidth, rheight), numbands, meta

    if os.path.isdir(filepath):
        if sensor.lower() == 's2':
            ext = '.jp2'
            nb_bands = 4 # 4 bands at 10m
        elif sensor.lower() == 'ls8':
            ext = '.tif'

        listf = glob.glob(os.path.join(filepath, '*'+ext), recursive=True)

    elif os.path.isfile(filepath):
        output, proj, dimensions, numbands, meta = read(filepath)

    return output, proj, dimensions, numbands, meta


def makemask(ogr_in, filepath):
    """
    Build a mask array from an OGR geometry
    :param ogr_in:
    :param filepath:
    :return:
    """
    return maskarray


def resample_and_reproject(image_in, out_width, out_height, out_geo_transform, out_proj=None, mode='bicubic'):
    """
    Resample and reproject a raster

    :param image_in: input raster
    :param out_width: pixel width of the output raster
    :param out_height: pixel height of the output raster
    :param out_geo_transform: GeoTransform of the output raster
    :param out_proj: output projection (default to input projection)
    :param mode: interpolation mode ['bicubic' (default), 'average', 'bilinear', 'lanczos' or 'nearest']
    :type image_in: ``ogr.DataSet``
    :type out_width: int
    :type out_height: int
    :type out_geo_transform: tuple of floats
    :type out_proj: string
    :type mode: string
    :return: the reprojected and resampled raster, None otherwise
    :rtype: ``gdal.DataSet``
    """
    if isinstance(image_in, str):
        image_in = gdal.Open(image_in)
    in_proj = image_in.GetProjection()

    out_raster = gdal.GetDriverByName('MEM').Create("", out_width, out_height, image_in.RasterCount,
                                                    image_in.GetRasterBand(1).DataType)
    out_raster.SetGeoTransform(out_geo_transform)

    mode_gdal = gdal.GRA_Cubic
    if mode.lower() == 'average':
        mode_gdal = gdal.GRA_Average
    elif mode.lower() == 'bilinear':
        mode_gdal = gdal.GRA_Bilinear
    elif mode.lower() == 'lanczos':
        mode_gdal = gdal.GRA_Lanczos
    elif mode.lower() == 'nearest':
        mode_gdal = gdal.GRA_NearestNeighbour

    reproj_res = None
    if out_proj is None:
        out_raster.SetProjection(in_proj)
        reproj_res = gdal.ReprojectImage(image_in, out_raster, None, None, mode_gdal)
    else:
        out_raster.SetProjection(out_proj)
        reproj_res = gdal.ReprojectImage(image_in, out_raster, in_proj, out_proj, mode_gdal)

    if reproj_res != 0:
        logging.error("Error of reprojection/resampled")
        return None
    return out_raster