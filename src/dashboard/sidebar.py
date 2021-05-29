import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict


def latest_comp_widget(earliest_comp, latest_comp):

    latest_comp = st.sidebar.slider(
        'Latest Completion Date',
        min_value=earliest_comp,
        max_value=latest_comp,
        value=datetime(2022, 1, 1),
        step=timedelta(days=30),
        format='Y/M'
    )
    return latest_comp


def race_widget():
    race = st.sidebar.selectbox(
        'Ethnicity', options=['Chinese', 'Malay', 'Indian']
    )
    return race


def town_sel_widget(town_options):
    town_selection = st.sidebar.multiselect(
        label='Towns', options=town_options, default='All Towns'
    )
    return town_selection


def flat_sel_widget(flat_options):
    flat_selection = st.sidebar.multiselect(
        label='Flat Types', options=flat_options, default=['4-Room', '5-Room']
    )
    return flat_selection


def floor_range_widget(overall_max_floor):
    min_floor, max_floor = st.sidebar.slider(
        'Floor Levels',
        min_value=1, max_value=overall_max_floor,
        value=(5, overall_max_floor)
    )
    return min_floor, max_floor


def lease_range_widget():
    min_lease, max_lease = st.sidebar.slider(
        'Remaining Lease Years',
        min_value=50, max_value=99,
        value=(90, 99)
    )
    return min_lease, max_lease


def price_range_widget(overall_min_price, overall_max_price):
    min_price, max_price = st.sidebar.slider(
        'Price Range',
        min_value=overall_min_price,
        max_value=overall_max_price,
        value=(overall_min_price * 2, overall_min_price * 5),
        format='$%dk',
        step=10
    )
    return min_price, max_price


@st.cache
def get_widget_info(proj_info: pd.DataFrame) -> Dict:

    town_options = ['All Towns'] + sorted(proj_info['Town'].unique().tolist())
    flat_options = ['3-Room', '4-Room', '5-Room']
    overall_max_floor = int(proj_info['floor_num'].max())
    overall_earliest_comp = proj_info['Est_Completion'].min().to_pydatetime()
    overall_latest_comp = proj_info['Est_Completion'].max().to_pydatetime()
    overall_min_price = int(proj_info['unit_price'].min().round(-1))
    overall_max_price = int(proj_info['unit_price'].max().round(-1))

    return {
        'town_options': town_options,
        'flat_options': flat_options,
        'overall_max_floor': overall_max_floor,
        'overall_earliest_comp': overall_earliest_comp,
        'overall_latest_comp': overall_latest_comp,
        'overall_min_price': overall_min_price,
        'overall_max_price': overall_max_price
    }


def get_summary_page_widgets_input(**kwargs):
    st.sidebar.header('SBF Selection Criteria')
    race = race_widget()
    town_selection = town_sel_widget(kwargs['town_options'])
    flat_selection = flat_sel_widget(kwargs['flat_options'])
    min_price, max_price = price_range_widget(
        kwargs['overall_min_price'], kwargs['overall_max_price'])
    min_floor, max_floor = floor_range_widget(kwargs['overall_max_floor'])
    min_lease, max_lease = lease_range_widget()
    latest_comp = latest_comp_widget(
        kwargs['overall_earliest_comp'], kwargs['overall_latest_comp'])

    return {
        'race': race.lower(),
        'town_selection': town_selection,
        'flat_selection': flat_selection,
        'min_floor': min_floor,
        'max_floor': max_floor,
        'min_lease': min_lease,
        'max_lease': max_lease,
        'latest_comp': latest_comp,
        'min_price': min_price,
        'max_price': max_price
    }
