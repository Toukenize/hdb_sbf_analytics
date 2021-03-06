import pandas as pd
from datetime import datetime
from typing import List
from ..constants import (
    PROJ_INFO_PATH, APP_INFO_PATH,
    BLOCK_INFO_PATH, FLAT_INFO_PATH, SBF_PAGE_PREFIX)


def load_all():

    app_info = get_app_info()
    proj_info = get_proj_info()
    flat_info = get_flat_info()

    return app_info, proj_info, flat_info


def get_proj_info():

    df_proj_info = pd.read_csv(PROJ_INFO_PATH)

    # Get upper limit of remaining lease
    # Lower limit only affect 2-Room Flexi
    df_proj_info['Remaining_Lease_years'] = (
        df_proj_info['Remaining_Lease']
        .str.extract(r'(\d+) years')
        .astype(int)
        .squeeze()
        .tolist()
    )

    # Get latest completion date
    sel = df_proj_info['Est_Completion'] != 'Keys Available'
    df_proj_info.loc[sel, 'Est_Completion'] = (
        df_proj_info.loc[sel, 'Est_Completion']
        .str.extract(r'(\d{1,2}/\d{4})$')
        .squeeze()
        .tolist()
    )

    # Set those immediately available to current date
    sel = df_proj_info['Est_Completion'] == 'Keys Available'
    df_proj_info.loc[sel, 'Est_Completion'] = '6/2021'

    df_proj_info['Est_Completion'] = pd.to_datetime(
        df_proj_info['Est_Completion'])

    # Title case for merging
    df_proj_info['flat_type'] = df_proj_info['flat_type'].str.title()

    # Get floor number from floor number text
    df_proj_info['floor_num'] = (
        df_proj_info['floor_num']
        .str.extract(r'(\d+)')
        .squeeze()
        .astype(int)
        .tolist()
    )

    # Process Unit info
    df_proj_info['unit_num'] = (
        df_proj_info['unit_num']
        .str.extract(r'(\w+)').squeeze().tolist()
    )
    df_proj_info['unit_size'] = (
        df_proj_info['unit_size']
        .str.extract(r'(\d+)').squeeze().tolist()
    )
    df_proj_info['unit_price'] = (
        df_proj_info['unit_price']
        .str.extract(r'(\d+),(\d+)').sum(axis=1)
        .astype(float)
        .div(1_000)
    )

    # Return only 3,4,5 room info
    sel = df_proj_info['flat_type'].isin(['4-Room', '3-Room', '5-Room'])
    df_proj_info = df_proj_info.loc[sel].copy().reset_index(drop=True)

    return df_proj_info


def get_flat_supply_info():

    df_flat_supply_info = pd.read_csv(FLAT_INFO_PATH)

    return df_flat_supply_info


def get_block_info():

    df_block_info = pd.read_csv(BLOCK_INFO_PATH)
    df_block_info['flatType'] = df_block_info['flatType'].str.title()

    return df_block_info


def get_flat_info():

    df_block_info = get_block_info()
    df_flat_supply_info = get_flat_supply_info()

    # Get ethnic quota
    ethnic_quota = (
        df_block_info
        .groupby(['proj_id', 'flatType'])
        [['chinese', 'malay', 'indian']]
        .sum()
    )

    df_flat_info = (
        df_flat_supply_info
        .set_index(['proj_id', 'flatType'])
        .merge(ethnic_quota, left_index=True, right_index=True)
        .reset_index()
    )

    df_flat_info.rename(columns={'flatType': 'flat_type'}, inplace=True)

    return df_flat_info


def get_app_info():

    # Note : Estimates for 5-Room isn't as accurate, the computed # applicants
    # is generally lower than the # applicants shown on HDB website
    df_app_status = pd.read_csv(APP_INFO_PATH)

    # Since the application info for 5-Room, 3Gen and Exec are combined
    # we make an assumption that most of these applications are for 5-Room
    sel = df_app_status['flat_type'].str.startswith('5-Room')
    df_app_status.loc[sel, 'flat_type'] = '5-Room'

    # Remove income ceiling info from 3-Room flats (move to tooltip instead)
    sel = df_app_status['flat_type'].str.startswith('3-Room')
    df_app_status.loc[sel, 'flat_type'] = '3-Room'

    return df_app_status


