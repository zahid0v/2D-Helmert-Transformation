import math
import streamlit as st
#import pandas as pd
import numpy as np

import altair as alt
from st_aggrid import GridOptionsBuilder, AgGrid, ColumnsAutoSizeMode, JsCode
from streamlit_extras.switch_page_button import switch_page


@st.cache_data
def local_css():
    # function to use local style from file style.css
    # style is used to change font size of expander text
    with open("style.css") as style_css_file:
        st.markdown(f"<style>{style_css_file.read()}</style>", unsafe_allow_html=True)


def deg_to_degminsec(degrees):
    # calculates degminsec from decimal degrees, returns string
    degint = int(degrees)
    minutes = ((abs(degrees) - abs(degint)) * 60)
    minint = int(minutes)
    seconds = (minutes - minint) * 60
    secint = int(seconds)
    #out = "{:02d}".format(degint) + " " + "{:02d}".format(minint) + " ""{:02d}".format(secint) + "." + "{:0.5f}".format(seconds)[-5:]
    out = f'{"{:02d}".format(degint)} {"{:02d}".format(minint)} {"{:02d}".format(secint)}.{"{:0.5f}".format(seconds)[-5:]}'
    return out


def update_transformation():
    #updates dataframe according to value in "Selected" column
    st.session_state.mean_source_y = st.session_state.common_points_df.loc[st.session_state.common_points_df["Selected"], "y_1"].mean()
    st.session_state.mean_source_x = st.session_state.common_points_df.loc[st.session_state.common_points_df["Selected"], "x_1"].mean()
    st.session_state.mean_target_y = st.session_state.common_points_df.loc[st.session_state.common_points_df["Selected"], "y_2"].mean()
    st.session_state.mean_target_x = st.session_state.common_points_df.loc[st.session_state.common_points_df["Selected"], "x_2"].mean()
    st.session_state.common_points_df["y_1_c"] = st.session_state.common_points_df["y_1"] - st.session_state.mean_source_y
    st.session_state.common_points_df["x_1_c"] = st.session_state.common_points_df["x_1"] - st.session_state.mean_source_x
    st.session_state.common_points_df["y_2_c"] = st.session_state.common_points_df["y_2"] - st.session_state.mean_target_y
    st.session_state.common_points_df["x_2_c"] = st.session_state.common_points_df["x_2"] - st.session_state.mean_target_x
    st.session_state.common_points_df["x_1_c*y_2_c"] = st.session_state.common_points_df["x_1_c"] * st.session_state.common_points_df["y_2_c"]
    st.session_state.common_points_df["x_2_c*y_1_c"] = st.session_state.common_points_df["x_2_c"] * st.session_state.common_points_df["y_1_c"]
    st.session_state.common_points_df["y_1_c*y_2_c"] = st.session_state.common_points_df["y_1_c"] * st.session_state.common_points_df["y_2_c"]
    st.session_state.common_points_df["x_2_c*x_1_c"] = st.session_state.common_points_df["x_2_c"] * st.session_state.common_points_df["x_1_c"]
    st.session_state.common_points_df["y_1_cp2+x_1_cp2"] = st.session_state.common_points_df["y_1_c"] * st.session_state.common_points_df["y_1_c"] + st.session_state.common_points_df["x_1_c"] * st.session_state.common_points_df["x_1_c"]

    sum4 = st.session_state.common_points_df.loc[st.session_state.common_points_df["Selected"], "x_1_c*y_2_c"].sum()
    sum3 = st.session_state.common_points_df.loc[st.session_state.common_points_df["Selected"], "x_2_c*y_1_c"].sum()
    sum2 = st.session_state.common_points_df.loc[st.session_state.common_points_df["Selected"], "y_1_c*y_2_c"].sum()
    sum1 = st.session_state.common_points_df.loc[st.session_state.common_points_df["Selected"], "x_2_c*x_1_c"].sum()
    sum5 = st.session_state.common_points_df.loc[st.session_state.common_points_df["Selected"], "y_1_cp2+x_1_cp2"].sum()

    st.session_state.a = (sum1 + sum2) / sum5
    st.session_state.b = (-sum3 + sum4) / sum5
    st.session_state.scale = math.sqrt(st.session_state.a * st.session_state.a + st.session_state.b * st.session_state.b)
    rotation = math.degrees(math.atan2(st.session_state.b,st.session_state.a))
    st.session_state.rotation_dms = deg_to_degminsec(rotation)

    st.session_state.Y0 = st.session_state.mean_target_y - (st.session_state.b * st.session_state.mean_source_x + st.session_state.a * st.session_state.mean_source_y)
    st.session_state.X0 = st.session_state.mean_target_x - (st.session_state.a * st.session_state.mean_source_x - st.session_state.b * st.session_state.mean_source_y)

    st.session_state.common_points_df["y_new"] = st.session_state.Y0 + st.session_state.b * st.session_state.common_points_df["x_1"] + st.session_state.a * st.session_state.common_points_df["y_1"]
    st.session_state.common_points_df["x_new"] = st.session_state.X0 + st.session_state.a * st.session_state.common_points_df["x_1"] - st.session_state.b * st.session_state.common_points_df["y_1"]

    st.session_state.common_points_df["vy"] = st.session_state.common_points_df["y_2"] - st.session_state.common_points_df["y_new"]
    st.session_state.common_points_df["vx"] = st.session_state.common_points_df["x_2"] - st.session_state.common_points_df["x_new"]

    n = st.session_state.common_points_df.loc[st.session_state.common_points_df["Selected"], "vy"].count()
    st.session_state.common_points_df["vy*vy+vx*vx"] = st.session_state.common_points_df["vy"] * st.session_state.common_points_df["vy"] + st.session_state.common_points_df["vx"] * st.session_state.common_points_df["vx"]
    sum6 = st.session_state.common_points_df.loc[st.session_state.common_points_df["Selected"], "vy*vy+vx*vx"].sum()
    number_cp_used = st.session_state.common_points_df.loc[st.session_state.common_points_df["Selected"], "vy"].count()
    if number_cp_used > 2:
        st.session_state.stdev = math.sqrt(sum6 / (n * n - 4))
    else:
        st.session_state.stdev = None
    # sum of residuals must be 0
    # sumvy = st.session_state.common_points_df.loc[st.session_state.common_points_df["Selected"], "vy"].sum()
    # sumvx = st.session_state.common_points_df.loc[st.session_state.common_points_df["Selected"], "vx"].sum()


