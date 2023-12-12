import geopandas as gpd
import rasterio
from rasterio.plot import show
import matplotlib.pyplot as plt
import numpy as np
import zipfile
import os
#from scipy.interpolate import griddata
from scipy.interpolate import RectBivariateSpline
import warnings
import time
import sarquicklook

#datafile = "SanJoaquin/S1A_IW_GRDH_1SDV_20230307T140803_20230307T140828_047539_05B55C_DD0A.zip"

#datafile = "SanJoaquin/S1A_IW_SLC__1SDV_20230319T140802_20230319T140829_047714_05BB47_82FC.zip"

#datafile = "SanJoaquin/S1A_IW_GRDH_1SDV_20230319T140803_20230319T140828_047714_05BB47_158D.zip"

#datafile = "Sacramento/S1A_IW_GRDH_1SDV_20221220T020007_20221220T020032_046409_058F3D_8966.zip"

# USING
#datafile = "Sacramento/S1A_IW_GRDH_1SDV_20230101T020006_20230101T020031_046584_059528_327A.zip"

# USING
#datafile = "Sacramento/S1A_IW_GRDH_1SDV_20230113T020005_20230113T020030_046759_059B08_127C.zip"

datafile = "Sacramento/S1A_IW_SLC__1SDV_20230113T020004_20230113T020031_046759_059B08_6327.zip"

flg_saving = False #True #False

dir = "/".join(datafile.split("/")[0:-1])+"/"
if dir =="/":
    dir = "./"

# zipファイルに含まれているテキストファイルの読み込み
lst = []
with zipfile.ZipFile(datafile) as myzip:
    for ff in myzip.namelist(): #zipファイルに含まれているファイルのリストを返す
        path, ext = os.path.splitext(ff)
        if ext == ".tiff":
            lst.append(ff)
#print(lst)
for ii, ff in enumerate(lst):
    print("{}: {}".format(ii,ff))
print("choose > ", end="")
choice = int(input())
loadFile = lst[choice]
data = rasterio.open("zip+file://"+datafile+"!"+loadFile)
print(data)
print("W x H: {0} x {1}".format(data.width, data.height))
print("Bounds: {0}".format(data.bounds))
print("CRS: {0}".format(data.crs))
gcps, gcp_crs = data.gcps
print("GCP_CRS: ", gcp_crs) # https://epsg.io/4326
print("GCPS: ", len(gcps) , " ?= ", data.width * data.height)
print(gcps[-1])
print(gcps[-1].row, gcps[-1].col )

start_time = time.process_time()

gcp_idx = []
gcp_idy = []
for gg in gcps:
    if gg.row not in gcp_idx:
        gcp_idx.append(gg.row)
    if gg.col not in gcp_idy:
        gcp_idy.append(gg.col)

gcp_idx.sort()
gcp_idy.sort()
if len(gcp_idx) * len(gcp_idy) != len(gcps):
    raise ValueError("GCP grid is not distributed homogeneously.")

gcp_shp = (len(gcp_idx),len(gcp_idy))
print(gcp_shp)
gcpxx = np.zeros(gcp_shp)
gcpyy = np.zeros(gcp_shp)
gcpzz = np.zeros(gcp_shp)
for gg in gcps:
    idx = gcp_idx.index(gg.row)
    idy = gcp_idy.index(gg.col)
    gcpxx[idx][idy] = gg.x
    gcpyy[idx][idy] = gg.y
    gcpzz[idx][idy] = gg.z
# San Joaquin
#lons = [-121.6, -120.9]
#lats = [37.5, 38.1]

# Sacramento
lons = [-122.15, -121.25]
lats = [38.2, 38.8]

# North part of the Bay
#lons = [-122.6, -122.2]
#lats = [37.9, 38.2]

band = data.read(1)
print("band shape: ", band.shape)
idx = np.arange(band.shape[0])
idy = np.arange(band.shape[1])
idyy, idxx = np.meshgrid(idy, idx)
print(np.shape(idxx))

print("Interpolating Coordinates")
lap_time1 = time.process_time()
print("1/3")
gcpInterpX = RectBivariateSpline(gcp_idx, gcp_idy, gcpxx)
xx = gcpInterpX(idx, idy)
lap_time2 = time.process_time()
print(f"{lap_time2-lap_time1}")
print("2/3")
gcpInterpY = RectBivariateSpline(gcp_idx, gcp_idy, gcpyy)
yy = gcpInterpY(idx, idy)
lap_time3 = time.process_time()
print(f"{lap_time3-lap_time2}")
print("3/3")
gcpInterpZ = RectBivariateSpline(gcp_idx, gcp_idy, gcpzz)
zz = gcpInterpZ(idx, idy)
end_time = time.process_time()
print(f"{lap_time3-end_time}")
#print("coord shape: ", xx.shape)

print("Preparation Process Time: {0}".format(end_time-start_time)) #=> 114.75

sarquicklook.quicklook(xx,yy,band)

msk = (lons[0] <= xx) * (xx <= lons[1]) * (lats[0] <= yy) * (yy <= lats[1])

trim_msk_x = np.any(msk, axis=0)
trim_msk_y = np.any(msk, axis=1)

if (np.sum(trim_msk_x)==0) or (np.sum(trim_msk_y)==0):
    print("trim_msk_x shape: ", trim_msk_x.shape, "| TRUEs: ", np.sum(trim_msk_x))
    print("trim_msk_y shape: ", trim_msk_y.shape, "| TRUEs: ", np.sum(trim_msk_y))
    print("trim middle shape: ", xx[trim_msk_y,:].shape)
    raise ValueError("No data chosen: bad bounding condition.")

xx_trim = xx[trim_msk_y,:][:,trim_msk_x]
yy_trim = yy[trim_msk_y,:][:,trim_msk_x]
zz_trim = zz[trim_msk_y,:][:,trim_msk_x]
band_trim = band[trim_msk_y,:][:,trim_msk_x]

print("trimed shape: ", xx_trim.shape)

#watermasked = np.ma.masked_where(band_trim < 17, band_trim)

sarquicklook.quicklook(xx_trim, yy_trim, band_trim, dd=10, xlim=lons, ylim=lats)


if flg_saving:
    saveFile = dir+loadFile.split("/")[-1].split(".")[0]+"_lon{0}_{1}_lat{2}_{3}{4}.npz".format(lons[0], lons[1], lats[0], lats[1],"_2")
    print("Saving to: ", saveFile)
    np.savez(saveFile, data=band_trim, lon=xx_trim, lat=yy_trim, alt=zz_trim)
