import streamlit as st
import pandas as pd
import numpy as np

# import altair as alt
# from st_aggrid import GridOptionsBuilder, AgGrid, ColumnsAutoSizeMode, JsCode
from streamlit_extras.switch_page_button import switch_page


@st.cache_data
def example_source_upload():
    # uploads example source csv file and returns dataframe
    df = pd.read_csv("source_withheader.csv")
    return df


@st.cache_data
def example_target_upload():
    # uploads example source csv file and returns dataframe
    df = pd.read_csv("target_withheader.csv")
    return df


def calc_domain():
    # takes common points df from session state,
    # calculates min/max and range values for y/x coordinates
    # returns list of list with y/x coordinates for domain for altair chart
    min_y = st.session_state.common_points_df['y_1'].min()
    max_y = st.session_state.common_points_df['y_1'].max()
    min_x = st.session_state.common_points_df['x_1'].min()
    max_x = st.session_state.common_points_df['x_1'].max()
    range_y = max_y - min_y
    range_x = max_x - min_x
    if range_y > range_x:
        offset_range_x = (range_y - range_x) / 2 + range_y / 10
        llist = [
            [min_y - range_y / 10, max_y + range_y / 10],
            [min_x - offset_range_x, max_x + offset_range_x],
        ]
    else:
        offset_range_y = (range_x - range_y) / 2 + range_x / 10
        llist = [
            [min_y - offset_range_y, max_y + offset_range_y],
            [min_x - range_x / 10, max_x + range_x / 10],
        ]
    return llist


# -----Page Configuration
st.set_page_config(page_title="2D Helmert Transformation", page_icon="🌐", layout="wide")

# ----menu button invisible
# st.markdown(""" <style>#MainMenu {visibility: hidden;}footer {visibility: hidden;}</style> """, unsafe_allow_html=True)

# defining session states
if "source_df" not in st.session_state:
    st.session_state.source_df = pd.DataFrame()
if "target_df" not in st.session_state:
    st.session_state.target_df = pd.DataFrame()
if "source_header_names" not in st.session_state:
    st.session_state.source_header_names = ["Name", "y", "x", "h"]
if "target_header_names" not in st.session_state:
    st.session_state.target_header_names = ["Name", "y", "x", "h"]
if "uploaded_source_file" not in st.session_state:
    st.session_state.uploaded_source_file = None
if "uploaded_target_file" not in st.session_state:
    st.session_state.uploaded_target_file = None
if "common_points_df" not in st.session_state:
    st.session_state.common_points_df = pd.DataFrame()

# ---- Title and Description
st.markdown('<h1 style="margin-bottom:0rem;margin-top:-4rem;text-align: center">2D Helmert Transformation</h1>',unsafe_allow_html=True,)
st.markdown('<h5 style="color:grey;margin-bottom:2rem;margin-top:-1rem;text-align: center">4 Parameter Similarity Transformation</h5>', unsafe_allow_html=True)


col1, col2 = st.columns(2,gap="large")

