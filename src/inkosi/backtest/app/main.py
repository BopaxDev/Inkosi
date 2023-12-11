import random
import string
from datetime import datetime, timedelta

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

from inkosi.backtest.operation.asset import Asset
from inkosi.backtest.operation.backtest import backtest, filter_dataset
from inkosi.backtest.operation.models import (
    BacktestRecord,
    BacktestRequest,
    SourceType,
    TradeResult,
    TradeStatus,
)
from inkosi.backtest.operation.schemas import (
    AvailableTechincalIndicators,
    Colors,
    DataSourceType,
    Filter,
    Relation,
    SamplingMethods,
    TimeFrames,
    VisualisationOptions,
)
from inkosi.backtest.operation.sources import Dataset
from inkosi.database.mongodb.schemas import Position
from inkosi.database.postgresql.database import PostgreSQLCrud
from inkosi.log.log import Logger
from inkosi.utils.settings import get_default_tickers

logger = Logger(module_name="backtest", package_name="main")

st.set_page_config(page_title="Inkosi Backtesting", layout="wide")
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

st.title("Trading Strategy Backtest")
st.session_state["token"] = st.experimental_get_query_params().get("token", [0])[0]

if "count" not in st.session_state:
    st.session_state.count = 0

if "sampled" not in st.session_state:
    st.session_state["sampled"] = False

if "filters" not in st.session_state:
    st.session_state["filters"] = {}

if "asset" in st.session_state:
    pass


def random_id() -> str:
    return random.choice(string.ascii_uppercase) + str(random.randint(0, 999999))


def add_new_rule_expander(count: int):
    expander = st.expander(label="Rule")
    form_rule = expander.form(key=random_id(), clear_on_submit=False)

    element_first_role_key = random_id()
    period_first_role_key = random_id()

    relation_key = random_id()

    element_second_role_key = random_id()
    period_second_role_key = random_id()

    form_rule.selectbox(
        "element_first_feature",
        key=element_first_role_key,
        options=list(
            set(VisualisationOptions.list()).union(AvailableTechincalIndicators.list())
        ),
        placeholder="First Feature",
        label_visibility="hidden",
    )
    form_rule.number_input(
        "period_first_feature",
        key=period_first_role_key,
        label_visibility="hidden",
        min_value=1,
        value=20,
        max_value=200,
        step=1,
    )

    form_rule.selectbox(
        "relation",
        key=relation_key,
        options=Relation.list(),
        label_visibility="hidden",
    )

    form_rule.selectbox(
        "element_second_role",
        key=element_second_role_key,
        options=list(
            set(VisualisationOptions.list()).union(AvailableTechincalIndicators.list())
        ),
        label_visibility="hidden",
    )
    form_rule.number_input(
        element_second_role_key,
        key=period_second_role_key,
        label_visibility="hidden",
        min_value=1,
        value=20,
        max_value=200,
        step=1,
    )

    if form_rule.form_submit_button("Save"):
        st.session_state["filters"][count] = Filter(
            first_element={
                "ELEMENT": st.session_state.get(element_first_role_key),
                "PERIOD": st.session_state.get(period_second_role_key),
            },
            second_element={
                "ELEMENT": st.session_state.get(element_second_role_key),
                "PERIOD": st.session_state.get(period_second_role_key),
            },
            relation=st.session_state.get(relation_key),
        )

    if form_rule.form_submit_button("Remove"):
        st.session_state["filters"].pop(count, None)


def reset_asset():
    st.session_state["sampled"] = False


def set_asset(data: tuple):
    st.session_state["asset"] = data


if not st.session_state.get("token", None):
    st.error("No token authentication has been provided", icon="🚨")
