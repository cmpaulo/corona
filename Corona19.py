
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
from datetime import timedelta

# https://labs.wesleycota.com/sarscov2/br
# http://plataforma.saude.gov.br/novocoronavirus/#COVID-19-brazil
# https://covid19br.github.io/index.html
# tabela :: wget -r https://raw.githubusercontent.com/wcota/covid19br/master/cases-brazil-states.csv
# 412 mil leitos o BRasil. 1,95 por mi hab (https://super.abril.com.br/saude/grafico-a-quantidade-de-leitos-hospitalares-ao-redor-do-mundo/)
# wget -r https://s3-us-west-1.amazonaws.com/starschema.covid/JHU_COVID-19.csv

# importa os dados usando pandas e trasforma em dataFrame
#data = pd.read_csv("/content/JHU_COVID-19.csv",header=0)
data = pd.read_csv("./s3-us-west-1.amazonaws.com/starschema.covid/JHU_COVID-19.csv",header=0)
# dates = pd.read_csv("/content/cases-brazil-states.csv",header=0,index_col="date")

# Total de casos: 1.128 (18 mortes*) 21 março 2020
# Total de casos: 1.546 (25 mortes*) 22 março 2020
# Total de casos: 1.891 (34 mortes*) 22 março 2020
# Total de casos: 2006 (34 mortes*) 24 março 2020
# Total de casos: 2452 (57 mortes*) 25 março 2020
# Total de casos: 2985 (77 mortes*) 26 março 2020
cfm = np.array([(18/1128.),(25/1546.), (34/1891.),(46/2201.),(57/2452.),(77/2985.)])
cfm*100.

# seleciona os dados do Brasil
br = data[data["Country/Region"] == "Brazil"]
# seleciona os dados do Argentina
ar = data[data["Country/Region"] == "Argentina"]
# seleciona os dados do Uruguay
uy = data[data["Country/Region"] == "Uruguay"]
# seleciona os dados do Italia
ita = data[data["Country/Region"] == "Italy"]
# seleciona os dados da China
china = data[data["Country/Region"] == "China"]
# seleciona os dados do Peru
china = data[data["Country/Region"] == "Peru"]


# seleciona somente casos confirmados no Brasil
confirmadosbr = br[br["Case_Type"] == "Confirmed"]
# ativos = br[br["Case_Type"] == "Active"]
timebr = confirmadosbr["Date"]
# transforma para datatime
for i in enumerate(timebr):
  timebr[timebr.index.values[i[0]]] = datetime.strptime(i[1], "%Y-%m-%d %H:%M:%S.%f")


# modifica os dados para utilizar no curve fit
xtime=[]
ydata=[]
xtimebr=[]
ydatabr=[]
dia=[]
today=datetime.now().date()
################################### quantidade de casos #####
cond_idx = confirmadosbr.index[np.where(confirmadosbr["Cases"]>0)]
case1 = pd.to_datetime(confirmadosbr["Date"][cond_idx[0]])
########################################
for ib in enumerate(timebr):
  # somente dias onde o numero de casos confirmados é maior que 0
  # para o Brasil
  if confirmadosbr["Cases"][confirmadosbr.index[ib[0]]] > 0:
    # procura os dias..
    # print(ib[1])
    selday = (ib[1]-case1).days == np.arange(0,32,3)
    # a cada dois dias pegamos o numero de casos e convete o dia para dia inteiro
    if True in selday:
      xtimebr.append((ib[1]-case1).days)
      ydatabr.append(confirmadosbr["Cases"][confirmadosbr.index[ib[0]]])
      dia.append(timebr[confirmadosbr.index[ib[0]]])

# dados selecionador para fazer o ajsute
ydatabr = np.array(sorted(ydatabr))
xdatabr = np.array(sorted(xtimebr))
for i in range(5):
  dia.append(dia[-1]+timedelta(days=1))

# ajuste exponencial com a func, dos dasos xdata e ydata Brasil
from scipy.optimize import curve_fit
def func(x, a, b, c):
    return a * np.exp(b * x) + c

poptbr, pcovbr = curve_fit(func, xdatabr, ydatabr)
perrbr = np.sqrt(np.diag(pcovbr))
poptbr


# MODEL S I E R
# population 
N = 1e4
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
lamda = 0.3
lamda = poptbr[1]
# recover rate
gamma = 0.0821
# exposed period
sigma = 1 / 8

