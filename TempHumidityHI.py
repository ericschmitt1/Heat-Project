import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from matplotlib.dates import DateFormatter, HourLocator
import os
import re
import math
import matplotlib.dates as mdates
import matplotlib.patches as patches
from scipy import stats



def CreateFileList(startdate,enddate):
    currentdate=startdate
    filelist=[]
    while currentdate <= enddate:
        formatdate= currentdate.strftime('%Y-%m-%d')
        filename = f'iseechange-sensor-data-mdc-heat-and-transit-{formatdate}-sensors.csv'
        filelist.append(filename)
        currentdate+=timedelta(days=1)
    return filelist

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
        Direct1=Direct
        Diffuse1=Diffuse
    else:
        Direct1=Direct/SI
        Diffuse1=Diffuse/SI
    angle= math.radians(Z)
    z= math.cos(angle)
    h=.315
    e= (math.exp((17.67*(DP-T))/(DP+243.5)))*(1.007+(.00000346*P))*(6.112*math.exp((17.502*T)/(240.97+T)))
    eA= .575*(e**(1/7))
    B=SI*(((1.2/s)*Diffuse1))+(eA*(T**4))
    C= (h*(u**.58))/(5.3865*(10**-8))
    GT=(B+(C*T)+7680000)/(C+256000)
    WB=(-5.806 + 0.672 * T - 0.006 * T**2 + (0.061 + 0.004 * T + 99e-6 * T**2) * RH + (-33e-6 - 5e-6 * T - 1e-7 * T**2) * RH**2)
    if SI==0:
        WBGT= (.7*WB)+(.3*GT)
    else:
        WBGT= (.7*WB)+(.2*GT)+(.1*T)
    
    #*Diffuse1

    
    return WBGT

def CalculateWetBulbTemp(T, RH):
    Tw = (T * math.atan(.151977 * math.sqrt(RH + 8.313659))) + ((.00391838 * math.sqrt(RH ** 3)) * (math.atan(.023101 * RH))) - (math.atan(RH - 1.676331)) + (math.atan(T + RH)) - 4.686035
    return Tw

def ReadWSData(filename2,filename3,sunlightfilename,windfilename,pressurefilename,hourlysunlightfilename,weatherstemwbgtfilename,weatherstemhourlyfilename,nheaders2=0,nheaders3=0):
    Time2=[]
    Temperature2=[]
    Time3=[]
    Humidity3=[]
    WSTemperatureF=[]
    Sunlight =[]
    SunlightTime = []
    WindSpeed = []
    WindSpeedTime = []
    Pressure = []
    HourlySunlight = []
    WeatherStemWBGT = []
    WSWBGTTime= []
    HourlyTemp = []
    HourlyHumidity = []
    
    
    with open(filename2,'r') as fobjs:    
        linelist = fobjs.readlines()                
    

    for line in linelist[nheaders2:]:
        words=line.split(',')
        Temperature=(float(words[2]))
        WSTemperatureF.append(Temperature)
        Temperature2.append((Temperature-32)*(5/9))
        Time2.append(datetime.strptime(words[1],'%Y-%m-%d %H:%M:%S'))
        
    with open(filename3,'r') as fobjs:    
        linelist2 = fobjs.readlines()                
        

    for line in linelist2[nheaders3:]:
        words2=line.split(',')
        Humidity3.append(float(words2[2]))
        Time3.append(datetime.strptime(words2[1],'%Y-%m-%d %H:%M:%S'))
        
    with open(sunlightfilename,'r') as fobjs:    
        linelist3 = fobjs.readlines() 
        
    for line in linelist3[nheaders3:]:
        words3=line.split(',')
        Sunlight.append(float(words3[1]))
        SunlightTime.append(datetime.strptime(words3[0],'%Y-%m-%d %H:%M:%S'))
        
    with open(windfilename,'r') as fobjs:    
        linelist4 = fobjs.readlines() 
    
    for line in linelist4[nheaders3:]:
        words4=line.split(',')
        windspeed=float(words4[1])
        WindSpeed.append(windspeed * 1609.34)
        windspeedtime= datetime.strptime(words4[0],'%Y-%m-%d %H:00:00')
        formattedtime=f'0000-{windspeedtime.month:02d}-{windspeedtime.day:02d} {windspeedtime.hour:02d}:00:00'
        WindSpeedTime.append(formattedtime)
    
        
    with open(pressurefilename,'r') as fobjs:    
        linelist5 = fobjs.readlines() 
     
    for line in linelist5[nheaders3:]:
         words5=line.split(',')
         pressure=float(words5[1])
         Pressure.append(pressure * 33.8639)
         
    with open(hourlysunlightfilename,'r') as fobjs:    
         linelist6 = fobjs.readlines() 
      
    for line in linelist6[nheaders3:]:
          words6=line.split(',')
          HourlySunlight.append(float(words6[1]))
          
    with open(weatherstemwbgtfilename,'r') as fobjs:    
          linelist7 = fobjs.readlines() 
 
    for line in linelist7[nheaders3:]:
          words7=line.split(',')
          WSWBGT=float(words7[1])
          WeatherStemWBGT.append((WSWBGT-32)*(5/9))
          WSWBGTTime.append(datetime.strptime(words7[0],'%Y-%m-%d %H:%M:%S'))
          
    with open(weatherstemhourlyfilename,'r') as fobjs:
        linelist8 = fobjs.readlines()
    
    for line in linelist8[nheaders3:]:
        words8 = line.split(',')
        Temp = float(words8[2])
        HourlyTemp.append((Temp-32)*(5/9))
        HourlyHumidity.append(float(words8[1]))
        
        
        
          
          

         
        
    return Temperature2,Time2,Humidity3,Time3,WSTemperatureF, Sunlight, SunlightTime, WindSpeed, WindSpeedTime,Pressure,HourlySunlight,WeatherStemWBGT, WSWBGTTime, HourlyTemp, HourlyHumidity    

