import streamlit as st
from datetime import timedelta, datetime
from src.process_data import (
    get_app_info, get_proj_info, get_flat_info, get_selected_proj_info)

from src.utils import format_as_pc


@st.cache
def load_data():

    app_info = get_app_info()
    proj_info = get_proj_info()
    flat_info = get_flat_info()

    return app_info, proj_info, flat_info


def show_dashboard():

    st.set_page_config(
        layout="wide", page_title='SBF Analytics (May 2021 Exercise)')

    app_info, proj_info, flat_info = load_data()
    town_options = ['All Towns'] + sorted(proj_info['Town'].unique().tolist())
    flat_options = sorted(proj_info['flat_type'].unique().tolist())
    flat_options.remove('2-Room Flexi')
    overall_max_floor = int(proj_info['floor_num'].max())
    overall_earliest_comp = proj_info['Est_Completion'].min().to_pydatetime()
    overall_latest_comp = proj_info['Est_Completion'].max().to_pydatetime()

    # Format sidebar
    st.sidebar.header('Sales of Balance Flat Criteria')
    town_selection = st.sidebar.multiselect(
        label='Towns', options=town_options, default='All Towns'
    )
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
        value=datetime(2022, 1, 1),
        step=timedelta(days=30),
        format='Y/M'

    )
    race = st.sidebar.selectbox(
        'Ethnicity', options=['Chinese', 'Malay', 'Indian']
    )

    selected_proj_info = get_selected_proj_info(
        app_info, proj_info, flat_info,
        min_floor=min_floor,
        max_floor=max_floor,
        min_lease=min_lease,
        max_lease=max_lease,
        flat_selection=flat_selection,
        town_selection=town_selection,
        latest_comp=latest_comp,
        race=race.lower()
    )

    selected_proj_info.reset_index(drop=True, inplace=True)

    selected_proj_info.rename(
        columns={
            'town': 'Town',
            'flat_type': 'Flat Type',
            'supply_within_crit_n_quota': 'Units (#)',
            'num_first_timers': '1st-Timers (#)',
            'adjusted_chance_pc': 'Chance (%)'},
        inplace=True)

    st.title('Chance of Getting SBF as a 1st-Timer')
    st.markdown(
        """
        This table summarizes the chance of getting SBF that meets
        your selected criteria within each town.
        """
    )

    st.dataframe(selected_proj_info.style.format(
        {'Chance (%)': format_as_pc}), 800, 500)


if __name__ == '__main__':
    show_dashboard()
