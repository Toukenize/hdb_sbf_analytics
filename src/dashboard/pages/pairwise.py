import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from typing import List, Dict
from matplotlib.figure import Figure
from ..data import get_selected_town_and_flat_proj_info


def plot_unit_within_crit_pie(
        proj_info_selected: pd.DataFrame,
        proj_info_not_selected: pd.DataFrame) -> Figure:

    num_within_crit = len(proj_info_selected)
    num_out_of_crit = len(proj_info_not_selected)

    data = pd.DataFrame(
        {'Description': ['Units (Others)', 'Units (Within Critiria)'],
         'Number of Units': [num_out_of_crit, num_within_crit]})

    fig, ax = plt.subplots(1, 1, figsize=(8, 6))

    patches, texts, auto_txts = ax.pie(
        x=data['Number of Units'],
        labels=data['Description'],
        labeldistance=None,
        autopct='%d',
        startangle=90,
        colors=['lightgrey', '#F63366'],
        explode=[0.1, 0])

    auto_txts[0].set_fontweight('heavy')
    auto_txts[0].set_c('gray')
    auto_txts[0].set_fontsize(20)
    auto_txts[1].set_fontweight('heavy')
    auto_txts[1].set_c('white')
    auto_txts[1].set_fontsize(20)

    ax.legend(bbox_to_anchor=[1.05, 0.5], fontsize=16)

    return fig


def town_sel_widget(town_options, key):
    town_selection = st.selectbox(
        label='Towns', options=town_options, key=key
    )
    return town_selection


def flat_sel_widget(flat_options, key):
    flat_selection = st.selectbox(
        label='Flat Types', options=flat_options, key=key
    )
    return flat_selection


def get_additional_input(
        town_options: List[str], flat_options: List[str],
        key: str):
    town_selection = town_sel_widget(
        town_options, key)
    flat_selection = flat_sel_widget(
        flat_options, key)
    return {'town_selection': town_selection,
            'flat_selection': flat_selection}


def get_column_info(
        widget_info: Dict, widget_input: Dict,
        proj_info: pd.DataFrame, column_key: str):
    # TODO: Provide a more intuitive func name
    add_input = get_additional_input(
        town_options=widget_info['town_options'],
        flat_options=widget_info['flat_options'],
        key=column_key)

    info_all, info_selected, info_not_selected =\
        get_selected_town_and_flat_proj_info(
            proj_info, **widget_input, **add_input)

    return info_all, info_selected, info_not_selected


def render_content(
        widget_info: Dict, widget_input: Dict, proj_info: pd.DataFrame):

    st.title('Pairwise Comparison')

    c1, c2 = st.beta_columns(2)

    for i, col in enumerate([c1, c2]):
        with col:

            # Get additional options from main content widgets

            info_all, info_selected, info_not_selected =\
                get_column_info(
                    widget_info, widget_input,
                    proj_info, column_key=str(i))

            st.pyplot(plot_unit_within_crit_pie(
                info_selected, info_not_selected))
