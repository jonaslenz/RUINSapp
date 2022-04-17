"""
Topic Selector
==============

"""
from typing import List
import streamlit as st
from PIL import Image

from ruins.core import Config
from ruins.core.debug_view import debug_view


_TRANSLATE_EN = dict(
    introduction="""Inside the RUINS App you can explore different topics. Please select one, you can select another topic later in the sidebar.""",
    warming_explainer="""**Warming**: In this topic we provide visualisations to explore changes in observed weather data. Based on different variables and climate indices it is possible to investigate how climate change manifests itself in different variables, at different stations and with different temporal aggregation.""",
    weather_indices_explainer="""**Weather indices**: Short weather indices description."""
    )
_TRANSLATE_DE = dict(
    introduction="""Innerhalb der RUINS App können verschiedene Themen erkundet werden. Bitte wählen Sie eines aus, das Thema kann später über die Seitenleiste geändert werden.""",
    warming_explainer="""**Erwärmung**: In diesem Thema werden Visualisierungen zur Verfügung gestellt, anhand derer sich Veränderungen in beobachteten Wetterdaten untersuchen lassen. Anhand verschiedener Variablen und Klimaindizes lässt sich untersuchen, wie sich der Klimawandel in verschiedenen Variablen, an verschiedenen Stationen und mit unterschiedlicher zeitlicher Aggregation manifestiert.""",
    weather_indices_explainer="""**Klimaindizes**: Kurze Beschreibung des Themas Klimaindizes"""
    )


def current_topic_selector(config: Config, expander_container = st.sidebar, **kwargs):
    """
    Select a topic from a list of topics with a short description and a 
    symbolic image.
    """
    container = st if 'container' not in kwargs else kwargs['container']
    t = kwargs.get('translator', config.translator(en=_TRANSLATE_EN, de=_TRANSLATE_DE))

    if 'topic_list' in kwargs:
        topic_list = kwargs['topic_list']
    else:
        topic_list = config['topic_list']

    # check if the topic was set
    if config.has_key('current_topic'):
        cap = 'Select topic:' if config.lang == 'en' else 'Thema auswählen:'
        expander_container.selectbox(cap, topic_list, key='current_topic')
        return

    # From here on full topic select
    # introduction
    container.title("Select a topic you would like to explore" if config.lang == 'en' else "Wählen Sie ein Thema, das Sie erkunden möchten")
    container.markdown(t('introduction'))
    
    # default value
    warming = None

    if 'Warming' in topic_list:
        # use a new container for each row
        row_container = st

        # column topic select (image, description, button)
        image_column, description_column, button_column = row_container.columns([1,3,1])
        image = Image.open('RUINS_logo_small.png') # idea: display symbol images for each topic
    
        image_column.image(image)
        warming = button_column.button("Click here to select topic Warming" if config.lang == 'en' else "Hier klicken um das Thema Erwärmung auszuwählen")
        description_column.markdown(t('warming_explainer'))
        row_container.markdown("""___""")

    # default value
    weather_indices = None

    if 'Weather Indices' in topic_list:
        # use a new container for each row
        row_container = st
        
        # column topic select (image, description, button)
        image_column, description_column, button_column = row_container.columns([1,3,1])

        image_column.image(image)
        weather_indices = button_column.button("Click here to select topic Weather indices" if config.lang == 'en' else "Hier klicken um das Thema Klimaindizes auszuwählen")
        description_column.markdown(t('weather_indices_explainer')) # TODO
        row_container.markdown("""___""")
    
    if warming:
        st.session_state.current_topic = 'Warming'  
        st.experimental_rerun()  
    elif weather_indices:
        st.session_state.current_topic = 'Weather Indices'
        st.experimental_rerun()
    else:
        # dev only
        debug_view(dataManager=None, config=config)
        st.stop()



def topic_select(config: Config, expander_container=st.sidebar, **kwargs) -> str:
    """
    Through this function a topic is selected.
    If we are either not in story_mode or if a topic is already selected, 
    a topic can be selected in a selectbox in the sidebar 
    (compact_topic_selector()).
    Otherwise a topic is selected in the full_topic_selector() which 
    provides a list of topics with a short description and a symbolic 
    image.
    """
    # set default story mode 
    story_mode = config.get('story_mode', True)
    if 'story_mode' in kwargs:
        story_mode = kwargs['story_mode']

    # switch the story_mode
    if not story_mode:
        st.session_state.current_topic = 'Warming'
    
    # select topic
    current_topic_selector(config=config, expander_container=expander_container, **kwargs)

    
def debug_main(**kwargs):
    from ruins.core import build_config
    params = st.experimental_get_query_params()
    config, _ = build_config(omit_dataManager=True, url_params=params, **kwargs)

    topic_select(config=config)

    st.json(st.session_state)

if __name__ == '__main__':
    import fire
    fire.Fire(debug_main)
