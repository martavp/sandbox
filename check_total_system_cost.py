# -*- coding: utf-8 -*-
"""
Created on Thu Oct 19 21:21:12 2023

@author: marta.victoria.perez
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib as mpl
import os
import pypsa

def annuity(n,r):
    """Calculate the annuity factor for an asset with lifetime n years and
    discount rate of r, e.g. annuity(20,0.05)*20 = 1.6"""

    if isinstance(r, pd.Series):
        return pd.Series(1/n, index=r.index).where(r == 0, r/(1. - 1./(1.+r)**n))
    elif r > 0:
        return r/(1. - 1./(1.+r)**n)
    else:
        return 1/n

#import network transmission=0, co2 emissions=5%
network = pypsa.Network('postnetwork-elec_only_0_0.05.h5')
#network = pypsa.Network('postnetwork-elec_only_0.125_0.05.h5')

"""
Option A: calculate total system cost from the sum of electricity price
weigthed by served load.
"""
loads=network.loads_t.p[network.buses.index[network.buses.carrier=='AC']]

prices=network.buses_t.marginal_price[network.buses.index[network.buses.carrier=='AC']]

ccc=loads.mul(prices)
system_cost_a=ccc.values.sum()/1000000000 # G€

check_transmission_capacity=network.links.p_nom_opt[network.links.index[network.links.index.str.len() == 5]].sum()

"""
Option B: calculate total system cost from the objective function
"""
# Lines copied from : https://github.com/martavp/PyPSA-plots/blob/aaf16df6d125784779d3e316488d4a0c4987d3ab/scripts/1_plot_storage_vs_co2.py#L89

#hydro_capital_cost=0 in options.yml, so hydro cost must be added
hydro_FOM_cost = (0.01*2e6*network.storage_units.p_nom[network.storage_units.index[network.storage_units.carrier == 'PHS']].sum() #1% FOM ; 2000€/kWh 
                 + 0.01*2e6*network.storage_units.p_nom[network.storage_units.index[network.storage_units.carrier == 'hydro']].sum() #1% FOM ; 2000€/kWh 
                 + 0.02*3e6*network.generators.p_nom[network.generators.index[network.generators.carrier == 'ror']].sum())/1000000000 #2% FOM ; 3000€/kWh 
            
#CAP_transmission=2*today's, so cost of transmission must be added
transmission_cost = ((400*1.25*network.links.length+150000.)*network.links.p_nom_opt)[network.links.index[network.links.index.str.len() == 5]].sum()*1.5*(annuity(40., 0.07)+0.02)/1000000000            
# 1.25 because lines are not straight, 400 is per MWkm of line, 150000 is per MW cost of
# converter pair for DC line,
# lifetime =40 years, discount rate=7%
# n-1 security is approximated by an overcapacity factor 1.5 ~ 1./0.666667
#FOM of 2%/a
system_cost_b = network.objective/1000000000 # G€
system_cost_c= (network.objective/1000000000 + hydro_FOM_cost + transmission_cost)

"""
Hydro revenues
"""

#Hydro stores
Hydro_storages = list(network.storage_units.index[network.storage_units.carrier == "hydro"])
Hydro_rev=[]

for i,storage in enumerate(Hydro_storages):
    Hydro_pn= network.storage_units_t.p[storage.split(' ')[0]+ ' hydro']             
    price = network.buses_t.marginal_price[storage.split(' ')[0]]
    Hydro_rev_=np.sum([x*y for x,y in zip(price,Hydro_pn)])
    Hydro_rev.append(Hydro_rev_)

revenues_hydro=np.sum(Hydro_rev)/1000000000.0 #G€
        
PHS_storages = list(network.storage_units.index[network.storage_units.carrier == "PHS"])
PHS_rev=[]
for i,storage in enumerate(PHS_storages):
    PHS_pn= network.storage_units_t.p[storage.split(' ')[0]+ ' PHS']        
    price = network.buses_t.marginal_price[storage.split(' ')[0]]
    PHS_rev_=np.sum([x*y for x,y in zip(price,PHS_pn)])
    PHS_rev.append(PHS_rev_)
revenues_PHS= np.sum(PHS_rev)/1000000000.0 #G€

ror_generators = list(network.generators.index[network.generators.carrier == "ror"])
ror_rev=[]
for i,generator in enumerate(ror_generators):
    ror_pn= network.generators_t.p[generator]        
    price = network.buses_t.marginal_price[generator.split(' ')[0]]
    ror_rev_=np.sum([x*y for x,y in zip(price,ror_pn)])
    ror_rev.append(ror_rev_)
revenues_ror= np.sum(ror_rev)/1000000000.0 #G€

"""
Gas CO2 price
"""
co2_cost=60/1000000000*network.stores.e_nom_opt[network.stores.index[network.stores.index.str[-9:] == 'gas Store']].sum()

system_cost_a-system_cost_c
co2_cost+(revenues_hydro+revenues_PHS+revenues_ror-hydro_FOM_cost) 