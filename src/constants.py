from pathlib import Path

CHROME_EXEC = '/home/chewzy/selenium_drivers/chromedriver'

SBF_APP_INFO_PAGE = \
    'https://services2.hdb.gov.sg/webapp/'\
    'BP13BTOENQWeb/AR_May2021_SBF?strSystem=SBF'

TABLE_2ROOM_COLS = ['town', 'flat_type', 'num_units', 'num_applicants',
                    'elderly', 'first_timers', 'second_timers', 'singles',
                    'overall']
TABLE_3ROOM_ABV_COLS = ['town', 'flat_type', 'num_units', 'num_applicants',
                        'first_timers', 'second_timers', 'overall']

DATA_FOLDER = Path('/home/chewzy/Personal/hdb/data')  # Change me
PROJ_INFO_PATH = DATA_FOLDER / 'SBF_project_info_v2.csv'
BLOCK_INFO_PATH = DATA_FOLDER / 'SBF_block_info.csv'
FLAT_INFO_PATH = DATA_FOLDER / 'SBF_flat_supply_info.csv'
APP_INFO_PATH = DATA_FOLDER / 'SBF_application_status.csv'
