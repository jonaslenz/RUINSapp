import streamlit as st
import pandas as pd

from ruins.core import DataManager


INDICES = dict(
    summer='Summer days (Tmax ≥ 25°C)',
    ice='Ice days (Tmax < 0°C)',
    frost='Frost days (Tmin < 0°C)',
    hot='Hot days (Tmax ≥ 30°C)',
    tropic='Tropic nights (Tmin ≥ 20°C)',
    rainy='Rainy days (Precip ≥ 1mm)'
)


def climate_index_agg(ts, index):
    """Aggregate the index days based on the available INDICES"""
     # drop NA
    ts = ts.dropna()

    if index == 'summer':  # summer days
        return (ts >= 25.).groupby(ts.index.year).sum()
    elif index == 'ice':  # ice days
        return (ts < 0.).groupby(ts.index.year).sum()
    elif index == 'frost':  # frost days
        return (ts < 0.).groupby(ts.index.year).sum()
    elif index == 'hot':  # hot days
        return (ts >= 30.).groupby(ts.index.year).sum()
    elif index == 'tropic':  # tropic night
        return (ts >= 20.).groupby(ts.index.year).sum()
    elif index == 'rainy':  # rainy days
        return (ts >= 1.).groupby(ts.index.year).sum()
    else:
        raise ValueError(f"The Index {index} is not supported. Use one of: {','.join(INDICES.keys())}")


@st.experimental_memo
def calculate_climate_indices(_dataManager: DataManager, station: str, variable: str, ci: str, rolling_windows=(10, 5), rolling_center=True, rcps=('rcp26', 'rcp45', 'rcp85')) -> pd.DataFrame:
    """
    Calculates all relevant climate indices for the given climate data, as configured in the DataManager.
    The procedure will return a pandas DataFrame with aggregated index information for the weather data.
    For each of the available RCP scenarios, the indices are calculated as well. 
    By default, for each scenario and the weather data, a rolling mean is calculated

    Parameters
    ----------
    _dataManager : ruins.core.DataManager
        DataManager instance containing the 'weather' and 'climate' data
    station : str
        Station name for filtering weather data. Has to exist as data variable
        in the weather netCDF
    variable : str
        Variable name for filtering. Has to exist as dimension value in both,
        the weather and climate netCDF
    ci : str
        Index name. Can be any key of ruins.processing.climate_indices.INDICES
    rolling_windows : Tuple[int, int]
        The window sizes for weather (0) and climate (1) rolling means
    rolling_center : bool
        If True (default), the rollwing window center will be used as value
    rcps : List[str]
        Short names of the RCP scenarios to include. Usually only 
        ('rcp26', 'rcp45', 'rcp85') are available.

    Returns
    -------
    data : pd.DataFrame
        DataFrame with all calcualted indices and the year as index

    """
    dataManager = _dataManager
    # load data
    weather = dataManager['weather'].read()[station].sel(vars=variable).to_dataframe()[station].dropna()
    climate = dataManager['cordex_krummh'].read().sel(vars=variable).to_dataframe()
    climate.drop('vars', axis=1, inplace=True)

    # get weather index and rolling
    data = pd.DataFrame(climate_index_agg(weather, ci).astype(int))
    data.columns = [variable]
    data['rolling'] = data.rolling(rolling_windows[0], center=rolling_center).mean()

    # get climate index
    for col in climate.columns:
        df = pd.DataFrame(climate_index_agg(climate[col], ci).astype(int))
        data = pd.merge(data, df, right_index=True, left_index=True, how='outer')

    # get RCP rolling
    for rcp in rcps:
        # select columns that end with rcp
        criteria = [c.endswith(rcp) for c in data.columns]
    
        # subset
        df = data[data.columns[criteria]]
    
        # rolling mean of mean rcp values
        roll = df.mean(axis=1).rolling(rolling_windows[1], center=rolling_center).mean()
        roll = pd.DataFrame(index=roll.index, data={f'{rcp}.rolling': roll.values})
    
        # add back to data
        data = pd.merge(data, roll, right_index=True, left_index=True, how='outer')

    return data