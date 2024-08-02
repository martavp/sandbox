# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

#%%
import pypsa
n=pypsa.Network("elec_s_37_lv1.0__3H-T-H-B-I-A-solar+p3-dist1-cb25.7ex0_2050.nc")

#Number of cars in Germany 48,000,000

# A.Check balance of energy (Eq.1 in your paper)
-(n.links_t.p1['DE1 0 land transport EV-2035'].iloc[0]
  +n.links_t.p1['DE1 0 land transport EV-2040'].iloc[0]
  +n.links_t.p1['DE1 0 land transport EV-2045'].iloc[0]
  +n.links_t.p1['DE1 0 land transport EV-2050'].iloc[0]).round(2) 
==n.loads_t.p['DE1 0 land transport'].iloc[0].round(2)
#Ok, this is working, checked :)



# B.Check the the charging and discharging capacity for EVs is the same (Eq. 3 in your paper)
n.links.p_nom['DE1 0 BEV charger-2040']==n.links.p_nom['DE1 0 V2G-2040']
#Ok, this is working, checked :)



# C.Check that the capacity of the lumped charging link is limited by the number of
# cars in the country (Eq. 4 in your paper)
n.links.p_nom['DE1 0 BEV charger-2035']/0.011
42,928,000
#Ok, this seems to be working for 2035, but...

n.links.p_nom['DE1 0 BEV charger-2040']/0.011
42,928,000
#The same capacities are installed in 2040 

n.links.p_nom['DE1 0 BEV charger-2045']/0.011
42,928,000
#The same capacities are installed in 2045 

n.links.p_nom['DE1 0 BEV charger-2050']/0.011
42,928,000
#and 2050 so it seems as if in Germany we have now 4x42,928,000 cars



#D.Check Eq.5 in your paper. (assuming the fix coefficient on the right to be 9.5)
n.stores.e_nom['DE1 0 EV battery storage-2045']/0.050
10,385,685
n.links.p_nom['DE1 0 land transport EV-2045']/0.01*9.5
10,385,685
#ok, this is checked


#E.Check that the number of vehicles according to the energy capacity of the battery
n.stores.e_nom_opt['DE1 0 EV battery storage-2035']/0.100
nan
n.stores.e_nom_opt['DE1 0 EV battery storage-2040']/0.100
nan
n.stores.e_nom_opt['DE1 0 EV battery storage-2045']/0.100
5,192,00
n.stores.e_nom_opt['DE1 0 EV battery storage-2050']/0.100
5,539,157

#So, there are cars in 2040 and 2050 according the the charging capacity of the
#battery but there are no cars according to the energy capacity of the battery
#Installed in 2045, there are 42,928,000 cars according to the charging capacity 
#but only 5,192,00 cars according to their battery energy capacity