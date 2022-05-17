import streamlit as st

from ruins.core import build_config, debug_view, DataManager, Config


def main_app(**kwargs):
    """Describe the params in kwargs here
    """
    # build the config and dataManager from kwargs
    url_params = st.experimental_get_query_params()
    config, dataManager = build_config(url_params=url_params, **kwargs)

    # set page properties and debug view    
    st.set_page_config(page_title='Agriculture Explorer', layout=config.layout)
    debug_view.debug_view(dataManager, config, debug_name='DEBUG - initial state')

    # build the app
    st.header('Agriculture Explorer')
    # TODO: move this text also into story mode?
    st.markdown('''In this section, we provide visualizations to assess the impacts of climate change on yields of different crops and the uncertainty of these impacts. Under these uncertainties, farmers must make decisions that also involve uncertainty.''',unsafe_allow_html=True)

    # TODO: drought stress index plot (uses weather data)

    # TODO: crop models: harvest / yield curve plot

    # end state debug
    debug_view.debug_view(dataManager, config, debug_name='DEBUG - finished app')


if __name__ == '__main__':
    import fire
    fire.Fire(main_app)