def ReadSolarData(solarfilename,anglefilename, solarnheaders=3):
    DiffuseRad=[]
    DirectRad=[]
    SolarRadiationTime=[]
    SolarAngle=[]
    SolarAngleTime=[]
    SolarFinalTime = []
    year=int(2023)
    StartDate=datetime(2023,8,25)
    EndDate=datetime(2023,11,8)
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
       
def ReadSensorData(filename,currentdate,WindSpeedDict,HourlySunlightDict,PressureDict,DiffuseDict,DirectDict,AngleDict,nheaders=0):
     Time1=[]
     Temperature=[]
     SensorID1=[]
     Humidity=[]
     Time2=[]
     SensorID2=[]
     SensorID3=[]
     Time3=[]
     WetBulbGlobe= []
     WetBulbTemp = []
     
     currenttemp={}
     currenthumidity= {}
     currentCtemp = {}
     lastsensorID= 'SBgi3wG1EXkTavBUC2UUVGOZ' 
     HeatIndex=[]
     lasttype= None

     
     with open(filename,'r') as fobjs:    
         linelist = fobjs.readlines()                
     

     for line in linelist[nheaders:]:
         line=line.strip()
         words=line.strip('"').split('","')
         
         if len(words)==5 and words[3]=='humidity':
            humidityvalue=(float(words[4]))
            Humidity.append(humidityvalue)
            timestamp2=f"{words[0]} {words[1]}"
            currenthumidity[words[2]]= humidityvalue
            try:
                 fixedtime2=datetime.strptime(timestamp2,'%Y-%m-%d %H:%M:%S')
            except ValueError:
                 fixedtime2=datetime.strptime(timestamp2,'%H:%M:%S %Y-%m-%d')   
            formattime2 = fixedtime2.strftime('%Y-%m-%d %H:%M:%S')
            Time2.append(formattime2)
            SensorID2.append(words[2])
            DictDate=f'0000-{formattime2[5:13]}:00:00'
            if lasttype == 'temperature' and lastsensorID==words[2]:
                heatindex= CalculateHeatIndex(currenttemp[lastsensorID],humidityvalue)
                wetbulbtemp = CalculateWetBulbTemp(currentCtemp[lastsensorID], humidityvalue)
                Fdewpoint= CalculateDewPoint(currenttemp[lastsensorID],humidityvalue)
                Cdewpoint = (Fdewpoint - 32) * 5/9
                WBtemp=(currenttemp[lastsensorID]-32)*5/9
                wetbulbglobe= CalculateWetBulbGlobe(WBtemp,humidityvalue,Cdewpoint,HourlySunlightDict[DictDate],DirectDict[DictDate],DiffuseDict[DictDate],AngleDict[DictDate],PressureDict[DictDate],WindSpeedDict[DictDate])
                HeatIndex.append(heatindex)
                Time3.append(formattime2)
                SensorID3.append(words[2])
                WetBulbGlobe.append(wetbulbglobe)
                WetBulbTemp.append(wetbulbtemp)
                lasttype= None
                lastsensorID=None
                
            
            else:
                lasttype= 'humidity'
                lastsensorID=words[2]
                
        
         elif len(words)==5 and words[3]=='temperature':
            Ctemp=(float(words[4].strip()))
            Temperature.append(Ctemp)
            Ftemp=(Ctemp * 9/5) + 32
            timestamp1=f"{words[0]} {words[1]}"
            currenttemp[words[2]]= Ftemp
            currentCtemp[words[2]] = Ctemp
            try:
                 fixedtime1=datetime.strptime(timestamp1,'%Y-%m-%d %H:%M:%S')
            except ValueError:
                 fixedtime1=datetime.strptime(timestamp1,'%H:%M:%S %Y-%m-%d')   
            formattime1 = fixedtime1.strftime('%Y-%m-%d %H:%M:%S')
            Time1.append(formattime1)
            SensorID1.append(words[2])
            DictDate=f'0000-{formattime1[5:13]}:00:00'
            
            if lasttype == 'humidity' and lastsensorID==words[2]:
                heatindex= CalculateHeatIndex(Ftemp,currenthumidity[lastsensorID])
                wetbulbtemp = CalculateWetBulbTemp(Ctemp, currenthumidity[lastsensorID])
                dewpoint= CalculateDewPoint(Ctemp,currenthumidity[lastsensorID])
                wetbulbglobe= CalculateWetBulbGlobe(Ctemp,currenthumidity[lastsensorID],dewpoint,HourlySunlightDict[DictDate],DirectDict[DictDate],DiffuseDict[DictDate],AngleDict[DictDate],PressureDict[DictDate],WindSpeedDict[DictDate])
                HeatIndex.append(heatindex)
                Time3.append(formattime1)
                SensorID3.append(words[2])
                WetBulbGlobe.append(wetbulbglobe)
                WetBulbTemp.append(wetbulbtemp)
                lasttype= None
                lastsensorID=None
              
            else:
                lasttype= 'temperature'
                lastsensorID=words[2]
            

  
     return Temperature,Time1,SensorID1,Humidity,Time2,SensorID2, HeatIndex, Time3, SensorID3, WetBulbGlobe, WetBulbTemp


