import matplotlib.pyplot as plt
from datetime import datetime
import os
import math
import numpy as np

def CalculateRelativeHumidity(T,TD):
   RH=100*(math.exp((17.625*TD)/(243.04+TD))/math.exp((17.625*T)/(243.04+T))) 
   return RH

def ReadWSData(locations,folderpath, nheaders = 0):
    WSData = {}

    for location in locations:
        filename = os.path.join(folderpath,location)
        fullFileName = filename + ".csv"
        humidity = []
        time = []
        rainfall = []
    
        with open(fullFileName,'r') as fobjs:    
            linelist = fobjs.readlines()                
        
        DailyAverageHumidity = {}
        DailyCount = {}
        DailyAverageRainfall = {}
        
        for line in linelist[nheaders:]:
            words=line.split(',')
            humidity = (float(words[1]))
            rainfall = (float(words[2]))
            time=(datetime.strptime(words[0],'%Y-%m-%d %H:%M:%S'))
            day = time.date()
            if day not in DailyAverageHumidity:
                DailyAverageRainfall[day] = 0
                DailyAverageHumidity[day] = 0
                DailyCount[day] = 0
            DailyAverageHumidity[day] += humidity
            DailyCount[day] += 1
            DailyAverageRainfall[day] += rainfall
            
        AveragedHumidity = {}
        AveragedRainfall = {}
        for Day in DailyAverageHumidity:
            AveragedHumidity[Day] = DailyAverageHumidity[Day] / DailyCount[Day]
            
        for Day in DailyAverageRainfall:
            AveragedRainfall[Day] = DailyAverageRainfall[Day] / DailyCount[Day]
            
        WSData[location] = {"dates": list(DailyAverageHumidity.keys()),"humidity":list(AveragedHumidity.values()), "rainfall":list(AveragedRainfall.values())}
        
    return WSData
        
              
                

