import numpy as np
import netCDF4 as nc
import geokit as gk
from geokit import Location, LocationSet, Extent
import ogr, osr
import pandas as pd
from collections import namedtuple, OrderedDict
from scipy.interpolate import splrep, splev
from scipy.stats import norm
from glob import glob
import re
from os.path import join, dirname, basename, splitext
import types
from types import FunctionType
from datetime import datetime as dt

# making an error
class ResError(Exception): pass # this just creates an error that we can use

# Make some type-helpers
LATLONSRS = gk.srs.EPSG4326

def extentFromFile(*args, **kwargs): return gk.Extent.fromVector(*args, **kwargs)
BoundsNT = namedtuple("Bounds","lonMin latMin lonMax latMax")
class Bounds(BoundsNT):
    #def __init__(s, lonMin, latMin, lonMax, latMax):
    #    BoundsNT.__init__(s, lonMin, latMin, lonMax, latMax)
    def __str__(s):
        out =  "Lat: %.4f  -  %.4f\n"%(s.latMin, s.latMax)
        out += "Lon: %.4f  -  %.4f"%(s.lonMin, s.lonMax)
        return out

## STAN
def storeTimeseriesAsNc(output, timedata, varmeta={}, keydata=None, keydatameta={}, timeunit="minutes since 1900-01-01 00:00:00"):
    """
    Create a netCDF4 file from a set of time series arrays

    Inputs:
        output : str -- An output file path

        timedata
            Pandas-DataFrame -- The time-series data to write
                * Must be time-indexed
                * Will be written with the variable name "var"
            { <varname>:Pandas-DataFrame, } -- A dictionary of variable names to DataFrames
                * All variables will be written to the output file
                * All DataFrames must share the same index and columns

        varmeta : dict -- Optional meta data to apply to the time-series variables
            * If time data is a DataFrame, the varmeta dictionary will be applied directly to the "var" variable
            * Otherwise varmeta needs to be a dictionary of dictionaries
            * Example:
                varmeta = { "power_output":{ "name":"The power output of each turbine",
                                             "units":"kWh", } }
        
        keydata : Pandas-DataFrame -- Optional data to save for each key
            * Must be a pandas DataFrame whose index matches the columns in the timedata DataFrames
            * Could be, for example, the hub height of each turbine or a the model

        keydatameta : dict -- Optional meta data to apply to the key data variables
            * Must be a dictionary of dictionaries

        timeunit : str -- The time unit to use when compressing the time index

    """
    # correct the time data
    if isinstance(timedata, pd.DataFrame):
        timedata = {"var":timedata, }
        varmeta = {"var":varmeta, }

    # Check the input data, just in case
    cols = list(timedata.keys())
    if len(cols)>1:
        for i in range(1,len(cols)):
            if not (timedata[cols[i]].columns == timedata[cols[0]].columns).all():
                raise RuntimeError("timedata columns do not match eachother")

            if not (timedata[cols[i]].index == timedata[cols[0]].index).all():
                raise RuntimeError("timedata indicies do not match eachother")

    # Make an output file
    ds = nc.Dataset(output, mode="w")
    try:
        # Make the dimensions
        ds.createDimension("time", size=timedata[cols[0]].shape[0])
        ds.createDimension("key", size=timedata[cols[0]].shape[1])

        # Make the time variable
        timeV = ds.createVariable("time", "u4", dimensions=("time",), contiguous=True)
        timeV.units = timeunit

        times = timedata[cols[0]].index
        if timedata[cols[0]].index[0].tz is None:
            timeV.tz = "unknown"
        else:
            timeV.tz = timedata[cols[0]].index[0].tzname()
            times = times.tz_localize(None)

        timeV[:] = nc.date2num(times.to_pydatetime(), timeunit)

        # Make the data variables
        for varN, tab in timedata.items():
            var = ds.createVariable(varN, tab.iloc[0,0].dtype, dimensions=("time", "key",), contiguous=True)
            if varN in varmeta and len(varmeta[varN])>0:
                var.setncatts(varmeta[varN])
            var[:] = tab.values

        # Make some key variables, maybe
        if not keydata is None:
            # test if the keys are in the right order
            if not (timedata[cols[0]].columns == keydata.index).all():
                raise RuntimeError("timedata columns do not match keydata indecies")

            for col in keydata.columns:
                dtype = str if keydata[col].dtype == np.dtype("O") else keydata[col].dtype
                var = ds.createVariable(col, dtype, dimensions=( "key",), contiguous=True)
                if col in keydatameta and len(keydatameta[col])>0:
                    var.setncatts(keydatameta[col])
                
                var[:] = keydata[col].values if not dtype is str else keydata[col].values.astype(np.str)
        ds.close()
        
    except Exception as e:
        ds.close() # make sure the ds is closed!
        raise e

    # All done!
    return