else:
    postgresql = PostgreSQLCrud()
    if not postgresql.valid_authentication(st.session_state.get("token", 0)):
        st.error("Unable to authenticate through the token provided", icon="🚨")
    else:
        st.sidebar.header("Settings")

        source_type = st.sidebar.selectbox(
            "Select the Data Source Type",
            options=DataSourceType.list(),
            on_change=reset_asset(),
        )

        ticker_selection = st.sidebar.selectbox(
            label="Ticker",
            options=get_default_tickers(),
            placeholder="Select Ticker",
            on_change=reset_asset(),
        )
        time_frame = st.sidebar.selectbox(
            label="Time Frame",
            options=TimeFrames.list(),
            placeholder="Select Time Frames",
            on_change=reset_asset(),
        )
        column = st.sidebar.selectbox(
            label="Column",
            options=VisualisationOptions.list(),
            placeholder="Select Column",
            on_change=reset_asset(),
        )
        start_date = st.sidebar.date_input(
            "Start Date",
            value=datetime.today() - timedelta(days=4),
            on_change=reset_asset(),
        )
        end_date = st.sidebar.date_input(
            "End Date",
            max_value=datetime.today(),
            on_change=reset_asset(),
        )

        backtesting_tab, sampling_tab = st.tabs(["Backtesting", "Sampling"])

        form_rules = backtesting_tab.form(
            key="Form Rules",
            clear_on_submit=False,
        )
        first_expander = form_rules.expander(label="First Rule")

        first_rule_checkbox = first_expander.checkbox(
            "Active",
            value=False,
            key="first_rule_checkbox",
        )

        first_element_first_rule = first_expander.selectbox(
            "first_element_first_rule",
            options=list(
                set(VisualisationOptions.list()).union(
                    AvailableTechincalIndicators.list()
                )
            ),
            placeholder="First Feature",
            label_visibility="hidden",
        )
        first_period_first_rule = first_expander.number_input(
            "first_period_first_rule",
            label_visibility="hidden",
            min_value=1,
            value=20,
            max_value=200,
            step=1,
        )

        relation_first_rule = first_expander.selectbox(
            "relation_first_rule",
            options=Relation.list(),
            label_visibility="hidden",
        )

        second_element_first_rule = first_expander.selectbox(
            "second_element_first_rule",
            options=list(
                set(VisualisationOptions.list()).union(
                    AvailableTechincalIndicators.list()
                )
            ),
            label_visibility="hidden",
        )
        second_period_first_rule = first_expander.number_input(
            "second_period_first_rule",
            label_visibility="hidden",
            min_value=1,
            value=20,
            max_value=200,
            step=1,
        )

        second_expander = form_rules.expander(label="Second Rule")

        second_rule_checkbox = second_expander.checkbox(
            "Active",
            value=False,
            key="second_rule_checkbox",
        )

        first_element_second_rule = second_expander.selectbox(
            "first_element_second_rule",
            options=list(
                set(VisualisationOptions.list()).union(
                    AvailableTechincalIndicators.list()
                )
            ),
            placeholder="First Feature",
            label_visibility="hidden",
        )
        first_period_second_rule = second_expander.number_input(
            "first_period_second_rule",
            label_visibility="hidden",
            min_value=1,
            value=20,
            max_value=200,
            step=1,
        )

        relation_second_rule = second_expander.selectbox(
            "relation_second_rule",
            options=Relation.list(),
            label_visibility="hidden",
        )

        second_element_second_rule = second_expander.selectbox(
            "second_element_second_rule",
            options=list(
                set(VisualisationOptions.list()).union(
                    AvailableTechincalIndicators.list()
                )
            ),
            label_visibility="hidden",
        )
        second_period_second_rule = second_expander.number_input(
            "second_period_second_rule",
            label_visibility="hidden",
            min_value=1,
            value=20,
            max_value=200,
            step=1,
        )

        position_selected = form_rules.selectbox(
            label="Position",
            options=Position.list(),
            placeholder="Select Position",
        )
        take_profit = form_rules.number_input(
            label="Take Profit", placeholder="Type Take Profit", value=15.0
        )
        stop_loss = form_rules.number_input(
            label="Stop Loss", placeholder="Type Stop Loss", value=15.0
        )

        if form_rules.form_submit_button(
            "Backtest",
            use_container_width=True,
        ):
            asset = Asset(
                asset_name=ticker_selection,
                time_frame=time_frame,
                start=start_date,
                end=end_date,
            )

            filters = []
            if first_rule_checkbox:
                filters.append(
                    Filter(
                        first_element={
                            "ELEMENT": first_element_first_rule,
                            "PERIOD": first_period_first_rule,
                        },
                        second_element={
                            "ELEMENT": second_element_first_rule,
                            "PERIOD": second_period_first_rule,
                        },
                        relation=relation_first_rule,
                    )
                )

            if second_rule_checkbox:
                filters.append(
                    Filter(
                        first_element={
                            "ELEMENT": first_element_second_rule,
                            "PERIOD": first_period_second_rule,
                        },
                        second_element={
                            "ELEMENT": second_element_second_rule,
                            "PERIOD": second_period_second_rule,
                        },
                        relation=relation_second_rule,
                    )
                )

            if not filters:
                st.error(body="No Trading Rule specified", icon="🚨")

            if not take_profit or not stop_loss:
                st.info(
                    "Unable to conduct the backtest. No take profit has been provided"
                )

            try:
                filtering = filter_dataset(asset.data_frame(), filters=filters)
                backtest_request = BacktestRequest(
                    starting_indexes=filtering.tolist(),
                    direction=np.repeat(
                        position_selected,
                        repeats=filtering.shape[0],
                    ).tolist(),
                    take_profits=(
                        np.ones(shape=filtering.shape[0]) * take_profit
                    ).tolist(),
                    stop_losses=(
                        np.ones(shape=filtering.shape[0]) * stop_loss
                    ).tolist(),
                    dataset=Dataset(asset, source_type=SourceType.ASSET),
                )

                backtest_result: list[BacktestRecord] = backtest(backtest_request)

                profit_trades, losses_trades, na_trades = 0, 0, 0
                closed_trades, pending_trades = 0, 0

                for result in backtest_result:
                    match result.result:
                        case TradeResult.PROFIT:
                            profit_trades += 1
                        case TradeResult.LOSS:
                            losses_trades += 1
                        case TradeResult.PENDING:
                            na_trades += 1

                    match result.status:
                        case TradeStatus.CLOSED:
                            closed_trades += 1
                        case TradeStatus.PENDING:
                            pending_trades += 1

                trades = profit_trades + losses_trades + pending_trades

                profitable_ratio_trades: str = (
                    format(profit_trades / trades, ".2f")
                    if trades > 0
                    else "Not Available"
                )

                profitable_ratio_trades_no_pending_trades: str = (
                    format(profit_trades / (profit_trades + losses_trades), ".2f")
                    if (profit_trades + losses_trades) > 0
                    else "Not Available"
                )

                pending_ratio_trades: str = (
                    format(pending_trades / closed_trades, ".2f")
                    if closed_trades > 0
                    else "Not Available"
                )

                if not len(backtest_result):
                    st.warning(
                        "It is kindly suggested to edit variables such as date periods,"
                        " rules, take profit, stop loss, ...\n"
                    )

                st.title("Backtesting Result")
                st.markdown(
                    body=f"""
                    <p>Number of Trades <strong>{len(backtest_result)}</strong></p>
                    <p>Chosen Take Profit <strong>{take_profit}</strong></p>
                    <p>Chosen Stop Loss <strong>{stop_loss}</strong></p>
                    <p>Position Type <strong>{position_selected}</strong></p>
                    <p>Profit Trades <strong>{profit_trades}</strong></p>
                    <p>Losses Trades <strong>{losses_trades}</strong></p>
                    <p>Pending Trades <strong>{pending_trades}</strong></p>
                    <p>Profitable Ratio Trades <strong>
                    {profitable_ratio_trades}
                    </strong></p>
                    <p>Profitable Ratio Trades (No Pending Trades) <strong>
                    {profitable_ratio_trades_no_pending_trades}
                    </strong></p>
                    <p>Closed Trades <strong>
                    {closed_trades}</strong></p>
                    <p>Pending Ratio Trades <strong>
                    {pending_ratio_trades}</strong></p>
                    """,
                    unsafe_allow_html=True,
                )
            except Exception as error:
                logger.error(
                    f"Unable to correctly perform the backtest. Error occurred: {error}"
                )
                st.error(
                    body=(
                        "Unable to correctly conduct backtesting. Check log console."
                        " Please try using new configuration."
                    ),
                    icon="🚨",
                )

        form_sampling_method = sampling_tab.form(
            key="Form Sampling Method",
            clear_on_submit=True,
        )
        sampling_method = form_sampling_method.selectbox(
            label="Select Sampling Methods",
            options=SamplingMethods.list(),
        )
        steps_forward = form_sampling_method.number_input(
            label="Steps Forward",
            min_value=2,
            max_value=254,
            value=10,
            step=1,
        )
        samples = form_sampling_method.number_input(
            label="Samples",
            value=100,
            min_value=1,
            max_value=10000,
        )

        if form_sampling_method.form_submit_button(
            label="Sample",
            use_container_width=True,
        ):
            st.session_state["sampled"] = True
            asset = Asset(
                ticker_selection,
                time_frame=time_frame,
                start=start_date,
                end=end_date,
            )
            set_asset(
                data=asset.sampling(
                    sampling_method=sampling_method,
                    steps_forward=steps_forward,
                    column=column,
                    samples=samples,
                )
            )

        if not st.session_state.get("sampled", False):
            asset = Asset(
                ticker_selection,
                time_frame=time_frame,
                start=start_date,
                end=end_date,
            )
            set_asset(asset.plotting())

        charts = []
        for data in st.session_state.get("asset")[1]:
            line_chart = (
                alt.Chart(
                    pd.DataFrame(
                        {
                            "Dates": st.session_state.get("asset")[0],
                            column: data,
                        }
                    )
                )
                .mark_line()
                .encode(
                    x=alt.X("Dates"),
                    y=alt.Y(column, scale=alt.Scale(zero=False)),
                    color=alt.value(random.choice(Colors)),
                )
            )
            charts.append(line_chart)

        st.altair_chart(alt.layer(*charts), use_container_width=True)