# --- Source System ------------------------------------------------------------------
with col1:
    st.markdown(
        '<h3 style="margin-bottom:0rem;margin-top:-1rem">Source System Coordinate File:</h3>',
        unsafe_allow_html=True,
    )

    uploaded_source_file = st.file_uploader(
        """File must have at least 3 columns, for example:&nbsp;&nbsp;**| Name  |  y  |  x  |**&nbsp;&nbsp;&nbsp;-&nbsp;&nbsp;*Header row optional*""",
        accept_multiple_files=False,
        key="upload_source_file",
        type=None,
        on_change=None,
        disabled=False,
        label_visibility="visible",
    )

    #code taken from desktop version and adapted to streamlit, could be improved
    if uploaded_source_file is None:
        upload1 = False # setting to determine if common_points_df needs to be recalculated
        if st.session_state.uploaded_source_file is None:
            show_uploaded_sourcefile_df = False
        else: # if a file was uploaded already it is used as the source df until a new one is uploaded
            uploaded_source_file = st.session_state.uploaded_source_file
            show_uploaded_sourcefile_df = True
            st.write("Uploaded file: " + st.session_state.uploaded_source_file.name)
    else:
        upload1 = True
        show_uploaded_sourcefile_df = True
        #c = pd.DataFrame()
        lastpointindex = uploaded_source_file.name.rfind(".")

        if uploaded_source_file.name[lastpointindex + 1 :] == "csv":  # try to read csv
            try:
                st.session_state.source_df = pd.read_csv(uploaded_source_file, header=None)
            except UnicodeDecodeError:
                try:
                    st.session_state.source_df = pd.read_csv(uploaded_source_file, encoding="latin-1")
                except:
                    st.error("Error with file encoding. Please delete special characters (ä.ö,ü,...). Or try opening and saving the file in a text editor with encoding 'utf-8'.", icon="⚠️")
                    show_uploaded_sourcefile_df = False
            except:
                try:
                    st.session_state.source_df = pd.read_fwf(uploaded_source_file, header=None)
                except:
                    st.error("Cannot read file")
                    show_uploaded_sourcefile_df = False
        else:  # try to read textfile as table
            try:
                st.session_state.source_df = pd.read_fwf( uploaded_source_file, header=None)
            except UnicodeDecodeError:
                st.error("Error with file encoding. Please delete special characters (ä.ö,ü,...). Or try opening and saving the file in a text editor with encoding 'utf-8'.", icon="⚠️")
                show_uploaded_sourcefile_df = False
            except:
                st.error("Cannot read file", icon="⚠️")
                show_uploaded_sourcefile_df = False

        if show_uploaded_sourcefile_df:  # check for number of columns and rows
            if len(st.session_state.source_df.columns) < 3:
                try:  # if csv file was imported as text file it has only one column, will then try to read csv correctly
                    st.session_state.source_df = pd.read_csv(uploaded_source_file, header=None)
                    if len(st.session_state.source_df.columns) < 3:
                        st.error("File has less than 3 columns", icon="⚠️")
                        show_uploaded_sourcefile_df = False
                except:
                    st.error("File has less than 3 columns", icon="⚠️")
                    show_uploaded_sourcefile_df = False
            elif len(st.session_state.source_df.columns) > 4: # only first 4 columns taken
                st.session_state.source_df  = st.session_state.source_df.iloc[: , :4]
                #st.error("File has more than 4 columns", icon="⚠️")
                #show_uploaded_sourcefile_df = False
            elif len(st.session_state.source_df.index) < 2:
                st.error("File has less than 2 rows", icon="⚠️")
                show_uploaded_sourcefile_df = False

        if show_uploaded_sourcefile_df:
            # check for header rows in dataframes
            try:
                float(st.session_state.source_df.iloc[0][1])  # check if first row is header
                st.session_state.source_header_names = ["Name", "y", "x", "h"]
            except:
                st.session_state.source_header_names = st.session_state.source_df.iloc[0].tolist()  # grab the first row for the header
                st.session_state.source_df = st.session_state.source_df[1:] # take the data less the header row
                if len(st.session_state.source_df.index) < 2:  # repeat this check as file is one row shorter
                    st.error("File has less than 2 rows", icon="⚠️")
                    show_uploaded_sourcefile_df = False

        if show_uploaded_sourcefile_df:
            # dataframes headers set to default for common points df and display
            st.session_state.source_header_names = st.session_state.source_header_names[: len(st.session_state.source_df.columns)]
            st.session_state.source_df.columns = st.session_state.source_header_names
            st.session_state.source_df.iloc[:,0] = st.session_state.source_df.iloc[:, 0 ].astype(str)

            for i in st.session_state.source_header_names[1:]:  # convert string columns to float(tpe is string if import was with header)
                try:
                    st.session_state.source_df[i] = st.session_state.source_df[i].astype(float)
                except:
                    st.error("Wrong file format, column " + i, icon="⚠️")
                    show_uploaded_sourcefile_df = False
                    st.session_state.source_header_names = ["Name", "y", "x", "h"]

            if st.session_state.source_df.isnull().values.any():
                st.error("File contains rows with empty values", icon="⚠️")
                show_uploaded_sourcefile_df = False

    if show_uploaded_sourcefile_df:
        st.session_state.uploaded_source_file = uploaded_source_file
    else:
        st.session_state.uploaded_source_file = None
        st.write(" ")
        st.write("Awaiting file to be uploaded. Currently using example coordinates:")
        st.session_state.source_df = example_source_upload()

    source_output_format = {}
    for col in st.session_state.source_header_names[1:]:
        source_output_format[col] = "{:.3f}"

    if len(st.session_state.source_df) < 6:
        st.dataframe(st.session_state.source_df.loc[:, st.session_state.source_df.columns!='Duplicate'].style.format(source_output_format))
    else:
        st.dataframe(st.session_state.source_df.loc[:, st.session_state.source_df.columns!='Duplicate'].style.format(source_output_format), height=235)
    #st.experimental_data_editor(st.session_state.source_df, num_rows = "dynamic", width=600,key="data_editor")
    #st.experimental_data_editor(st.session_state.source_df, num_rows = "dynamic", key="data_editor", height=200)

    duplicates_array = st.session_state.source_df.duplicated(subset=[st.session_state.source_header_names[0]])
    st.session_state.source_df["Duplicate"] = duplicates_array

    if True in st.session_state.source_df["Duplicate"].array:  # if duplicates exist
        duplicate_names_list = st.session_state.source_df.loc[st.session_state.source_df["Duplicate"] == True, st.session_state.source_header_names[0]].tolist()
        if len(duplicate_names_list) == 1:
            st.warning("Duplicate point: " + duplicate_names_list[0], icon="⚠️")
        elif len(duplicate_names_list) > 1:
            duplicate_names_string = duplicate_names_list[0]
            for i in duplicate_names_list[1:]:
                duplicate_names_string += ", " + str(i)
            st.warning("Duplicate points: " + duplicate_names_string, icon="⚠️")


