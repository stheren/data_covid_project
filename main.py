import json
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm

import csv

EthPerDay = {}

with open('coin_Ethereum.csv', newline='') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=',')
    for row in spamreader:
        try:
            EthPerDay[row[3].split()[0]] = float(row[4])
        except ValueError:
            None



with open('owid-covid-data.json') as f:
    data = json.load(f)


# selectedCountry = ['IND', 'FRA', 'USA']
selectedCountry = ['FRA']

for country in selectedCountry:
    x, y, z, k, eth = [], [], [], [], []
    countryData = data[country]
    for e in tqdm(countryData['data'], desc=country):
        try:
            if e['new_deaths'] > 0:
                k.append(e['new_deaths']/1500)
            else:
                k.append(0)
                print(e)
        except KeyError:
            k.append(0)

        try:
            z.append(e['people_fully_vaccinated']/countryData['population'])
        except KeyError:
            z.append(0)

        try:
            y.append(e['new_cases']/400000)
        except KeyError:
            y.append(0)
        try:
            eth.append(EthPerDay[e['date']]/4500)
        except KeyError:
            eth.append(0)

        x.append(e['date'])
        
    plt.plot(x, y, label="Case per day")
    plt.plot(x, z, label="Vaccinated (%)", linestyle=":")
    plt.plot(x, k, label="Death per day", linestyle="-.")
    # plt.plot(x, eth, label="Eth Value", linestyle="-")

plt.legend()
plt.show()  # affiche la figure a l'ecran
