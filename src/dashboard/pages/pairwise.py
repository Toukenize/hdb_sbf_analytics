import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import altair as alt
import numpy as np
import textwrap

from bs4 import BeautifulSoup
from typing import List, Dict
from matplotlib.figure import Figure
from ..data import get_selected_town_and_flat_proj_info
from ..utils import format_pie_pct_as_val


def make_crit_prop_df(
        proj_info_selected: pd.DataFrame,
        proj_info_all: pd.DataFrame,
        flat_info_selected: pd.DataFrame) -> pd.DataFrame:

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

    crit_prop_df = pd.DataFrame(
        {'Description': ['Units (Others)', 'Units (Within Criteria)'],
         'Number of Units': [num_out_of_crit, num_within_crit]})

    return crit_prop_df


def make_overall_chance_string(
        crit_prop_df: pd.DataFrame,
        app_info: pd.DataFrame,
        town: str,
        flat_type: str) -> str:

    sel = (
        (app_info['town'] == town) &
        (app_info['flat_type'] == flat_type)
    )

    total_1st_timers = int(
        app_info.loc[sel, 'num_first_timers'].squeeze())

    units_within_crit = int(
        crit_prop_df
        .query('Description == "Units (Within Criteria)"')
        ['Number of Units']
        .squeeze()
    )

    chance = units_within_crit / total_1st_timers
    app_str = "No of 1st Timers Applicants"
    unit_str = "No of Units Within Criteria"
    chance_str = "Chance of Getting a Unit"

    markdown_str = textwrap.dedent(f"""
        <table style="width:100%; border: none;">
        <tr style="border: none;">
            <th style="border: none;width: 70%;">{unit_str}</th>
            <th style="border: none;width: 30%;">{units_within_crit}</th>
        </tr>
        <tr style="border: none;">
            <th style="border: none;">{app_str}</th>
            <th style="border: none;">{total_1st_timers}</th>
        </tr>
        <tr style="border: none;">
            <th style="border: none;">{chance_str}</th>
            <th style="border: none;">{chance:.2%}</th>
        </tr>
        </table>
        """)

    return markdown_str


def plot_unit_within_crit_pie(
        crit_prop_df: pd.DataFrame) -> Figure:

    fig, ax = plt.subplots(1, 1, figsize=(8, 4))

    patches, texts, auto_txts = ax.pie(
        x=crit_prop_df['Number of Units'],
        labels=crit_prop_df['Description'],
        labeldistance=None,
        autopct=format_pie_pct_as_val(crit_prop_df['Number of Units']),
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

    legend = ax.legend(bbox_to_anchor=[1.05, 0.5], fontsize=8, frameon=False,
                       handlelength=1, handleheight=1)
    legend.set_title(title='Unit Type', prop={'weight': 'heavy'})
    legend._legend_box.align = "left"

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
            y=alt.Y(y_col, axis=alt.Axis(tickMinStep=1)),
            tooltip=[color_col, x_col, y_col],
            color=alt.Color(color_col,
                            scale=color_scale,
                            legend=alt.Legend(
                                orient="top-right")
                            )
        )
        .configure_axisX(labelAngle=label_angle)
    )

    return chart


def round_value_to_nearest(val, div, rem_thres):
    rem = val % div
    if rem >= rem_thres:
        val = val - rem + div
    else:
        val = val - rem
    return val