# --- Target System ------------------------------------------------------------------
with col2:
    st.markdown(
        '<h3 style="margin-bottom:0rem;margin-top:-1rem">Target System Coordinate File:</h3>',
        unsafe_allow_html=True,
    )
    uploaded_target_file = st.file_uploader(
        """File must have at least 3 columns, for example: **Name | y | x |&nbsp;&nbsp;**&nbsp;-&nbsp;&nbsp;*Header row optional*""",
        accept_multiple_files=False,
        key="upload_target_file",
        type=None,
        on_change=None,
        disabled=False,
        label_visibility="visible",
    )

    if uploaded_target_file is None:
        upload2 = False
        if st.session_state.uploaded_target_file is None:
            show_uploaded_targetfile_df = False
        else:
            uploaded_target_file = st.session_state.uploaded_target_file
            show_uploaded_targetfile_df = True
            st.write("Uploaded file: " + st.session_state.uploaded_target_file.name)
    else:
        upload2 = True
        show_uploaded_targetfile_df = True

        st.session_state.target_df = pd.DataFrame()
        lastpointindex = uploaded_target_file.name.rfind(".")

        if uploaded_target_file.name[lastpointindex + 1 :] == "csv":  # try to read csv
            try:
                st.session_state.target_df = pd.read_csv(uploaded_target_file, header=None)
            except UnicodeDecodeError:
                try:
                    st.session_state.target_df = pd.read_csv(uploaded_target_file, encoding="latin-1")
                except:
                    st.error("Error with file encoding. Please delete special characters (ä.ö,ü,...). Or try opening and saving the file in a text editor with encoding 'utf-8'.", icon="⚠️")
                    show_uploaded_targetfile_df = False
            except:
                try:
                    st.session_state.target_df = pd.read_fwf(uploaded_target_file, header=None)
                except:
                    st.error("Cannot read file", icon="⚠️")
                    show_uploaded_targetfile_df = False
        else:  # try to read textfile as table
            try:
                st.session_state.target_df = pd.read_fwf(uploaded_target_file, header=None)
            except UnicodeDecodeError:
                st.error("Error with file encoding. Please delete special characters (ä.ö,ü,...). Or try opening and saving the file in a text editor with encoding 'utf-8'.", icon="⚠️")
                show_uploaded_targetfile_df = False
            except:
                st.error("Cannot read file", icon="⚠️")
                show_uploaded_targetfile_df = False

        if show_uploaded_targetfile_df:  # check for number of columns and rows
            if len(st.session_state.target_df.columns) < 3:
                try:  # if csv file was imported as text file it has only one column, will then try to read csv correctly
                    st.session_state.target_df = pd.read_csv(uploaded_target_file, header=None)
                    if len(st.session_state.target_df.columns) < 3:
                        st.error("File has less than 3 columns", icon="⚠️")
                        show_uploaded_targetfile_df = False
                except:
                    st.error("File has less than 3 columns", icon="⚠️")
                    show_uploaded_targetfile_df = False
            elif len(st.session_state.target_df.columns) > 4:
                st.session_state.target_df  = st.session_state.target_df.iloc[: , :4]

            elif len(st.session_state.target_df.index) < 2:
                st.error("File has less than 2 rows", icon="⚠️")
                show_uploaded_targetfile_df = False

        if show_uploaded_targetfile_df:
            # check for header rows in dataframes
            try:
                float(st.session_state.target_df.iloc[0][1])
                st.session_state.target_header_names = ["Name", "y", "x", "h"]  # check if first row is header
            except:
                st.session_state.target_header_names = st.session_state.target_df.iloc[0].tolist()  # grab the first row for the header
                st.session_state.target_df = st.session_state.target_df[1:]  # take the data less the header row
                if len(st.session_state.target_df.index) < 2:  # repeat this check as file is one row shorter
                    st.error("File has less than 2 rows", icon="⚠️")
                    show_uploaded_targetfile_df = False

        if show_uploaded_targetfile_df:
            st.session_state.target_header_names = st.session_state.target_header_names[: len(st.session_state.target_df.columns)]
            st.session_state.target_df.columns = st.session_state.target_header_names
            st.session_state.target_df.iloc[:, 0] = st.session_state.target_df.iloc[:, 0].astype(str)

            for i in st.session_state.target_header_names[1:]:  # convert string columns to float(tpe is string if import was with header)
                try:
                    st.session_state.target_df[i] = st.session_state.target_df[i].astype(float)
                except:
                    st.error("Wrong file format, column " + i, icon="⚠️")
                    show_uploaded_targetfile_df = False
                    st.session_state.target_header_names = ["Name", "y", "x", "h"]

            if st.session_state.target_df.isnull().values.any():

                st.error("File contains rows with empty values", icon="⚠️")
                show_uploaded_targetfile_df = False


    if show_uploaded_targetfile_df:
        st.session_state.uploaded_target_file = uploaded_target_file
    else:
        st.write(" ")
        st.write("Awaiting file to be uploaded. Currently using example coordinates:")
        st.session_state.target_df = example_target_upload()

    target_output_format = {}
    for col in st.session_state.target_header_names[1:]:
        target_output_format[col] = "{:.3f}"
    if len(st.session_state.target_df) < 6:
        st.dataframe(st.session_state.target_df.style.format(target_output_format))
    else:
        st.dataframe(st.session_state.target_df.style.format(target_output_format), height=235)

    duplicates_array_target = st.session_state.target_df.duplicated(subset=[st.session_state.target_header_names[0]])
    st.session_state.target_df["Duplicate"] = duplicates_array_target

    if True in st.session_state.target_df["Duplicate"].array: # if duplicates exist
        duplicate_names_list_t = st.session_state.target_df.loc[st.session_state.target_df["Duplicate"], st.session_state.target_header_names[0]].tolist()
        if len(duplicate_names_list_t) == 1:
            st.warning("Duplicate point: " + duplicate_names_list_t[0]+" - Only first point is used in common points", icon="⚠️")
        elif len(duplicate_names_list_t) > 1:
            duplicate_names_string_t = duplicate_names_list_t[0]
            for i in duplicate_names_list_t[1:]:
                duplicate_names_string_t += ", " + str(i)
            st.warning("Duplicate points: " + duplicate_names_string_t+" - Only first points are used in common points", icon="⚠️")

    st.session_state.target_df.drop("Duplicate", inplace=True, axis=1)#deletes "Duplicate" column from target_df
    # target_df is kept with possible duplicates
    # but for merging for common points a temporary df is created without duplicates
    temp_target_df=st.session_state.target_df.drop_duplicates(subset=[st.session_state.target_header_names[0]])


