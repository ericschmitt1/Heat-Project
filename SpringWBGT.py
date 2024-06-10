import math
from datetime import datetime
import os
from matplotlib.dates import DateFormatter, HourLocator
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.patches as patches

def CalculateHeatIndex(T,H):

        heatindexsimple = 0.5 * (T + 61.0 + ((T - 68.0) * 1.2) + (H * 0.094))
        if heatindexsimple >= 80.0:
            heatindex = -42.379 + 2.04901523 * T + 10.14333127 * H - 0.22475541 * T * H - 0.00683783 * T**2 - 0.05481717 * H**2 + 0.00122874 * T**2 * H + 0.00085282 * T * H**2 - 0.00000199 * T**2 * H**2
        
            if H < 13 and 80 <= T <= 112:
                adjustment = ((13 - H) / 4) * math.sqrt((17 - abs(T - 95.0)) / 17)
                heatindex -= adjustment
        
            if H > 85 and 80 <= T <= 87:
                adjustment = ((H - 85) / 10) * ((87 - T) / 5)
                heatindex += adjustment
        
           
            return (heatindex)
        
        
       
        return (heatindexsimple)  
    
def CalculateDewPoint(T,H):
    DewPoint= T-((100-H)/5)
    return DewPoint

def CalculateWetBulbGlobe(T,RH,DP,SI,Direct,Diffuse,Z,P,u):
    s=5.67*(10**-8)
    if SI==0:
        Direct1=0
        Diffuse1=0
    else:
        Direct1=Direct/SI
        Diffuse1=Diffuse/SI
    #if Diffuse1 > .4 or Direct1 > .4:
        #print(Diffuse1,Direct1)
        #Diffuse1 = Diffuse1/2000
        #Direct1 = Direct1/2000
    angle= math.radians(Z)
    z= math.cos(angle)
    h=.315
    e= (math.exp((17.67*(DP-T))/(DP+243.5)))*(1.007+(.00000346*P))*(6.112*math.exp((17.502*T)/(240.97+T)))
    eA= .575*(e**(1/7))
    B=SI +(eA*(T**4))
    C= (h*(u**.58))/(5.3865*(10**-8))
    GT=(B+(C*T)+7680000)/(C+256000)
    WB=(-5.806 + 0.672 * T - 0.006 * T**2 + (0.061 + 0.004 * T + 99e-6 * T**2) * RH + (-33e-6 - 5e-6 * T - 1e-7 * T**2) * RH**2)
    if SI==0:
        WBGT= (.7*WB)+(.3*GT)
    else:
        WBGT= (.7*WB)+(.2*GT)+(.1*T)
       
    return WBGT
    #Direct1/(4*s*z)+     *Diffuse1)

def CalculateRelativeHumidity(T,TD):
   RH=100*(math.exp((17.625*TD)/(243.04+TD))/math.exp((17.625*T)/(243.04+T))) 
   return RH

def ReadWSData(WSFullFilename, nheaders=0):
    HourlySunlight = []
    WindSpeed = []
    Pressure = []
    WSTime = []
    with open(WSFullFilename,'r') as fobjs:    
        linelist = fobjs.readlines() 
    
    for line in linelist[nheaders:]:
        words=line.split(',')
        windspeedtime= datetime.strptime(words[0],'%Y-%m-%d %H:00:00')
        StartDate=datetime(2023,6,1)
        EndDate=datetime(2023,8,31)
        if StartDate<=windspeedtime<=EndDate:
            windspeed=float(words[1])
            WindSpeed.append(windspeed * 1609.34)
            formattedtime=f'0000-{windspeedtime.month:02d}-{windspeedtime.day:02d} {windspeedtime.hour:02d}:00:00'
            WSTime.append(formattedtime)
            pressure=float(words[2])
            Pressure.append(pressure * 33.8639)
            HourlySunlight.append(float(words[3]))
        
    return HourlySunlight, WindSpeed, Pressure, WSTime
    

