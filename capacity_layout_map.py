# -*- coding: utf-8 -*-
"""
Crear layout_wind que incluya la capacidad instalada en cada gridcell,
luego se puede pintar el histograma con 
data==capacity factor y weigths=layout_wind

"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

# using two separators, EOL=\r\n  and ','
database = pd.read_csv('data/Windfarms_World_20180224.csv', 
                            sep="\r\n|','", engine='python' )

# correct error in data format in input file
database['Commissioning date (Format: yyyy or yyyymm)'][26739]='2011/01/01'
database['Commissioning date (Format: yyyy or yyyymm)'][26740]='2012/11/26'
database['Commissioning date (Format: yyyy or yyyymm)'][26741]='2014/12/31'

#filter by continent
database = database.loc[database['Continent'] == 'Europe']

#filter by plants currently in production
database = database.loc[database['Status'] == 'Production']

technology='onshore'

#filter by technology
if technology=='onshore':    
    database = database.loc[database['Offshore - Shore distance (km)'] == 'No']
if technology=='offshore':
    database = database.loc[database['Offshore - Shore distance (km)'] != 'No']
    
#filter plants whose total power, number of turbines or location is known
database = database.loc[database['Total power (kW)']   != '#ND']
database = database.loc[database['Number of turbines'] != '#ND']
database = database.loc[database['Latitude (WGS84)']   != '#ND']
database = database.loc[database['Longitude (WGS84)']  != '#ND']
                                 
# if the Comissioning date is unknown, it assumes the plant was always there
database['Commissioning date (Format: yyyy or yyyymm)'] = ['0000' if (x=='#ND')
       else x for x in database['Commissioning date (Format: yyyy or yyyymm)']]  
                               
year=2000
                     
#load cutout metadata
meta=np.load('cutouts/meta_Europe_2017_1_10.npz')
latitudes = meta['latitudes'][:,0]
longitudes = meta['longitudes'][0,:]


capacity_map = np.zeros((len(latitudes),len(longitudes)))
     
# # filter by capacities category
# # the total power in every plant is divied by the number of turbines to 
# # estimate turbine's capacity
# database_capacity = database.loc[(database['Total power (kW)'].astype(np.int)/
#                     database['Number of turbines'].astype(np.int) >= 
#                     categories[i]) & (database['Total power (kW)'].astype(np.int)/
#                     database['Number of turbines'].astype(np.int) 
#                     < categories[i+1])]

database_capacity=database    
indices = [x for x in database.index]
# select only indices with commissioning date earlier or equal to year
for indice in indices:
    if int(database_capacity['Commissioning date (Format: yyyy or yyyymm)'][indice][0:4]) > year:
        indices.remove(indice)
    
              
plant_list_df = pd.DataFrame(
        index=pd.Series(
            data= indices,
            name='index',
        ),
        columns=pd.Series(
            data=['capacity (kW)', 'lat pos', 'lon pos'],
            name='data',
        )
    )

for ind in indices:
    plant_list_df['capacity (kW)'][ind] = float(database_capacity['Total power (kW)'][ind])
    error_latitude = np.array([np.abs(float(database_capacity['Latitude (WGS84)'][ind].replace(',','.'))-lat) 
                               for lat in latitudes])
    plant_list_df['lat pos'][ind] = error_latitude.argmin()
    error_longitude = np.array([np.abs(float(database_capacity['Longitude (WGS84)'][ind].replace(',','.'))-lat) 
                                 for lat in longitudes])
    plant_list_df['lon pos'][ind] = error_longitude.argmin()
        
for u,v,x in zip(plant_list_df['lat pos'], plant_list_df['lon pos'], plant_list_df['capacity (kW)']):
    capacity_map[u,v] = capacity_map[u,v] + x
        
np.save('Europe_'+str(year)+'_thewindpower'+str(year)+'_wind-' +technology+'.npy', capacity_map)
plt.contour(capacity_map)


