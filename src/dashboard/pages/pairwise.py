import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import altair as alt
import numpy as np

from typing import List, Dict
from matplotlib.figure import Figure
from ..data import get_selected_town_and_flat_proj_info
from ..utils import format_pie_pct_as_val


def plot_unit_within_crit_pie(
        proj_info_selected: pd.DataFrame,
        proj_info_all: pd.DataFrame,
        flat_info_selected: pd.DataFrame) -> Figure:

    num_within_crit = (
        proj_info_selected
        .groupby('proj_id')
        [['Town']]
        .count()
        .merge(
            flat_info_selected['race_quota'], on='proj_id', how='left')
        .min(axis=1)
        .sum()
    )

    num_out_of_crit = len(proj_info_all) - num_within_crit

    data = pd.DataFrame(
        {'Description': ['# Units (Others)', '# Units (Within Critiria)'],
         'Number of Units': [num_out_of_crit, num_within_crit]})

    fig, ax = plt.subplots(1, 1, figsize=(8, 4))

    patches, texts, auto_txts = ax.pie(
        x=data['Number of Units'],
        labels=data['Description'],
        labeldistance=None,
        autopct=format_pie_pct_as_val(data['Number of Units']),
        startangle=90,
        colors=['lightgrey', '#F63366'],
        explode=[0.1, 0])

    if auto_txts[0].get_text() == '0':
        auto_txts[0].set_text('')
    else:
        auto_txts[0].set_fontweight('heavy')
        auto_txts[0].set_c('gray')
        auto_txts[0].set_fontsize(20)

    auto_txts[1].set_fontweight('heavy')
    auto_txts[1].set_c('white')
    auto_txts[1].set_fontsize(20)

    ax.legend(bbox_to_anchor=[1.05, 0.5], fontsize=12)

    return fig


def plot_bar(df, x_col, y_col, color_col, label_angle=0):

    color_scale = alt.Scale(
        domain=[
            "Unit (Others)",
            "Unit (Within Criteria)"
        ],
        range=["lightgrey", "#F63366"]
    )

    chart = (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x=alt.X(f'{x_col}:O', sort=df[x_col].tolist()),
            y=y_col,
            tooltip=[x_col, y_col],
            color=alt.Color(color_col, scale=color_scale, legend=None)
        )
        .configure_axisX(labelAngle=label_angle)
    )

    return chart


def round_value_to_nearest_5(val):
    rem = val % 5
    if rem >= 3:
        val = val - rem + 5
    else:
        val = val - rem
    return val


def make_barchart_df_rem_lease(df, min_lease, max_lease):

    # Round lease to nearest 5 years
    min_lease = round_value_to_nearest_5(min_lease)
    max_lease = round_value_to_nearest_5(max_lease)

    # Setting bins for Remaining Lease Years
    bins = np.concatenate([[0], np.arange(40, 101, 5)])
    labels = ['40 or less'] + \
        [f'{i+1}-{i+5}' for i in np.arange(40, 95, 5)] + ['95-99']

    assert len(bins) - 1 == len(labels), 'Check bins and labels'

    df_bar = (
        pd.cut(df['Remaining_Lease_years'], bins, labels=labels)
        .value_counts()
        .sort_index()
        .reset_index(name='No of Units')
        .rename(columns={'index': 'Remaining Lease Years'})
    )

    df_bar['bin_lower'] = bins[:-1]

    # Set criteria for bar coloring
    df_bar['bin_group'] = 'Unit (Others)'
    sel = (
        (df_bar['bin_lower'] >= min_lease) &
        (df_bar['bin_lower'] < max_lease)
    )
    df_bar.loc[sel, 'bin_group'] = 'Unit (Within Criteria)'

    df_bar['Remaining Lease Years'] =\
        df_bar['Remaining Lease Years'].astype(object)

    return df_bar