def ReadSolarData(solarfilename,anglefilename, solarnheaders=3):
    DiffuseRad=[]
    DirectRad=[]
    SolarRadiationTime=[]
    SolarAngle=[]
    SolarAngleTime=[]
    SolarFinalTime = []
    year=int(2023)
    StartDate=datetime(2023,6,1)
    EndDate=datetime(2023,8,31)
    with open(solarfilename,'r') as fobjs:    
        linelist = fobjs.readlines()
    for line in linelist[solarnheaders:]:
        words=line.split(',')
        month,day,hour,minute=map(int,words[1:5])
        currentdate=datetime(year,month,day,hour)
        if StartDate<=currentdate<=EndDate:
            SolarFinalTime.append(currentdate)
            diffuserad=float(words[5])
            directrad=float(words[6])
            DiffuseRad.append(diffuserad)
            DirectRad.append(directrad)
            formattedtime=f'0000-{currentdate.month:02d}-{currentdate.day:02d} {currentdate.hour:02d}:00:00'
            SolarRadiationTime.append(formattedtime)
    
    with open(anglefilename,'r') as fobjs:    
        linelist2 = fobjs.readlines()
    for line in linelist2[solarnheaders:]:
        words2=line.split(',')
        month,day,hour,minute=map(int,words2[1:5])
        date2=datetime(year,month,day,hour)
        if StartDate<=date2<=EndDate:
            solarangle=float(words2[5])
            SolarAngle.append(solarangle)
            formattedtime2=f'0000-{date2.month:02d}-{date2.day:02d} {date2.hour:02d}:00:00'
            SolarAngleTime.append(formattedtime2)
            
    
          
    return DiffuseRad,DirectRad,SolarRadiationTime,SolarAngle,SolarAngleTime, SolarFinalTime


def CreateWBGTDict(WindSpeed,WindSpeedTime,Pressure,HourlySunlight,DiffuseRad,DirectRad,SolarRadiationTime,SolarAngle,SolarAngleTime):
    WindSpeedDict={time1:windspeed for time1, windspeed in zip(WindSpeedTime,WindSpeed)}
    HourlySunlightDict={time2:hourlysunlight for time2,hourlysunlight in zip(WindSpeedTime,HourlySunlight)}
    PressureDict={time3:pressure for time3,pressure in zip(WindSpeedTime,Pressure)}
    DiffuseDict= {time4:diffuse for time4,diffuse in zip(SolarRadiationTime,DiffuseRad)}
    DirectDict= {time5:direct for time5,direct in zip(SolarRadiationTime,DirectRad)}
    AngleDict= {time6:solarangle for time6,solarangle in zip(SolarAngleTime,SolarAngle)}

    

    return WindSpeedDict,HourlySunlightDict,PressureDict,DiffuseDict,DirectDict,AngleDict  

