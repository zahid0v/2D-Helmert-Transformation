import streamlit as st
#import pandas as pd
#import numpy as np
#import math
#import altair as alt
#from st_aggrid import GridOptionsBuilder, AgGrid, ColumnsAutoSizeMode, JsCode
#from streamlit_extras.switch_page_button import switch_page



@st.cache_data
def local_css():
    # function to use local style from file style.css
    with open("style.css") as style_css_file:
        st.markdown(f"<style>{style_css_file.read()}</style>", unsafe_allow_html=True)


@st.cache_data
def load_image():
    st.image("yx1.jpg")

# -----Page Configuration
st.set_page_config(page_title="2D Helmert Transformation", page_icon="🌐", layout="wide")

# cached function to use local css from file style.css
local_css()

col1,col2 = st.columns([5,1])

# ---- Title and Description
col1.markdown('<h1 style="margin-bottom:1rem;margin-top:-6rem;text-align: center">2D Helmert Transformation</h1>',unsafe_allow_html=True,)

with col2:
    load_image()

with col1:
    tab1, tab2 = st.tabs(["General Information", "How to use this app"])
    with tab1:
        st.markdown("""
        A 2D Helmert transformation is used to transform coordinates from one rectangular source coordinate system to another target coordinate system.
        It is also known as 4 parameter similarity transformation.  
        The 2D Helmert transformation is the most common 2D transformation method in surveying. The shape of objects is not distorted.  
        The transformation consists of 4 parameters:
            
        $Y_0:$&ensp;Translation (shift) from source into target system in the y-axis direction   
        $X_0:$ Translation (shift) from source into target system in the x-axis direction  
        $k:$ Scale  
        $θ:$ Rotation
        """)
        st.latex(r'''
            \begin{bmatrix} Y\\ X \end{bmatrix}^{Target} = 
            \begin{bmatrix} Y_0 \\ X_0\end{bmatrix} 
            + k  \begin{bmatrix} cos\theta & sin\theta \\ -sin\theta & cos\theta \end{bmatrix} 
            \begin{bmatrix} Y \\ X \end{bmatrix} ^{Source}
         
            ''')
        st.write("With $a=k \cdot cosθ$ and $b=k \cdot sinθ$ the equations can be written with the 4 parameters $Y_0,X_0,a,b$ as:")
        st.latex(r'''
            y^{Target} = Y_0 + b \cdot x^{Source} + a \cdot y^{Source}
            ''')
        st.latex(r'''
            x^{Target} = X_0 + a \cdot x^{Source} - b \cdot y^{Source}
            ''')
        st.caption("Please note that contrary to the mathematical convention, the equations are written according to geodetic practice, where the x-axis points North and the y-axis East.")
        st.markdown("""
        Two or more points with known coordinates in both source and target system must be known
        to determine the transformation parameters.
        If more than 2 common points are given, a standard deviation and residuals of the common
        points can be calculated.  
        """)

    with tab2:
        st.markdown(
        """
        - **Upload Coordinates:** The user can upload files with the coordinates in the source
          and target system. The files must have at least three columns with column 1 for
           the point name, column 2 for the East coordinate and column 3 for the North coordinate.
           The files may have one header row (i.e. Name/East/North or Point/x/y). If no text header 
           row is detected the default header is used (Name/y/x). If nothing is uploaded example
           coordinates are used.
        - **Select Common Points:** Common points are identified by the point name.
           At first all common points are selected and shown with their residuals.
          The user can unselect or select points but at least 2 common points need to be selected.
          The transformation parameters are re-calculated after every change in the selection of
           common points.
        - **Download Transformed Points:**  The coordinates that were uploaded as source
           coordinates are transformed with the calculated transformation parameters.  
          The transformed coordinates can be downloaded as csv file.
           A transformation report can be downloaded as txt file.
        - **Python libraries:** streamlit, pandas, st_aggrid, streamlit_extras, altair
        - for problems and suggestions contact: s.engelhard@gmx.net
        """
        )
        