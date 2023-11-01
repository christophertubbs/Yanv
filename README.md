# Yanv
Yet Another Netcdf Viewer

Yanv is a netcdf viewer implemented via python that will launch a server providing web access to visualizations for one or 
more netcdf files via commandline and possibly simple application (long term goal).

Basic use should look like:

```shell
$ python3 -m yanv path/to/file1.nc path/to/fileN.nc

The following netcdf files are viewable at http://127.0.0.1:9234
    path/to/file1.nc
    path/to/file2.nc
```

The port will be randomized if not given via cli parameters.

The command will also invoke the `webbrowser` library to immediately launch the announced viewable page in the default browser.

## Features

The web view offers 4 major functions:

1. Paginated Grids for each file
2. The ability to perform basic queries on each file
3. The ability to join your files and create intermediate data such as new columns
4. The ability to generate different types of interactive graphs

## Long term goals

"Double click to launch" app functionality along with being able to select/load your datasets via the web view are 
desirable in the long term but out of scope until the core functions are complete.

## Important Dependencies

This will rely on:

- Plotly
- Pandas
- Xarray
- websockets
- aiohttp
- jQuery
