from typing import Union, Tuple, List
import warnings

import numpy as np
import pandas as pd

from ruins.core import DataManager


TURBINES = dict(
    e53=(0.8, 53),
    e115=(3, 115),
    e126=(7.5, 126)
)


def turbine_footprint(turbine: Union[str, Tuple[float, int]], unit: str = 'ha'):
    """Calculate the footprint for the given turbine dimension"""
    if isinstance(turbine, str):
        turbine = TURBINES[turbine]
    mw, r = turbine
    
    # get the area - 5*x * 3*y 
    area = ((5 * r) * (3 * r))   # m2

    if unit == 'ha':
        area /= 10000
    elif unit == 'km2':
        area / 1000000

    # return area, mw
    return area, mw


def upscale_windenergy(turbines: List[Union[str, Tuple[float, int]]], specs: List[Tuple[float]], site: float = 396.0) -> np.ndarray:
    """
    Upscale the given turbines to the site.
    Pass a list of turbine definitions (either names or MW, rotor_diameter tuples.).
    The function will apply the specs to the site. The specs can either be absolute number of
    turbines per turbine or relative shares per turbine type.
    Returns a tuple for each turbine type.

    Returns
    -------
    List[Tuple[float, int, float]]
        A list of tuples per turbine type. (n_turbines, total_area, total_mw)
    """
    # check input data
    #if not all([len(spec)==len(turbines) for spec in specs]):
    #    raise ValueError('The number of turbines and the number of specs must be equal.')
    
    # result container
    results = np.ones((len(specs) * len(turbines), 3)) * np.NaN

    # get the area and MW for each used turbine type
    turbine_dims = [turbine_footprint(turbine) for turbine in turbines]

    for i in range(len(specs)):
        for j in range(len(turbine_dims)):
            # get the footprint
            #area, mw = turbine_footprint(turbine, unit='ha')
            area, mw = turbine_dims[j]

            # get the available space and place as many turbines as possible
            n_turbines = int((site * specs[i][j]) / area)
            
            # get the used space and total MW
            used_area = n_turbines * area
            used_mw = n_turbines * mw

            results[i * len(turbines) + j,:] = [n_turbines, used_area, used_mw]

    return results


def load_windpower_data(dataManager: DataManager, joint_only=False) -> pd.DataFrame:
    """
    Load the raw windpower simulations and apply a MultiIndex
    
    joint_only : bool
        If True, only data for 16 joint simulations are returned (combinations of global circulation 
        model (GCM), regional climate model (RCM) and ensemble available for all three RCPs).
    """
    
    # read windpower timeseries data
    raw = dataManager.read('wind_timeseries').copy()

    # build the MultiIndex
    multi_index = pd.MultiIndex.from_tuples(
        list(zip(raw['LMO'], raw['RCP'], raw['GCM'], raw['RCM'], raw['Ensemble'], raw['joint'])), 
        names=['LMO', 'RCP', 'GCM', 'RCM', 'Ensemble', 'joint']
    )

    # tstamp index from year columns
    tstamp = pd.date_range(start='2006-12-31', periods=94, freq='Y')
    
    # transpose data
    df = raw.transpose()

    # apply multiindex
    df.columns = multi_index

    # drop multiindex rows
    df.drop(df.index[0:6], axis=0, inplace=True)

    # replace index
    df.index = tstamp
    df.index.name = 'time'

    # drop na values
    df.dropna(axis=1, how='all', inplace=True)

    if joint_only:
        # only return columns where joint==True
        return df.drop(False, level=5, axis=1)
    else:
        return df


def windpower_actions_projection(dataManager: DataManager, specs, site: float = 396.0, filter_={}) -> Tuple[List[pd.DataFrame], List[Tuple[int, float]]]:
    """
    """
    # ignore MultiIndex sorting warnings as the df is small anyway
    warnings.simplefilter('ignore', category=pd.errors.PerformanceWarning) 
    
    # I guess we have to stick to those here
    turbines=['e53', 'e115', 'e126']

    # handle the specs
    if len(specs) == 1 and any([isinstance(s, range) for s in specs]):
        # there is a range definition
        scenarios = []
        for e1 in specs[0]:
            for e2 in specs[1]:
                for e3 in specs[2]:
                    scenarios.append((e1 / 100, e2 / 100, e3 / 100))
    else:
        scenarios = specs

    # upscale the turbines to the site
    power_share = upscale_windenergy(turbines, scenarios)

    # get the data
    df = load_windpower_data(dataManager, joint_only=filter_.get('joint', False))

    # set the filter keys
    gcm_level = 2
    rcm_level = 3
    # apply filters
    for key, val in filter_.items():
        if key == 'year':
            df = df[val]
        elif key == 'rcp':
            df = df.xs(val, level=1, axis=1)

            # Multiindex has one level less
            gcm_level -= 1
            rcm_level -= 1

        elif key == 'gcm':
            df = df.xs(val, level=gcm_level, axis=1)

            # Multiindex has one level less
            rcm_level -= 1
        
        elif key == 'rcm':
            df = df.xs(val, level=rcm_level, axis=1)

    # aggregate everything
    actions = []
    dims = []
    for i in range(0, len(power_share), len(turbines)):
        data = None
        dim = []
        for j, turbine in enumerate(turbines):
            # get the chunk for this turbine (can have more than one col)
            c = df[turbine.upper(), ]

            # check the type
            if isinstance(c, pd.Series):
                chunk = c
            else:
                # c is a Dataframe -> there was more than one GCM RCM RCP combination
                chunk = c.melt().value

            # multiply with the number of turbines
            chunk *= power_share[i + j][0]

            # append the number of turbines
            dim.append(power_share[i + j][0])
            
            # merge
            if data is None:
                data = {turbine: chunk.values}
            elif turbine in data:
                data[turbine] = np.concatenate([data[turbine], chunk.values])    
            else:
                data[turbine] = chunk.values
        
        # append the data
        actions.append(pd.DataFrame(data))
        dims.append(dim)

    return actions, dims

