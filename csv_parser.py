import csv
import numpy as np
import pandas as pd
import json
import os
import sys
from datetime import datetime
import h5py

def parseData(file_path):
    contents = None
    try:
        with open(file_path, newline='') as fp:
            site, freq_start, step, lat, lon, data = csv.reader(fp,delimiter=' ')
        data = {
                "site": site[0],
                "freq_start": freq_start[0],
                "step": step[0],
                "lat-long": (np.float64(lat[0]),np.float64(lon[0])),
                "data": data
                }
        saveData(**data)
    except IOError as e:
        print(e)

def saveData(**kwargs):
    site = kwargs['site']
    date = kwargs['data'].pop(0)
    rssi = kwargs['data'][0].split(',')
    lat = kwargs['lat-long'][0]
    lon = kwargs['lat-long'][1]
    time = rssi.pop(0)
    rssi = np.array(rssi,dtype=np.float32)
    base_freq = np.float16(kwargs['freq_start'])
    step = float(kwargs['step']/1000.0)
    step = np.float16(step)
    
    with h5py.File('data.hdf5','a') as h5file:
        group = os.path.join(site,date,time)
        try:
            g = h5file.create_group(group)
        except ValueError as e:
            print(e)
            g = h5file[group]
        try:
            g.create_dataset("DATA",data=rssi)
            g.attrs["lat"] = lat
            g.attrs["lon"] = lon
            g.attrs["base_freq"] = base_freq
            g.attrs["step"] = step
        except:
            pass

def printGroup(name):
    if 'DATA' in name:
        print(name)

def readData(group):
    try:
        with h5py.File('data.hdf5','r') as h5file:
            g  = h5file[group]
            print(g['DATA'][()])
            for attr in g.attrs:
                print(g.attrs[attr])
    except IOError as e:
        print(e)
data = []
def getData(group):
    if "DATA" in group:
        data.append(group)
    
def loopData():
    try:
        with h5py.File('/home/wrt/server/data.hdf5','r') as h5file:
            h5file.visit(getData)
    except IOError as e:
        print(e)

def readDF(group):
    try:
        with h5py.File('/home/wrt/server/data.hdf5','r') as h5file:
            group = h5file[group]
            step = group.attrs['step']
            step = float(step)
            step = round(step,2)
            base_freq = float(group.attrs['base_freq'])
            np_arr = group.get('DATA')[()]
            index_freq = np.arange(base_freq,base_freq + (step * len(np_arr) ),step)
            index_freq = index_freq
            df = pd.DataFrame(np_arr,index=index_freq)
            df.to_csv(sys.stdout,header=['Power'],index_label="Frequency",float_format="%.2f")
                    
    except IOError as e:
        print(e)

def searchData(location,date,time):
    #d = datetime.strptime("2020-05-27 09:29:57","%Y-%m-%d %H:%M:%S")
    date_time = "{} {}".format(date,time)
    record_location = location
    record_datetime = datetime.strptime(date-time,"%Y-%m-%d %H:%M:%S")

def searchByDate(date):
    loc = "B2M_ASTI_Rooftop2"
    search_path = os.path.join(loc,date)
    try:
        with h5py.File('data.hdf5','r') as h5file:
            h5file.visit(getData)
    except IOError as e:
        print(e)

def getPathByDate(dataset,date, hour):
    paths = []
    for path in dataset:
        time =  path.split('/')[2]
        time_file = datetime.strptime(time,'%H:%M:%S')
        date_file = path.split('/')[1]
        date_file = datetime.strptime(date_file,'%Y-%m-%d')
        try:
            hour = int(hour)
        except:
            pass
        if date == date_file and time_file.hour ==  hour:
            paths.append(time[3:])
    return paths



if __name__ == "__main__":
    req = sys.stdin.readlines()
    req = req[0]
    serverdata = json.loads(req)
    sites = []
    if serverdata["req"] == "updateboot":
        loopData()
        last = data[len(data)-1]
        last = last.split("/")
        #searchByDate(date)
        files_from_date = getPathByDate(data,last[1])
        print(",".join(files_from_date))
    if serverdata["req"] == "update":
        try:
            loopData()
            date = serverdata["date"].strip()
            date = datetime.strptime(date,"%Y-%m-%d")
            #date = date.strftime("%Y-%m-%d")
            hour = serverdata["hour"].strip()
            files_from_date = getPathByDate(data,date,hour)
            path_length = len(files_from_date)
            if path_length > 0:
                if path_length == 1: 
                    print(files_from_date[0])
                else:
                    print(",".join(files_from_date))
            else:
                print(0)
        except:
            print(0)

    if serverdata["req"] == "select":
        try:
            time = serverdata["time"].strip()
            date = serverdata["date"].strip()
            loc = "NRTDC"
            full_path = os.path.join(loc,date,time)
            readDF(full_path)
        except:
            print(0)


        
