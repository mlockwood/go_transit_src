#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-

# Python libraries and packages
import csv
import datetime
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import re
from scipy import stats
import seaborn as sns
import xlsxwriter
import multiprocessing as mp

# Classes and variables from src
from src.scripts.constants import PATH


__author__ = 'Michael Lockwood'
__github__ = 'mlockwood'
__projectclass__ = 'go'
__projectsubclass__ = 'transit'
__projectname__ = 'ridership.py'
__date__ = 'February2015'
__credits__ = None
__collaborators__ = None


OUT = '{}/reports/ridership/graphics'.format(PATH)

rs_frame = pd.read_csv('{}/reports/ridership/custom/Ridership_On_Stop_Off_Stop.csv'.format(PATH))
  
sns.clustermap(rs_frame, center=40, annot=True, fmt='d', figsize=(15, 15))
   
f, (axis1, axis2) = plt.subplots(2,1)
total = rs_frame.sum()

a = pd.Series(total.index.values)
a = pd.DataFrame(a)

b = pd.Series(total.values)
b = pd.DataFrame(b)

new_frame = pd.concat((a, b), axis=1)
new_frame.columns = ['On', 'Off']

sns.barplot('On',y='Off', data=new_frame, ax=axis1)
sns.heatmap(rs_frame, cmap='Blues', ax=axis2, cbar_kws={'orientation': 'horizontal'})

sns.clustermap(rs_frame, center=0.25, annot=True, fmt='.2f', standard_scale=0.5, figsize=(25, 25)).savefig(
    '{}/clustermap.png'.format(OUT))
 
dow_frame = pd.read_csv('{}/reports/ridership/custom/Ridership_Week_Dow.csv'.format(PATH))

dow = dow_frame.as_matrix()
riders = []
for row in dow:
	riders.append(row[1])
	riders = np.array(riders)
  
sns.kdeplot(riders)
   
sns.lmplot('Riders', 'Riders', dow_frame, hue='Day of the Week')

npr = []
for R in records.as_matrix():
	time = re.sub(':', '', R[10])
	time = round((int(time[:-2]) * 100) + (int(time[-2:]) / 0.6), 2)
	npr.append(time)
   
sns.kdeplot(np.array(npr))
