import netCDF4 as nc
import numpy as np
from os.path import join, dirname
import geokit as gk

from reskit.weather.windutil import *
from reskit.weather import MerraSource
from reskit.util import ResError, Location

## setup some common inputs
loc = Location(lat=50.105, lon=6.005)
locInAachen = Location(lat=50.763, lon=6.202)
locOutsideAachen = Location(lat=51.255, lon=5.605)
locs = [loc, locOutsideAachen, Location(lat=50.605, lon=6.605)]

windspeed = np.arange(30)
windspeeds = np.column_stack( [windspeed, windspeed+0.3333, windspeed+0.6667] )

try:
    wsSrc = MerraSource(join("data","merra-like.nc4"))
    wsSrc.loadWindSpeed()
except Exception as e:
    print("Loading MerraSource failed somewhere. Investigate by running the MerraSource unit tests...")
    raise e


## Make testing functions!!
def test_adjustLraToGwa():
    print("testing adjustLraToGwa...")
    lraSource = join(dirname(__file__), "..", "data","merra_average_windspeed_50m.tif")

    # Use a defined long run average value with a single location and windspeed set
    wsOut = adjustLraToGwa( windspeed, targetLoc=locInAachen, 
                            gwa=join("data","gwa50-like.tif"), 
                            longRunAverage=5.0)
    
    if  not (abs(wsOut.sum()-389.442808628) < 1e-6 and\
             abs(wsOut.std()-7.74896420133) < 1e-6): 
            raise RuntimeError("  Single loc, given long run average: Fail")
    else: print("  Single loc, given long run average: Success")

    # Use defined long run average values with multiple location and windspeed sets
    wsOut = adjustLraToGwa( windspeeds, targetLoc=locs, 
                            gwa=join("data","gwa50-like.tif"), 
                            longRunAverage=[5.0,4.0,3.0])
    
    if  not (abs(wsOut.sum()-1700.08787573) < 1e-6 and\
             abs(wsOut.std()-11.9730191575) < 1e-6): 
            raise RuntimeError("  Multi loc, given long run average: Fail")
    else: print("  Multi loc, given long run average: Success")

    # Use a precalculated long run average source with a single locations
    wsOut = adjustLraToGwa( windspeed, targetLoc=locInAachen, 
                            gwa=join("data","gwa50-like.tif"), 
                            longRunAverage=lraSource)
    
    if  not (abs(wsOut.sum()-288.562361769) < 1e-6 and\
             abs(wsOut.std()-5.74168879655) < 1e-6): 
            raise RuntimeError("  Single loc, long run average source: Fail")
    else: print("  Single loc, long run average source: Success")

    # Use a precalculated long run average source with multiple location and windspeed sets
    wsOut = adjustLraToGwa( windspeeds, targetLoc=locs, 
                            gwa=join("data","gwa50-like.tif"), 
                            longRunAverage=lraSource)

    if  not (abs(wsOut.sum()-984.056285175) < 1e-6 and\
             abs(wsOut.std()-6.38348058372) < 1e-6): 
            raise RuntimeError("  Multi loc, given long run average: Fail")
    else: print("  Multi loc, given long run average: Success")

    # Use a MerraSoure with a single locations
    wsOut = adjustLraToGwa( wsSrc, targetLoc=locInAachen, 
                            gwa=join("data","gwa50-like.tif"), 
                            longRunAverage=wsSrc.LONG_RUN_AVERAGE_50M_SOURCE)
    if  not (abs(wsOut.sum()-4428.88769531) < 1e-6 and\
             abs(wsOut.std()-2.42754483223) < 1e-6): 
            raise RuntimeError("  Single loc, MerraSource: Fail")
    else: print("  Single loc, MerraSource: Success")

    # Use a MerraSoure with multiple locations
    wsOut = adjustLraToGwa( wsSrc, targetLoc=locs, 
                            gwa=join("data","gwa50-like.tif"), 
                            longRunAverage=wsSrc.LONG_RUN_AVERAGE_50M_SOURCE)
    
    if  not (abs(wsOut.values.sum()-14244.9913174) < 1e-6 and\
             abs(wsOut.values.std()-2.57847289055) < 1e-6): 
            raise RuntimeError("  Multi loc, MerraSource: Fail")
    else: print("  Multi loc, MerraSource: Success")