#-----Page Configuration
st.set_page_config(page_title='2D Helmert Transformation',
    page_icon='🌐',layout='wide')
    #initial_sidebar_state="collapsed"

#----menu button invisible
#st.markdown(""" <style>#MainMenu {visibility: hidden;}footer {visibility: hidden;}</style> """, unsafe_allow_html=True)

# cached function to use local css from file style.css
local_css()


col1,col2 = st.columns([7,3])
#---- Title and Description
col1.markdown('<h1 style="margin-bottom:0rem;margin-top:-5rem;text-align: center">Common Points</h1>', unsafe_allow_html=True)
col1.markdown('<h5 style="color:grey;margin-bottom:0.5rem;margin-top:-1rem;text-align: center">At least 2 points have to be selected</h5>', unsafe_allow_html=True)

try:
    number_of_cp = len(st.session_state.common_points_df.index)
except:
    switch_page("Upload_Coordinates")

if number_of_cp == 0:
    col1.error("No common points", icon="⚠️")
    button_Upload_Coordinates= col1.button(
            """**Upload Coordinates**""",
            key="StartTrafo3",
            help=None,
            on_click=None,
            args=None,
            type="primary",
            disabled=False,
        )

    if button_Upload_Coordinates:
        switch_page("Upload_Coordinates")

elif number_of_cp == 1:
    col1.error("Only one common point", icon="⚠️")
    button_Upload_Coordinates= col1.button(
            """**Upload Coordinates**""",
            key="StartTrafo4",
            help=None,
            on_click=None,
            args=None,
            type="primary",
            disabled=False,
        )
    if button_Upload_Coordinates:
        switch_page("Upload_Coordinates")
