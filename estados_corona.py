import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
from datetime import timedelta

# tabela :: wget -r https://raw.githubusercontent.com/wcota/covid19br/master/cases-brazil-states.csv
#dates = pd.read_csv("/content/cases-brazil-states.csv",header=0,index_col="date")
dates = pd.read_csv("./raw.githubusercontent.com/wcota/covid19br/master/cases-brazil-states.csv",header=0,index_col="date")

stado = dates[dates["state"] == "SP"]
# print(stado.totalCases)

# listaEstados =  sorted(dates["state"].unique())[:-1]
# dates.index = pd.to_datetime(dates.index)
# for ke in listaEstados:
#   estado = dates[dates["state"] == ke]
#   plt.plot(estado["totalCases"])
# plt.grid()
# plt.show()

# ajuste exponencial com a func, dos dasos xdata e ydata Brasil
from scipy.optimize import curve_fit
def func(x, a, b, c):
    return a * np.exp(b * x) + c
def funcpol(x, a, b):
    return a * x + b


# modifica os dados para utilizar no curve fit

today=datetime.now().date()
# lista os estados 
listaEstados = sorted(dates["state"].unique())[:-1]
coef_estado = pd.DataFrame(columns=["Estado","coefts","coefts_err","Ajuste","ndata","pcaso"])
for ke in listaEstados:
  xtimebr=[]; ydatabr=[]; dia=[]
  estado = dates[dates["state"] == ke]
  estado.index = pd.to_datetime(estado.index)
# primeiro caso no estado dia
  case1 = estado.index[np.where(estado["totalCases"] > 0)][0]
  for ib in enumerate(estado.index):
    # somente dias onde o numero de casos confirmados é maior que 0
    if estado["totalCases"][estado.index[ib[0]]] >0:
      # procura os dias..
      selday = ((ib[1])-case1).days == np.arange(0,len(estado)+3,2)
      # a cada dois dias pegamos o numero de casos e convete o dia para dia inteiro
      # dia negativo está no passado.. -2 ==dois dias antes do atual var(today)
      if True in selday:
        xtimebr.append((ib[1]-case1).days)
        ydatabr.append(estado["totalCases"][estado.index[ib[0]]])
        dia.append(estado.index[ib[0]])

  # dados selecionador para fazer o ajsute
  ydatabr  = np.array(ydatabr)
  xdatabr = np.array(xtimebr)
  if ke in ["PE","PI","RO","PA","PB","RR"]:
    poptbr, pcovbr = curve_fit(funcpol, xdatabr, ydatabr)
    Ajuste = "Linear"
    lendata = len(ydatabr)
  else:
    poptbr, pcovbr = curve_fit(func, xdatabr, ydatabr)
    Ajuste = "Expo"
    lendata = len(ydatabr)
  perrbr = np.sqrt(np.diag(pcovbr))
  coef_estado.loc[len(coef_estado),:] = [ke,poptbr,perrbr,Ajuste,lendata,case1]
# coef_estado

# #  cria 5 dias para previsão
# for i in range(5):
#   dia.append(dia[-1]+timedelta(days=1))




fig, ax = plt.subplots(figsize=(10,6))
coefl=[]
for ik in coef_estado.loc[:,"coefts"]:
  if len(ik) != 3:
    coefl.append(ik[0])
  else:
    coefl.append(ik[1])
ndata = (coef_estado["ndata"].values).astype(np.str)
coefl=np.array(coefl)
plt.bar(coef_estado.loc[:,"Estado"],coefl)
for ii in range(len(ndata)):
  plt.text(coef_estado.loc[:,"Estado"][ii],coefl[ii],ndata[ii])
plt.bar(["PE","PI","RO","PA","PB","RR"],np.ones(6)*0.1,color="b")
plt.axhline(0.2)
# plt.ylim(0,2)
plt.show()

# # ajuste exponencial com a func, dos dasos xdata e ydata Brasil
# from scipy.optimize import curve_fit
# def func(x, a, b, c):
#     return a * np.exp(b * x) + c

# # Brasil
# poptbr, pcovbr = curve_fit(func, xdatabr, ydatabr)
# perrbr = np.sqrt(np.diag(pcovbr))
# poptbr

# seleciona o estado
UF="RS"
coefl=[]
ik = coef_estado.loc[:,["Estado","coefts","pcaso"]]
ikd = ik.loc[:,"Estado"] == UF
ikd = ikd.index[ikd ==True].values
nk = ik.loc[ikd,"coefts"].values[0]
if len(nk) != 3:
  coefl = (nk[0])
else:
  coefl = (nk[1])
coefl
caso1 = coef_estado["pcaso"][ikd].values

#  MODELO S E I R 
# population
N = 1e3
# simuation Time / Day
T = 160
tm = np.linspace(0, T, T)
# susceptiable ratio
s = np.zeros([T])
# exposed ratio
e = np.zeros([T])
# infective ratio
i = np.zeros([T])
# remove ratio
r = np.zeros([T])

# contact rate
lamda = 0.2
lamba = coefl
# recover rate
gamma = 0.0821
# exposed period
sigma = 1 / 7

# initial infective people
i[0] = 1.0 / N
e[0] = 1.0 / N
s[0] = N / N - i[0] - e[0]
# s[0] = N / N
for t in range(T-1):
    s[t + 1] = s[t] - lamda * s[t] * i[t]
    e[t + 1] = e[t] + lamda * s[t] * i[t] - sigma * e[t]
    i[t + 1] = i[t] + sigma * e[t] - gamma * i[t]
    r[t + 1] = r[t] + gamma * i[t]

diasim = []
for kk in range(T):
  diasim.append(caso1[0]+timedelta(days=kk))
  
fig, ax = plt.subplots(figsize=(10,6))
# ax.plot(s, c='b', lw=2, label='S')
ax.plot(diasim,e, c='orange', lw=2, label='E')
ax.plot(diasim,i, c='r', lw=2, label='I')
# ax.plot(r, c='g', lw=2, label='R')
ax.set_xlabel('Dia',fontsize=20)
ax.set_ylabel('razao de infectados', fontsize=20)
ax.grid(1)
# ax.set_xlim(0,50)
ax.set_xlim(today,diasim[-1])
plt.xticks(fontsize=10)
plt.yticks(fontsize=20)
plt.legend();

# SC_i = i
# SP_i = i
# RS_i = i
RJ_i = i
# SC_dia = []
# SP_dia = []
# RS_dia = []
RJ_dia = []
for kk in range(T):
  # SP_dia.append(caso1[0]+timedelta(days=kk))
  # SC_dia.append(caso1[0]+timedelta(days=kk))
  # RS_dia.append(caso1[0]+timedelta(days=kk))
  RJ_dia.append(caso1[0]+timedelta(days=kk))

 
fig, ax = plt.subplots(figsize=(10,6))
# ax.plot(s, c='b', lw=2, label='S')
# ax.plot(diasim,e, c='orange', lw=2, label='E')
ax.plot(SC_i, c='r', lw=2, label='SC_I')
ax.plot(SP_i, c='b', lw=2, label='SP_I')
ax.plot(RS_i, c='g', lw=2, label='RS_I')
ax.plot(RJ_i, c='c', lw=2, label='RJ_I')
# ax.plot(r, c='g', lw=2, label='R')
ax.set_xlabel('Dia',fontsize=20)
ax.set_ylabel('razao de infectados', fontsize=20)
ax.grid(1)
# ax.set_xlim(0,50)
# ax.set_xlim(today,diasim[-1])
plt.xticks(fontsize=10)
plt.yticks(fontsize=20)
plt.legend();
