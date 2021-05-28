import time
import pandas as pd
from selenium import webdriver
from bs4 import BeautifulSoup
from typing import List
from ..constants import (
    CHROME_EXEC, SBF_APP_INFO_PAGE, TABLE_3ROOM_ABV_COLS)


def get_app_info_table() -> str:

    # Read and load html as soup
    driver = webdriver.Chrome(executable_path=CHROME_EXEC)
    driver.get(SBF_APP_INFO_PAGE)
    driver.maximize_window()
    time.sleep(1)
    soup = BeautifulSoup(driver.page_source, features='lxml')
    driver.close()

    # Get tables
    _, table_3room_abv = soup.find_all('table', class_='scrolltable')

    return str(table_3room_abv)


def table_str_to_df(
        table_str: str, columns: List[str]) -> pd.DataFrame:

    # Convert table str to df
    df = pd.read_html(table_str)[0]
    df.columns = columns

    # Title-case flat_type for ease of merging w other tables
    df['flat_type'] = df['flat_type'].str.title()

    # Remove redundant rows
    sel = df['town'].isin(
        ['Non-Mature Towns/Estates', 'Mature Towns/Estates', 'TOTAL'])
    df = df.loc[~sel].copy()

    # Cast numeric columns
    for col in ['num_units', 'num_applicants']:
        df[col] = df[col].astype(int)

    for col in ['first_timers', 'second_timers', 'overall']:
        df[col] = df[col].astype(float)

    # Derived from applicantion rate's formulae
    # Note that the computed # doesnt match the actual # exactly (no idea why)
    df['num_first_timers'] = (
        (df['first_timers'] * df['num_units'] * 0.95)
        .round().astype(int)
    )

    sel = df['second_timers'].notna()
    df.loc[sel, 'num_second_timers'] = (
        (df.loc[sel, 'second_timers'] * df.loc[sel, 'num_units'] * 0.05)
        .round()
        .astype(int)
    )
    df['num_applicants_computed'] = (
        df['num_first_timers'] + df['num_second_timers'].fillna(0)
    )
    return df


def get_data() -> pd.DataFrame:

    table_str = get_app_info_table()
    df = table_str_to_df(table_str, TABLE_3ROOM_ABV_COLS)

    return df