def CreateAllData(filelist,folderpath,WindSpeedDict,HourlySunlightDict,PressureDict,DiffuseDict,DirectDict,AngleDict,n=1):
    alltemps=[]
    alltimes1=[]
    allsensorids1=[]
    allhumidity=[]
    alltimes2=[]
    allsensorids2=[]
    allsensorids3=[]
    alltimes3=[]
    allHI=[]
    allWetBulbGlobe = []
    allWetBulbTemp = []
    datepattern=r'\d{4}-\d{2}-\d{2}'
    for filename in filelist:
        match=re.search(datepattern,filename)
        if match:
            
            
            datepart=match.group(0)
            currentdate=datetime.strptime(datepart,'%Y-%m-%d')
            fullfilepath=os.path.join(folderpath,filename)
            Temperature,Time1,SensorID1,Humidity,Time2,SensorID2, HeatIndex, Time3, SensorID3,WetBulbGlobe, WetBulbTemp = ReadSensorData(fullfilepath,currentdate,WindSpeedDict,HourlySunlightDict,PressureDict,DiffuseDict,DirectDict,AngleDict,nheaders=0)
            numsamples1=len(Temperature)
            subsamples1=range(0,numsamples1,n)
            subsampletemp=[Temperature[i] for i in subsamples1]
            subsampletime1=[Time1[i] for i in subsamples1]
            subsampleID1=[SensorID1[i] for i in subsamples1]
            alltemps.extend(subsampletemp)
            alltimes1.extend(subsampletime1)
            allsensorids1.extend(subsampleID1)
            
            numsamples2=len(Humidity)
            subsamples2=range(0,numsamples2,n)
            subsamplehumidity=[Humidity[i] for i in subsamples2]
            subsampletime2=[Time2[i] for i in subsamples2]
            subsampleID2=[SensorID2[i] for i in subsamples2]
            allhumidity.extend(subsamplehumidity)
            alltimes2.extend(subsampletime2)
            allsensorids2.extend(subsampleID2)
            
            numsamples3=len(HeatIndex)
            subsamples3=range(0,numsamples3,n)
            subsampleHI=[HeatIndex[i] for i in subsamples3]
            subsampletime3=[Time3[i] for i in subsamples3]
            subsampleID3=[SensorID3[i] for i in subsamples3]
            alltimes3.extend(subsampletime3)
            allsensorids3.extend(subsampleID3)
            allHI.extend(subsampleHI)
            
            
            numsamples4=len(WetBulbGlobe)
            subsamples4=range(0,numsamples4,n)
            subsampleWB=[WetBulbGlobe[i] for i in subsamples4]
            allWetBulbGlobe.extend(subsampleWB)
            
            numsamples5 = len(WetBulbTemp)
            subsamples5 = range(0, numsamples5, n)
            subsampleWBT = [WetBulbTemp[i] for i in subsamples5]
            allWetBulbTemp.extend(subsampleWBT)
            

        else:
            print('error')
     
    return alltemps,alltimes1,allsensorids1,allhumidity,alltimes2,allsensorids2,allHI, alltimes3,allsensorids3, allWetBulbGlobe, allWetBulbTemp


