from typing import List

import pandas as pd


def multiindex_pdsi_data(pdsi: pd.DataFrame, grouping: List[str] = ['rcp', 'gcm'], filters: dict = None, inplace: bool = False) -> pd.DataFrame:
    """
    """
    # make a copy if not inplace
    if not inplace:
        data = pdsi.copy()
    else:
        data = pdsi

    # unpack the columns 
    unpack = [c.split('.') for c in pdsi.columns]

    # split into GCM, RCM, RCP
    levels = dict(
        rcp=[u[-1] for u in unpack],
        gcm=[u[1] if len(u)==5 else u[0] for u in unpack],
        rcm=[u[2] if len(u)==5 else u[2] for u in unpack]
    )
    # build the multiindex
    data.columns = pd.MultiIndex.from_tuples(zip(*[levels.get(l) for l in grouping], data.columns.to_list()))

    if filters is not None:
        for key, filt in filters.items():
            data.drop(columns=filt, level=grouping.index(key), inplace=True)

    # apply the index
    _ , indexer = data.columns.sortlevel(list(range(len(grouping))))
    data = data.iloc[:, indexer]

    return data