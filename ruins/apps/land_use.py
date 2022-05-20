import streamlit as st

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
    if config.has_key('land_use_explainer'):
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
        st.session_state.land_use_explainer = True
        st.experimental_rerun()
    else:
        st.stop()


def drought_index_plot(config:Config, **kwargs):
    """
    TODO: Drought index plot based on weather data.
    """
    # get the container and translator
    container = kwargs['container'] if 'container' in kwargs else st
    t = config.translator(de=_TRANSLATE_DE, en=_TRANSLATE_EN)

    st.empty()


def cropmodel(config:Config, **kwargs):
    """
    TODO: Yield curve based on cropmodels.
    """
    container = kwargs['container'] if 'container' in kwargs else st
    t = config.translator(de=_TRANSLATE_DE, en=_TRANSLATE_EN)

    st.empty()


def main_app(**kwargs):
    """
    """
    # build the config and dataManager from kwargs
    url_params = st.experimental_get_query_params()
    config, dataManager = build_config(url_params=url_params, **kwargs)

    # set page properties and debug view    
    st.set_page_config(page_title='Land use Explorer', layout=config.layout)
    debug_view.debug_view(dataManager, config, debug_name='DEBUG - initial state')

    # explainer
    concept_explainer(config)

    # TODO: drought stress index plot (uses weather data)
    drought_index_plot(config)

    # TODO: crop models: harvest / yield curve plot
    cropmodel(config)

    # end state debug
    debug_view.debug_view(dataManager, config, debug_name='DEBUG - finished app')


if __name__ == '__main__':
    import fire
    fire.Fire(main_app)
