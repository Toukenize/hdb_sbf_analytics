import pandas as pd
from selenium import webdriver
from bs4 import BeautifulSoup

from .constants import CHROME_EXEC, SBF_APP_INFO_PAGE


def get_application_info_df() -> pd.DataFrame:
    driver = webdriver.Chrome(executable_path=CHROME_EXEC)
    driver.get(SBF_APP_INFO_PAGE)
    soup = BeautifulSoup(driver.page_source)

    # Get 2nd table, which consists info for 3 rooms and above
    table = soup.find_all('table', class_='scrolltable')[-1]

    df = pd.read_html(str(table))[0]
    df.columns = ['town', 'flat_type', 'num_units', 'num_applicants',
                  'first_timers', 'second_timers', 'overall']

    df['flat_type'] = df['flat_type'].str.title()

    # Remove invalid rows
    sel = df['town'].isin(
        ['Non-Mature Towns/Estates', 'Mature Towns/Estates', 'TOTAL'])
    df = df.loc[~sel].copy()

    for col in ['num_units', 'num_applicants']:
        df[col] = df[col].astype(int)

    for col in ['first_timers', 'second_timers', 'overall']:
        df[col] = df[col].astype(float)
