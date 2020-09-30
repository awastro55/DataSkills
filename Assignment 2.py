import os
import numpy as np
import pandas as pd
import us
import calendar 
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
from itertools import cycle

path = r'/Users/andrewweis/Documents/GitHub/DataSkills/assignment-2-sam-roth-and-andrew-weis/'
folder = path + r'weather/'
weather_data = os.listdir(folder)

retrieve_weather = False



def download_weather():


    state_id = list(range(1, 49))
    month_id = [1,8]

    urls = ['https://www.ncdc.noaa.gov/cag/statewide/time-series/' + str(s) + '-tavg-1-' + str(m) + '-1895-2019.csv?base_prd=true&begbaseyear=1901&endbaseyear=2000' for s in state_id for m in month_id]

    for url in urls:
        response = requests.get(url)
        state, measure, month = response.text.split('\n')[0].split(', ')
        with open(folder + state + ' ' + month + '.csv', 'w') as ofile:
            ofile.write(response.text)

if retrieve_weather:
    download_weather()



def weather_df():


    dfs = []
    for file in weather_data:
        state_df = pd.read_csv(folder + file)
        state = state_df.columns[0]
        cols = list(state_df.loc[3])
        state_df.columns = cols
        state_df.columns = state_df.columns.str.lower()
        state_df = state_df.loc[4:].reset_index(drop=True) # the last few lines eliminate junk in the csv files
        state_df['state'] = state
        state_df['date'] = pd.to_datetime(state_df['date'], format='%Y%m')
        dfs.append(state_df)

    df = pd.concat(dfs)
    df = df.sort_values(['state', 'date']).reset_index(drop=True)
    df['year'] = df['date'].map(lambda d: d.year)
    df['month'] = df['date'].map(lambda d: d.month)

    df = df.astype({'value':'float64', 'anomaly':'float64'})

    return df



def download_energy():

    url = r'https://www.eia.gov/electricity/data/state/annual_consumption_state.xls'
    df = pd.read_excel(url, header=1, na_values='.')

    return df



def energy_df():


    df = download_energy()

    df.columns = df.columns.str.lower()
    df.rename(columns = {'type of producer':'producer_type',
                         'energy source              (units)':'energy_source',
                         'consumption for electricity':'consumption'},
                         inplace=True)

    df = df[df['producer_type'] == 'Total Electric Power Industry']
    totals = df.groupby(['state', 'year'], as_index=False)['consumption'].sum() # https://stackoverflow.com/questions/10373660/converting-a-pandas-groupby-output-from-series-to-dataframe

    totals = totals.loc[~((totals['state'] == 'AK') | (totals['state'] == 'HI') | (totals['state'] == 'DC') | (totals['state'] == 'US-TOTAL') | (totals['state'] == 'US-Total'))] # https://stackoverflow.com/questions/52456874/drop-rows-on-multiple-conditions-in-pandas-dataframe
    # looking for more generalized solution:
    non_lower_48 = ['AK', 'HI', 'DC', 'US-TOTAL', 'US-Total']

    state_abbr = us.states.mapping('abbr', 'name')
    totals.replace({'state': state_abbr}, inplace=True) # https://stackoverflow.com/questions/20250771/remap-values-in-pandas-column-with-a-dict

    return totals



def data_merge():


    weather = weather_df()
    energy = energy_df()

    full_df = weather.merge(energy, on=['state', 'year'])

    return full_df



def delta_calculator(month_pair):


    df = weather_df()
    delta_df = df[df['month'].isin(month_pair)]
    df['Delta'] = df.groupby(['state', 'year'])['value'].diff()
    deltas = df.dropna(subset=['Delta'])[['state', 'year', 'Delta']]

    return deltas



def delta_plotter(state_list, month_pair):


    deltas = delta_calculator(month_pair)
    fig, ax = plt.subplots(len(state_list), 1)
    colors = cycle('bgrcmk')

    for state in state_list:
        st = deltas[deltas['state'] == state]
        state_plot = ax[state_list.index(state)] # the index of each subplot corresponds to the index of position of the state within the list being plotted, https://stackoverflow.com/questions/176918/finding-the-index-of-an-item-given-a-list-containing-it-in-python
        state_plot.plot(st['year'], st['Delta'], c=next(colors)) # rather than hard code four colors, this cycles through colors as needed given the list of states https://stackoverflow.com/questions/14720331/how-to-generate-random-colors-in-matplotlib
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


    df = weather_df()
    df = df[df['state'].isin(state_list)]
    fig, ax = plt.subplots(len(month_list), 1, squeeze=False, constrained_layout=True) # https://stackoverflow.com/questions/19953348/error-when-looping-to-produce-subplots, https://matplotlib.org/3.1.1/gallery/subplots_axes_and_figures/figure_title.html

    for month in month_list:
        state_plot = ax[month_list.index(month), 0]
        monthly_df = df[df['month'] == month]

        for state in state_list:
            state_df = monthly_df[monthly_df['state'] == state]

            state_plot.plot(state_df['year'], state_df['value'], label=state)
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


    df = weather_df()
    for month in month_list:
        monthly_df = df[df['month'] == month]
        print('Max/Mean/Min for ' + calendar.month_name[month] + ' in: ')

        for state in state_list:
            state_df = monthly_df[monthly_df['state'] == state]
            values = state_df['value']
            print('\n' + '\t' + state + ': ', values.max(), round(values.mean(), ndigits=1), values.min())

        print('\n') # for readability



def energy_plotter(state_list, month_list): #Global vars.  We could change these lists if we wanted.


    df = data_merge() #Calling data merge function, combine the weather and energy data into one data frame.
    #All temp, energy data for each state year.  
    df = df[df['state'].isin(state_list)] #Restrict data frame to our list of states. 

    for month in month_list:

        month_df = df[df['month'] == month] #Restrict to the month in the loop.  January and then August. 
        fig, ax = plt.subplots(len(state_list), 1) #Subplots=number of states. 

        for state in state_list: 

            st = month_df[month_df['state'] == state] 
            state_plot = ax[state_list.index(state)] #Index--position of the state working with. Which subplot.
            state_plot.set_title(state)#Object for the plot is state_plot variable.
            state_plot.plot(st['year'], st['value'], '-r')
            state_plot.set_ylabel('Temperature')
            state_plot.tick_params(axis='y', labelcolor='red') # might need to fix color name
            ax_right = state_plot.twinx() #Share x axis, different y axis. 
            ax_right.plot(st['year'], st['consumption'], '--m')
            ax_right.set_ylabel('Annual Energy Consumption')
            ax_right.tick_params(axis='y', labelcolor='magenta')

            if state_list[-1] == state:
                pass

            else:
                state_plot.set_label('')
                state_plot.set_xticks([])

        #ax[0, 0].legend(loc='upper right')

        title = 'Average Temperature vs Energy Consumption, {}'
        title = title.format(month)
        plt.suptitle(title) #Make plot like this for each month.  

        plt.show()



def run_program(month_pair, month_list, state_list):


    #data_loader()
    #delta_plotter(state_list, month_pair)
    monthly_plotter(month_list, state_list)
    #monthly_summarizer(month_list, state_list)
    energy_plotter(state_list, month_list)



run_program(month_pair=[1, 8], month_list=[8], state_list=['Illinois', 'California', 'New York', 'Texas'])