def OrganizeBySensor(UniqueSensor, allsensorids1,alltemps,alltimes1,allsensorids2,allhumidity,alltimes2,allsensorids3,allHI,alltimes3,allWetBulbGlobe, allWetBulbTemp):
    finaldata1={}
    finaldata2={}
    finaldata3={}
    finaldatawetbulb={}
    finaldatawetbulbtemp = {}

    for ID in UniqueSensor:
        IDTemp = [(temp, datetime.strptime(time, '%Y-%m-%d %H:%M:%S')) for temp, sensorID, time in zip(alltemps, allsensorids1, alltimes1) if sensorID == ID]
        finaldata1[ID]={'temp': [data[0] for data in IDTemp], 'time': [data[1] for data in IDTemp]}
    
   
    for ID in UniqueSensor:
        IDHumidity = [(humidity, datetime.strptime(time, '%Y-%m-%d %H:%M:%S')) for humidity, sensorID, time in zip(allhumidity, allsensorids2, alltimes2) if sensorID == ID]
        finaldata2[ID]={'humidity': [data[0] for data in IDHumidity], 'time': [data[1] for data in IDHumidity]}
    
    
    for ID in UniqueSensor:
        IDHI = [(HI, datetime.strptime(time, '%Y-%m-%d %H:%M:%S')) for HI, sensorID, time in zip(allHI, allsensorids3, alltimes3) if sensorID == ID]
        finaldata3[ID]={'heat index': [data[0] for data in IDHI], 'time': [data[1] for data in IDHI]}
        
    for ID in UniqueSensor:
        IDWB = [(WB, datetime.strptime(time, '%Y-%m-%d %H:%M:%S')) for WB, sensorID, time in zip(allWetBulbGlobe, allsensorids3, alltimes3) if sensorID == ID]
        finaldatawetbulb[ID]={'wet bulb globe': [data[0] for data in IDWB], 'time': [data[1] for data in IDWB]}
        
    for ID in UniqueSensor:
        IDWBT = [(WBT, datetime.strptime(time, '%Y-%m-%d %H:%M:%S')) for WBT, sensorID, time in zip(allWetBulbTemp, allsensorids3, alltimes3) if sensorID == ID]
        finaldatawetbulbtemp[ID]={'wet bulb temp': [data[0] for data in IDWBT], 'time': [data[1] for data in IDWBT]}
        
        
    return finaldata1,finaldata2,finaldata3,finaldatawetbulb, finaldatawetbulbtemp

def CalculateRollingMean(data,windowsize):
    rollingavg=[]
    for i in range(len(data)-windowsize+1):
        window=data[i:i+windowsize]
        avg= sum(window)/windowsize
        rollingavg.append(avg)
    return rollingavg


def CalculateRelativeHumidity(T,TD):
   RH=100*(math.exp((17.625*TD)/(243.04+TD))/math.exp((17.625*T)/(243.04+T))) 
   return RH

