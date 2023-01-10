#!/usr/bin/env python
# coding: utf-8

import matplotlib.pyplot as plt
from matplotlib import path
import numpy as np
import pandas as pd
from IPython.display import clear_output
from datetime import datetime
from mpl_toolkits.axes_grid1 import make_axes_locatable
import importlib
def reload(module_name):
    importlib.reload(module_name)

def shorelinetogrid(x, y, dx, dy, plotdata=True):
    """ function to convert xy shoreline to gridded elevation for input to CEM
        takes arrays of x and y in UTM or lat lon values. Assumes a Dean Profile.
        Will plot output unless specified plotdata=False
            """
    # build grid
    # find the smallest and largest x's and y's to initialize grid boundaries
    x0 = int(np.ceil(min(x) / dx) * dx)
    y0 = int(np.ceil(min(y) / dy) * dy)
    x1 = x0 + int(np.ceil((max(x) - min(x)) / dx) * dx - 2 * dx)  # add total length of x to origin x
    y1 = y0 + int(np.ceil((max(y) - min(y)) / dy) * dy + 5000)

    # create mesh grid of x and y
    [xg, yg] = np.meshgrid(list(range(x0, x1, dx)), list(range(y0, y1, dy)), sparse=False, indexing='ij')

    # generate bathy using dean profile
    surf_width = 1000
    A = 0.1
    landmax = 1
    rng = 100000
    zg = np.zeros_like(xg)
    dist = np.zeros_like(xg)

    for i in range(0, xg.shape[1]):
        for j in range(0, xg.shape[0]):
            inrange = (abs(x - xg[j, i]) < rng) & (abs(y - yg[j, i]) < rng);
            r = np.zeros_like(x);
            r[inrange] = (x[inrange] - xg[j, i]) ** 2 + (y[inrange] - yg[j, i]) ** 2;
            r[~inrange] = 1.e10;
            # Compute closest grid cell
            value = min(r);
            dist[j, i] = np.sqrt(value);
            zg[j, i] = -A * (dist[j, i]) ** (2 / 3);

    p = path.Path(np.transpose([x, y]))
    IN = p.contains_points(np.transpose([xg.flatten(), yg.flatten()]))
    IN = IN.reshape(xg.shape)
    zg[IN] = (min(A * (dist[IN]) ** (2 / 3))) + 1
    zg = zg * -1
    if plotdata == True:
        M,N = zg.shape
        s = M/N
        plt.figure(figsize=(int(s*8),7))
        Bathy = plt.contourf(xg, yg, zg, cmap=plt.cm.GnBu)
        cbar = plt.colorbar(Bathy)
        cbar.ax.set_ylabel('Water Depth (m)', fontsize=20, rotation=-90, labelpad=30)
        plt.xlabel('Eastings', fontsize=20)
        plt.ylabel('Northings', fontsize=20)
        plt.tick_params('both', labelsize=15)
        cbar.ax.tick_params('y', labelsize=15)
        Shore = plt.plot(x, y, 'k')
    return xg, yg, zg


def plotmeteo(X):
    fig, axes = plt.subplots(2, sharex=True);
    axes[0].plot(X.index,X.WVHT)
    axes[1].plot(X.index,X.DPD)
    axes[0].set_ylabel('Wave Height (m)', fontsize=12);
    axes[1].set_ylabel('Dominant Period (s)', fontsize=12);
    axes[1].set_xlabel('');

def plot_coast(domain,dx,dy):
    '''Plot the coastline.
    
    Inputs:
    ------
    domain = any 2D array (though colorbar label is specific for water depth)
    
    '''
    N,M = domain.shape
    s = M/N
    fig,ax = plt.subplots(figsize=(int(s*8),7))
    im = ax.imshow(domain, origin='lower', cmap='viridis')
    
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.05)
    cb = fig.colorbar(im,cax=cax)
    cb.ax.tick_params('both',labelsize=15)
    cb.ax.set_ylabel('Water Depth (m)',fontsize=20,rotation=-90, labelpad=30)
    y = np.linspace(0,N,4)
    x = np.linspace(0,M,4)
    Y = (y*dy/(1000)).astype('int')
    X = np.asarray(x*dx/(1000)).astype('int')
    ax.set_yticks(y)
    ax.set_xticks(x)
    ax.set_yticklabels(Y)
    ax.set_xticklabels(X)
    ax.set_xlabel('Along shore (km)',fontsize=20)
    ax.set_ylabel('Cross shore (km)',fontsize=20)
    ax.tick_params('both',labelsize=15)



def run_model_loop(time_years, domain ,cem ,waves, animate=True,update_ani_years=1):
    '''Loop to run the cem-waves models.
    This loop only couples the wave angles and will need to be changed to add additional coupling.
    It also assumes static variables such as sediment input and would need modification to update such variables.
    
    Inputs:
    ------
    
    -time_years = time you want to run the model in years
    
    -domain = initial elevation domain
        ---> domain values in (-inifinity,1] 
                -->> 1 = land, <1 = water
                
    -cem,waves = the imported models 
        --->ex: cem = pymt.Cem()
        
    '''
    
    alpha = 'sea_surface_water_wave__azimuth_angle_of_opposite_of_phase_velocity'
    update_ani = int(365*update_ani_years/cem.get_value('model__time_step'))
    T = int(365*time_years/cem.get_value('model__time_step'))
    dx,dy = cem.grid_spacing(cem.var_grid('sea_water__depth'))
    for time in range(T):
        waves.update()
        angle = waves.get_value(alpha)
        cem.set_value(alpha, angle)
        cem.update()
        if animate:
            if time%update_ani == 0 or time==T-1:
                clear_output(wait=True)
                plot_coast(cem.get_value('land_surface__elevation').reshape(domain.shape),dx,dy)
                plt.title('Time : '+ str(round((time*cem.get_value('model__time_step')/365)[0],1)) +' years',fontsize=20)
                plt.show()

        else:
            clear_output(wait=True)
            print('Time Step: ',time, ' days')


def initialize_models(params,domain,cem,waves,set_land=True):
    '''
    Inputs:
    ------
    
    -params = parameter dictionary
    
    -domain = initial elevation domain
        ---> domain values in (-inifinity,1] 
                -->> 1 = land, <1 = water
                
    -cem,waves = the imported models 
        --->ex: cem = pymt.Cem()
            
    '''
    p = params
    
    N,M = domain.shape
    
    args = cem.setup( number_of_rows = N , number_of_cols = M, 
                      grid_spacing = p['grid_spacing'] ,  shelf_slope = p['shelf_slope'] , 
                      shoreface_depth = p['shoreface_depth'] , shoreface_slope = p['shoreface_slope']
                    )
    
    waves.initialize(*waves.setup())
    cem.initialize(*args)

    
    waves.set_value('sea_surface_water_wave__height', p['wave_height']);
    waves.set_value('sea_surface_water_wave__period',p['wave_period']);
    waves.set_value('sea_shoreline_wave~incoming~deepwater__ashton_et_al_approach_angle_highness_parameter',
                   p['wave_angle_highness']);
    waves.set_value('sea_shoreline_wave~incoming~deepwater__ashton_et_al_approach_angle_asymmetry_parameter',
                   p['wave_angle_asymmetry']);

    if set_land==True: #if need set land elevation; 'False' used default
        cem.set_value('land_surface__elevation',domain.flatten());
    cem.set_value('model__time_step', float(p['model__time_step']));


# In[ ]:




