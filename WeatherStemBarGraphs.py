import matplotlib.pyplot as plt
from datetime import datetime
import os
import math
import numpy as np


def ReadWSData(locations,folderpath,variable, nheaders = 0):
    WSData = {}

    for location in locations:
        filename = os.path.join(folderpath,location)
        fullFileName = filename + variable + ".csv"
        heatindex = []
        temp = []
        humidity = []
        Time = []
    
        with open(fullFileName,'r') as fobjs:    
            linelist = fobjs.readlines()                
            
        for line in linelist[nheaders:]:
            words=line.split(',')
            heatindex.append((float(words[1])))
            humidity.append((float(words[2])))
            temp.append((float(words[3])))
            time=(datetime.strptime(words[0],'%Y-%m-%d %H:%M:%S'))
            Time.append(time.date())
           
            
        WSData[location] = {"dates":Time,"humidity":humidity,"temp":temp,"heatindex": heatindex}

        
    return WSData
  
def getSeason(month):
    if month in [12,1,2]:
        return 'DJF'
    elif month in [3,4,5]:
        return 'MAM'
    elif month in [6,7,8]:
        return 'JJA'
    elif month in [9,10,11]:
        return 'SON'

def PlotSeasonalData(seasonalData, distances, title,ylabel):
    colorMap = plt.cm.get_cmap('coolwarm')
    norm = plt.Normalize(vmin=1, vmax=12)
    fig, axes = plt.subplots(1, 4, figsize=(20, 6), sharey=False)
    fig.suptitle(title)

    for ax, season in zip(axes, ['DJF', 'MAM', 'JJA', 'SON']):
        sortedLocations = sorted(seasonalData[season].keys(), key=lambda loc: distances[loc])
        dataToPlot = [seasonalData[season][loc] for loc in sortedLocations]
        Max = max(dataToPlot)
        Min = min(dataToPlot)
        ax.bar(range(len(sortedLocations)), dataToPlot, color=[colorMap(norm(distances[loc])) for loc in sortedLocations])
        ax.set_title(season)
        ax.set_xticks(range(len(sortedLocations)))
        ax.set_xticklabels(sortedLocations, rotation=90)
        ax.set_ylabel(ylabel)
        ax.set_ylim(Min-3,Max+3)

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.show()

