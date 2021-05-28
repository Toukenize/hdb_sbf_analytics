import streamlit as st
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from src.process_data import (
    get_app_info, get_proj_info, get_flat_info, get_selected_proj_info)


@st.cache
def load_data():

    app_info = get_app_info()
    proj_info = get_proj_info()
    flat_info = get_flat_info()

    return app_info, proj_info, flat_info


def show_dashboard():

    st.set_page_config(layout="wide")

    app_info, proj_info, flat_info = load_data()

    flat_options = proj_info['flat_type'].unique().tolist()
    overall_max_floor = int(proj_info['floor_num'].max())
    overall_earliest_comp = proj_info['Est_Completion'].min().to_pydatetime()
    overall_latest_comp = proj_info['Est_Completion'].max().to_pydatetime()
    flat_selection = st.sidebar.multiselect(
        label='Flat Types', options=flat_options, default=['4-Room', '5-Room']
    )

    min_floor, max_floor = st.sidebar.slider(
        'Floor Levels',
        min_value=1, max_value=overall_max_floor,
        value=(5, overall_max_floor)
    )

    min_lease, max_lease = st.sidebar.slider(
        'Remaining Lease Years',
        min_value=50, max_value=99,
        value=(60, 99)
    )

    latest_comp = st.sidebar.slider(
        'Latest Completion Date',
        min_value=overall_earliest_comp,
        max_value=overall_latest_comp,
        value=overall_latest_comp,
        step=timedelta(days=30),
        format='Y/M'

    )

    selected_proj_info = get_selected_proj_info(
        app_info, proj_info, flat_info,
        min_floor=min_floor,
        max_floor=max_floor,
        min_lease=min_lease,
        max_lease=max_lease,
        flat_selection=flat_selection,
        latest_comp=latest_comp
    )

    selected_proj_info.reset_index(drop=True, inplace=True)

    st.title('Chance of Getting SBF')
    st.dataframe(selected_proj_info)


if __name__ == '__main__':
    show_dashboard()
