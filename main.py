import json
import numpy as np
import matplotlib.pyplot as plt
import requests
from tqdm import tqdm
import datetime
import csv
import pandas as pd


def sortListPerDate(dateList, valueList):
    lists = sorted(zip(*[dateList, valueList]))
    return list(zip(*lists))


## ETH READER
# https://www.nasdaq.com/market-activity/cryptocurrency/eth/historical
EthPerDay = {}
with open('HistoricalData_1642496997704.csv', newline='') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=',')
    for row in spamreader:
        try:
            dt = datetime.datetime.strptime(row[0], "%m/%d/%Y").strftime("%Y-%m-%d")
            EthPerDay[dt] = float(row[4])
        except ValueError:
            None

## ValeurFonciere
# https://www.data.gouv.fr/fr/datasets/demandes-de-valeurs-foncieres/
fileForValue = ["valeursfoncieres-2017.txt", "valeursfoncieres-2018.txt", "valeursfoncieres-2019.txt",
                "valeursfoncieres-2020.txt", "valeursfoncieres-2021-s1.txt"]

ValuePerDay = {}
for f in fileForValue[3:5]:
    with open(f) as txtfile:
        spamreader = csv.reader(txtfile, delimiter='|')
        for row in tqdm(spamreader, desc=f):
            try:
                newValue = int(row[10].replace(",00", ""))
                dep = row[18]
                dt = datetime.datetime.strptime(row[8], "%d/%m/%Y").strftime("%Y-%m-%d")

                try:
                    ValuePerDay[dep] != 0
                except KeyError:
                    ValuePerDay[dep] = {}

                try:
                    if ValuePerDay[dep][dt] != 0:
                        ValuePerDay[dep][dt] = (ValuePerDay[dt] + newValue) / 2
                    else:
                        ValuePerDay[dep][dt] = newValue
                except KeyError:
                    ValuePerDay[dep][dt] = newValue

            except ValueError:
                None

## NumberSellPerTrimestre
# http://www.cgedd.developpement-durable.gouv.fr/prix-immobilier-evolution-a-long-terme-a1048.html
# https://www.cgedd.fr/nombre-vente-maison-appartement-ancien.xls

SellPerDay = {}
xls = pd.ExcelFile(r"nombre-vente-maison-appartement-ancien.xls")  # use r before absolute file path
sheetX = pd.read_excel(xls,
                       'Données - data')  # 2 is the sheet number+1 thus if the file has only 1 sheet write 0 in paranthesis

dates = sheetX["Unnamed: 2"]
sells = sheetX["Unnamed: 3"]

for idx in range(22, 307):
    dt = str(dates[idx]).split()[0]
    if sells[idx] != "-":
        SellPerDay[dt] = int(sells[idx])

## Covid Data
# https://github.com/owid/covid-19-data/tree/master/public/data
# https://covid.ourworldindata.org/data/owid-covid-data.json
with open('owid-covid-data.json') as f:
    data = json.load(f)


houseValue, houseDate = [], []
ethValue, ethDate = [], []
covidValue, covidDate = [], []
sellValue, sellDate = [], []

countryData = data["FRA"]
for e in tqdm(countryData['data'], desc="FRA"):
    date = e['date']
    try:
        houseValue.append(int(ValuePerDay['91'][date])/10620000)
        houseDate.append(date)
    except KeyError:
        None

    try:
        covidValue.append(e['new_cases']/368379.0)
        covidDate.append(date)
    except KeyError:
        None

    try:
        ethValue.append(EthPerDay[e['date']]/4813.62)
        ethDate.append(date)
    except KeyError:
        None

    try:
        sellValue.append(SellPerDay[e['date']]/1211)
        sellDate.append(date)
    except KeyError:
        None

houseDate, houseValue = sortListPerDate(houseDate, houseValue)
ethDate, ethValue = sortListPerDate(ethDate, ethValue)
covidDate, covidValue = sortListPerDate(covidDate, covidValue)
sellDate, sellValue = sortListPerDate(sellDate, sellValue)

plt.plot(covidDate, covidValue, label="Case per day", linestyle=":")
# plt.plot(ethDate, ethValue, label="Eth Value", linestyle="-")
plt.plot(sellDate, sellValue, label="Number Sell", linestyle="-.")
plt.plot(houseDate, houseValue, label="House Price")

plt.legend()
plt.show()
