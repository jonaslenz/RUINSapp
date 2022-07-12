from typing import List

import streamlit as st
from streamlit_graphic_slider import graphic_slider
from plotly.subplots import make_subplots

from ruins.core import build_config, debug_view, DataManager, Config
from ruins.plotting import pdsi_plot, tree_plot
from ruins.processing.pdsi import multiindex_pdsi_data


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


def quick_access(config: Config, container=st.sidebar) -> None:
    """Add quick access buttons"""
    # get the step
    step = config.get('landuse_step', 'intro')

    # make translations
    if config.lang == 'de':
        lab_drought = 'Dürreindex'
        lab_crop = 'Wuchsmodelle'
    else:
        lab_drought = 'Drought index'
        lab_crop = 'Crop models'
    
    # build the colums
    l, r = container.columns(2)

    # switch the cases
    if step == 'intro':
        go_pdsi = l.button(lab_drought)
        go_crop = r.button(lab_crop)
    elif step == 'pdsi':
        go_pdsi = False
        go_crop = l.button(lab_crop)
    elif step == 'crop_model':
        go_pdsi = l.button(lab_drought)
        go_crop = False
    
    # navigate the user
    if go_pdsi:
        st.session_state.landuse_step = 'pdsi'
        st.experimental_rerun()
    
    if go_crop:
        st.session_state.landuse_step = 'crop_model'
        st.experimental_rerun()

@st.experimental_memo
def cached_pdsi_plot(_data, group_by: List[str] = None, add_tree: bool = True, lang='de'):
        # build the multiindex and group
    if group_by is not None:
        _data = multiindex_pdsi_data(_data, grouping=group_by, inplace=True)

        # build the figure
        fig = make_subplots(2, 1, shared_xaxes=True, vertical_spacing=0.0, row_heights=[0.35, 0.65])
        fig = tree_plot(_data, fig=fig, row=1, col=1)
        fig.update_layout(height=600)
    else:
        fig = make_subplots(1, 1)

    # run heatmap plot    
    fig = pdsi_plot(_data, fig=fig, row=2 if group_by is not None else 1, col=1, lang=lang)

    # return
    return fig

def drought_index(dataManager: DataManager, config: Config) -> None:
    """Loading Palmer drought severity index data for the region"""
    st.title('Drought severity index')
    
    # add some controls
    pdsi_exp = st.sidebar.expander('PDSI options', expanded=True)
    group_by = st.sidebar.multiselect('GROUPING ORDER', options=['rcp', 'gcm', 'rcm'], default=['rcp', 'gcm'], format_func=lambda x: x.upper())
    if len(group_by) == 0:
        group_by = None
    
    # load the data
    pdsi = dataManager.read('pdsi').dropna()

    # use the cached version
    fig = cached_pdsi_plot(pdsi, group_by=group_by)

    # add the figure
    st.plotly_chart(fig, use_container_width=True)


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
    elif config.get('landuse_step', 'intro') == 'intro':
        # if not in story mode, skip the intro
        step = 'pdsi'
    
    # show the quick access buttons
    quick_expander = st.sidebar.expander('QUICK ACCESS', expanded=True)
    quick_access(config, quick_expander)
    
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