def get_selected_proj_info(
        df_app_status: pd.DataFrame,
        df_proj_info: pd.DataFrame,
        df_flat_info: pd.DataFrame,
        min_floor: int = 0,
        max_floor: int = 99,
        min_lease: int = 0,
        max_lease: int = 99,
        min_price: int = 100,
        max_price: int = 900,
        race: str = 'chinese',
        flat_selection: List[str] = ['4-Room', '5-Room'],
        town_selection: List[str] = ['All Towns'],
        latest_comp: datetime = datetime(2030, 1, 1)
) -> pd.DataFrame:

    sel = (
        (
            (df_proj_info['Remaining_Lease_years'] >= min_lease) &
            (df_proj_info['Remaining_Lease_years'] <= max_lease)
        ) &
        (
            (df_proj_info['floor_num'] >= min_floor) &
            (df_proj_info['floor_num'] <= max_floor)
        ) &
        (
            (df_proj_info['unit_price'] >= min_price) &
            (df_proj_info['unit_price'] <= max_price)
        ) &
        (df_proj_info['flat_type'].isin(flat_selection)) &
        (df_proj_info['Est_Completion'] <= latest_comp)
    )

    if 'All Towns' not in town_selection:
        sel = sel & (df_proj_info['Town'].isin(town_selection))

    # Get project supply info tts within selection criteria
    df_proj_info_selected = (
        df_proj_info
        .loc[sel]
        .groupby(['proj_id', 'flat_type'])
        .agg(
            town=('Town', 'first'),
            supply_within_crit=('Town', 'count'),
            price_list=('unit_price', list)
        )
        .reset_index()
    )

    # Merge with flat info
    df_proj_info_selected = (
        df_proj_info_selected
        .merge(df_flat_info, on=['proj_id', 'flat_type'])
    )

    # Select the upper limit of supply
    df_proj_info_selected['supply_within_crit_n_quota'] = (
        df_proj_info_selected[['supply_within_crit', race]].min(axis=1)
    )

    # Merge application status
    df_merged = (
        df_proj_info_selected
        .groupby(['town', 'flat_type'], as_index=False)
        .agg(
            supply_within_crit_n_quota=('supply_within_crit_n_quota', 'sum'),
            proj_list=(
                'proj_id', lambda x: list(SBF_PAGE_PREFIX + i for i in x)),
            avg_price=(
                'price_list',
                lambda x: x.explode().mean().astype(int)
            )
        )
        .merge(
            df_app_status[['town', 'flat_type', 'num_first_timers']],
            on=['town', 'flat_type']
        )
    )

    # Calculate adjusted chance
    df_merged['adjusted_chance_pc'] = (
        (df_merged['supply_within_crit_n_quota'] /
         df_merged['num_first_timers'])
    )

    # Show results
    return df_merged.sort_values('adjusted_chance_pc', ascending=False)


def get_selected_town_and_flat_proj_info(
        proj_info: pd.DataFrame,
        min_floor: int = 0,
        max_floor: int = 99,
        min_lease: int = 0,
        max_lease: int = 99,
        min_price: int = 100,
        max_price: int = 900,
        race: str = 'chinese',
        flat_selection: str = '4-Room',
        town_selection: str = 'Punggol',
        latest_comp: datetime = datetime(2030, 1, 1)
):
    town_flat_sel = (
        (proj_info['flat_type'] == flat_selection) &
        (proj_info['Town'] == town_selection)
    )

    crit_sel = (
        (
            (proj_info['Remaining_Lease_years'] >= min_lease) &
            (proj_info['Remaining_Lease_years'] <= max_lease)
        ) &
        (
            (proj_info['floor_num'] >= min_floor) &
            (proj_info['floor_num'] <= max_floor)
        ) &
        (
            (proj_info['unit_price'] >= min_price) &
            (proj_info['unit_price'] <= max_price)
        ) &
        (proj_info['Est_Completion'] <= latest_comp)
    )

    proj_info_all = proj_info.loc[town_flat_sel].copy()
    proj_info_selected = proj_info.loc[town_flat_sel & crit_sel].copy()
    proj_info_not_selected = proj_info.loc[town_flat_sel & ~crit_sel].copy()

    assert len(proj_info_selected) + len(proj_info_not_selected) ==\
        len(proj_info_all), 'Project dataframe subset does not tally.'

    return proj_info_all, proj_info_selected, proj_info_not_selected