def ReadAirportData(filename4,nheaders4=0):
    TimeAirport=[]
    TempAirport= []
    HumidityAirport=[]
    HeatIndexAirport=[]
    
    with open(filename4,'r') as fobjs:    
        linelist = fobjs.readlines() 
    for line in linelist[nheaders4:]:
        words=[word.strip('"') for word in line.rstrip().split(',')]
        if len(words) >= 8 and words[8]!='+9999' and words[6]!='+9999':
            Temperaturestr=(words[8].split('+')[1].split('"'))
            Temperature=''.join(Temperaturestr+[words[9]])
            TempFinal=(float(Temperature.replace(',','.')))/100
            Dewpointstr=(words[6].split('+')[1].split('"'))
            Dewpoint=''.join(Dewpointstr+[words[7]])
            DewFinal=(float(Dewpoint.replace(',','.')))/100
            Humidity= CalculateRelativeHumidity(TempFinal,DewFinal)
            Ftemp=(TempFinal * 9/5) + 32
            HeatIndex=CalculateHeatIndex(Ftemp,Humidity)
            ReadTime=datetime.strptime(words[1],'%Y-%m-%dT%H:%M:%S')
            Time=datetime.strftime(ReadTime,'%Y-%m-%d %H:%M:%S')
            TempAirport.append(TempFinal)
            HumidityAirport.append(Humidity)
            HeatIndexAirport.append(HeatIndex)
            TimeAirport.append(Time)
        
        
    return TempAirport,HumidityAirport,HeatIndexAirport, TimeAirport


    
def CalculateWSHeatIndex(T,H):


        
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

def CalculateWSWBGT(T,RH,SI,Direct,Diffuse,Z,P,u):
    DP = CalculateDewPoint(T,RH)
    WSWBGT = CalculateWetBulbGlobe(T,RH,DP,SI,Direct,Diffuse,Z,P,u)

    return WSWBGT

def CreateMatches(CalcWSWBGT,SolarFinalTime,WeatherStemWBGT, WSWBGTTime):
    CalculatedDict = {time: value for time, value in zip(SolarFinalTime, CalcWSWBGT)}
    matchedCalculated = []
    matchedMeasured = []
    for time, measuredvalue in zip(WSWBGTTime, WeatherStemWBGT):
        if time in CalculatedDict:
            matchedCalculated.append(CalculatedDict[time])
            matchedMeasured.append(measuredvalue)
            
    return matchedCalculated, matchedMeasured
    
    
    
    

                       

