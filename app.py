import streamlit as st

# Set up the Streamlit app layout
st.title('Juridische Werkbank')

# Create tabs
tab1, tab2, tab3 = st.tabs(['ECLI Invoer', 'Kennisbank', 'Stappenplan'])

with tab1:
    st.header('ECLI Invoer')
    # Content for ECLI input will go here

with tab2:
    st.header('Kennisbank')
    # Content for Knowledge Base will go here

with tab3:
    st.header('Stappenplan')
    # Content for Steps Plan will go here
