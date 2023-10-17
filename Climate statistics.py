'''
@author: wangjian
@descr：Calculate climate statistics for each county
'''

import netCDF4 as nc
import xarray as xr
import pandas as pd
from shapely.geometry import Polygon
from shapely.geometry import Point
import geopandas as gpd
import glob
import csv
import time
import os
os.chdir(r'E:\Essay\climate & yield & quality\prediction-yield-quality\Data')
global var, climate


def progress_bar(finish_tasks_number, tasks_number, complete_time):
    """
    进度条

    :param finish_tasks_number: int,
    :param tasks_number: int,
    :param complete_time: float,
    :return:
    """

    percentage = round(finish_tasks_number / tasks_number * 100)
    finished_label = "▓" * (percentage // 2)
    unfinished_label = "-" * (100 - percentage)
    arrow = "->"
    if not finished_label or not unfinished_label:
        arrow = ""
    print("\r{}% [{}{}{}] {:.2f}s".format(percentage, finished_label, arrow, unfinished_label, complete_time), end="")


def nc_to_csv(file):
    filename = os.path.splitext(os.path.basename(file))[0]
    ds = xr.open_dataset(file)
    # Derived time series
    df = ds.to_dataframe().reset_index()
    print('-------------Loading-------------')
    df.to_csv('./' + "climate" + '/' + filename + '.csv', index=False)
    open_day = '1990-01'
    close_day = '2019-01'
    df['time'] = pd.to_datetime(df['time'])
    df['time_bounds'] = df['time'].dt.strftime('%Y-%m')
    con1=df['time_bounds'] >= open_day
    con2=df['time_bounds'] < close_day
    df2 = df[con1&con2]
    df2.to_csv('./climate/' + filename + '-1.csv', index=False)


def calculate_average(file, climate):  # file: Point file of geographical boundaries of counties
    # Read irregular region boundary coordinate points
    # print(file)
    boundary_df = pd.read_csv(file)
    boundary_coords = [(row['lon'], row['lat']) for _, row in boundary_df.iterrows()]
    # print(boundary_coords)

    # Convert points into Polygon objects
    boundary_poly = Polygon(boundary_coords)

    # The latitude and longitude information of the observation station is converted into a Point object
    geometry = [Point(xy) for xy in zip(climate['lon'], climate['lat'])]

    # The latitude and longitude information of the observatory and the meteorological data are merged into a GeoDataframe
    crs = {'init': 'epsg:4326'}
    gdf = gpd.GeoDataFrame(climate, crs=crs, geometry=geometry)
    # print(gdf)

    # The intersection operation is used to filter the stations located within the irregular region
    gdf_subset = gdf[gdf.geometry.intersects(boundary_poly)]
    # print(list(gdf_subset))
    # print('-----time bounds-------')
    # print(gdf_subset['time_bounds'])

    # Calculation mean
    grounp = gdf_subset.groupby(['time_bounds']).mean()
    # print(grounp)
    dirStr, ext = os.path.splitext(file)
    fname = dirStr.split("\\")[-1]
    grounp.to_csv('./climate/' + var + '/' + fname + '.csv', index=True)


def combine_csv():
    listName = []
    csv_list = glob.glob('E:/Essay/climate & yield & quality/prediction-yield-quality/Data/climate/wind/*.csv')
    for file in csv_list:
        dirStr, ext = os.path.splitext(file)
        name = dirStr.split("\\")[-1]
        listName.append(name)
    print(listName)
    readList = []
    titleList = ["date", 'lat',	'lon', 'wind', "region"]  # file header
    os.chdir('E:/Essay/climate & yield & quality/prediction-yield-quality/Data/climate/wind' )
    for i in listName:
        # i is file name
        #############Read the contents of multiple csv files###################
        with open('{}.csv'.format(i), 'r', newline="", encoding="GB18030") as read_csvfile:
            readcsv_all = csv.reader(read_csvfile)
            next(read_csvfile)  # Skip the first line "title"
            for line in readcsv_all:
                line.append(i)  # Add "File name" as a new column
                readList.append(line)

                ############Writing to a file##############################
    with open('./wind_alldata.csv', 'a+', newline="", encoding="GB18030") as f:
        csv_write = csv.writer(f)
        csv_write.writerow(titleList)  # Write the file title
        for line in readList:
            csv_write.writerow(line)


if __name__ == '__main__':
    # step 1
    # file_list = glob.glob(r'E:\Essay\data\Data_forcing_01mo_010deg\*.nc')
    # for file in file_list:
    #     nc_to_csv(file)

    # step 2
    # start = time.perf_counter()
    # vars = ['prec', 'pres', 'shum', 'srad', 'temp', 'wind']
    # fs = glob.glob(r'E:\Essay\climate & yield & quality\prediction-yield-quality\Data\county\*.csv')
    # for var in vars:
    # # var = 'lrad'
    #     filename = './climate/' + var + '_CMFD_V0106_B-01_01mo_010deg_197901-201812-XJ-1.csv'
    #     climate = pd.read_csv(filename)
    #     i = 0
    #     for f in fs:
    #         i += 1
    #         duration = time.perf_counter() - start
    #         progress_bar(i, 73, duration)
    #         time.sleep(0.05)
    #         calculate_average(f, climate)
    combine_csv()
