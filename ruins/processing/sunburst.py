from collections import defaultdict

import pandas as pd

from ruins.core import DataManager


def ordered_sunburst_data(dataManager: DataManager, order=['GCM', 'RCM', 'RCP']) -> pd.DataFrame:
    """Order the info about GCM / RCM /RCP usage amounts"""
    # TODO: this can be updated later
    NAME = 'RUINS'

    # get the data 
    climate_models = dataManager.read('climate')

    # get all combinations
    combinations = [climate_models[v].attrs for v in climate_models.data_vars]
    N = len(combinations)

    # create the aggreated data structure
    agg = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: 0)))

    # fill the structure - this is the crucial part for order
    for c in combinations:
        agg[c[order[0]]][c[order[1]]][c[order[2]]] += 1

    # final lists for the sunburn plot
    ids = [NAME]
    labels = [NAME]
    parents = [""]
    values = [N]
    customdata = [(f'100% of {NAME}', '-', )]

    # Go for each order element and add as a element to the lists
    for lvl1 in agg.keys():
        ids.append(f'{NAME}.{lvl1}')
        labels.append(lvl1)
        parents.append(NAME)
        lvl1_val = sum([sum([r for r in lvl2.values()]) for lvl2 in agg[lvl1].values()])
        values.append(lvl1_val)
        customdata.append((f'{int(lvl1_val / N * 100)}% of {NAME}', '-', ))

        # level 2
        for lvl2 in agg[lvl1].keys():
            ids.append(f'{NAME}.{lvl1}.{lvl2}')
            labels.append(lvl2)
            parents.append(f'{NAME}.{lvl1}')
            lvl2_val = sum([r for r in agg[lvl1][lvl2].values()])
            values.append(lvl2_val)
            customdata.append((f'{int((lvl2_val / N * 100))}% of {NAME}', f'{int(lvl2_val / lvl1_val * 100)}% of {lvl1}', ))

            # level 3
            for lvl3 in agg[lvl1][lvl2].keys():
                ids.append(f'{NAME}.{lvl1}.{lvl2}.{lvl3}')
                labels.append(lvl3.upper())
                parents.append(f'{NAME}.{lvl1}.{lvl2}')
                val = agg[lvl1][lvl2][lvl3]
                values.append(val)
                customdata.append((f'{int(val / N * 100)}% of {NAME}', f'{int(val / lvl2_val * 100)}% of {lvl2}', ))
    
    # puh done
    return pd.DataFrame(dict(
        ids=ids,
        labels=labels,
        parents=parents,
        values=values,
        customdata1=[_[0] for _ in customdata],
        customdata2=[_[1] for _ in customdata]
    ))