from ruins.apps import weather
from ruins.tests.util import get_test_config

from ruins.core import DataManager, Config


# TODO use the config and inject the dedub config here

# TODO only run this test when the Value Error is solved
#def test_run_app():
#    """Make sure the appp runs without failing"""
#    weather.main_app()


def test_climate_indices():
    """Test only climate indices """
    config = Config(include_climate=True)
    dm = DataManager()

    # run
    weather.climate_indices(dataManager=dm, config=config)


def test_climate_indi():
    """Test climate indi function"""
    conf = get_test_config()
    dm = DataManager(**conf)

    weath = dm['weather'].read()

    # make an arbitrary selection
    w = weath['coast'].sel(vars='Tmax').to_dataframe().dropna()
    w.columns = ['_', 'Tmax']

    # run
    weather.climate_indi(w, 'Ice days (Tmax < 0°C)')