# initial infective people
i[0] = 1.0 / N
s[0] = N / N - i[0]
e[0] = 8.0 / N
r[0] = 0.0

for t in range(T-1):
    s[t + 1] = s[t] - lamda * s[t] * i[t]
    e[t + 1] = e[t] + lamda * s[t] * i[t] - sigma * e[t]
    i[t + 1] = i[t] + sigma * e[t] - gamma * i[t]
    r[t + 1] = r[t] + gamma * i[t]

diasimu=[]
for iy in range(160):
  diasimu.append(case1.date()+timedelta(days=iy))

fig, ax = plt.subplots(figsize=(10,6))
# ax.plot(s, c='b', lw=2, label='S')
ax.plot(diasimu,e[:len(diasimu)]*N, c='orange', lw=2, label='E')
ax.plot(diasimu,i[:len(diasimu)]*N, c='r', lw=2, label='I')
# ax.plot(r, c='g', lw=2, label='R')
ax.set_xlabel('Dia',fontsize=20)
ax.set_ylabel('rzao da pop. inctadada [/10.000 hab]', fontsize=20)
ax.grid(1)
# ax.set_xlim(0,50)
ax.set_xlim(today,today+timedelta(days=(160-50)))
# ax.set_xlim(today,"2020-04-30")
plt.xticks(fontsize=10)
plt.yticks(fontsize=20)
plt.legend();


# dados do fit no ajuste
brdata = func(xdatabr, *poptbr)
# prediacao 5 dias
prbrxdata = np.arange(xdatabr.max(),xdatabr.max()+6)
prbrdata = func(prbrxdata, *poptbr)
supEprbr = func(prbrxdata, *(poptbr+perrbr))
infEprbr = func(prbrxdata, *(poptbr-perrbr))

dprevisto = (today-case1.date()).days
su = func(dprevisto, *(poptbr+perrbr))
inf= func(dprevisto, *(poptbr-perrbr))
vabr = (su-inf)/2
hojebr = (func(dprevisto, *poptbr))
# dia_anterior = (func(-1, *poptbr))
print("hoje "+str(today)+" o numero de casos no Brasil será :: >>>>>>> ",str(inf)[:7]," no melhor dos casos")
print("hoje "+str(today)+" o numero de casos no Brasil será :: >>>>>>> ",str(su)[:7]," no pior dos casos")
print("hoje "+str(today)+" o numero de casos no Brasil esperado será ::  >>>>>>> ",str(hojebr)[:7]," no dia.")


# Brasil grafico
fig = plt.figure(figsize=[10,8])
ax2 = plt.subplot()

ax2.plot(dia[:len(ydatabr)],ydatabr,"k*",label="confirmados 2dias")
ax2.plot(dia[:len(brdata)],brdata,"r+-",label="fit 2dias")
ax2.plot(dia[len(ydatabr)-1:],prbrdata,"b+-",label="previsao para 5 dias")
ax2.plot(timebr,confirmadosbr["Cases"],"k--",label="confirmados Brasil")
# # ax2.plot(xdatabr,brdata,"r+-",label="fit 2dias")
# ax2.plot(prbrxdata,prbrdata,"b+-",label="previsao para 5 dias")
# ax2.plot(pr2xdata,supEprbr,"gray",lw=0.8,label="incerteza da previsao")
# ax2.plot(pr2xdata,infEprbr,"gray",lw=0.8)
# ax2.text(-8,hojebr,"previsão de casos dia ")
# ax2.text(-8,hojebr-150,str(datetime.now().date())+" "+str(hojebr)[:7])
# # ax2.text(-5,hojebr-100,"variaçao de "+str(vabr)[:7])
ax2.text("2020-03-18",4000,"previsão de casos dia ")
ax2.text("2020-03-10",4000-500,str(datetime.now().date())+" "+str(hojebr)[:7])
# ax2.plot(timebr[timebr.index[-1]],ultimodia,"*")
ax2.axvline(today,ls="dotted",lw=1.8)

ax2.set_title("CORONA virus Brasil update "+str(br["Date"][br.index[-1]]))
ax2.set_xlabel("Dias ")
ax2.set_ylabel("numero de casos confirmados")
# ax2.set_xlim(-25,) #; ax1.set_ylim(0,2500)
# ax2.set_xlim("2020-03-01",datetime.now().date()+timedelta(days=5))
ax2.legend()
ax2.grid()
plt.show()
