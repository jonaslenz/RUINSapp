from typing import Tuple
import numpy as np
import pandas as pd

### Define parameters of the default pumping function / pump chart
x = np.array([7.,6.,5.,4.,3.5,3.,2,1,0,5.,4.,3.5,3.,2]) * 1000 # water gradient [mm] (by factor 1000 from m)
y = np.array([0,4.2,8.4,12.6,14.5,15.8,17.5,19,20.5,8.4,12.6,14.5,15.8,17.5]) * 3600 / (35000 * 100 * 100) * 1000 * 4  # "*3600 / (35000 * 100 * 100) * 1000 * 4)" converts m^3/s in mm/h
pumpcap_fit = np.polynomial.polynomial.Polynomial.fit(x = x, y = y, deg = 2)

 
def drain_cap(h_tide: np.ndarray, h_store: np.ndarray, h_min: int = -2000, pump_par = pumpcap_fit, canal_par: Tuple[float, float] = [1.016 , 2572.], h_increment: int = 50, h_wind_safe: int = 0, h_grad_pump_max: int = 4000):
    """
    Find the maximal flow rate in a system with a pump and a canal.
    The flow through the pump is determined by the gradient from inner to outer water level and a pump function.
    The flow through the canal is determined by the gradient from the canal water level to the pump inner water level and a canal flow function.
    The inner water level is unknown and estimated within this function, but a lower limit can be set.
    
    Parameters
    ----------
    h_tide : np.ndarray
        the outer water level at the pump
    h_store : np.ndarray
         the canal water level
    h_min : int
        the lower boundary of the inner water level
    pump_par : np.ndarray
        parameters of the pump function
    canal_par : Tuple[float, float]
        parameters of the canal flow function
    h_increment : int
        increment of inner water level estimation
    h_wind_safe : int
        gradient from canal to inner water level, which is induced by wind and therefore not contributing to flow
    h_grad_pump_max :int
        maximum gradient from inner to outer water level, at which pumps shall run 

    Returns
    -------
    q_channel : np.ndarray
        the actual maximum flow through canal and pump
    h_min : float
        the estimated inner water level
    q_pump : float
         the maximum flow, which could be pumped if not limited by canals

    """
    # set h_min to either absolute technical lower limit or maximal pump gradient 
    h_min = np.maximum(h_min, h_tide - h_grad_pump_max)
    
    pumplim = True
    
    # in case drainage ist limited by pumps, the minimum water level at knock increases until the flow is limited by channel_
    while pumplim:
        if(h_tide <= h_min): # if outer water level is lower then inner water level we can sluice
            q_pump = pump_par(1) # assume 1 mm gradient to pump to get some estimate - eventually sluicing is more effective
        else:
            q_pump = pump_par(h_tide - h_min)

        if(((h_store - h_min) - h_wind_safe) <= 0):
            q_channel = 0.
        else:
            q_channel = ((((h_store - h_min) - h_wind_safe)**canal_par[0])/canal_par[1])
            
        # end the loop, if h_min is set to value that q_channel is smaller than q_pump, otherwise increase h_min
        if(q_pump >= q_channel or q_channel <= 0) :
            pumplim = False
        else:
            h_min += h_increment

    # set output h_min to either technical lower limit or water level in canals
    h_min = np.minimum(h_min, h_store)

    return (q_channel, h_min, q_pump)

def storage_model (x, z, storage = 0, h_store = -1400, canal_area = 4, advance_pump = 0, maxdh = 6000):
    """
    Storage model used for the Krummhörn region
    """
    store = []
    h_min = []
    q_pump = []
    pump_cost = []
    flow_rec = []
    
    for idx, game in x.iterrows():

        # recharge storage
        storage += game['recharge']

        # get drain_cap, do not pump if dh > than specified limit
#        if(game['h_tide'] - (h_store + storage*100/canal_area)>maxdh):
#            cap = [0,h_store + storage*100/canal_area, 0.0000000001]
#        else:
#        cap = drain_cap( , channel_par = z, dh = 1, wind_safe = game['wig'], gradmax = maxdh)
        cap = drain_cap(h_tide = game['h_tide'],                                      # parse tidal water level
                        h_store = (h_store + storage*100/canal_area),   # limit maximal water flow at upper canal crest
                        canal_par = z,                                     # parse canal parameters
                        h_increment = 1,                                              # increment inner water level by 1 mm steps
                        h_wind_safe = game['wig'],                             # parse wind induced gradient
                        h_grad_pump_max = maxdh)                                     # parse maximum pump gradient
        # drain storage
        storage -= cap[0]
        # compare new storage value to lower limit of storage
        storage = np.maximum(storage, -advance_pump)
        # save time step
        store = np.append(store, storage)
        h_min = np.append(h_min, cap[1])
        q_pump = np.append(q_pump, cap[2])
            
        # save "power consumption" of pumps
        if(storage > -advance_pump):
            flow = cap[0]
        else:
            flow = game['recharge']
        flow_rec = np.append(flow_rec, flow)
        pump_cost = np.append(pump_cost, flow/cap[2])

    h_store_rec = h_store + store*100/canal_area
    
    return (h_store_rec, q_pump, h_min, flow_rec, pump_cost)
