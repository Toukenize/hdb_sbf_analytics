import streamlit as st

from src.dashboard.pages import summary, pairwise
from src.dashboard.data import (
    load_all, get_selected_proj_info
)
from src.dashboard.sidebar import (
    get_widget_info, get_summary_page_widgets_input,
    get_pairwise_page_widgets_input
)


def show_dashboard():

    st.set_page_config(
        layout="wide", page_title='SBF Analytics (May 2021 Exercise)')

    app_info, proj_info, flat_info = load_all()

    st.sidebar.header('SBF Analytics')
    page = st.sidebar.selectbox(
        'Analytics Type', options=['Overall', 'Pairwise Comparison'])

    if page == 'Overall':
        # Render sidebar widgets and get user input
        widget_info = get_widget_info(proj_info)
        widget_input = get_summary_page_widgets_input(**widget_info)

        # Render content for summary page
        selected_proj_info = get_selected_proj_info(
            app_info, proj_info, flat_info,
            **widget_input)

        summary.render_content(selected_proj_info)

    elif page == 'Pairwise Comparison':
        # Render sidebar widgets and get user input
        widget_info = get_widget_info(proj_info)
        widget_input = get_pairwise_page_widgets_input(**widget_info)

        pairwise.render_content(
            widget_info, widget_input, proj_info
        )


if __name__ == '__main__':
    show_dashboard()
