
# coding: utf-8

# In[17]:


import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
from datetime import timedelta
import wget
import os
plt.style.use('seaborn')

# # delete a old file
# # os.remove("./JHU_COVID-19.csv")
# os.remove("./full_data.csv")
# # download the new datasheet form JH
# # url ="https://s3-us-west-1.amazonaws.com/starschema.covid/JHU_COVID-19.csv"
# url ="https://covid.ourworldindata.org/data/ecdc/full_data.csv"
# output_directory = "."
# filename = wget.download(url, out=output_directory)


# read a csv to DataFrame with pandas
data = pd.read_csv("https://covid.ourworldindata.org/data/ecdc/full_data.csv")

# data from 🔅 Worldometers:
Cases =  30425. #❗️(103 novos)
Deaths = 1924 #❗️(11 novos) 😔
Recupered = 4390
txfa = Deaths/Cases
txre = Recupered/Cases

data.index = pd.to_datetime(data.date)
# sel data form Brazil
ctry = data[data["location"] == 'Brazil']
tested = ctry.copy()

# create a arrays for curve fit parameters of a exponential equation
xdays = []
ydata = []
dateCase=[]
today=datetime.now().date()
offsetcases = 20.
ndays=2
################################### Cases #####
cond_idx = tested.index[np.where(tested["total_cases"]>offsetcases)]
case1 = cond_idx[0]
ndate = cond_idx
########################################
for ib in enumerate(ndate):
    if tested["total_cases"][cond_idx[ib[0]]] >= offsetcases:
        selday = (ib[1]-case1).days == np.arange(0,len(cond_idx)+ndays,ndays)
        if True in selday:
            xdays.append((ib[1]-case1).days)
            ydata.append(tested["total_cases"][cond_idx[ib[0]]])
            dateCase.append(tested["date"][cond_idx[ib[0]]])

# do fiting
ydata = np.array(ydata)
xdata = np.array(xdays)
for i in range(5):
    dateCase.append(str((pd.to_datetime(dateCase[-1])+timedelta(days=1)).date()))
dateCase = pd.to_datetime(dateCase)
# ajuste exponencial com a func, dos dasos xdata e ydata Brasil
from scipy.optimize import curve_fit
def func(x, a, b, c):
    return a * np.exp(b * x) + c
poptbr, pcovbr = curve_fit(func, xdata, ydata)
perrbr = np.sqrt(np.diag(pcovbr))
# Forecast 5 days
prbrxdata = np.arange(xdata.max(),xdata.max()+6)
prbrdata = func(prbrxdata, *poptbr)

dprevisto = (today-case1.date()).days
hojebr = (func(dprevisto, *poptbr))

# Graphic Brazil
fig = plt.figure(figsize=[10,6])
ax2 = plt.subplot()

ax2.plot(dateCase[len(ydata)-1:],prbrdata,"b*-",label="5-day Forecast")
ax2.plot(tested.index,tested["total_cases"],"k*--",label="Confirmed Brazil")

ax2.text(pd.to_datetime("2020-03-02"),hojebr-8e3,"Forecast for "+str(datetime.now().date()))
ax2.text(pd.to_datetime("2020-03-02"),hojebr-16e3,"ninfect :: "+str(hojebr)[:7])
# ax2.axvline(today,ls="dotted",lw=1.8)

ax2.set_title("COVID19 - Brazil data updated "+str(tested["date"][tested.index[-1]]))
ax2.set_xlabel("Days")
ax2.set_ylabel("Number of Infections")
ax2.set_xlim(pd.to_datetime("2020-03-01"),datetime.now().date()+timedelta(days=5))
ax2.set_yscale('log')
ax2.set_ylim(1,)
ax2.legend(loc="lower right")
ax2.grid(1)
plt.show()
fig.savefig("log_data_forecast_brazil.png",dpi=350)