else:
    update_transformation()

    domain = [True, False]
    range1 = ['mediumblue', 'aqua']

    title1 = alt.TitleParams('Common Points', anchor='middle')
    chart_points=alt.Chart(st.session_state.common_points_df,title=title1).mark_circle(size=60).encode(
        alt.X('y_1', title=st.session_state.source_header_names[1],scale=alt.Scale(zero=False,domain=st.session_state.domain_list[0])),
        alt.Y('x_1', title=st.session_state.source_header_names[2],scale=alt.Scale(zero=False,domain=st.session_state.domain_list[1])),
        alt.Color('Selected',scale=alt.Scale(domain=domain, range=range1),legend=None),
        alt.Size('Selected', scale=alt.Scale(range=[60, 100]),legend=None),
        tooltip=["Name"]
    ).interactive()

    col2.write("")
    col2.write("")
    col2.altair_chart(chart_points,use_container_width=True)

    if 'selected_rows_array' not in st.session_state:
        st.session_state.selected_rows_array = st.session_state.common_points_df["Selected"].array
    if 'grid_key' not in st.session_state:
        st.session_state.grid_key = 0

    #define height parameter for height of AG-Grid
    if number_of_cp < 6:
        height = 120 + number_of_cp * 30
    else:
        height = 300


    #JSCode to render checkbox in AG-Grid
    checkbox_renderer = JsCode("""
    class CheckboxRenderer{
        init(params) {
            this.params = params;
            this.eGui = document.createElement('input');
            this.eGui.type = 'checkbox';
            this.eGui.checked = params.value;
            this.checkedHandler = this.checkedHandler.bind(this);
            this.eGui.addEventListener('click', this.checkedHandler);
        }
        checkedHandler(e) {
            let checked = e.target.checked;
            let colId = this.params.column.colId;
            this.params.node.setDataValue(colId, checked);
        }
        getGui(params) {
            return this.eGui;
        }
        destroy(params) {
        this.eGui.removeEventListener('click', this.checkedHandler);
        }
    }//end class
    """)

    rowStyle_renderer = JsCode(
        """
        function(params) {
            if (params.data.Selected) {
                return {
                    'color': 'black',
                    'backgroundColor': 'paleturquoise'

                }
            }
            else {
                return {
                    'color': 'black',
                    'backgroundColor': 'honeydew'
                }
            }
        };
    """
    )

    gb = GridOptionsBuilder.from_dataframe(st.session_state.common_points_df[["Selected","Name","y_1","x_1","y_2","x_2","vy","vx"]])
    #gb.configure_default_column(headerClass='ag-center-aligned-header')
    gb.configure_column( "Selected", headerName=" ", minWidth=49, maxWidth=49, editable=True, cellRenderer=checkbox_renderer)
    gb.configure_column("Name", headerName=st.session_state.source_header_names[0], headerClass='ag-justify-content-header',minWidth=30, maxWidth=90)
    gb.configure_column("y_1", headerName="- - - - - Source System  - - - - -",
        children=[
             { "headerName": st.session_state.source_header_names[1], "minWidth": "90", "maxWidth": "115", "field": "y_1", "type": ["numericColumn","numberColumnFilter","customNumericFormat"], "precision":3},
             { "headerName": st.session_state.source_header_names[2], "minWidth": "90", "maxWidth": "115", "field": "x_1", "type": ["numericColumn","numberColumnFilter","customNumericFormat"], "precision":3},
           ])
    gb.configure_column("y_2", headerName="- - - - -  Target System  - - - - -",
        children=[
             { "headerName": st.session_state.source_header_names[1], "minWidth": "90", "maxWidth": "115", "field": "y_2", "type": ["numericColumn","numberColumnFilter","customNumericFormat"], "precision":3},
             { "headerName": st.session_state.source_header_names[2], "minWidth": "90", "maxWidth": "115", "field": "x_2", "type": ["numericColumn","numberColumnFilter","customNumericFormat"], "precision":3},
           ])
    gb.configure_column("vy", headerName="- - - Residuals - - -",
        children=[
             #{ "headerName": "vy", "field": "vy", "type": ["numericColumn","numberColumnFilter","customNumericFormat"], "cellStyle" :cellstyle_jscode,"precision":3},
             { "headerName": "v"+st.session_state.source_header_names[1][:1], "minWidth": "60", "maxWidth": "75", "field": "vy", "type": ["numericColumn","numberColumnFilter","customNumericFormat"], "precision":3},
             { "headerName": "v"+st.session_state.source_header_names[2][:1], "minWidth": "60", "maxWidth": "75", "field": "vx", "type": ["numericColumn","numberColumnFilter","customNumericFormat"], "precision":3},
           ])
    gb.configure_column("x_1", hide=True)
    gb.configure_column("x_2", hide=True)
    gb.configure_column("vx", hide=True)
    gb.configure_selection('multiple', use_checkbox=False)
    gb.configure_grid_options(groupHeaderHeight = 40, headerHeight = 35, rowHeight = 35,domLayout='normal')

    gridOptions = gb.build()
    gridOptions["getRowStyle"] = rowStyle_renderer

    with col1:
        st.session_state.ag_grid=AgGrid(
            st.session_state.common_points_df[["Selected","Name","y_1","x_1","y_2","x_2","vy","vx"]],
            key=st.session_state.grid_key,
            gridOptions = gridOptions,
            height = height,
            #fit_columns_on_grid_load = True,
            data_return_mode = 'as_input',
            update_mode='grid_changed',
            allow_unsafe_jscode = True,
            columns_auto_size_mode=ColumnsAutoSizeMode.NO_AUTOSIZE,
            reload_data = True,
            enable_enterprise_modules=False,
            theme= 'alpine'
            #theme= 'balham'
            #theme='streamlit'
        )

    exp = col1.expander("2D Helmert Transformation:",expanded=True)

    with exp:
        col_e01,col_e02,col_e03,col_e04,col_e05,col_e06 = st.columns([3,2,2,2,2,4])
        col_e01.markdown('<p style="margin-bottom:0rem;margin-top:-0.5rem;text-align: left">Mean:</p>', unsafe_allow_html=True)
        col_e02.markdown(f'<p style="margin-bottom:0rem;margin-top:-0.5rem;text-align: left">{"{:>12.3f}".format(st.session_state.mean_source_y)}</p>', unsafe_allow_html=True)
        col_e03.markdown(f'<p style="margin-bottom:0rem;margin-top:-0.5rem;text-align: left">{"{:>12.3f}".format(st.session_state.mean_source_x)}</p>', unsafe_allow_html=True)
        col_e04.markdown(f'<p style="margin-bottom:0rem;margin-top:-0.5rem;text-align: left">{"{:>12.3f}".format(st.session_state.mean_target_y)}</p>', unsafe_allow_html=True)
        col_e05.markdown(f'<p style="margin-bottom:0rem;margin-top:-0.5rem;text-align: left">{"{:>12.3f}".format(st.session_state.mean_target_x)}</p>', unsafe_allow_html=True)

        col_e11,col_e12,col_e13,col_e14,col_e15,col_e16 = st.columns([3,2,2,2,2,4])
        col_e11.markdown('<p style="margin-bottom:-0.5rem;margin-top:0rem;text-align: left">Shift Mean:</p>', unsafe_allow_html=True)
        col_e12.markdown(f'<p style="margin-bottom:-0.5rem;margin-top:0rem;text-align: left">{"{:>12.3f}".format(st.session_state.mean_target_y-st.session_state.mean_source_y)}</p>', unsafe_allow_html=True)
        col_e13.markdown(f'<p style="margin-bottom:-0.5rem;margin-top:0rem;text-align: left">{"{:>12.3f}".format(st.session_state.mean_target_x-st.session_state.mean_source_x)}</p>', unsafe_allow_html=True)


        if st.session_state.stdev is None:
            line_sd="Standard Deviation (m): &ensp;---"
        else:
            line_sd="Standard Deviation (m): &ensp;{:>6.3f}".format(st.session_state.stdev)

        col_e21,col_e22,col_e23 = st.columns([2,2,1])

        with col_e21:
            st.markdown(f'<p style="margin-bottom:0rem;margin-top:0rem;text-align: left"><strong>{line_sd}</strong></p>', unsafe_allow_html=True)
            st.markdown(f'<p style="margin-bottom:0rem;margin-top:0rem;text-align: left"><strong>{"Scale: &ensp;{:0.8f}".format(st.session_state.scale)}</strong></p>', unsafe_allow_html=True)
            st.markdown(f'<p style="margin-bottom:1rem;margin-top:0rem;text-align: left"><strong>{"Rotation (dms): &ensp;" + st.session_state.rotation_dms}</strong></p>', unsafe_allow_html=True)

        with col_e22:
            st.markdown('<p style="margin-bottom:0rem;margin-top:0rem;text-align: left">Transformation Parameters:</p>', unsafe_allow_html=True)
            st.markdown(f'<p style="margin-bottom:0rem;margin-top:0rem;text-align: left">{"Y0: &ensp;{:0.3f}".format(st.session_state.Y0)}</p>', unsafe_allow_html=True)
            st.markdown(f'<p style="margin-bottom:1rem;margin-top:0rem;text-align: left">{"X0: &ensp;{:0.3f}".format(st.session_state.X0)}</p>', unsafe_allow_html=True)

        with col_e23:
            st.markdown(f'<p style="margin-bottom:0rem;margin-top:1.5rem;text-align: left">{"A: &ensp;{:0.8f}".format(st.session_state.a)}</p>', unsafe_allow_html=True)
            st.markdown(f'<p style="margin-bottom:1rem;margin-top:0rem;text-align: left">{"B: &ensp;{:0.8f}".format(st.session_state.b)}</p>', unsafe_allow_html=True)


    if sum(st.session_state.ag_grid['data']["Selected"])<2:
        st.warning("At least 2 common points have to be selected", icon="⚠️")
        st.session_state.grid_key += 1
        st.experimental_rerun()
    else:
        st.session_state.common_points_df["Selected"]= st.session_state.ag_grid['data']["Selected"]

        if not np.array_equal(st.session_state.selected_rows_array,st.session_state.common_points_df["Selected"].array):
            update_transformation()
            st.session_state.selected_rows_array = st.session_state.common_points_df["Selected"].array
            #st.session_state.grid_key += 1
            st.experimental_rerun()


    row2_col1, row2_col2,row2_col3 = st.columns([3,2,6])
    with row2_col2:
        button_Compute = st.button(
            """**Transformed Points**""",
            key="StartTrafo2",
            help=None,
            on_click=None,
            args=None,
            type="primary",
            disabled=False,
        )

    if button_Compute:
        switch_page("Download_Transformed_Points")
