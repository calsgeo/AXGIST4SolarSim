r.import input=**path to input File** output=**Name of layer in GRASS**
<code>

    Data to import:
    - DSM
    - Resampled raster files of the Linke Turbidity
</code>
g.region raster=**Name of DSM raster file**

r.slope.aspect elevation=**Name of DSM raster layer in GRASS** slope=**Name of output slope layer** aspect=**Name of output aspect layer**
<code>

    Slope layer name should follow the structure: slope_locationName_Resolution
    Aspect layer name should follow the structure: aspect_locationName_Resolution
</code>
r.horizon -d --overwrite elevation=**Name DSM layer** direction=0 step=1 output=**Prefix output layer**
<code>

    The horizon layer name should follow the structure: horizon_locationName_Resolution
</code>