def test_adjustContextMeanToGwa():
    print("testing adjustContextMeanToGwa...")
    contextSource = join(dirname(__file__), "..", "data","gwa50_mean_over_merra.tif")

    # Use a defined context mean value with a single location and windspeed set
    wsOut = adjustContextMeanToGwa( windspeed, targetLoc=locInAachen, 
                                    gwa=join("data","gwa50-like.tif"), 
                                    contextMean=4.0)

    if  not (abs(wsOut.sum()-486.803510785) < 1e-6 and\
             abs(wsOut.std()-9.68620525167) < 1e-6): 
            raise RuntimeError("  Single loc, given context: Fail")
    else: print("  Single loc, given context: Success")

    # Use defined context mean values with multiple location and windspeed sets
    wsOut = adjustContextMeanToGwa( windspeeds, targetLoc=locs, 
                                    gwa=join("data","gwa50-like.tif"), 
                                    contextMean=[4.0,5.0,6.0])

    if  not (abs(wsOut.sum()-1330.00777684) < 1e-6 and\
             abs(wsOut.std()-9.0257067751) < 1e-6): 
            raise RuntimeError("  Multi loc, given context: Fail")
    else: print("  Multi loc, given context: Success")

    # Use a precalculated contextutal mean source with a single locations
    wsOut = adjustContextMeanToGwa( windspeed, targetLoc=locInAachen, 
                                    gwa=join("data","gwa50-like.tif"), 
                                    contextMean=contextSource)

    if  not (abs(wsOut.sum()-371.514705686) < 1e-6 and\
             abs(wsOut.std()-7.39223857996) < 1e-6): 
            raise RuntimeError("  Single loc, context source: Fail")
    else: print("  Single loc, context source: Success")

    # Use a precalculated contextutal mean source with multiple location and windspeed sets
    wsOut = adjustContextMeanToGwa( windspeeds, targetLoc=locs, 
                                    gwa=join("data","gwa50-like.tif"), 
                                    contextMean=contextSource)

    if  not (abs(wsOut.sum()-1344.26855344) < 1e-6 and\
             abs(wsOut.std()-8.74279056528) < 1e-6): 
            raise RuntimeError("  Multi loc, given context: Fail")
    else: print("  Multi loc, given context: Success")

    # Use a MerraSoure with a single locations
    wsOut = adjustContextMeanToGwa( wsSrc, targetLoc=locInAachen, 
                                    gwa=join("data","gwa50-like.tif"), 
                                    contextMean=wsSrc.GWA50_CONTEXT_MEAN_SOURCE)

    if  not (abs(wsOut.sum()-5702.04931641 ) < 1e-6 and\
             abs(wsOut.std()-3.12538552 ) < 1e-6): 
            raise RuntimeError("  Single loc, MerraSource: Fail")
    else: print("  Single loc, MerraSource: Success")

    # Use a MerraSoure with multiple locations
    wsOut = adjustContextMeanToGwa( wsSrc, targetLoc=locs, 
                                    gwa=join("data","gwa50-like.tif"), 
                                    contextMean=wsSrc.GWA50_CONTEXT_MEAN_SOURCE)

    if  not (abs(wsOut.values.sum()-19443.73842715) < 1e-6 and\
             abs(wsOut.values.std()-3.52234571) < 1e-6): 
            raise RuntimeError("  Multi loc, MerraSource: Fail")
    else: print("  Multi loc, MerraSource: Success")


def test_projectByLogLaw():
    print("Testing projectByLogLaw...")

    # testing single wind speed array
    wsOut = projectByLogLaw(windspeed, measuredHeight=20, targetHeight=100, roughness=0.01)
    if abs(wsOut.sum() - 527.10820631304512) < 1e-6: # checked by hand computation
        print("  Single array: Success")
    else: raise RuntimeError("Single array: Fail")

    # testing multiple wind speed array
    wsOut = projectByLogLaw(windspeeds, measuredHeight=20, targetHeight=100, roughness=0.01)
    if abs(wsOut[:,0].sum() - 527.10820631304512) < 1e-6 and \
       abs(wsOut[:,1].sum() - 539.22442460022705) < 1e-6 and \
       abs(wsOut[:,2].sum() - 551.34427811641797) < 1e-6 : # checked by hand computation
        print("  Multiple arrays: Success")
    else: raise RuntimeError("Multiple arrays: Fail")

    # testing multiple wind speed arrays with multiple roughnesses 
    wsOut = projectByLogLaw(windspeeds, measuredHeight=20, targetHeight=100, roughness=np.array([0.01, 0.121, 0.005]))
    if abs(wsOut[:,0].sum() - 527.10820631304512) < 1e-6 and \
       abs(wsOut[:,1].sum() - 585.21841016121857) < 1e-6 and \
       abs(wsOut[:,2].sum() - 543.29271410486263) < 1e-6 : # checked by hand computation
        print("  Multiple arrays and roughnesses: Success")
    else: raise RuntimeError("Multiple arrays and roughnesses: Fail")

