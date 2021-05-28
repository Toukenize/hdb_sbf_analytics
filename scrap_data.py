import argparse
from src.web_scrap import (
    application_info,
    # block_info, flat_info,
    # project_info, project_link
)
from src.constants import APP_INFO_PATH


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--app_only', type=str,
        choices=['yes', 'no'],
        default='yes',
        help="When set to `yes`, will get only the latest application info"
    )
    args = parser.parse_args()

    return args


def main():

    args = parse_args()

    app_info = application_info.get_data()
    app_info.to_csv(APP_INFO_PATH, index=False)

    if args.app_only == 'yes':
        return
    else:
        # TODO: Add remaining scrapping functions
        pass


if __name__ == "__main__":
    main()
