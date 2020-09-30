import os
import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
from itertools import cycle
import calendar

path = r'/Users/Sam/Documents/School/Data Skills/assignment-1-slroth/'
#path = r'/Users/Sam/Documents/School/Data Skills/assignment-1-test-folder/'
folder = path + r'weather/'
weather_data = os.listdir(folder)

def data_loader():
    if not weather_data:
        urls = []
        state_id = list(range(1, 49))
        month_id = list(range(1, 13))

        urls = ['https://www.ncdc.noaa.gov/cag/statewide/time-series/' + str(s) + '-tavg-1-' + str(m) + '-1895-2019.csv?base_prd=true&begbaseyear=1901&endbaseyear=2000' for s in state_id for m in month_id]
        # for help determining ways to create the list of IDs and turn them into strings https://stackoverflow.com/questions/5618878/how-to-convert-list-to-string
        # refresher on looping over multiple dimensions https://stackoverflow.com/questions/16384109/iterate-over-all-combinations-of-values-in-multiple-lists-in-python

        for url in urls:
            response = requests.get(url)
            state, measure, month = response.text.split('\n')[0].split(', ')
            with open(folder + state + ' ' + month + '.csv', 'w') as ofile:
                ofile.write(response.text)
    else:
        pass

def df_builder():
    dfs = []
    for file in weather_data:
        state_df = pd.read_csv(folder + file)
        state = state_df.columns[0]
        cols = list(state_df.loc[3]) # https://stackoverflow.com/questions/11346283/renaming-columns-in-pandas, https://www.geeksforgeeks.org/create-a-list-from-rows-in-pandas-dataframe-set-2/
        state_df.columns = cols
        state_df = state_df.loc[4:].reset_index(drop=True) # the last few lines eliminate junk in the csv files
        state_df['State'] = state
        state_df['Date'] = pd.to_datetime(state_df['Date'], format='%Y%m')
        dfs.append(state_df)

    df = pd.concat(dfs)
    df = df.sort_values(['State', 'Date']).reset_index(drop=True)
    df['Year'] = df['Date'].map(lambda d: d.year)
    df['Month'] = df['Date'].map(lambda d: d.month)

    df = df.astype({'Value':'float64', 'Anomaly':'float64'})

    return df

def delta_calculator(month_pair):
    df = df_builder()
    delta_df = df[df['Month'].isin(month_pair)]
    df['Delta'] = df.groupby(['State', 'Year'])['Value'].diff()
    deltas = df.dropna(subset=['Delta'])[['State', 'Year', 'Delta']]

    return deltas

def delta_plotter(state_list, month_pair):
    deltas = delta_calculator(month_pair)
    fig, ax = plt.subplots(len(state_list), 1)
    colors = cycle('bgrcmk')

    for state in state_list:
        st = deltas[deltas['State'] == state]
        state_plot = ax[state_list.index(state)] # the index of each subplot corresponds to the index of position of the state within the list being plotted, https://stackoverflow.com/questions/176918/finding-the-index-of-an-item-given-a-list-containing-it-in-python
        state_plot.plot(st['Year'], st['Delta'], c=next(colors)) # rather than hard code four colors, this cycles through colors as needed given the list of states https://stackoverflow.com/questions/14720331/how-to-generate-random-colors-in-matplotlib
        state_plot.set_ylabel(state)

        if state_list[0] == state:
            state_plot.xaxis.tick_top()

        elif state_list[-1] == state:
            pass

        else:
            state_plot.set_label('')
            state_plot.set_xticks([])

    plt.suptitle('Average ' + calendar.month_abbr[month_pair[0]] + '-' + calendar.month_abbr[month_pair[1]] + ' Temperature Variation') # https://stackoverflow.com/questions/6557553/get-month-name-from-number

    plt.savefig(path + 'plot 1')
    plt.show()

def monthly_plotter(month_list, state_list):
    df = df_builder()
    df = df[df['State'].isin(state_list)]
    fig, ax = plt.subplots(len(month_list), 1, squeeze=False, constrained_layout=True) # https://stackoverflow.com/questions/19953348/error-when-looping-to-produce-subplots, https://matplotlib.org/3.1.1/gallery/subplots_axes_and_figures/figure_title.html

    for month in month_list:
        state_plot = ax[month_list.index(month), 0]
        monthly_df = df[df['Month'] == month]

        for state in state_list:
            state_df = monthly_df[monthly_df['State'] == state]

            state_plot.plot(state_df['Year'], state_df['Value'], label=state)
            state_plot.spines['right'].set_visible(False)
            state_plot.spines['top'].set_visible(False)

            ax[0, 0].legend(loc='upper right')

        if len(month_list) == 1: # adding labels for individual subplots in the figure only if there is more than one subplot
            pass

        else:
            state_plot.set_ylabel(calendar.month_name[month])

    if len(month_list) == 1: # specifies figure title depending on whether there is one subplot or multiple
        plt.suptitle('Average ' + calendar.month_name[month_list[0]] + ' Temperature')

    else:
        plt.suptitle('Average Monthly Temperature')

    plt.savefig(path + 'plot 2')
    plt.show()

def monthly_summarizer(month_list, state_list):
    df = df_builder()
    for month in month_list:
        monthly_df = df[df['Month'] == month]
        print('Max/Mean/Min for ' + calendar.month_name[month] + ' in: ')

        for state in state_list:
            state_df = monthly_df[monthly_df['State'] == state]
            values = state_df['Value']
            print('\n' + '\t' + state + ': ', values.max(), round(values.mean(), ndigits=1), values.min())

        print('\n') # for readability

def run_program(month_pair, month_list, state_list):
    data_loader()
    delta_plotter(state_list, month_pair)
    monthly_plotter(month_list, state_list)
    monthly_summarizer(month_list, state_list)

run_program(month_pair=[1, 8], month_list=[8], state_list=['Illinois', 'California', 'New York', 'Texas'])
# not sure whether this last line is preferred to the following:
# month_pair, month_list, state_list = [[1,8], [8], ['Illinois', 'California', 'New York', 'Texas']]
# run_program(month_pair, month_list, state_list)
# I did it the way I have above to avoid assigning global variables where possible, but either works
