import csv
import numpy as np
import pandas as pd
import json
from pathlib import Path
import os
import sys
from datetime import datetime, timedelta
from geodecoder import get_location

dfs = []
measurements = {}
def parse_data(file_path,dest_path,filename):
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
        #saveData(filename,dest_path,**data)
        return data

    except IOError as e:
        print(e)

def get_data(**kwargs):

    site = kwargs['site']
    date = kwargs['data'].pop(0)
    rssi = kwargs['data'][0].split(',')
    lat = kwargs['lat-long'][0]
    lon = kwargs['lat-long'][1]
    time = rssi.pop(0)

    dt = date + " " +  time
    date_time = datetime.strptime(dt, "%Y-%m-%d %H:%M:%S")
    try:
        rssi = np.array(rssi, dtype = np.float64)
        base_freq = np.float16(kwargs['freq_start'])
        step = float(kwargs['step'])/1000.0 # Khz
        step = round(step,2)
        index_freqs = np.arange(base_freq,base_freq + (step * len(rssi) ),step)
        index_freqs = np.round(index_freqs, decimals=2)
        time_stamp = pd.Timestamp(date_time)
        rssi = np.round(rssi, decimals=1)
    except:
        return None

    return [site, time_stamp, rssi, base_freq, step, (float(lat), float(lon)), date_time]

def save_data(fname,dest_path,**kwargs):
    
    try:
        try:
            mul_index =zip ( *[ts, index_freq] )
            tups = list(mul_index)
            index = pd.MultiIndex.from_tuples(tups, names=["timestamp","FREQ"])
            df = pd.DataFrame(data = rssi, index=index, columns=["RSSI"])
            dfs.append(df)
            # json_record = df.to_json(orient="columns")
            # parsed = json.loads(json_record)
            # json_s = json.dumps(parsed, indent=4)
            # print(json_s)

            context = {
                    "bucket":"spectrum_test",
                    "org": "ASTI",
                    "token": "3r3tKvsRrs934WQ4LXQ_HmtFhNy01gKVbpvACShUxw5wbS5N4TKAZBa7gFiv8laJEyhC9BS4Op4gdcfrkGT_Eg==",
                    "url": "http://localhost:8086"
                }
            #pushData(df, **context)
            #readData(**context)
        except ValueError as e:
            print(e)
            
    except ValueError as e:
        print("Skipping existing file..",fname)

def push_data(data, **kwargs):

    client = influxdb_client.InfluxDBClient(
            url = kwargs["url"],
            token = kwargs["token"],
            org = kwargs["org"]
    )
    bucket = kwargs["bucket"]
    write_api = client.write_api(write_options=WriteOptions(batch_size=500,
                                                     flush_interval=10_000,
                                                     jitter_interval=2_000,
                                                     retry_interval=5_000,
                                                     max_retries=5,
                                                     max_retry_delay=30_000,
                                                     exponential_base=2))
    write_api = client.write_api(write_options=SYNCHRONOUS)
    write_api.write(bucket,record=data, data_frame_measurement_name='spectrum',
             data_frame_tag_columns=['FREQ'])


    write_api.__del__()
    client.__del__()

def read_data(**kwargs):
    client = influxdb_client.InfluxDBClient(
            url = kwargs["url"],
            token = kwargs["token"],
            org = kwargs["org"]
    )

    query_api = client.query_api()
    # query = ' from(bucket:"spectrum_test")\
    #         |> range(start: -10m)\
    #      |> filter(fn:(r) => r._measurement == "spectrum")\
    #      |> filter(fn:(r) => r._field == "RSSI" )'
    query = 'from(bucket:"spectrum_test") \
    |> range(start: -1h) \
    |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value") \
    |> keep(columns: ["FREQ","RSSI"])'

    result = client.query_api().query_data_frame(org = kwargs["org"], query = query)
    print(result.to_string())
    client.__del__()
    
     
if __name__ == "__main__":
    CWD = Path.cwd() 
    HOME_DIR = CWD.home()
    # DATA_FOLDER = HOME_DIR.joinpath("ED_Data")
    DATA_FOLDER = CWD.joinpath("brocoli_data/ED_Data")
    DEST_PATH = HOME_DIR.joinpath("server","data.hdf5")
    for root, dirs, files in os.walk(str(DATA_FOLDER)):
        for filename in files:
            if filename.endswith(".csv"):
                # parseData(str(DATA_FOLDER.joinpath(filename)),str(DEST_PATH),filename)
                ret = parse_data(DATA_FOLDER.joinpath(filename),str(DEST_PATH),filename)
                data = get_data(**ret)
                try:
                    key = data.pop()
                    key = key.strftime("%Y-%m-%d")
                    key = str(key)
                    measurements[key] = measurements.get(key, []) + [data]
                except:
                    pass
    #['2020-09-28']
    dfs = []
    for val in measurements.values():
        df = pd.DataFrame(data= val, columns=['SITE', 'TIMESTAMP', 'RSSI', 'START', 'STEP', 
            'geom'])
        if df.empty:
            continue
        df["address"] = df['geom'].apply(get_location)
        dfs.append(df)
    
    print(pd.concat(dfs,ignore_index=True, sort=False))
    # frames = dfs
    # new_df = pd.concat(frames)
    # print(new_df.groupby('FREQ').get_group(400))