def test_projectByPowerLaw():
    print("Testing projectByPowerLaw...")

    # testing single wind speed array
    wsOut = projectByPowerLaw(windspeed, measuredHeight=20, targetHeight=100, alpha=0.2)
    if abs(wsOut.sum() - 600.18240273562856) < 1e-6: # checked by hand computation
        print("  Single array: Success")
    else: raise RuntimeError("Single array: Fail")

    # testing multiple wind speed array
    wsOut = projectByPowerLaw(windspeeds, measuredHeight=20, targetHeight=100, alpha=0.2)
    if abs(wsOut[:,0].sum() - 600.18240273562856) < 1e-6 and \
       abs(wsOut[:,1].sum() - 613.97831962057921) < 1e-6 and \
       abs(wsOut[:,2].sum() - 627.77837569451424) < 1e-6 : # checked by hand computation
        print("  Multiple arrays: Success")
    else: raise RuntimeError("Multiple arrays: Fail")

    # testing multiple wind speed arrays with multiple alphas 
    wsOut = projectByPowerLaw(windspeeds, measuredHeight=20, targetHeight=100, alpha=np.array([0.2, 0.23, 0.25]))
    if abs(wsOut[:,0].sum() - 600.18240273562856) < 1e-6 and \
       abs(wsOut[:,1].sum() - 644.35044981969804) < 1e-6 and \
       abs(wsOut[:,2].sum() - 680.38519080443655) < 1e-6 : # checked by hand computation
        print("  Multiple arrays and alphas: Success")
    else: raise RuntimeError("Multiple arrays and alphas: Fail")

def test_alphaFromLevels():
    print("Testing alphaFromLevels...")

    a = alphaFromLevels(lowWindSpeed=5, lowHeight=10, highWindSpeed=7.9244659623055682, highHeight=100)
    if a-0.2 < 1e-6: print("  Single Conversion: Success")
    else: raise RuntimeError("Single Conversion: Fail")

    a = alphaFromLevels(lowWindSpeed=np.array([5,5,5]), lowHeight=10, highHeight=100, 
                        highWindSpeed=np.array([7.9244659623055682, 7.0626877231137719, 6.6676071608166199]))
    if (a[0]-0.2) < 1e-6 and (a[1]-0.15) < 1e-6 and (a[2]-0.125) < 1e-6 : 
        print("  Multiple windspeed conversion: Success")
    else: raise RuntimeError("Multiple windspeed conversion: Fail")

    a = alphaFromLevels(lowWindSpeed=np.array([5,5,5]), 
                            lowHeight=np.array([10,15,20]), 
                            highWindSpeed=np.array([7.9244659623055682, 6.6459384598839435, 6.1142227249692596]), 
                            highHeight=100)

    if (a[0]-0.2) < 1e-6 and (a[1]-0.15) < 1e-6 and (a[2]-0.125) < 1e-6 :  # checked by hand computation
        print("  Multiple height conversion: Success")
    else: raise RuntimeError("Multiple height conversion: Fail")

def test_alphaFromGWA():
    print("Testing alphaFromGWA...")

    a = alphaFromGWA(gwaDir="data", loc=loc, _structure="gwa%d-like.tif", pairID=0)
    if a-0.2180788 < 1e-6: print("  Single location: Success")
    else: raise RuntimeError("Single location: Fail")

    a = alphaFromGWA(gwaDir="data", loc=locs, _structure="gwa%d-like.tif", pairID=0)
    if abs(a[0]-0.2180788) < 1e-6 and abs(a[1]-0.223474) < 1e-6 and abs(a[2]-0.220947) < 1e-6: 
        print("  Multiple locations: Success")
    else: raise RuntimeError("Multiple locations: Fail")