def ReadAirportData(filename4,WindSpeedDict,HourlySunlightDict,PressureDict,DiffuseDict,DirectDict,AngleDict, nheaders=0):
    TimeAirport=[]
    TempAirport= []
    HumidityAirport=[]
    HeatIndexAirport=[]
    WBGTAirport = []

    
    with open(filename4,'r') as fobjs:    
        linelist = fobjs.readlines() 
    for line in linelist[nheaders:]:
        words=[word.strip('"') for word in line.rstrip().split(',')]
        if len(words) >= 8 and words[8]!='+9999' and words[6]!='+9999':
            ReadTime=datetime.strptime(words[1],'%Y-%m-%dT%H:%M:%S')
            StartTime = datetime.strptime('2023-6-1 00:00:00', '%Y-%m-%d %H:%M:%S')
            EndTime = datetime.strptime('2023-8-31 00:00:00', '%Y-%m-%d %H:%M:%S')
            if StartTime <= ReadTime <= EndTime:
                if words[9].isdigit():
                    Time=datetime.strftime(ReadTime,'%Y-%m-%d %H:%M:%S')
                    DictDate=f'0000-{Time[5:13]}:00:00'
                    if DictDate in HourlySunlightDict and DictDate in PressureDict and DictDate in DiffuseDict and DictDate in DirectDict and DictDate in AngleDict:
                        Temperaturestr=(words[8].split('+')[1].split('"'))
                        Temperature=''.join(Temperaturestr+[words[9]])
                        TempFinal=(float(Temperature.replace(',','.')))/100
                        Dewpointstr=(words[6].split('+')[1].split('"'))
                        Dewpoint=''.join(Dewpointstr+[words[7]])
                        DewFinal=(float(Dewpoint.replace(',','.')))/100
                        Humidity= CalculateRelativeHumidity(TempFinal,DewFinal)
                        Ftemp=(TempFinal * 9/5) + 32
                        HeatIndex=CalculateHeatIndex(Ftemp,Humidity)
                        wetbulbglobe = CalculateWetBulbGlobe(TempFinal,Humidity,DewFinal,HourlySunlightDict[DictDate],DirectDict[DictDate],DiffuseDict[DictDate],AngleDict[DictDate],PressureDict[DictDate],WindSpeedDict[DictDate])
                        TempAirport.append(TempFinal)
                        HumidityAirport.append(Humidity)
                        HeatIndexAirport.append(HeatIndex)
                        TimeAirport.append(Time)
                        WBGTAirport.append(wetbulbglobe)
                    
            
    return TempAirport,HumidityAirport,HeatIndexAirport, TimeAirport, WBGTAirport

 
