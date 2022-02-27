import csv
import datetime
import json
import sys

import matplotlib.pyplot as plt
import pandas as pd
import tqdm


def displayData(d):
    caseMax, ethMax, sellMax, priceMax = 0, 0, 0, 0
    for elt in d:
        caseMax = max(caseMax, elt["case_per_day"])
        ethMax = max(ethMax, elt["eth_value"])
        sellMax = max(sellMax, elt["Number_of_sell"])
        priceMax = max(priceMax, elt["Price_of_sell"])

    dates, cases, eths, sells, prices = [], [], [], [], []
    for elt in d:
        dates.append(elt["date"])
        cases.append(elt["case_per_day"] / caseMax)
        eths.append(elt["eth_value"] / ethMax)
        sells.append(elt["Number_of_sell"] / sellMax)
        prices.append(elt["Price_of_sell"] / priceMax)

    plt.plot(dates, cases, label="Case per day", linestyle=":")
    plt.plot(dates, eths, label="Eth Value", linestyle="-")
    plt.plot(dates, sells, label="Number Sell", linestyle="-.")
    plt.plot(dates, prices, label="House Price")

    plt.legend()
    plt.show()


if len(sys.argv) > 1:
    with open('json_data_out.json') as f:
        displayData(json.load(f))
    exit()


def sortListPerDate(dateList, valueList):
    lists = sorted(zip(*[dateList, valueList]))
    return list(zip(*lists))


## ETH READER
# https://www.nasdaq.com/market-activity/cryptocurrency/eth/historical
EthPerDay = {}
with open('HistoricalData_1645971630465.csv', newline='') as csvfile:
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

result = []
countryData = data["FRA"]
for e in tqdm(countryData['data'], desc="FRA"):
    date = e['date']
    result.append({
        "date": date,
        "case_per_day": 0.0,
        "Number_of_sell": 0.0,
        "Price_of_sell": 0.0,
        "eth_value": 0.0

    })
    try:
        result[-1]["Price_of_sell"] = ValuePerDay['91'][date]
    except KeyError:
        try:
            result[-1]["Price_of_sell"] = result[-2]["Price_of_sell"]
        except IndexError:
            None

    try:
        result[-1]['case_per_day'] = e['new_cases']
    except KeyError:
        try:
            result[-1]['case_per_day'] = result[-2]['case_per_day']
        except IndexError:
            None

    try:
        result[-1]["eth_value"] = EthPerDay[e['date']]
    except KeyError:
        try:
            result[-1]["eth_value"] = result[-2]["eth_value"]
        except IndexError:
            None

    try:
        result[-1]["Number_of_sell"] = SellPerDay[e['date']]
    except KeyError:
        try:
            result[-1]["Number_of_sell"] = result[-2]["Number_of_sell"]
        except IndexError:
            None

with open('json_data_out.json', 'w') as outfile:
    outfile.write(json.dumps(result))

displayData(result)
