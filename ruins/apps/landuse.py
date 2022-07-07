from typing import List

import streamlit as st
from streamlit_graphic_slider import graphic_slider

from ruins.core import build_config, debug_view, DataManager, Config


_TRANSLATE_EN = dict(
    title='Land use, climate change & uncertainty',
    introduction="""
    In this section, we provide visualizations to assess the impacts of climate change on yields of different crops 
    and the uncertainty of these impacts. Under these uncertainties, farmers must make decisions that also involve 
    uncertainty.
"""
)

_TRANSLATE_DE = dict(
    title='Landnutzung, Klimawandel und Unsicherheiten',
    introduction="""
    In diesem Abschnitt stellen wir Visualisierungen zur Verfügung, um die Auswirkungen des Klimawandels auf die 
    Erträge verschiedener Kulturpflanzen und die Unsicherheit dieser Auswirkungen zu bewerten. 
    Unter diesen Ungewissheiten müssen Landwirte Entscheidungen treffen, die ihrerseits mit Ungewissheit verbunden sind.
"""
)

def concept_explainer(config: Config, **kwargs):
    """Show an explanation, if it was not already shown.
    """
    # check if we saw the explainer already
    if not config.get('story_mode', True) or config.get('landuse_step', 'intro') != 'intro':
        return
    
    # get the container and a translation function
    container = kwargs['container'] if 'container' in kwargs else st
    t = config.translator(en=_TRANSLATE_EN, de=_TRANSLATE_DE)

    # place title and intro
    container.title(t('title'))
    container.markdown(t('introduction'), unsafe_allow_html=True)

    # check if the user wants to continue
    accept = container.button('WEITER' if config.lang == 'de' else 'CONTINUE')
    if accept:
        st.session_state.landuse_step = 'pdsi'
        st.experimental_rerun()
    else:
        st.stop()


def drought_index(dataManager: DataManager, config: Config) -> None:
    """Loading Palmer drought severity index data for the region"""
    st.title('Drought severity index')
    st.warning('Drought severity index output is not yet implemented')


def crop_models(dataManager: DataManager, config: Config) -> None:
    """Load and visualize crop model yields"""
    st.title('Crop models')
    st.warning('Crop model output is not yet implemented')

def main_app(**kwargs):
    """
    """
    # build the config and dataManager from kwargs
    url_params = st.experimental_get_query_params()
    config, dataManager = build_config(url_params=url_params, **kwargs)

    # set page properties and debug view    
    st.set_page_config(page_title='Land use Explorer', layout=config.layout)
    debug_view.debug_view(dataManager, config, debug_name='DEBUG - initial state')

    if config.get('story_mode', True):
        step = config.get('landuse_step', 'intro')
    else:
        # always go to crop models
        step = 'crop_model'
    
    # explainer
    if step == 'intro':
        concept_explainer(config)
    elif step == 'pdsi':
        drought_index(dataManager, config)
    elif step == 'crop_model':
        crop_models(dataManager, config)
    else:
        st.error(f"Got unknown input. Please tell the developer: landuse_step=='{step}'")
        st.stop()


    # end state debug
    debug_view.debug_view(dataManager, config, debug_name='DEBUG - finished app')


if __name__ == '__main__':
    import fire
    fire.Fire(main_app)
