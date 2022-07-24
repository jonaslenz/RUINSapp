import os
import streamlit as st
import pandas as pd
import numpy as np
import datetime

from ruins.core import build_config, debug_view, DataManager, Config
from ruins.plotting import floodmodel


_TRANSLATE_EN = dict(
    title='Extreme events & flooding',
    introduction="""
    In this section, a model is presented to assess the influence of sea level change, inland precipitation, and 
    management options on flooding risks in a below sea level and thus drained area in northern Germany.
"""
)

_TRANSLATE_DE = dict(
    title='Extremereignisse & Überflutungen',
    introduction="""
    In diesem Abschnitt wird ein Modell vorgestellt, mit dem sich der Einfluss von Meeresspiegelveränderungen, 
    Inlandsniederschlägen und Managementoptionen auf Überflutungsrisiken in einem unterhalb des Meeresspiegels 
    liegenden und damit entwässerten Gebiet in Norddeutschland auswirken.
"""
)



def user_input_defaults():
    # streamlit input stuff:
    
    slr = 400   # sea level rise in mm (0, 400, 800, 1200, 1600)

    #recharge_vis = "absolute"   # "cumulative" or "absolute"
    
    # default event z.B.:
    # (wählt Jonas noch aus)
    
    #if time == "2012":
    t1 = datetime.date(2011, 12, 28)
    t2 = datetime.date(2012, 1, 12)

        
    ## KGE
    # kge = st.slider("Canal flow uncertainty [KGE * 100]",71,74, value = 74)
    kge = 74 # nicht mehr user input
    
    ## canal flow input
    # canal_flow_scale = st.number_input("Factor to canal capacity", min_value=0.5, max_value=3., value= 1.0, step=0.1) 
    canal_flow_scale = 1.0 # jetzt nicht mehr user input
    

    canal_area = 4 # user input: st.radio(
        #"Share of water area on catchment [%].",
        #(3, 4))
    
    ## pump before event
    advance_pump = 0. # user input: st.radio(
        #"Forecast Pumping",
        #(0, 4)

    ## visualisation of used pump capacity
    # pump_vis = st.radio("Pump capacity visualisation", ["absolute", "cumulative"])

    ## pump efficiency
    # maxdh = st.number_input("Stop pumping if dh at Knock is greater than x dm\n(technical limit = 70dm)", min_value=10, max_value=70, value= 40, step=2) 
    maxdh = 4000 # nicht mehr user input
        
    return slr, t1, t2, kge, canal_flow_scale, canal_area, advance_pump, maxdh


def timeslice_observed_data(t1, t2, slr, dataManager):

    raw = dataManager['levelknock'].read()
    weather_1h = dataManager['prec'].read()

    # tide data
    tide = raw['L011_pval'][t1:t2]*1000 + slr

    # hourly recharge data
    hourly_recharge = weather_1h["Prec"][t1:t2]
    hourly_recharge = hourly_recharge.rolling("12h").mean() # changed by Jonas
    
    # EVEx5 observed
    
    EVEx5 = pd.read_csv('//home/lucfr/hydrocode/RUINS_hydropaper-newlayout/streamlit/data/levelLW.csv')
    EVEx5.index = pd.to_datetime(EVEx5.iloc[:,0])
    EVEx5_lw_pegel_timesliced = (EVEx5['LW_Pegel_Aussen_pval']/100+0.095)[t1:t2]
    
    # pump observed
    pump_capacity_observed = raw['sumI'][t1:t2] / 12.30
    
    return tide, hourly_recharge, EVEx5_lw_pegel_timesliced, pump_capacity_observed


def create_initial_x_dataset(tide_data, hourly_recharge):
    
    wig = tide_data*0
    # what is this and why? Unused!
    
    x = pd.DataFrame.from_dict({'recharge' : hourly_recharge,
                                'h_tide' : tide_data,
                                'wig' : wig})
    
    return x 


def create_all_kge_canal_par_dataframe(dhq_folder_path):
    all_kge_canal_par_df = pd.DataFrame()

    for file in os.listdir(dhq_folder_path):
        if file.startswith('dhq_post'):
            dhq_ndarray = np.load(dhq_folder_path + file)['a']
            dhq_df = pd.DataFrame(dhq_ndarray)
            dhq_df.insert(loc=0, column='KGE', value=int(''.join(filter(str.isdigit, file))))
            all_kge_canal_par_df = pd.concat([all_kge_canal_par_df, dhq_df], ignore_index=True)
            
    return all_kge_canal_par_df


def create_model_runs_list(all_kge_canal_par_df, kge, canal_flow_scale, canal_area, x_df, advance_pump, maxdh):
    import dev.drain_cap as drain_cap
    
    model_runs = []
    
    kge_canal_par_df = all_kge_canal_par_df.loc[all_kge_canal_par_df.KGE == kge]
    canal_par_array = kge_canal_par_df[['parexponent', 'parfactor']].to_numpy()
    
    for z in canal_par_array:
    
        z[1] /= canal_flow_scale
        
        # run storage model
        (x_df['h_store'], 
         q_pump,
         x_df['h_min'], 
         x_df['flow_rec'], 
         pump_cost) = drain_cap.storage_model(x_df,
                                              z, 
                                              storage = 0, 
                                              h_store = -1350, # geändert von Jonas
                                              canal_area = canal_area, 
                                              advance_pump = advance_pump, 
                                              maxdh = maxdh)
        model_runs.append((x_df['h_store'], pump_cost))
        #pump_capacity_model_runs.append(pump_cost)
    
    # q_pump no usage later?
    
    # return hg_model_runs, pump_capacity_model_runs
    return model_runs