def main():
    StartDate = datetime(2023,5,25)
    enddate = datetime(2023,9,6)
    nheaders, solarnheaders = 1,3
    folderpath='/Users/ericschmitt/Documents/Heat Project Data'
    WSFullFilename=os.path.join(folderpath,'WSData5-8_23.csv')
    solarfilename= os.path.join(folderpath,'AverageSolarRadiation.csv')
    anglefilename= os.path.join(folderpath,'SolarAngle.csv')
    MIAFullFilename=os.path.join(folderpath,'FullAirportData.csv')
    
    HourlySunlight, WindSpeed, Pressure, WSTime = ReadWSData(WSFullFilename, nheaders)
    
    DiffuseRad,DirectRad,SolarRadiationTime,SolarAngle,SolarAngleTime, SolarFinalTime= ReadSolarData(solarfilename,anglefilename,solarnheaders)
    WindSpeedDict,HourlySunlightDict,PressureDict,DiffuseDict,DirectDict,AngleDict= CreateWBGTDict(WindSpeed,WSTime,Pressure,HourlySunlight,DiffuseRad,DirectRad,SolarRadiationTime,SolarAngle,SolarAngleTime)

    TempAirport,HumidityAirport,HeatIndexAirport, TimeAirport, WBGTAirport = ReadAirportData(MIAFullFilename,WindSpeedDict,HourlySunlightDict,PressureDict,DiffuseDict,DirectDict,AngleDict, nheaders)

    HICaution = (80,90)  
    HIExtremeCaution = (90,103)
    HIDanger = (103,124)
    HIExtremeDanger = (124,180)
    WBGTLow = (27.89,30.5)
    WBGTModerate = (30.5,32.22)
    WBGTHigh = (32.22,33.28)
    WBGTExtreme = (33.28,100)
    
    fig, ax = plt.subplots(figsize=(35,20))
    fig2,ax2= plt.subplots(figsize=(35,20))
    
    ax_warnings = ax.twinx()
    ax.plot(mdates.date2num(TimeAirport),HeatIndexAirport, label='MIA Weather Station',color='black')
    ax.set_xlabel('Time')
    ax.set_ylabel('Heat Index(Degrees F)')

    ax.xaxis.set_major_formatter(DateFormatter('%m-%d'))
    ax.xaxis.set_major_locator(HourLocator(interval=144))
    ax.set_title('Time vs Heat Index for MIA Data from 06/01-08/31')
    ax.axis('auto')
    ax.legend(loc='lower left')
    ax_warnings.set_yticks([])
    HIcautionbox = patches.Rectangle((StartDate, HICaution[0]), enddate - StartDate, HICaution[1] - HICaution[0],linewidth=1, edgecolor='none', facecolor='yellow', alpha=0.4, label='Caution',zorder=50)
    ax.add_patch(HIcautionbox)
   
    HIextremecautionbox = patches.Rectangle((StartDate, HIExtremeCaution[0]), enddate - StartDate, HIExtremeCaution[1] - HIExtremeCaution[0],linewidth=1, edgecolor='none', facecolor='orange', alpha=0.4, label=' Extreme Caution',zorder=50)
    ax.add_patch(HIextremecautionbox)
    HIdangerbox = patches.Rectangle((StartDate, HIDanger[0]), enddate - StartDate, HIDanger[1] - HIDanger[0],linewidth=1, edgecolor='none', facecolor='red', alpha=0.4, label='Danger',zorder=50)
    ax.add_patch(HIdangerbox)
    HIextremedangerbox = patches.Rectangle((StartDate, HIExtremeDanger[0]), enddate - StartDate, HIExtremeDanger[1] - HIExtremeDanger[0],linewidth=1, edgecolor='none', facecolor='violet', alpha=0.4, label=' Extreme Danger',zorder=50)
    ax.add_patch(HIextremedangerbox)
    legend_rectangles = [patches.Patch(color='yellow', alpha=0.43, label='Caution'),patches.Patch(color='orange', alpha=0.43, label='Extreme Caution'),patches.Patch(color='red', alpha=0.43, label='Danger'),patches.Patch(color='violet', alpha=0.43, label='Extreme Danger')]
    ax_warnings.legend(handles=legend_rectangles, loc='lower right')
    
    ax2.plot(mdates.date2num(TimeAirport),WBGTAirport, label='MIA Weather Station',color='black')
    ax2.set_xlabel('Time')
    ax2.set_ylabel('Wet Bulb Globe Temperature(Degrees C)')
    ax2.xaxis.set_major_formatter(DateFormatter('%m-%d'))
    ax2.xaxis.set_major_locator(HourLocator(interval=144))
    ax2.set_title('Time vs Wet Bulb Globe Temperature for MIA Data from 06/01-08/31')
    ax2.axis('auto')
    ax2.legend(loc='lower left')
    ax2_warnings = ax2.twinx()
    ax2_warnings.set_yticks([])
    
    WBGTLowbox = patches.Rectangle((StartDate, WBGTLow[0]), enddate - StartDate, WBGTLow[1] - WBGTLow[0],linewidth=1, edgecolor='none', facecolor='green', alpha=0.4, label='Low',zorder=50)
    ax2.add_patch(WBGTLowbox)
    WBGTModeratebox = patches.Rectangle((StartDate, WBGTModerate[0]), enddate - StartDate, WBGTModerate[1] - WBGTModerate[0],linewidth=1, edgecolor='none', facecolor='yellow', alpha=0.4, label='Moderate',zorder=50)
    ax2.add_patch(WBGTModeratebox)
    WBGTHighbox = patches.Rectangle((StartDate, WBGTHigh[0]), enddate - StartDate, WBGTHigh[1] - WBGTHigh[0],linewidth=1, edgecolor='none', facecolor='red', alpha=0.4, label='High',zorder=50)
    ax2.add_patch(WBGTHighbox)
    WBGTExtremebox = patches.Rectangle((StartDate, WBGTExtreme[0]), enddate - StartDate, WBGTExtreme[1] - WBGTExtreme[0],linewidth=1, edgecolor='none', facecolor='black', alpha=0.4, label='Low',zorder=50)
    ax2.add_patch(WBGTExtremebox)
    legend_rectangles = [patches.Patch(color='green', alpha=0.43, label='Low'),patches.Patch(color='yellow', alpha=0.43, label='Moderate'),patches.Patch(color='red', alpha=0.43, label='High'),patches.Patch(color='black', alpha=0.43, label='Extreme')]
    ax2_warnings.legend(handles=legend_rectangles, loc='lower right')
    
    plt.show()
    
main()