def simpleLCOE(capex, meanProduction, opexPerCapex=0.02, lifetime=20, discountRate=0.08):
    r = discountRate
    N = lifetime
    return capex * ( r /(1-np.power(1+r,-N)) + opexPerCapex ) / (meanProduction)

def lcoe( expenditures, productions, discountRate=0.08 ):
    """Provides a raw computation of LCOE. Requires input time-series for annual expenditures and annual productions"""
    # Initialize variables
    exp = np.array(expenditures)
    pro = np.array(productions)
    if not exp.size==pro.size: raise ResError("expenditures length does not match productions length")

    yr = np.arange(exp.size)
    if isinstance(r,float):
        r = np.zeros(exp.size)+discountRate
    else:
        r = np.array(r)

    # Do summation and return
    lcoe = (exp/np.power(1+r, yr)).sum() / (pro/np.power(1+r, yr)).sum()

    return lcoe

def removeLeapDay(x):
    if isinstance(x, pd.Series) or isinstance(s, pd.DataFrame):
        times = x.index
        sel = np.logical_and((times.day==29), (times.month==2))
        if isinstance(x, pd.Series): return x[~sel]
        else: return x.loc[~sel]

    elif isinstance(x, np.ndarray) and x.shape[0] == 8784:
        times = pd.date_range("01-01-2000 00:00:00", "12-31-2000 23:00:00", freq="H")
        sel = np.logical_and((times.day==29), (times.month==2))
        if len(x.shape)==1: return x[~sel]
        else: return x[~sel,:]

    else:
        return removeLeapDay(np.array(x))

def linearTransition(x, start, stop, invert=False):
    tmp = np.zeros(x.shape)

    s = x<=start
    tmp[s] = 0

    s = (x>start)&(x<=stop)
    tmp[s] = (x[s]-start)/(stop-start)

    s = x>stop
    tmp[s]=1

    if invert: return 1-tmp
    else: return tmp

_SGF = namedtuple("RESGeneration", "capacity capex generation regionName variable capacityUnit capexUnit generationUnit")
def parseRESGenerationFile(f, capacity, generationName="generation"):
    ds = nc.Dataset(f)
    try:
        timeIndex = nc.num2date(ds["time"][:], ds["time"].units)
        CAP = ds["total_capacity"][:]
        try:
            COST = ds["total_cost"][:]
        except:
            COST = None

        try:
            capacity = list(capacity)
        except:
            capacity = [capacity,]

        def atCapacity(cap):
            s = np.argmin(np.abs(CAP-cap))

            if CAP[s] == cap: 
                gen = ds["generation"][:,s]
                if not COST is None: capex = ds["total_cost"][s]
                else: capex = None
            else:
                if CAP[s] > cap: low, high = s-1,s
                else: low, high = s,s+1

                raw = ds["generation"][:,[low, high]]

                factor = (cap-CAP[low])/(CAP[high]-CAP[low])
                
                gen = raw[:,0]*(1-factor) + raw[:,1]*factor

                if not COST is None: 
                    lowCost, highCost = ds["total_cost"][[low,high]]
                    capex = lowCost*(1-factor) + highCost*factor
                else: capex = None
            return gen, capex

        generations = pd.DataFrame(index=timeIndex,)
        capexes = []
        for cap in capacity:
            gen,capex = atCapacity(cap)
            generations[cap] = gen
            capexes.append(capex)

    except Exception as e:
        ds.close()
        raise e

    return _SGF(capacity=np.array(capacity), capex=np.array(capexes), generation=generations, 
                regionName=ds["generation"].region, variable=ds["generation"].technology,
                capacityUnit=ds["total_capacity"].unit, capexUnit=None if COST is None else ds["total_cost"].unit, 
                generationUnit=ds["generation"].unit)