import streamlit as st
import pandas as pd

from ruins.core import build_config, debug_view, DataManager, Config
from ruins.plotting import bubble_plot


_TRANSLATE_EN = dict(
    title='Bubble plot',
    introduction="""
    Bubble plot of RCP scenarios.
"""
)

_TRANSLATE_DE = dict(
    title='Bubble plot',
    introduction="""
    Bubble plot der RCP Szenarien.
"""
)


def concept_explainer(config: Config, **kwargs):
    """Show an explanation, if it was not already shown.
    """
    # check if we saw the explainer already
    if config.has_key('bubbles_explainer'):
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
        st.session_state.bubbles_explainer = True
        st.experimental_rerun()
    else:
        st.stop()


def show_bubbles(dataManager: DataManager, config: Config):
    """
    Shows the bubble plot.
    """
    data = dataManager['cordex_krummh_nobias_chk_f32_ET'].read()

    possibles = list(data.columns)
    possibles[0] = 'None'

    level1 = st.sidebar.radio('Select Index1:', possibles, index = 1)
    level2 = st.sidebar.radio('Select Index2:', possibles, index = 2)
    level3 = st.sidebar.radio('Select Index3:', possibles, index = 0)

    if(level1 == possibles[0]):
        select = []
    else:
        if (level2 == possibles[0]):
            select = [level1]
        else:
            if (level3 == possibles[0]):
                select = [level1, level2]
            else:
                select = [level1, level2, level3]

    fig = bubble_plot.draw_bubbles(data, selectors = select)

    st.pyplot(fig)
    

def main_app(**kwargs):
    """
    """
    # build the config and dataManager from kwargs
    url_params = st.experimental_get_query_params()
    config, dataManager = build_config(url_params=url_params, **kwargs)

    # set page properties and debug view    
    st.set_page_config(page_title='Bubble plot', layout=config.layout)
    debug_view.debug_view(dataManager, config, debug_name='DEBUG - initial state')

    # explainer
    concept_explainer(config)

    # show bubbles
    show_bubbles(dataManager, config)

    # end state debug
    debug_view.debug_view(dataManager, config, debug_name='DEBUG - finished app')


if __name__ == '__main__':
    import fire
    fire.Fire(main_app)
