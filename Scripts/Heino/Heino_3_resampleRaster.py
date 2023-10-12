# Copyright 2019 Luke Pinner
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from contextlib import contextmanager
import rasterio
from rasterio import Affine, MemoryFile
from rasterio.enums import Resampling
import os
import sys
import platform
import sys
import pycrs

print("Script starts")

script_folder = os.path.abspath(__file__)
data_folder = os.path.dirname(os.path.dirname(os.path.dirname(script_folder)))
data_subfolder = 'Input_Data'
location = 'Heino'
data_output = 'outputRaster'
root_folder = os.path.join(data_folder,data_subfolder,location,data_output)
print(root_folder)
# sys.exit()
os.chdir(root_folder)

def resample_res(dataset, xres, yres, resampling=Resampling.cubic_spline):
    scale_factor_x = dataset.res[0]/xres
    scale_factor_y = dataset.res[1]/yres

    profile = dataset.profile.copy()
    # resample data to target shape
    data = dataset.read(
        out_shape=(
            dataset.count,
            int(dataset.height * scale_factor_y),
            int(dataset.width * scale_factor_x)
        ),
        resampling=resampling
    )

    # scale image transform
    transform = dataset.transform * dataset.transform.scale(
        (1 / scale_factor_x),
        (1 / scale_factor_y)
    )
    profile.update({"height": data.shape[-2],
                    "width": data.shape[-1],
                   "transform": transform,
                   "crs": pycrs.parse.from_epsg_code(epsg_code).to_proj4()
                   })

    print("Function resample_res finished")
    return data, profile


def resample_scale(dataset, scale, resampling=Resampling.cubic_spline):
    """ Resample a raster
        multiply the pixel size by the scale factor
        divide the dimensions by the scale factor
        i.e
        given a pixel size of 250m, dimensions of (1024, 1024) and a scale of 2,
        the resampled raster would have an output pixel size of 500m and dimensions of (512, 512)
        given a pixel size of 250m, dimensions of (1024, 1024) and a scale of 0.5,
        the resampled raster would have an output pixel size of 125m and dimensions of (2048, 2048)
        returns a DatasetReader instance from either a filesystem raster or MemoryFile (if out_path is None)
    """
    # rescale the metadata
    # scale image transform
    t = dataset.transform
    transform = t * t.scale((scale), (scale))
    height = int(dataset.height / scale)
    width = int(dataset.width / scale)

    profile = dataset.profile.copy()
    profile.update(transform=transform, driver='GTiff', height=height, width=width)

    data = dataset.read(
            out_shape=(dataset.count, height, width),
            resampling=resampling,
        )

    # print("Function resample_scale finished")
    return data, profile


@contextmanager
def write_mem_raster(data, **profile):
    with MemoryFile() as memfile:
        with memfile.open(**profile) as dataset:  # Open as DatasetWriter
            dataset.write(data)

        with memfile.open() as dataset:  # Reopen as DatasetReader
            yield dataset  # Note yield not return


@contextmanager
def write_raster(path, data, **profile):

    with rasterio.open(path, 'w', **profile) as dataset:  # Open as DatasetWriter
        dataset.write(data)

    with rasterio.open(path) as dataset:  # Reopen as DatasetReader
        yield dataset


if __name__ == "__main__":
    input_raster = 'base_AHN_05m_dsm_1200m_InputDEM.tif'
    raster_file = os.path.join(root_folder,input_raster)

    # output_res = f"{base_name}_res.tif"
    raster =  rasterio.open(raster_file)
    param = raster.transform
    epsg_code = int(raster.crs.data['init'][5:])
    crs = rasterio.crs.CRS({"init": f"epsg:{epsg_code}"})

    xres, yres = param[0], -param[4]

    scale = 1.005
    with rasterio.open(raster_file) as dataset:
        data_res, profile_res = resample_res(dataset, xres/scale, yres/scale)
    output_res = raster_file.replace("base_", "" )
    with rasterio.open(output_res, "w", **profile_res) as dataset:
        dataset.crs = crs
        dataset.write(data_res)

    scale = 2
    with rasterio.open(raster_file) as dataset:
        data_scale, profile_scale = resample_scale(dataset, scale)
    output_scale = raster_file.replace("05", "1" ).replace("base_", "" )
    with rasterio.open(output_scale, "w", **profile_scale) as dataset:
        dataset.crs = crs
        dataset.write(data_scale)
print("script finishes")