def make_barchart_df_price(df, min_price, max_price):

    # TODO: Look into the bar groups (some are missing)

    # Round price to nearest 50k
    step_size = 50
    min_price = round_value_to_nearest(min_price, 50, 30)
    max_price = round_value_to_nearest(max_price, 50, 30)

    # Setting bins for unit price
    bin_min = df['unit_price'].min() // step_size * step_size
    bin_max = (df['unit_price'].max() // step_size + 1) * step_size + 1

    bins = np.arange(bin_min, bin_max, step_size)
    labels = [f'{i+1:.0f}-{i+step_size:.0f}k'
              for i in np.arange(bin_min, bin_max - 1, step_size)]
    assert len(bins) - 1 == len(labels), 'Check bins and labels'

    df_bar = (
        pd.cut(df['unit_price'], bins=bins, labels=labels)
        .value_counts()
        .sort_index()
        .reset_index(name='No of Units')
        .rename(columns={'index': 'Price Range (S$)'})
    )

    df_bar['bin_lower'] = bins[:-1]

    # Set criteria for bar coloring
    df_bar['Unit Type'] = 'Unit (Others)'
    sel = (
        (df_bar['bin_lower'] >= min_price) &
        (df_bar['bin_lower'] < max_price)
    )
    df_bar.loc[sel, 'Unit Type'] = 'Unit (Within Criteria)'

    df_bar['Price Range (S$)'] =\
        df_bar['Price Range (S$)'].astype(object)

    return df_bar


def make_barchart_df_rem_lease(df, min_lease, max_lease):

    # Round lease to nearest 5 years
    min_lease = round_value_to_nearest(min_lease, 5, 3)
    max_lease = round_value_to_nearest(max_lease, 5, 3)

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
    df_bar['Unit Type'] = 'Unit (Others)'
    sel = (
        (df_bar['bin_lower'] >= min_lease) &
        (df_bar['bin_lower'] < max_lease)
    )
    df_bar.loc[sel, 'Unit Type'] = 'Unit (Within Criteria)'

    df_bar['Remaining Lease Years'] =\
        df_bar['Remaining Lease Years'].astype(object)

    return df_bar


def make_barchart_df_latest_comp(df, latest_comp):
    df_bar = (
        df
        .set_index('Est_Completion')
        ['Town']
        .resample('3M')
        .count()
        .reset_index(name='No of Units')
    )

    df_bar['Estimated Completion Date'] = \
        df_bar['Est_Completion'].apply(get_quarter_year)

    df_bar['Unit Type'] = 'Unit (Within Criteria)'

    sel = df_bar['Est_Completion'] >= latest_comp
    df_bar.loc[sel, 'Unit Type'] = 'Unit (Others)'

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
        df_bar_mt15['Unit Type'] = 'Unit (Within Criteria)'
    else:
        df_bar_mt15['Unit Type'] = 'Unit (Others)'

    # Fill missing floors (i.e. floors without units)
    df_bar = (
        df_bar_lte15
        .append(df_fill)
        .drop_duplicates(subset='Floor')
        .sort_values('Floor')
    )

    # Set criteria for bar coloring
    df_bar['Unit Type'] = 'Unit (Others)'
    sel = (
        (df_bar['Floor'] >= min_floor) &
        (df_bar['Floor'] <= max_floor)
    )
    df_bar.loc[sel, 'Unit Type'] = 'Unit (Within Criteria)'

    # Append with units more than 15 floors
    df_bar = df_bar.append(df_bar_mt15)
    df_bar['Floor'] = df_bar['Floor'].astype('str')
    return df_bar


def make_precinct_html_table(
        info_selected: pd.DataFrame,
        precinct: str, units_per_row: int = 3):

    assert precinct in info_selected['precinct_name'].unique(), \
        f'{precinct} is not a valid precinct in selected dataframe.'
    cols = ['blk_num', 'unit_details']

    sel = info_selected['precinct_name'] == precinct
    prec_df = (
        info_selected
        .loc[sel]
        .sort_values(
            ['blk_num', 'floor_num', 'unit_num', 'unit_price'],
            ascending=[True, False, True, True])
        [cols]
        .groupby('blk_num')
        .apply(
            lambda x: (
                x
                .reset_index(drop=True)
                .assign(
                    col_val=lambda x: x.index % units_per_row,
                    row_idx=lambda x: x.index // units_per_row
                )
            )
        )
        .set_index(['blk_num', 'row_idx', 'col_val'])
        .unstack(fill_value='')
        .reset_index(-1, drop=True)
        .reset_index()
    )

    # Append additional columns & tidy column name
    new_cols = units_per_row - len(prec_df.columns) + 1
    for i in range(new_cols):
        prec_df[i] = ''

    prec_df.columns = ['Block Info', 'Units Info'] + [''] * (units_per_row - 1)

    # Generate block info dict
    block_info_dict = prec_df['Block Info'].value_counts().to_dict()

    # Replace block info such that each unique info only appear once
    prec_df['Block Info'] = prec_df['Block Info'].drop_duplicates(keep='first')
    prec_df['Block Info'] = prec_df['Block Info'].fillna('')

    prec_df.set_index(['Block Info'], inplace=True)

    # Generate html string
    table_html = prec_df.to_html(escape=False)

    # Process html string
    table_html = format_precinct_table_html(table_html, block_info_dict)

    return table_html


def get_unit_details(floor_num, unit_num, unit_price):
    unit_str = f'#{str(floor_num)}-{str(unit_num)}'
    price_str = f'(${unit_price:.0f}k)'
    unit_details = f'{unit_str} <br> {price_str}'
    return unit_details


def format_precinct_table_html(table_html, block_info_dict):

    # Convert html string to soup
    table_soup = BeautifulSoup(table_html, features='lxml')

    # Update table attributes
    tab_info = table_soup.find('table')
    tab_info.attrs = dict()
    tab_info['style'] = 'width:100%; border: none;'

    # Remove table header row
    table_soup.find('thead').replace_with('')

    # If th is something, replace it with the row span
    # If th is blank, remove it
    for c in list(table_soup.find('table').findChildren()):

        if c.name == 'th':
            if c.text != '':
                c['rowspan'] = block_info_dict[c.text]
                c['valign'] = 'top'
            else:
                c.replace_with('')
        if c.name == 'tr':
            if c.find('th').text != '':
                c['style'] = 'border-top: solid thin; width: 25%;'
        elif c.name == 'th':
            c['style'] = 'border: none; text-align: left; width: 25%;'
        else:
            c['style'] = 'border: none; text-align: center; width: 25%;'

    return table_soup.find('table').prettify()


def get_quarter_year(x):
    year = str(x.year)
    quarter = f'Q{x.month / 3:.0f}'
    return f'{quarter}/{year}'


def town_sel_widget(town_options, key):
    town_selection = st.selectbox(
        label='Town', options=town_options, key=key
    )
    return town_selection


def flat_sel_widget(flat_options, key):
    # TODO : Add tooltip on income ceiling for 3-Room flats
    flat_selection = st.selectbox(
        label='Flat Type', options=flat_options, key=key
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
        widget_input: Dict, add_input: Dict,
        proj_info: pd.DataFrame, flat_info: pd.DataFrame,


):
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
        proj_info: pd.DataFrame, flat_info: pd.DataFrame,
        app_info: pd.DataFrame):

    st.title('Pairwise Comparison')

    c1, c2 = st.beta_columns(2)

    for i, col in enumerate([c1, c2]):
        with col:

            # TODO: Provide a more intuitive func name
            st.header('Town & Flat Selector')
            add_input = get_additional_input(
                town_options=widget_info['town_options'],
                flat_options=widget_info['flat_options'],
                key=str(i))

            # Get additional options from main content widgets
            info_all, info_selected, info_not_selected, flat_info_selected =\
                get_column_info(
                    widget_input, add_input,
                    proj_info, flat_info)

            if len(info_all) == 0:
                st.error(
                    textwrap.dedent(
                        f"""
                        **ERROR** :
                        There is no {add_input['flat_selection']} flats
                        for {add_input['town_selection']}.
                        """
                    )
                )
            else:
                if len(info_selected) == 0:
                    st.warning(
                        '**WARNING** : None of the units fit the criteria.')

                df_floor = make_barchart_df_floor(
                    info_all,
                    widget_input['min_floor'],
                    widget_input['max_floor'])

                df_rem_lease = make_barchart_df_rem_lease(
                    info_all,
                    widget_input['min_lease'],
                    widget_input['max_lease'])

                df_price = make_barchart_df_price(
                    info_all,
                    widget_input['min_price'],
                    widget_input['max_price'])

                df_latest_comp = make_barchart_df_latest_comp(
                    info_all, widget_input['latest_comp'])

                # Tabulate all df required for charts/ markdown
                crit_prop_df = make_crit_prop_df(
                    info_selected, info_all, flat_info_selected)

                chance_string = make_overall_chance_string(
                    crit_prop_df, app_info,
                    town=add_input['town_selection'],
                    flat_type=add_input['flat_selection']
                )

                bar_price_range = plot_bar(
                    df_price, x_col='Price Range (S$)',
                    y_col='No of Units',
                    color_col='Unit Type', label_angle=-45)

                bar_rem_lease = plot_bar(
                    df_rem_lease, x_col='Remaining Lease Years',
                    y_col='No of Units',
                    color_col='Unit Type', label_angle=-45)

                bar_latest_comp = plot_bar(
                    df_latest_comp, x_col='Estimated Completion Date',
                    y_col='No of Units',
                    color_col='Unit Type', label_angle=-45)

                bar_floor = plot_bar(
                    df_floor, x_col='Floor', y_col='No of Units',
                    color_col='Unit Type')

                st.header('Overview of Chances')
                st.markdown(chance_string, unsafe_allow_html=True)

                st.header('Breakdown of Units Within Criteria')
                st.pyplot(plot_unit_within_crit_pie(crit_prop_df))

                st.subheader('By Price Range')
                st.altair_chart(bar_price_range, use_container_width=True)

                st.subheader('By Remaining Lease')
                st.altair_chart(bar_rem_lease, use_container_width=True)

                st.subheader('By Floor Level')
                st.altair_chart(bar_floor, use_container_width=True)

                st.subheader('By Estimated Completion Date')
                st.altair_chart(bar_latest_comp, use_container_width=True)

                if len(info_selected) > 0:

                    info_selected['unit_details'] = (
                        info_selected.apply(
                            lambda x: get_unit_details(
                                x.floor_num, x.unit_num, x.unit_price),
                            axis=1)
                    )

                    st.header('Project Details of Units within Criteria')
                    st.text('Racial quota is not taken into consideration.')

                    for precinct in sorted(
                            info_selected['precinct_name'].unique()):

                        html_table = make_precinct_html_table(
                            info_selected, precinct)

                        with st.beta_expander(precinct):
                            st.markdown(html_table, unsafe_allow_html=True)
