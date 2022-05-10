import bubbles
import streamlit as st
import pandas as pd

st.title('RUINS climate data app')

a = pd.read_csv('data/cordex_krummh_nobias_chk_f32_ET.csv')


possibles = list(a.columns)
possibles[0] = 'None'
#st.write(possibles)
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
            
            
#st.write(select)
plt = bubbles.draw_bubbles(a, selectors = select)

st.pyplot(plt)