def make_barchart_df_floor(df, min_floor, max_floor):

    df_bar = (
        df['floor_num']
        .value_counts()
        .sort_index()
        .reset_index(name='No of Units')
        .rename(columns={'index': 'Floor'})
    )

    # Prepare data to fill na later
    df_fill = (
        pd.DataFrame({'Floor': list(range(1, 16))})
    )
    df_fill['No of Units'] = 0

    # Grab those less than 15 floors
    df_bar_lte15 = df_bar.query('Floor <= 15')

    # Process those more than 15 floors separately
    num_mt15 = df_bar.query('Floor > 15')['No of Units'].sum()
    df_bar_mt15 = pd.DataFrame({'Floor': ['16+'], 'No of Units': [num_mt15]})
    if max_floor > 15:
        df_bar_mt15['group'] = 'Unit (Within Criteria)'
    else:
        df_bar_mt15['group'] = 'Unit (Others)'

    # Fill missing floors (i.e. floors without units)
    df_bar = (
        df_bar_lte15
        .append(df_fill)
        .drop_duplicates(subset='Floor')
        .sort_values('Floor')
    )

    # Set criteria for bar coloring
    df_bar['group'] = 'Unit (Others)'
    sel = (
        (df_bar['Floor'] >= min_floor) &
        (df_bar['Floor'] <= max_floor)
    )
    df_bar.loc[sel, 'group'] = 'Unit (Within Criteria)'

    # Append with units more than 15 floors
    df_bar = df_bar.append(df_bar_mt15)
    df_bar['Floor'] = df_bar['Floor'].astype('str')
    return df_bar


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
        proj_info: pd.DataFrame, flat_info: pd.DataFrame,
        column_key: str):
    # TODO: Provide a more intuitive func name
    add_input = get_additional_input(
        town_options=widget_info['town_options'],
        flat_options=widget_info['flat_options'],
        key=column_key)

    sel = (flat_info['flat_type'] == add_input['flat_selection'])

    flat_info_selected = (
        flat_info.loc[sel, ['proj_id', widget_input['race']]]
        .rename(columns={widget_input['race']: 'race_quota'})
        .set_index('proj_id')
    )

    info_all, info_selected, info_not_selected =\
        get_selected_town_and_flat_proj_info(
            proj_info, **widget_input, **add_input)

    return info_all, info_selected, info_not_selected, flat_info_selected


def render_content(
        widget_info: Dict, widget_input: Dict,
        proj_info: pd.DataFrame, flat_info: pd.DataFrame):

    st.title('Pairwise Comparison')

    c1, c2 = st.beta_columns(2)

    for i, col in enumerate([c1, c2]):
        with col:

            # Get additional options from main content widgets

            info_all, info_selected, info_not_selected, flat_info_selected =\
                get_column_info(
                    widget_info, widget_input,
                    proj_info, flat_info, column_key=str(i))

            df_floor = make_barchart_df_floor(
                info_all, widget_input['min_floor'], widget_input['max_floor'])

            df_rem_lease = make_barchart_df_rem_lease(
                info_all, widget_input['min_lease'], widget_input['max_lease'])

            # # Test expander
            # with st.beta_expander('Project 1'):
            #     st.write('House | 1 2 3 | asdasd | 123')
            #     st.write('House | 1 2 3 | asdasd | 123')
            #     st.write('House | 1 2 3 | asdasd | 123')

            st.pyplot(plot_unit_within_crit_pie(
                info_selected, info_all, flat_info_selected))

            bar_rem_lease = plot_bar(
                df_rem_lease, x_col='Remaining Lease Years',
                y_col='No of Units', color_col='bin_group', label_angle=-45)
            st.altair_chart(bar_rem_lease, use_container_width=True)

            bar_floor = plot_bar(
                df_floor, x_col='Floor', y_col='No of Units',
                color_col='group')
            st.altair_chart(bar_floor, use_container_width=True)

            st.markdown(
                "<h1 style='text-align: center;'>Overall Chance xx %</h1>",
                unsafe_allow_html=True)