def run_streamlit():
    from plotly.subplots import make_subplots

    config, dataManager = build_config()

    #st.set_page_config(layout="centered")
    #st.set_page_config(layout="wide")
    #st.title('RUINS - short term inland flood forecast')
    st.sidebar.header('Control Panel')


    slr, t1, t2, kge, canal_flow_scale, canal_area, advance_pump, maxdh = user_input_defaults()

    with st.sidebar.expander("Event selection"):
        time = st.radio(
            "Event",
            ("2012", "2017", "choose custom period")    # reduced to 2 nice events -> "custom period" only in expert mode or for self hosting users?
        )
        if time == 'choose custom period':
            t1 = st.date_input("start", datetime.date(2017, 12, 1))
            dt2 = st.number_input("Number of days", min_value=3, max_value=20, value= 10, step=1) 
            t2 = t1 + datetime.timedelta(dt2)
    
    with st.sidebar.expander("Sea level rise"):
        slr = st.radio(
            "Set SLR [mm]",
            (0, 400, 800, 1200, 1600)
        )
    
    if time == "2012":
        t1 = datetime.date(2011, 12, 28)
        t2 = datetime.date(2012, 1, 12)

    if time == "2017":
        t1 = datetime.date(2017, 3, 15)
        t2 = datetime.date(2017, 3, 25)
    
    with st.sidebar.expander("Management options"):
    # pump before event
    #    advance_pump = st.number_input("Additional spare volume in canals", min_value=-5., max_value=8., value= 0., step=0.1)
        advance_pump = st.radio(
            "Forecast Pumping",
            (0, 4)
        )
        Canal_area = st.radio(
            "Share of water area on catchment [%].",
            (3, 4)
        )

    # Model runs:

    (tide, 
    hourly_recharge, 
    EVEx5_lw_pegel_timesliced, 
    pump_capacity_observed) = timeslice_observed_data(t1, t2, slr, dataManager)

    x = create_initial_x_dataset(tide, hourly_recharge)

    jonas_repo_path = '//home/lucfr/hydrocode/RUINS_hydropaper/'

    dhq_folder_path = os.path.join(jonas_repo_path, 'streamlit', 'cache/')

    all_kge_canal_par_df = create_all_kge_canal_par_dataframe(dhq_folder_path)

    hg_model_runs = create_model_runs_list(all_kge_canal_par_df, kge, canal_flow_scale, canal_area, x, advance_pump, maxdh)

    # plotting:

    col1, col2 = st.columns(2)

    with col1:
        fig1 = make_subplots(2, 1)
        fig1 = floodmodel.sea_level(tide_data=tide, knock_level=6.5, fig=fig1, row=1, col=1)
        fig1 = floodmodel.canal_recharge(recharge_data=hourly_recharge, cumsum=False, fig=fig1, row=2, col=1)
        st.plotly_chart(fig1, use_container_width=True)   
    
    with col2:
        fig2 = make_subplots(2, 1)
        fig2 = floodmodel.absolute_water_level(hg_model_runs, EVEx5_lw_pegel_timesliced, fig=fig2, row=1, col=1)
        fig2 = floodmodel.pump_capacity(hg_model_runs, pump_capacity_observed, cumsum=False, fig=fig2, row=2, col=1)
        st.plotly_chart(fig2, use_container_width=True)



def concept_explainer(config: Config, **kwargs):
    """Show an explanation, if it was not already shown.
    """
    # check if we saw the explainer already
    if config.has_key('extremes_explainer'):
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
        st.session_state.extremes_explainer = True
        st.experimental_rerun()
    else:
        st.stop()


# def demonstrate_flood_model(config:Config, **kwargs):
#     """
#     Demonstrate the flooding model using a real-life flood disaster.
#     """
#     container = kwargs['container'] if 'container' in kwargs else st
#     t = config.translator(de=_TRANSLATE_DE, en=_TRANSLATE_EN)

#     st.empty()


def flood_model(config:Config, **kwargs):
    """
    Version of the flooding model in which the user can play around with the parameters.
    """
    container = kwargs['container'] if 'container' in kwargs else st
    t = config.translator(de=_TRANSLATE_DE, en=_TRANSLATE_EN)

    with st.empty():
        run_streamlit()
    

def main_app(**kwargs):
    """
    """
    # build the config and dataManager from kwargs
    url_params = st.experimental_get_query_params()
    config, dataManager = build_config(url_params=url_params, **kwargs)

    # set page properties and debug view    
    st.set_page_config(page_title='Sea level rise Explorer', layout=config.layout)
    debug_view.debug_view(dataManager, config, debug_name='DEBUG - initial state')

    # explainer
    concept_explainer(config)

    # TODO: Demonstrate model using one or two real flood events.
    #demonstrate_flood_model(config)

    # TODO: expert mode: user takes control over model parameters
    flood_model(config)

    # end state debug
    debug_view.debug_view(dataManager, config, debug_name='DEBUG - finished app')


if __name__ == '__main__':
    import fire
    fire.Fire(main_app)