def main():
    startdate= datetime(2023,9,25)
    enddate=datetime(2023,10,15)
    folderpath='/Users/ericschmitt/Documents/Heat Project Data'
    filename2=os.path.join(folderpath,'HechtACWeatherstem.csv')
    filename3=os.path.join(folderpath,'HechtACWeatherstemHumidity.csv')
    filename4=os.path.join(folderpath,'MIANov8Data.csv')
    sunlightfilename = os.path.join(folderpath,'WeatherStemSunlight.csv')
    windfilename= os.path.join(folderpath,'Windspeed.csv')
    solarfilename= os.path.join(folderpath,'AverageSolarRadiation.csv')
    anglefilename= os.path.join(folderpath,'SolarAngle.csv')
    pressurefilename= os.path.join(folderpath,'HourlyPressure.csv')
    hourlysunlightfilename= os.path.join(folderpath,'HourlySunlight.csv')
    weatherstemwbgtfilename=os.path.join(folderpath,'WeatherStemWBGT.csv')
    weatherstemhourlyfilename=os.path.join(folderpath,'WSHourly.csv')
    nheaders2,nheaders3,nheaders4=1,1,1
    solarnheaders=3
    filelist= CreateFileList(startdate,enddate)
    CalcWSWBGT = []
    HICaution = (80,90)  
    HIExtremeCaution = (90,103)
    HIDanger = (103,124)
    HIExtremeDanger = (124,180)
    WBGTLow = (27.8,30.5)
    WBGTModerate = (30.5,32.17)
    WBGTHigh = (32.17,33.28)
    WBGTExtreme = (33.28,100)
    
    Temperature2,Time2,Humidity3,Time3,WSTemperatureF,Sunlight,SunlightTime,WindSpeed, WindSpeedTime, Pressure, HourlySunlight,WeatherStemWBGT,WSWBGTTime, HourlyTemp, HourlyHumidity=ReadWSData(filename2,filename3,sunlightfilename,windfilename,pressurefilename,hourlysunlightfilename,weatherstemwbgtfilename,weatherstemhourlyfilename,nheaders2,nheaders3)
    DiffuseRad,DirectRad,SolarRadiationTime,SolarAngle,SolarAngleTime, SolarFinalTime= ReadSolarData(solarfilename,anglefilename,solarnheaders)
    WindSpeedDict,HourlySunlightDict,PressureDict,DiffuseDict,DirectDict,AngleDict= CreateWBGTDict(WindSpeed,WindSpeedTime,Pressure,HourlySunlight,DiffuseRad,DirectRad,SolarRadiationTime,SolarAngle,SolarAngleTime)
    
    
    
  
    alltemps,alltimes1,allsensorids1,allhumidity,alltimes2,allsensorids2,allHI,alltimes3,allsensorids3, allWetBulbGlobe, allWetBulbTemp =CreateAllData(filelist,folderpath,WindSpeedDict,HourlySunlightDict,PressureDict,DiffuseDict,DirectDict,AngleDict)
    TempAirport,HumidityAirport,HeatIndexAirport,TimeAirport=ReadAirportData(filename4,nheaders4)
        
    UniqueSensor=set(allsensorids1)
    finaldatatemp,finaldatahumidity,finaldataheatindex,finaldatawetbulb, finaldatawetbulbtemp =OrganizeBySensor(UniqueSensor, allsensorids1,alltemps,alltimes1,allsensorids2,allhumidity,alltimes2,allsensorids3,allHI,alltimes3,allWetBulbGlobe, allWetBulbTemp)
    fig, ax = plt.subplots(figsize=(35,20))
    fig2,ax2= plt.subplots(figsize=(35,20))
    fig3, ax3 = plt.subplots(figsize=(35,20))
    fig4, ax4 = plt.subplots(figsize=(35,20))
    fig5, ax5 = plt.subplots(figsize = (35,20))
    fig6, ax6 = plt.subplots(figsize = (35,20))
    
    windowsize1=4
    for ID, data in finaldatatemp.items():
        sensorlabel=ID[-4:]
        rollingtemp= CalculateRollingMean(data['temp'],windowsize1)
        rollingtime1=mdates.date2num(data['time'])[windowsize1-1:]
        ax.plot(rollingtime1,rollingtemp,label=f'SensorID:{sensorlabel}')
    #ax_sunlight = ax.twinx()
    #filteredsunlightdates = [date for date in SunlightTime if startdate <= date <= enddate]
    #filteredsunlight = [sunlight for date, sunlight in zip(SunlightTime, Sunlight) if startdate <= date <= enddate]
    #ax_sunlight.plot(mdates.date2num(filteredsunlightdates),filteredsunlight,label='Solar Radiation', color = 'gray')
    #ax_sunlight.set_ylabel('Solar Radiation (Watts Per Meters Squared)')
    filtereddates = [date for date in Time2 if startdate <= date <= enddate]
    filteredtemps = [temp for date, temp in zip(Time2, Temperature2) if startdate <= date <= enddate]
    ax.plot(mdates.date2num(filtereddates),filteredtemps, label='UM Hecht Athletic Center Weatherstem',color='black')
    #ax.plot(mdates.date2num(TimeAirport),TempAirport, label='MIA Weather Station',color='#FFFF00')
    ax.set_xlabel('Time')
    ax.set_ylabel('Temperature(Degrees Celsius)')
    ax.xaxis.set_major_formatter(DateFormatter('%m-%d'))
    ax.xaxis.set_major_locator(HourLocator(interval=72))
    ax.set_title('Time vs Temperature for ISeeChange Sensor Data from 08/25-11/08')
    ax.axis('auto')
    ax.legend(loc='upper left')
    #ax_sunlight.legend(loc='upper right')


    windowsize2=4
    for ID, data in finaldatahumidity.items():
        sensorlabel=ID[-4:]
        rollinghumidity= CalculateRollingMean(data['humidity'],windowsize2)
        rollingtime2=mdates.date2num(data['time'])[windowsize2-1:]
        ax2.plot(rollingtime2,rollinghumidity,label=f'SensorID:{sensorlabel}')
    #ax2_sunlight = ax2.twinx()
    #ax2_sunlight.plot(mdates.date2num(filteredsunlightdates),filteredsunlight,label='Solar Radiation', color = 'gray')
    #ax2_sunlight.set_ylabel('Solar Radiation (Watts Per Meters Squared)')
    filtereddates2 = [date for date in Time3 if startdate <= date <= enddate]
    filteredhumidity = [humidity for date, humidity in zip(Time3, Humidity3) if startdate <= date <= enddate]
    ax2.plot(mdates.date2num(filtereddates2),filteredhumidity, label='UM Hecht Athletic Center Weatherstem',color='black')
    #ax2.plot(mdates.date2num(TimeAirport),HumidityAirport, label='MIA Weather Station',color='#FFFF00')
    ax2.set_xlabel('Time')
    ax2.set_ylabel('Humidity')
    ax2.xaxis.set_major_formatter(DateFormatter('%m-%d'))
    ax2.xaxis.set_major_locator(HourLocator(interval=72))
    ax2.set_title('Time vs Humidity for ISeeChange Sensor Data from 08/25-11/08')
    ax2.set_ylim(0, 100)
    ax2.axis('auto')
    ax2.legend(loc='upper left')
    #ax2_sunlight.legend(loc='upper right')


    WSheatindexdata=[CalculateWSHeatIndex(T,H) for T,H in zip(WSTemperatureF,Humidity3)]
    WSheatindexdata=list(WSheatindexdata)
    for ID, data in finaldataheatindex.items():
        sensorlabel=ID[-4:]
        HItimes = data['time']
        heatindex = data['heat index']
        ax3.plot(mdates.date2num(HItimes),heatindex,label=f'SensorID:{sensorlabel}')
        
    #ax3_sunlight = ax3.twinx()
    ax3_warnings = ax3.twinx()
    #ax3_sunlight.plot(mdates.date2num(SunlightTime),Sunlight,label='Solar Radiation', color = 'gray')
    #ax3_sunlight.set_ylabel('Solar Radiation (Watts Per Meters Squared)')
    

    #WSHeatIndexTimes = mdates.date2num(Time3)
    filtereddates3 = [date for date in Time3 if startdate <= date <= enddate]
    filteredheatindex = [heatindex for date, heatindex in zip(Time3, WSheatindexdata) if startdate <= date <= enddate]
    ax3.plot(filtereddates3,filteredheatindex, label='UM Hecht Athletic Center Weatherstem',color='black')
    #ax3.plot(mdates.date2num(TimeAirport),HeatIndexAirport, label='MIA Weather Station',color='#FFFF00')
    ax3.set_xlabel('Time')
    ax3.set_ylabel('Heat Index(Degrees F)')
    ax3.xaxis.set_major_formatter(DateFormatter('%m-%d'))
    ax3.xaxis.set_major_locator(HourLocator(interval=72))
    ax3.set_title('Time vs Heat Index for ISeeChange Sensor Data from 08/25-11/08')
    ax3.axis('auto')
    ax3.legend(loc='upper left')
    #ax3_sunlight.legend(loc='upper right')
    HIcautionbox = patches.Rectangle((startdate, HICaution[0]), enddate - startdate, HICaution[1] - HICaution[0],linewidth=1, edgecolor='none', facecolor='yellow', alpha=0.4, label='Caution',zorder=50)
    ax3.add_patch(HIcautionbox)
   
    HIextremecautionbox = patches.Rectangle((startdate, HIExtremeCaution[0]), enddate - startdate, HIExtremeCaution[1] - HIExtremeCaution[0],linewidth=1, edgecolor='none', facecolor='orange', alpha=0.4, label=' Extreme Caution',zorder=50)
    ax3.add_patch(HIextremecautionbox)
    HIdangerbox = patches.Rectangle((startdate, HIDanger[0]), enddate - startdate, HIDanger[1] - HIDanger[0],linewidth=1, edgecolor='none', facecolor='red', alpha=0.4, label='Danger',zorder=50)
    ax3.add_patch(HIdangerbox)
    HIextremedangerbox = patches.Rectangle((startdate, HIExtremeDanger[0]), enddate - startdate, HIExtremeDanger[1] - HIExtremeDanger[0],linewidth=1, edgecolor='none', facecolor='violet', alpha=0.4, label=' Extreme Danger',zorder=50)
    ax3.add_patch(HIextremedangerbox)
    legend_rectangles = [patches.Patch(color='yellow', alpha=0.43, label='Caution'),patches.Patch(color='orange', alpha=0.43, label='Extreme Caution'),patches.Patch(color='red', alpha=0.43, label='Danger'),patches.Patch(color='violet', alpha=0.43, label='Extreme Danger')]
    ax3_warnings.legend(handles=legend_rectangles, loc='lower right')



    CalcWSWBGT = [CalculateWSWBGT(T,RH,SI,Direct,Diffuse,Z,P,u) for T, RH, SI,Direct,Diffuse,Z,P,u in zip(HourlyTemp, HourlyHumidity, HourlySunlight, DiffuseRad, DirectRad,SolarAngle , Pressure, WindSpeed)]
    CalcWSWBGT = list(CalcWSWBGT)
    
    for ID, data in finaldatawetbulb.items():
        sensorlabel=ID[-4:]
        WBtimes = data['time']
        WB = data['wet bulb globe']
        ax4.plot(mdates.date2num(WBtimes),WB,label=f'SensorID:{sensorlabel}')
        
    
    

    ax4.plot(mdates.date2num(SolarFinalTime),CalcWSWBGT, label= 'Weatherstem Calculated Value',color='#FFFF00' )
    filtereddates4 = [date for date in WSWBGTTime if startdate <= date <= enddate]
    filteredwetbulb = [wetbulb for date, wetbulb in zip(WSWBGTTime, WeatherStemWBGT) if startdate <= date <= enddate]
    ax4.plot(mdates.date2num(filtereddates4),filteredwetbulb, label='UM Weatherstem',color='black')
    ax4.set_xlabel('Time')
    ax4.set_ylabel('Wet Bulb Globe Temperature(Degrees C)')
    ax4.xaxis.set_major_formatter(DateFormatter('%m-%d'))
    ax4.xaxis.set_major_locator(HourLocator(interval=72))
    ax4.set_title('Time vs Wet Bulb Globe Temperature for ISeeChange Sensor Data from 08/25-11/08')
    ax4.axis('auto')
    ax4.legend(loc='upper left')
    ax4_warnings = ax4.twinx()
    
    WBGTLowbox = patches.Rectangle((startdate, WBGTLow[0]), enddate - startdate, WBGTLow[1] - WBGTLow[0],linewidth=1, edgecolor='none', facecolor='green', alpha=0.4, label='Low',zorder=50)
    ax4.add_patch(WBGTLowbox)
    WBGTModeratebox = patches.Rectangle((startdate, WBGTModerate[0]), enddate - startdate, WBGTModerate[1] - WBGTModerate[0],linewidth=1, edgecolor='none', facecolor='yellow', alpha=0.4, label='Moderate',zorder=50)
    ax4.add_patch(WBGTModeratebox)
    WBGTHighbox = patches.Rectangle((startdate, WBGTHigh[0]), enddate - startdate, WBGTHigh[1] - WBGTHigh[0],linewidth=1, edgecolor='none', facecolor='red', alpha=0.4, label='High',zorder=50)
    ax4.add_patch(WBGTHighbox)
    WBGTExtremebox = patches.Rectangle((startdate, WBGTExtreme[0]), enddate - startdate, WBGTExtreme[1] - WBGTExtreme[0],linewidth=1, edgecolor='none', facecolor='black', alpha=0.4, label='Low',zorder=50)
    ax4.add_patch(WBGTExtremebox)
    legend_rectangles = [patches.Patch(color='green', alpha=0.43, label='Low'),patches.Patch(color='yellow', alpha=0.43, label='Moderate'),patches.Patch(color='red', alpha=0.43, label='High'),patches.Patch(color='black', alpha=0.43, label='Extreme')]
    ax4_warnings.legend(handles=legend_rectangles, loc='lower right')
    matchedCalculated, matchedMeasured = CreateMatches(CalcWSWBGT,SolarFinalTime,WeatherStemWBGT, WSWBGTTime)
    ax5.scatter(matchedMeasured, matchedCalculated)
    ax5.set_xlabel('Measured Wet Bulb Globe Temperatures (Degrees C)')
    ax5.set_ylabel('Calculated Wet Bulb Globe Temperatures (Degrees C)')
    ax5.set_title('Measured vs Calculated Wet Bulb Globe Temperatures')
    ax5.plot([min(matchedMeasured),max(matchedMeasured)], [min(matchedCalculated),max(matchedCalculated)], color='red')
    slope, intercept, r_value, p_value, std_err = stats.linregress(matchedMeasured, matchedCalculated)
    r_squared = r_value ** 2

    print("R^2 value:", r_squared)


    ax5.plot()
    
    for ID, data in finaldatawetbulbtemp.items():
        sensorlabel=ID[-4:]
        WBTemptimes = data['time']
        WBTemp = data['wet bulb temp']
        ax6.plot(mdates.date2num(WBTemptimes),WBTemp,label=f'SensorID:{sensorlabel}')
        
    ax6.set_xlabel('Time')
    ax6.set_ylabel('Wet Bulb Temperature(Degrees C)')
    ax6.xaxis.set_major_formatter(DateFormatter('%m-%d'))
    ax6.xaxis.set_major_locator(HourLocator(interval=72))
    ax6.set_title('Time vs Wet Bulb Temperature for ISeeChange Sensor Data from 09/25-10/15')
    ax6.axis('auto')
    ax6.legend(loc='upper left')

    
    
    plt.show()
        
        
        
main() 