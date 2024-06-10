import math
from datetime import datetime
import os
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import percentileofscore
import pandas as pd


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
    

def CalculateRelativeHumidity(T,TD):
   RH=100*(math.exp((17.625*TD)/(243.04+TD))/math.exp((17.625*T)/(243.04+T))) 
   return RH

def ReadAirportData(filename, nheaders=0):
    dailyMaxHI = {}
    dailyMaxTemp = {}
    Tmax=[]
    dailyMinTemp = {}
    tempSum = {}
    tempCount = {}
    dailyAvgTemp = {}

    with open(filename,'r') as fobjs:    
        linelist = fobjs.readlines() 
    for line in linelist[nheaders:]:
        words=[word.strip('"') for word in line.rstrip().split(',')]
        if len(words) >= 8 and words[8]!='+9999' and words[6]!='+9999':
            ReadTime=datetime.strptime(words[1],'%Y-%m-%dT%H:%M:%S')
            if ReadTime.month in range(1,13):
                if words[9].isdigit():
                    if words[7].isdigit():
                        DateCheck = datetime.strftime(ReadTime,'%Y-%m-%d')
                        Temperaturestr=(words[8].split('+')[1].split('"'))
                        Temperature=''.join(Temperaturestr+[words[9]])
                        TempFinal=(float(Temperature.replace(',','.')))/100
                  
                        #Dewpointstr=(words[6].split('+')[1].split('"'))
                       # Dewpoint=''.join(Dewpointstr+[words[7]])
                        #DewFinal=(float(Dewpoint.replace(',','.')))/100
                        #Humidity= CalculateRelativeHumidity(TempFinal,DewFinal)
                        Ftemp=(TempFinal * 9/5) + 32
                        #HeatIndex=CalculateHeatIndex(Ftemp,Humidity)
                        Tmax.append(Ftemp)
                        #if DateCheck not in dailyMaxHI:
                            #dailyMaxHI[DateCheck] = HeatIndex
                       # else:
                           # dailyMaxHI[DateCheck] = max(dailyMaxHI[DateCheck], HeatIndex)
                        if DateCheck not in dailyMaxTemp:
                            dailyMaxTemp[DateCheck] = TempFinal
                        else:
                            dailyMaxTemp[DateCheck] = max(dailyMaxTemp[DateCheck], TempFinal)
                        if DateCheck not in dailyMinTemp:
                            dailyMinTemp[DateCheck] = TempFinal
                        else:
                            dailyMinTemp[DateCheck] = min(dailyMinTemp[DateCheck], TempFinal)
                        if DateCheck not in tempSum:
                            tempSum[DateCheck] = TempFinal
                            tempCount[DateCheck] = 1
                        else:
                            tempSum[DateCheck] += TempFinal
                            tempCount[DateCheck] += 1
                            
    for day in tempSum:
        dailyAvgTemp[day] = tempSum[day] / tempCount[day]
                            
        
    return dailyMaxHI, dailyMaxTemp, dailyMinTemp, dailyAvgTemp

def CalculatePercentiles(dailyMaxTemp, dailyMinTemp, dailyAvgTemp, targetDate):
    dateKey = targetDate.strftime('%Y-%m-%d')
    dayMonth = targetDate.strftime('%m-%d')
    
    maxTemps = [temp for date,temp in dailyMaxTemp.items() if date.endswith(dayMonth)]
    minTemps = [temp for date,temp in dailyMinTemp.items() if date.endswith(dayMonth)]
    avgTemps = [temp for date,temp in dailyAvgTemp.items() if date.endswith(dayMonth)]
    
    maxTemp = dailyMaxTemp[dateKey]
    minTemp = dailyMinTemp[dateKey]
    avgTemp = dailyAvgTemp[dateKey]
    
    maxPercentile = percentileofscore(maxTemps,maxTemp) if maxTemp is not None else None
    roundedMaxPercentile = round(maxPercentile,2) if maxPercentile is not None else None
    minPercentile = percentileofscore(minTemps, minTemp) if minTemp is not None else None
    roundedMinPercentile = round(minPercentile,2) if minPercentile is not None else None
    avgPercentile = percentileofscore(avgTemps, avgTemp) if avgTemp is not None else None
    roundedAvgPercentile = round(avgPercentile,2) if avgPercentile is not None else None
    
    return roundedMaxPercentile, roundedMinPercentile, roundedAvgPercentile
    
