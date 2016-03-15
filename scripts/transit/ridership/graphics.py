
import numpy as np
from numpy.random import randn
import pandas as pd

from scipy import stats

import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns

import os
import re
import sys



rs_frame = pd.read_clipboard()
  
sns.clustermap(rs_frame, center=40, annot=True, fmt='d', figsize=(15, 15))
   
   
f, (axis1, axis2) = plt.subplots(2,1)
total = rs_frame.sum()

a = pd.Series(total.index.values)
a = pd.DataFrame(a)

b = pd.Series(total.values)
b = pd.DataFrame(b)

new_frame = pd.concat((a,b), axis=1)\
new_frame.columns = ['On', 'Off']

sns.barplot('On',y='Off', data=new_frame, ax=axis1)
sns.heatmap(rs_frame, cmap='Blues', ax=axis2, cbar_kws={'orientation': 'horizontal'})

sns.clustermap(rs_frame, center=0.25, annot=True, fmt='.2f', standard_scale=1, figsize=(15, 15))
 
dow_frame = pd.read_clipboard()

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
