from typing import Tuple
import numpy as np
import pandas as pd

x = np.array([7.,6.,5.,4.,3.5,3.,2,1,0,5.,4.,3.5,3.,2])
y = np.array([0,4.2,8.4,12.6,14.5,15.8,17.5,19,20.5,8.4,12.6,14.5,15.8,17.5])
pumpcap_fit = np.polynomial.polynomial.Polynomial.fit(x = x, y = y, deg = 2)

 
def drain_cap(h_tide: np.ndarray, h_store: np.ndarray, h_min: int = -2000, pump_par = pumpcap_fit, channel_par: Tuple[float, float] = [1.016 , 2572.], dh: int = 50, wind_safe: int = 0, gradmax: int = 4000):
    """
    Find sthe maximal flow rate in a system with a pump and a canal.
    The flow through the pump is determined by the gradient from inner to outer water level and a pump function.
    The flow through the canal is determined by the gradient from the canal water level to the pump inner water level and a flow function.
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
    channel_par : Tuple[float, float]
        parameters of the canal flow function
    dh : int
        increment of inner water level estimation
    wind_safe : int
        gradient from canal to inner water level, which is induced by wind and therefore not contributing to flow
    gradmax :int
        maximum gradient from inner to outer water level, at which pumps shall run 

    Returns
    -------
    a_channel : np.ndarry
        the actual maximum flow through canal and pump
    h_min : float
        the estimated inner water level
    q_pump : float
         the maximum flow, which could be pumped if not limited by canals

    """
    # set h_min to either absolute technical lower limit or maximal pump gradient 
    h_min = np.maximum(h_min, h_tide - gradmax)
    
    pumplim = True
    
    # in case drainage ist limited by pumps, the minimum water level at knock increases until the flow is limited by channel_
    while pumplim:
        if(h_tide <= h_min):
            q_pump_m3 = pump_par((1)/1000) # assume 1 mm gradient to pump to get some estimate - eventually sluicing is more effective
            q_pump = q_pump_m3 * 3600 / (35000 * 100 * 100) * 1000 * 4  # "*3600 / (35000 * 100 * 100) * 1000 * 4)" converts m^3/s in mm/h
        else:
            q_pump_m3 = pump_par((h_tide - h_min)/1000)
            q_pump = q_pump_m3 *3600 / (35000 * 100 * 100) * 1000 * 4  # "*3600 / (35000 * 100 * 100) * 1000 * 4)" converts m^3/s in mm/h

        if(((h_store - h_min) - wind_safe) <= 0):
            q_channel = 0.
        else:
            q_channel = ((((h_store - h_min) - wind_safe)**channel_par[0])/channel_par[1])
            
        # end the loop, if h_min is set to value that q_channel is smaller than q_pump, otherwise increase h_min
        if(q_pump >= q_channel or q_channel <= 0) :
            pumplim = False
        else:
            h_min += dh

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
        cap = drain_cap(game['h_tide'], (h_store + storage*100/canal_area), channel_par = z, dh = 1, wind_safe = game['wig'], gradmax = maxdh)

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