def ProcessPsychData(inputCSV, dailyMaxTemp, dailyMinTemp, dailyAvgTemp):
     df = pd.read_csv(inputCSV)
     df.dropna(how='all',inplace=True)
     newColumns = ['MaxTempPercentileT1', 'MinTempPercentileT1', 'AvgTempPercentileT1',
                          'MaxTempPercentileT2', 'MinTempPercentileT2', 'AvgTempPercentileT2',
                          'MaxTempPercentileT3', 'MinTempPercentileT3', 'AvgTempPercentileT3']
     for col in newColumns:
         df[col] = None
         
     for i,row in df.iterrows():
        for timepoint in ['T1', 'T2', 'T3']:
            datecol = f'StartDate{timepoint}'
            if pd.notna(row[datecol]):
                targetDate = datetime.strptime(row[datecol], '%m/%d/%Y')
                maxPerc,minPerc,avgPerc = CalculatePercentiles(dailyMaxTemp,dailyMinTemp,dailyAvgTemp,targetDate)
                df.at[i,f'MaxTempPercentile{timepoint}'] = maxPerc
                df.at[i,f'MinTempPercentile{timepoint}'] = minPerc
                df.at[i,f'AvgTempPercentile{timepoint}'] = avgPerc
                
     outputCSV = 'PsychStudyDataPercentiles.csv'
     df.to_csv(outputCSV, index=False)

def CreateProbDist(dailyMaxHI, dailyMaxTemp):
    heatIndexValues = [round(hi) for hi in dailyMaxHI.values()]
    totalDays = len(heatIndexValues)
    plt.figure(figsize=(10,6))
    plt.hist(heatIndexValues, bins=range(int(min(heatIndexValues)), int(max(heatIndexValues))+1), color='#5C4033', weights=[1/totalDays] * len(heatIndexValues))
    plt.xlabel('HI (Degrees F)')
    plt.xlim(min(heatIndexValues)-2, max(heatIndexValues)+2)
    plt.ylabel('Probability')
    plt.title('HI Frequencies Recorded at MIA for May-October 2010-2024')
    plt.xticks(range(65,120,5))
    plt.yticks(np.arange(0.0,0.1,0.02))
    plt.axvspan(80,90,color='yellow', alpha=0.3, label='Caution',linewidth=0)
    plt.axvspan(90,103, color='orange', alpha=0.3, label='Extreme Caution',linewidth=0)
    plt.axvspan(103,124, color='red', alpha=0.3, label='Danger',linewidth=0)
    plt.axvspan(0,0, color='#800000', alpha=0.3, label='Extreme Danger',linewidth=0)
    plt.legend(loc='upper right')
    
    tempValues = [round(temp) for temp in dailyMaxTemp.values()]
    plt.figure(figsize=(10,6))
    days = len(tempValues)
    plt.hist(tempValues, bins=range(int(min(tempValues)), int(max(tempValues))+1), color='#5C4033', weights=[1/days] * len(tempValues))
    plt.xlabel('Temperature (Degrees F)')
    plt.xlim(min(tempValues)-2, max(tempValues)+2)
    plt.ylabel('Probability')
    plt.title('Temperature Frequencies Recorded at MIA for May-October 2010-2024')
    

    

    plt.show()

        

def main():
    folderpath='/Users/ericschmitt/Documents/Heat Project Data'
    filename = os.path.join(folderpath,'1993MIAData.csv')
    inputCSV = os.path.join(folderpath,'PsychStudyData.csv')
    nheaders = 1
    dailyMaxHI, dailyMaxTemp,dailyMinTemp, dailyAvgTemp = ReadAirportData(filename,nheaders)
    #CreateProbDist(dailyMaxHI,dailyMaxTemp)
    ProcessPsychData(inputCSV, dailyMaxTemp, dailyMinTemp, dailyAvgTemp)

main()
    
    