def main():    
    folderpath='/Users/ericschmitt/Documents/Heat Project Data'
    nheaders = 1
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

    variables = ['Avg','Min','Max']
    WSDataAvg = ReadWSData(locations,folderpath,variables[0], nheaders)
    WSDataMin = ReadWSData(locations,folderpath,variables[1], nheaders)
    WSDataMax = ReadWSData(locations,folderpath,variables[2], nheaders)
        
    seasonalAvgHumidity = {'DJF':{},'MAM':{},'JJA':{},'SON':{}}
    seasonalMaxHumidity = {'DJF':{},'MAM':{},'JJA':{},'SON':{}}
    seasonalMinHumidity = {'DJF':{},'MAM':{},'JJA':{},'SON':{}}
    seasonalAvgTemp = {'DJF':{},'MAM':{},'JJA':{},'SON':{}}
    seasonalMaxTemp = {'DJF':{},'MAM':{},'JJA':{},'SON':{}}
    seasonalMinTemp = {'DJF':{},'MAM':{},'JJA':{},'SON':{}}
    seasonalAvgHI = {'DJF':{},'MAM':{},'JJA':{},'SON':{}}
    seasonalMaxHI = {'DJF':{},'MAM':{},'JJA':{},'SON':{}}
    seasonalMinHI = {'DJF':{},'MAM':{},'JJA':{},'SON':{}}
    for location in locations:
        for season in seasonalAvgHumidity:
            seasonalAvgHumidity[season][location] = []
            seasonalMaxHumidity[season][location] = []
            seasonalMinHumidity[season][location] = []
            seasonalAvgTemp[season][location] = []
            seasonalMaxTemp[season][location] = []
            seasonalMinTemp[season][location] = []
            seasonalAvgHI[season][location] = []
            seasonalMaxHI[season][location] = []
            seasonalMinHI[season][location] = []
            

    for location,data in WSDataAvg.items():
        avgdates = data['dates']
        avghumidity = data['humidity']
        avgtemp = data['temp']
        avgHI = data['heatindex']
        for date, hum, temp, hi in zip(avgdates,avghumidity, avgtemp, avgHI):
            season = getSeason(date.month)
            seasonalAvgHumidity[season][location].append(hum)
            seasonalAvgTemp[season][location].append(temp)
            seasonalAvgHI[season][location].append(hi)
    for season in seasonalAvgHumidity:
        for location in seasonalAvgHumidity[season]:
            seasonalAvgHumidity[season][location] = np.mean(seasonalAvgHumidity[season][location])
    
    for season in seasonalAvgTemp:
        for location in seasonalAvgTemp[season]:
            seasonalAvgTemp[season][location] = np.mean(seasonalAvgTemp[season][location])
            
    for season in seasonalAvgHI:
        for location in seasonalAvgHI[season]:
            seasonalAvgHI[season][location] = np.mean(seasonalAvgHI[season][location])
            
    
    for location,data in WSDataMin.items():
        mindates = data['dates']
        minhumidity = data['humidity']
        mintemp = data['temp']
        minHI = data['heatindex']
        for date, hum, temp, hi in zip(mindates,minhumidity, mintemp, minHI):
            season = getSeason(date.month)
            seasonalMinHumidity[season][location].append(hum)
            seasonalMinTemp[season][location].append(temp)
            seasonalMinHI[season][location].append(hi)
    for season in seasonalMinHumidity:
        for location in seasonalMinHumidity[season]:
            seasonalMinHumidity[season][location] = np.mean(seasonalMinHumidity[season][location])
    
    for season in seasonalMinTemp:
        for location in seasonalMinTemp[season]:
            seasonalMinTemp[season][location] = np.mean(seasonalMinTemp[season][location])
            
    for season in seasonalMinHI:
        for location in seasonalMinHI[season]:
            seasonalMinHI[season][location] = np.mean(seasonalMinHI[season][location])
            
    
    for location,data in WSDataMax.items():
        maxdates = data['dates']
        maxhumidity = data['humidity']
        maxtemp = data['temp']
        maxHI = data['heatindex']
        for date, hum, temp, hi in zip(maxdates,maxhumidity, maxtemp, maxHI):
            season = getSeason(date.month)
            seasonalMaxHumidity[season][location].append(hum)
            seasonalMaxTemp[season][location].append(temp)
            seasonalMaxHI[season][location].append(hi)
    for season in seasonalMaxHumidity:
        for location in seasonalMaxHumidity[season]:
            seasonalMaxHumidity[season][location] = np.mean(seasonalMaxHumidity[season][location])
    
    for season in seasonalMaxTemp:
        for location in seasonalMaxTemp[season]:
            seasonalMaxTemp[season][location] = np.mean(seasonalMaxTemp[season][location])
            
    for season in seasonalMaxHI:
        for location in seasonalMaxHI[season]:
            seasonalMaxHI[season][location] = np.mean(seasonalMaxHI[season][location])

   
    PlotSeasonalData(seasonalAvgHumidity, distances, 'Average Humidity by Season','Relative Humidity(%)') 
    PlotSeasonalData(seasonalMinHumidity, distances, 'Average Minimum Humidity by Season','Relative Humidity(%)') 
    PlotSeasonalData(seasonalMaxHumidity, distances, 'Average Maximum Humidity by Season','Relative Humidity(%)') 
    
    PlotSeasonalData(seasonalAvgTemp, distances, 'Average Temperature by Season','Temperature(Degrees F)') 
    PlotSeasonalData(seasonalMinTemp, distances, 'Average Minimum Temperature by Season','Temperature(Degrees F)') 
    PlotSeasonalData(seasonalMaxTemp, distances, 'Average Maximum Temperature by Season','Temperature(Degrees F)') 
    
    PlotSeasonalData(seasonalAvgHI, distances, 'Average Heat Index by Season','Temperature(Degrees F)') 
    PlotSeasonalData(seasonalMinHI, distances, 'Average Minimum Heat Index by Season','Temperature(Degrees F)') 
    PlotSeasonalData(seasonalMaxHI, distances, 'Average Maximum Heat Index by Season','Temperature(Degrees F)') 
    
        
main()       