# if common points df was updated already on page 2 it has more than 6 columns
# if no new files are uploaded it doesn't have to be created again
if not upload1 and not upload2 and len(st.session_state.common_points_df.columns) > 6:
    pass
else:
    # --- merging source and target df and creating common points df --------------------------
    st.session_state.all_points_df = pd.merge(
    st.session_state.source_df.iloc[:, list(range(3)) + [-1]], # only using first 3 columns +"Duplicate"
    temp_target_df.iloc[:, list(range(3))], # only using first 3 columns
    #on=column_name1,
    how='left',
    left_on=st.session_state.source_header_names[0],
    right_on=st.session_state.target_header_names[0],
    sort=True,
    suffixes=("_1", "_2"),
    copy=True,
    indicator=False,
    validate=None,
    )


    if st.session_state.source_header_names[0] != st.session_state.target_header_names[0]:
        st.session_state.all_points_df.drop(st.session_state.target_header_names[0], inplace=True, axis=1)

    st.session_state.all_points_df["Selected"] = np.where(~st.session_state.all_points_df.isnull().any(axis=1) & ~st.session_state.all_points_df["Duplicate"].array, True, False)
    st.session_state.all_points_df.drop("Duplicate", inplace=True, axis=1)

    st.session_state.all_points_df.columns = ["Name","y_1","x_1","y_2","x_2","Selected"] # temporary header for common points to use my functions

    st.session_state.common_points_df = st.session_state.all_points_df[st.session_state.all_points_df.Selected]
    st.session_state.other_points_df = st.session_state.all_points_df[~st.session_state.all_points_df.Selected]
    st.session_state.common_points_df.reset_index(drop=True,inplace=True)# important to start new index numbers 0,1,2,etc.
    st.session_state.other_points_df.reset_index(drop=True,inplace=True)

    # session state settings to be used on next pages
    #needs to be done here because it is only done when new source and targets files are uploaded
    st.session_state.text_length = st.session_state.source_df.iloc[:,0].str.len().max()#get max text length and savefor output formatting
    st.session_state.text_length = max(st.session_state.text_length,4)
    st.session_state.domain_list = calc_domain()


row2_col1, row2_col2,row2_col3 = st.columns([5,3,5])
with row2_col2:
    button_Compute = st.button(
        """**Select Common Points**""",
        key="StartTrafo1",
        help=None,
        on_click=None,
        args=None,
        type="primary",
        disabled=False,
    )


if button_Compute:
    switch_page("Select_Common_Points")

