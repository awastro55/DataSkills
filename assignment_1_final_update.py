#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 14 22:42:34 2019

@author: andrewweis
"""

#Data Skills for Public Policy Pset1.  Reorganizing code.

#Import packages
import os
import us
import pandas as pd
import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt

#Webscraping function to create our csv files
def get_webpage(urls, filepath, data=None, headers=None, return_soup=True): 
    for url in urls:
        if data:
            response=requests.post(url, data=data)
        else:
            response=requests.get(url)
        soup=BeautifulSoup(response.text)
        state, measure, month = response.text.split('\n')[0].split(', ')

        with open(os.path.join(filepath, state+'_'+month+'.csv'), 'w') as ofile:
            ofile.write(response.text)
    if return_soup:
        return soup
    else: 
        return response
    
#Function to create data frame
def create_df(filepath, skiprows=0):
    dfs=[]
    files=os.listdir(filepath)
    for f in files:
        #print('f=',f)
        state, month = f.split('_')
        if f=='.DS_Store':
            continue
        df = pd.read_csv(os.path.join(filepath, f), skiprows=skiprows)
        df['State'] = state
        #print(state)
        df['Date'] = pd.to_datetime(df['Date'], format='%Y%m')
        dfs.append(df)
    df=pd.concat(dfs)
    df=df.sort_values(['State', 'Date'])
    
    return df

#Plotting function--temperature difference plot
def plotdiff(filepath_plotdiff,df,states):
    df['Year'] = df['Date'].map(lambda d: d.year)
    #print(df['Year'])
    df['Jan-Aug Delta'] = df.groupby(['State', 'Year'])['Value'].diff()
    df_delta = df.dropna(subset=['Jan-Aug Delta'])[['State', 'Year', 'Jan-Aug Delta']]
    #print(df_delta)

    fig, ax = plt.subplots(len(states), 1)
    il = df_delta[df_delta['State'] == states[0]]
    ax[0].plot(il['Year'], il['Jan-Aug Delta'], 'k-')
    ax[0].set_ylabel('Illinois')
    ax[0].xaxis.tick_top()

    ca = df_delta[df_delta['State'] == states[1]]
    #print(ca)
    ax[1].plot(ca['Year'], ca['Jan-Aug Delta'], 'r-')
    ax[1].set_ylabel('California')
    ax[1].set_label('')
    ax[1].set_xticks([])
    ax[1].xaxis.set_ticks_position('none')

    ny = df_delta[df_delta['State'] == states[2]]
    ax[2].plot(ny['Year'], ny['Jan-Aug Delta'], 'b-')
    ax[2].set_ylabel('New York')
    ax[2].set_label('')
    ax[2].set_xticks([])
    ax[2].xaxis.set_ticks_position('none')

    tx = df_delta[df_delta['State'] == states[3]]
    ax[3].plot(tx['Year'], tx['Jan-Aug Delta'], 'g-')
    ax[3].set_ylabel('Texas')

    plt.suptitle('Average Jan-Aug Temperature Variation')
    plt.savefig(filepath_plotdiff)
    plt.show()
    
def plotmonth(filepath_plotmonth,df,states):
    df['Month'] = df['Date'].map(lambda d: d.month)
    df_aug = df[df['Month'] == 8]

    fig, ax = plt.subplots(1, 1)
    il = df_aug[df_aug['State'] == states[0]]
    ca = df_aug[df_aug['State'] == states[1]]
    ny = df_aug[df_aug['State'] == states[2]]
    tx = df_aug[df_aug['State'] == states[3]]

    print('Max/Mean/Min for Illinois:', il['Value'].max(), il['Value'].mean(), il['Value'].min())
    print('Max/Mean/Min for California:', ca['Value'].max(), ca['Value'].mean(), ca['Value'].min())
    print('Max/Mean/Min for New York:', ny['Value'].max(), ny['Value'].mean(), ny['Value'].min())
    print('Max/Mean/Min for Texas:', tx['Value'].max(), tx['Value'].mean(), tx['Value'].min())

    ax.plot(il['Year'], il['Value'], 'k-', label=states[0])
    ax.plot(ca['Year'], ca['Value'], 'r-', label=states[1])
    ax.plot(ny['Year'], ny['Value'], 'b-', label=states[2])
    ax.plot(tx['Year'], tx['Value'], 'g-', label=states[3])
    ax.legend(loc='upper right')
    plt.suptitle('Average August Temperature')
    plt.savefig(filepath_plotmonth)
    plt.show()
    
#Get the urls
urls=[]
head_url='https://www.ncdc.noaa.gov/cag/statewide/time-series/'
tail_url = '-1895-2019.csv?base_prd=true&begbaseyear=1901&endbaseyear=2000'
for state in range(1,49):
    for month in [1,8]:
        urls.append(head_url+str(state)+'-tavg-1-'+str(month)+tail_url)

#States to plot
states=['Illinois','California', 'New York', 'Texas']
def main(urls, states, filepath, filepath_plotdiff, filepath_plotmonth, data=None, headers=None,
         return_soup=True, skiprows=0):
    get_webpage(urls, filepath, data=None, headers=None, return_soup=True)
    df=create_df(filepath, skiprows=skiprows)
    plotdiff(filepath_plotdiff,df,states)
    plotmonth(filepath_plotmonth,df,states)
    
main(urls, states, '/Users/andrewweis/Documents/GitHub/DataSkills/Pset1/weather/',
     '/Users/andrewweis/Documents/GitHub/DataSkills/Pset1/weather_plots/JanAugDiff.png',
     '/Users/andrewweis/Documents/GitHub/DataSkills/Pset1/weather_plots/Aug.png', skiprows=4)