def ReadAirportData(filename4, nheaders4=0):
    HourlyAverageHumidity = {}
    HourlyCount = {}
    translationTable = str.maketrans({char: '0' for char in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'})

    
    
    with open(filename4,'r') as fobjs:    
        linelist = fobjs.readlines() 
    for line in linelist[nheaders4:]:
        words=[word.strip('"') for word in line.rstrip().split(',')]

        if len(words) >= 8 and words[8]!='+9999' and words[6]!='+9999':
            try:
                Dewpointstr=(words[6].split('+')[1].split('"'))
                Dewpoint=''.join(Dewpointstr+[words[7]])
                if any(char.isalpha() for char in Dewpoint):
                    DewFinal = float(Dewpoint.translate(translationTable))
                else:
                    DewFinal=(float(Dewpoint.replace(',','.')))/100
            except IndexError:
                try:
                    Dewpointstr=(words[6].split('-')[1].split('"'))
                    Dewpoint=''.join(Dewpointstr+[words[7]])
                    DewFinal=((float(Dewpoint.replace(',','.')))/100) * (-1)
                except IndexError:
                    print('Error')
                    continue
            Temperaturestr=(words[8].split('+')[1].split('"'))
            Temperature=''.join(Temperaturestr+[words[9]])
            if any(char.isalpha() for char in Temperature):
                TempFinal = float(Temperature.translate(translationTable))
            else:
                TempFinal=(float(Temperature.replace(',','.')))/100
            Humidity= CalculateRelativeHumidity(TempFinal,DewFinal)
            ReadTime=datetime.strptime(words[1],'%Y-%m-%dT%H:%M:%S')
            Time=datetime.strftime(ReadTime,'%Y-%m-%d 00:00:00')
            if Time not in HourlyAverageHumidity:
                HourlyAverageHumidity[Time] = 0
                HourlyCount[Time] = 0
            HourlyAverageHumidity[Time] += Humidity
            HourlyCount[Time] += 1
    AveragedHumidity = []
    AveragedTimes = []
    
    for Hour in HourlyAverageHumidity:
        AveragedHumidity.append(HourlyAverageHumidity[Hour] / HourlyCount[Hour])
        AveragedTimes.append(Hour)
        
    return AveragedHumidity, AveragedTimes
        
def CreateMatches(MIAHumidity,MIATime,WSHumidity, WSTime):
    MIADict = {time: value for time, value in zip(MIATime, MIAHumidity)}
    matchedMIA = []
    matchedWS = []
    FinalWSTime = [time.strftime('%Y-%m-%d 00:00:00') for time in WSTime]
    for time, humidity in zip(FinalWSTime, WSHumidity):
        if time in MIADict:
            matchedMIA.append(MIADict[time])
            matchedWS.append(humidity)      
    return matchedMIA, matchedWS

def GetMatchedData(AveragedHumidity, AveragedTimes, WSData, locations):
    matchedData = {}
    for location in locations:
        WSDict = WSData[location]
        WSTime = WSDict['dates']
        WSHumidity = WSDict['humidity']
        WSRainfall = WSDict['rainfall']
        matchedMIA, matchedWS = CreateMatches(AveragedHumidity, AveragedTimes, WSHumidity, WSTime)
        matchedData[location] = (matchedMIA,matchedWS, WSRainfall)
        
    return matchedData

def getSeason(month):
    if month in [12,1,2]:
        return 'DJF'
    elif month in [3,4,5]:
        return 'MAM'
    elif month in [6,7,8]:
        return 'JJA'
    elif month in [9,10,11]:
        return 'SON'
    
def getRainfallShape(rainfall):
    if 0 <= rainfall < 0.15:
        return 'o'
    if 0.15 <= rainfall < .3:
        return '^'
    if .3 <= rainfall < .5:
        return 's'
    if .5 <= rainfall < 1:
        return '*'
    if rainfall >= 1:
        return 'x'
    

        
def main():
    nheaders, nheaders2 = 1,1
    folderpath='/Users/ericschmitt/Documents/Heat Project Data'
    MIAFilename = os.path.join(folderpath,'FullAirportData.csv')
    locations = ['MDCHialeah', 'MDCHomestead', 'MDCNorth', 'Frost', 'MDCWest', 'MDCWolfson', 'SunnyIsles', 'Rockway', 'UMiamiHealth', 'UMiamiHecht', 'UMiamiRosenstiel', 'UMiami']
    distances = {
        'SunnyIsles': 1,
        'UMiamiRosenstiel': 2,
        'Frost': 3,
        'MDCWolfson': 4,
        'UMiamiHealth': 5,
        'UMiami': 6,
        'UMiamiHecht': 7,
        'MDCNorth': 8,
        'Rockway': 9,
        'MDCHomestead': 10,
        'MDCHialeah': 11,
        'MDCWest': 12,   
    }
    colorMap = plt.cm.get_cmap('coolwarm')
    norm = plt.Normalize(vmin=1,vmax=12)
    WSData = ReadWSData(locations,folderpath,nheaders)
    AveragedHumidity, AveragedTimes = ReadAirportData(MIAFilename, nheaders2)
    DateTimeAvgTime = [datetime.strptime(timeStr, '%Y-%m-%d %H:%M:%S' ) for timeStr in AveragedTimes]
    matchedData = GetMatchedData(AveragedHumidity, AveragedTimes, WSData, locations)
    rainLegend = [plt.Line2D([],[],linestyle = 'None', marker = 'o', markersize = 10, color = 'black', label = '0.0 - 0.15'),
                  plt.Line2D([],[],linestyle = 'None', marker = '^', markersize = 10, color = 'black', label = '0.15 - 0.3'),
                  plt.Line2D([],[],linestyle = 'None', marker = 's', markersize = 10, color = 'black', label = '0.3 - 0.5'),
                  plt.Line2D([],[],linestyle = 'None', marker = '*', markersize = 10, color = 'black', label = '0.5 - 1.0'),
                  plt.Line2D([],[],linestyle = 'None', marker = 'x', markersize = 10, color = 'black', label = '1.0+'),]
    

    seasonData = {'DJF': [], 'MAM': [], 'JJA': [], 'SON': []}
    allStationData = {location : [] for location in matchedData.keys() }
    for location, (matchedMIA, matchedWS, rainfall) in matchedData.items():
        allStationData[location] = matchedWS
        for mia, ws, time, rain in zip(matchedMIA, matchedWS, DateTimeAvgTime, rainfall):
            month = time.month
            season = getSeason(month)
            seasonData[season].append((mia,ws,location, rain))
    
    for season,data in seasonData.items():
        plt.figure(figsize=(35,20))
        plt.title(f'MIIA vs Miami-Dade Weatherstem Stations ({season})')
        addedLocations = set()
        for mia, ws, location, rain in data:
            color = colorMap(norm(distances[location]))
            shape = getRainfallShape(rain)
            if location not in addedLocations:
                plt.scatter(mia, ws, label=location, color=color, marker=shape, alpha=1)
                addedLocations.add(location)
            else:
                plt.scatter(mia, ws, color=color, marker=shape, alpha=1)
                
        plt.plot([35, 100], [35, 100], color='red', linestyle='--')  # 
        plt.xlabel('MIA Humidity')
        plt.ylabel('Weatherstem Humidity')
        plt.xticks(range(35,100,10))
        plt.yticks(range(35,100,10))
        locationLegend = plt.legend(loc='upper left')
        plt.gca().add_artist(locationLegend)
        plt.legend(handles=rainLegend, loc='lower right')
        plt.grid(True)
        plt.gca().set_facecolor('black')
        plt.show()
                   
    
    plt.figure(figsize=(35,20))
    for location, (matchedMIA, matchedWS, rainfall) in matchedData.items():
        color = colorMap(norm(distances[location]))
        initialShape = getRainfallShape(rainfall[0])
        plt.scatter(matchedMIA[0], matchedWS[0], label=location, color=color, marker=initialShape, alpha=1)
        for mia, ws, rain in zip(matchedMIA[1:], matchedWS[1:], rainfall[1:]):
            shape = getRainfallShape(rain)
            plt.scatter(mia, ws,color=color, marker=shape, alpha=1)
       
    plt.plot([35, 100], [35, 100], color='red', linestyle='--')  # 
    plt.xlabel('MIA Humidity')
    plt.ylabel('Weatherstem Humidity')
    plt.title('MIA vs Miami-Dade Weatherstem Stations')
    plt.xticks(range(35,100,10))
    plt.yticks(range(35,100,10))
    locationLegend = plt.legend(loc='upper left')
    plt.gca().add_artist(locationLegend)
    plt.legend(handles=rainLegend, loc='lower right')
    plt.grid(True)
    plt.gca().set_facecolor('black')
    plt.show()
    
    avgRH = [np.mean(data) for data in allStationData.values()]
    stations = list(allStationData.keys())
    colors = [colorMap(norm(distances[station])) for station in stations]
    plt.figure(figsize=(10,6))
    plt.bar(stations, avgRH, color=colors)
    plt.title('Average Relative Humidity by Station')
    plt.xlabel('Station')
    plt.ylabel('Average Relative Humidity')
    plt.xticks(rotation=45)
    plt.grid(axis='y')
    plt.show()
    
    
    
main()
    
        
    
    

        
    
        
            
                
       

     

