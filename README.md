# HDB Sales of Balances Flat Analytics (May 2021)

This analytics dashboard was designed to estimate your chances of getting a SBF unit as a first timer in different towns of Singapore under different housing types based on your criterions:
1. Ethnicity
2. Budget range
3. Desired loor levels
4. Remaining lease years of the unit
5. The latest completion date you don't mind waiting until

The chances were estimated based on the number of first timer applicants for that particular town & flat type, which was updated every 3 hours during the SBF application period. The remaining flat information were also scraped from HDB website, which were available as additional information to all applicants. The web scraping scripts are available as notebooks (though I doubt they still can be used, since the SBF exercise was over).

In addition to looking at the overall chances by town and flat type, you can also do a more detailed pairwise comparison of your selected town & flat type, to further understand the pros and cons of selecting them for your application.

Another usage of this dashboard is that, after you have gotten your SBF queue number, you can compare your queue number to the number of units (under your balloted town/ flat type) that meets your criteria. If your queue number is less than or equal to the number of units that fulfils your criteria, congratulations & you just need to wait patiently for your turn to select a unit. Otherwise, good luck to you, there is still a chance as long as you have a queue number. If you are like me, didn't even get a queue number, wish you better luck in your next application! :joy:

Feel free to chat me up if you have any feedbacks. :smile:


# How to View the Dashboard

A hosted version of the dashboard is available on Streamlit Share [here](https://share.streamlit.io/toukenize/hdb_sbf_analytics/dashboard.py) (well,if it doesn't go sleep due to inactivity).

Otherwise:
1. Clone this repo
2. Install [poetry](https://python-poetry.org/docs/#installation)
3. Shell into the project root `cd <wherever-your-cloned-project-is>`
4. Install the project `poetry install`
5. Start the poetry environment `poetry shell`
6. Start the dashboard `streamlit run dashboard.py`
7. Go to the local URL (by default, it is http://localhost:8501) and you should see the dashboard!

Note : In case you are wondering why there is a `requirements.txt` sitting around since I'm already using `poetry` to manage my packages, it is actually meant for Streamlit Share. Read more about it [here](https://streamlit.io/sharing)