def test_roughnessFromLevels():
    print("Testing roughnessFromLevels...")

    r = roughnessFromLevels(lowWindSpeed=5, lowHeight=10, highWindSpeed=7.5, highHeight=100)
    if r-0.1 < 1e-6: print("  Single Conversion: Success")
    else: raise RuntimeError("Single Conversion: Fail")

    r = roughnessFromLevels(lowWindSpeed=np.array([5,5,5]), lowHeight=10, highWindSpeed=np.array([7.5, 6.25, 6.0]), highHeight=100)
    if (r[0]-0.1) < 1e-6 and (r[1]-0.001) < 1e-6 and (r[2]-0.0001) < 1e-6 : 
        print("  Multiple windspeed conversion: Success")
    else: raise RuntimeError("Multiple windspeed conversion: Fail")

    r = roughnessFromLevels(lowWindSpeed=np.array([5,5,5]), 
                            lowHeight=np.array([10,15,20]), 
                            highWindSpeed=np.array([7.5, 6.25, 6.0]), 
                            highHeight=100)

    if (r[0]-0.1) < 1e-6 and (r[1]-0.00759375) < 1e-6 and (r[2]-0.0064) < 1e-6: # checked by hand computation
        print("  Multiple height conversion: Success")
    else: raise RuntimeError("Multiple height conversion: Fail")

def test_roughnessFromGWA():
    print("Testing roughnessFromGWA...")

    r = roughnessFromGWA(gwaDir="data", loc=loc, _structure="gwa%d-like.tif", pairID=0)
    if abs(r-0.71488771) < 1e-6: print("  Single location: Success")
    else: raise RuntimeError("Single location: Fail")

    r = roughnessFromGWA(gwaDir="data", loc=locs, _structure="gwa%d-like.tif", pairID=0)
    if abs(r[0]-0.71488771) < 1e-6 and abs(r[1]-0.798400880115) < 1e-6 and abs(r[2]-0.75864270) < 1e-6: 
        print("  Multiple locations: Success")
    else: raise RuntimeError("Multiple locations: Fail")

def test_roughnessFromCLC():
    print("Testing roughnessFromCLC...")
    loc1 = Location(lat=50.370680, lon=5.752684) # grid value: 24 -> code: 312 -> rough: 0.75
    loc2 = Location(lat=50.52603, lon=6.10476) # grid value: 36 -> code: 412 -> rough: 0.0005
    loc3 = Location(lat=50.59082, lon=5.86483) # grid value: 1 -> code: 111 -> rough: 1.2

    r = roughnessFromCLC(clcPath=join("data","clc-aachen_clipped.tif"), loc=loc1)
    if r-0.75 < 1e-6: print("  Single location: Success")
    else: raise RuntimeError("Single location: Fail")

    r = roughnessFromCLC(clcPath=join("data","clc-aachen_clipped.tif"), loc=[loc1,loc2,loc3])
    if abs(r[0]-0.75) < 1e-6 and abs(r[1]-0.0005) < 1e-6 and abs(r[2]-1.2) < 1e-6: 
        print("  Multiple locations: Success")
    else: raise RuntimeError("Multiple locations: Fail")

    r = roughnessFromCLC(clcPath=join("data","clc-aachen_clipped.tif"), loc=[loc1,loc2,loc3], winRange=2)
    if abs(r[0]-0.7380) < 1e-6 and abs(r[1]-0.0005) < 1e-6 and abs(r[2]-1.0040) < 1e-6: 
        print("  Multiple locations with range: Success")
    else: raise RuntimeError("Multiple locations with range: Fail")

def test_roughnessFromLandCover():
    print("#####################")
    print("MAKE TEST FOR: roughnessFromLandCover()")
    print("#####################")

if __name__ == '__main__':
    test_adjustLraToGwa(); print("")
    test_adjustContextMeanToGwa(); print("")
    test_projectByLogLaw(); print("")
    test_projectByPowerLaw(); print("")
    test_alphaFromLevels(); print("")
    test_alphaFromGWA(); print("")
    test_roughnessFromLevels(); print("")
    test_roughnessFromGWA(); print("")
    test_roughnessFromCLC(); print("")
    test_roughnessFromLandCover(); print("")