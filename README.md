# Yanv
Yet Another Netcdf Viewer

Yanv is a netcdf viewer implemented via python that will launch a server providing web access to visualizations for one or 
more netcdf files via commandline and possibly simple application (long term goal).

Basic usage is:

```shell
$ python -m yanv
Access Yanv from http://0.0.0.0:10324/
======== Running on http://0.0.0.0:10324 ========
(Press CTRL+C to quit)

```
<p>
    <img src="YanvScreen.png" alt="A screenshot of Yanv in use"/>
</p>

## What This is Not

This is not meant to be a web application. Steps are in place to prevent this from running across a network. This application investigates and lets you see items and structures on
your filesystem. Allowing external access will reveal the file structure of your machine and is highly discouraged. 
$${\color{red}\textbf{Run} \space \textbf{on} \space \textbf{a} \space \textbf{network} \space \textbf{at} \space \textbf{your} \space \textbf{own} \space \textbf{risk}}$$

## Features

The web view offers 4 major functions:

- [x] Open and view multiple files at a time
- [x] Explore dimension data
- [x] Explore variable data
- [ ] Create scatter plots for vector data

## Long term goals

* Double-click to launch
* Map plotting
* Data querying
* Data transformations
* Simple data manipulation (such as joining two files)
* Other data types, such as CSV (to provide another avenue for data manipulation, such as providing further metadata 
for variables)

## Important Dependencies

This relies on:

- Plotly
- Xarray
- websockets
- aiohttp
- jQuery
