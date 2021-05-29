import streamlit as st
import pandas as pd
from ..utils import (
    format_as_pc, format_as_thousand_dollars, highlight_max
)


def format_dataframe(selected_proj_info: pd.DataFrame):

    selected_proj_info.reset_index(drop=True, inplace=True)
    selected_proj_info.drop(columns='proj_list', inplace=True)
    selected_proj_info.rename(
        columns={
            'town': 'Town',
            'flat_type': 'Flat Type',
            'supply_within_crit_n_quota': 'Units (#)',
            'avg_price': 'Average Price ($)',
            'num_first_timers': '1st-Timers (#)',
            'adjusted_chance_pc': 'Chance (%)'},
        inplace=True
    )

    selected_proj_info = (
        selected_proj_info.style
        .apply(
            highlight_max,
            subset=['Units (#)', '1st-Timers (#)',
                    'Chance (%)', 'Average Price ($)'])
        .format({'Chance (%)': format_as_pc,
                 'Average Price ($)': format_as_thousand_dollars})
    )

    return selected_proj_info


def render_content(selected_proj_info: pd.DataFrame):

    st.title('Chance of Getting SBF as a 1st-Timer')
    st.markdown(
        """
        This table summarizes the chance of getting SBF that meets
        your selected criteria within each town.
        """
    )
    st.dataframe(
        format_dataframe(selected_proj_info), 800, 500)
