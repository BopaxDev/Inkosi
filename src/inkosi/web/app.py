import random
import string
from datetime import datetime, timedelta

import pandas as pd
import requests
import streamlit as st
from fastapi import status
from streamlit.components.v1 import html

from inkosi.database.mongodb.schemas import Position
from inkosi.database.postgresql.database import PostgreSQLCrud
from inkosi.database.postgresql.schemas import CategoriesATS, FundInformation, UserRole
from inkosi.log.log import Logger
from inkosi.utils.settings import get_trading_tickers
from inkosi.utils.utils import AdministratorPolicies, CommissionTypes, InvestorPolicies

logger = Logger(module_name="app", package_name="web")

st.set_page_config(page_title="Inkosi Web App - Login", layout="centered")
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)


def open_page(page_url: str):
    open_script = f"""
        <script type="text/javascript">
            window.open('{page_url}', '_blank').focus();
        </script>
    """
    html(open_script)


def get_authentication() -> bool:
    session = st.session_state
    token = session.get("token", "")
    if not token:
        logger.critical("The token has not been found")
        return False

    postgres = PostgreSQLCrud()
    result = postgres.valid_authentication(
        token,
    )
    if not result:
        set_token("")

    return result


def set_token(token: str) -> None:
    session = st.session_state
    session["token"] = token


def set_policies(policies: list[str]) -> None:
    session = st.session_state
    session["policies"] = policies


def set_role(role: str) -> None:
    session = st.session_state
    session["role"] = role


def set_id(id: int) -> None:
    session = st.session_state
    session["id"] = id


def generate_id(length: int) -> str:
    return "".join(
        [
            random.choice(
                list(
                    set(string.ascii_uppercase)
                    .union(string.ascii_lowercase)
                    .union(set(string.digits))
                )
            )
            for _ in range(length)
        ]
    )


state = get_authentication()

if state:
    if "generate_id" not in st.session_state:
        st.session_state["generate_id"] = generate_id(12)

    request_list_funds = requests.get(
        url="http://localhost:44444/api/v1/list_funds",
        timeout=8000,
    )

    if request_list_funds.status_code != status.HTTP_200_OK:
        st.error(f"Server Response - {request_list_funds.json().get('detail', '')}")

    raw_funds_list: dict = request_list_funds.json()

    funds_list: list[str] = [
        str(fund.get("fund_name", "NA")) for fund in raw_funds_list
    ]
    fund_selected = st.sidebar.selectbox(
        "Fund Name",
        options=funds_list,
    )

    request_fund_information = requests.get(
        url=f"http://localhost:44444/api/v1/fund?fund_name={fund_selected}",
        timeout=8000,
    )

    if not request_fund_information.json().get("result", {}):
        st.error("No funds have been found")

        st.markdown(
            "<h1 style='text-align: center;'>Welcome!</h1>",
            unsafe_allow_html=True,
        )
    else:
        fund_information: FundInformation = FundInformation(
            **request_fund_information.json().get("result", {})
        )

        administrators: list = (
            ", ".join(
                "<strong>" + str(administrator) + "</strong>"
                for administrator in fund_information.administrators_full_name
            )
            if fund_information.administrators
            else "<strong>-</strong>"
        )
        investors: list[str] = (
            ", ".join(
                "<strong>" + investor + "</strong>"
                for investor in fund_information.investors
            )
            if fund_information.investors
            else "<strong>-</strong>"
        )

        raw_commission_type: str = fund_information.commission_type

        commission_type: str = (
            "<strong>"
            f"{'-' if raw_commission_type is None else raw_commission_type}</strong>"
        )

        raw_commission_value: str = fund_information.commission_value

        commission_value: str = (
            "<strong>"
            f"{'-' if raw_commission_value is None else raw_commission_value}</strong>"
        )

        strategies: list[str] = (
            ", ".join(
                "<strong>" + strategy + "</strong>"
                for strategy in fund_information.strategies
            )
            if fund_information.strategies
            else "<strong>-</strong>"
        )

        st.sidebar.markdown(
            body=f"""
            <p>Investment Firm <strong>{fund_information.investment_firm}</strong></p>
            <p>Fund Name <strong>{fund_information.fund_name}</strong></p>
            <p>Administrator {administrators}</p>
            <p>Investors {investors}</p>
            <p>Strategies {strategies}</p>
            <p>Commission Type {commission_type}</p>
            <p>Commission Value {commission_value}</p>
            """,
            unsafe_allow_html=True,
        )

        if (
            fund_information.raising_funds
            and st.session_state.get("role", UserRole.INVESTOR)
            == UserRole.ADMINISTRATOR
        ):
            if st.sidebar.button(
                "Conclude Fund Raising",
                use_container_width=True,
            ):
                request = requests.post(
                    url="http://localhost:44444/api/v1/conclude_fund_raising",
                    params={"fund_name": fund_information.fund_name},
                    headers={
                        "Content-Type": "application/json",
                    },
                    timeout=8000,
                )

                if request.status_code == status.HTTP_200_OK:
                    st.info(
                        "Fund raising phase has been concluded",
                        icon="ℹ️",
                    )
                    st.rerun()

        fund_raising_subtitle = (
            '<h3 style="text-align: center;">(Fund Raising Phase)</h3>'
        )

        st.markdown(
            f"""
            <h1 style='text-align: center;'>
            {'Welcome!' if not fund_selected else fund_selected}</h1>
            {fund_raising_subtitle if fund_information.raising_funds else ''}
            """,
            unsafe_allow_html=True,
        )

    request_fund_managers = requests.get(
        url="http://localhost:44444/api/v1/list_fund_managers",
        timeout=8000,
    )

    if request_fund_managers.status_code != status.HTTP_200_OK:
        st.error(f"Server Response - {request_fund_managers.json().get('detail', '')}")

    request_fund_managers_available = requests.get(
        url=(
            "http://localhost:44444/api/v1/list_fund_managers?fund_name="
            f"{fund_selected}"
        ),
        timeout=8000,
    )

    if request_fund_managers_available.status_code != status.HTTP_200_OK:
        st.error(
            "Server Response -"
            f" {request_fund_managers_available.json().get('detail', '')}"
        )

    raw_administrators_ids: list = request_fund_managers.json()

    administrators_ids: list[str] = [
        str(fund_manager.get("full_name", "NA"))
        for fund_manager in raw_administrators_ids
    ]

    if st.session_state.get("role", UserRole.INVESTOR) == UserRole.ADMINISTRATOR:
        fund_expander = st.sidebar.expander(label="Fund")
        fund_form = fund_expander.form(key="fund_form", clear_on_submit=True)
        fund_name = fund_form.text_input(
            label="Fund Name",
            placeholder="Fund Name",
            label_visibility="hidden",
        )
        fund_administrators = fund_form.selectbox(
            label="Fund Manager",
            placeholder="Choose Fund Manager",
            options=administrators_ids,
        )
        fund_commission_type = fund_form.selectbox(
            label="Commission Type",
            placeholder="Choose Commission Type",
            options=CommissionTypes.list(),
        )
        fund_commission_value = fund_form.number_input(
            label="Commission Value",
            placeholder="Choose Commission Value",
            value=0,
        )

        if fund_form.form_submit_button(
            "Raise New Fund",
            use_container_width=True,
        ):
            if (
                fund_commission_type == CommissionTypes.PERCENTUAL_TYPE
                and not 0 <= fund_commission_value <= 100
            ):
                st.error(
                    "Please select another value",
                    icon="🚨",
                )

            fund_manager = 0

            for administrator in raw_administrators_ids:
                full_name: str = administrator.get("full_name", "")
                if full_name == fund_administrators:
                    fund_manager = administrator.get("id", 0)

            request = requests.post(
                url="http://localhost:44444/api/v1/fund",
                json={
                    "fund_name": fund_name,
                    "investment_firm": None,
                    "commission_type": fund_commission_type,
                    "commission_value": fund_commission_value,
                    "administrators": [fund_manager],
                },
                headers={
                    "Content-Type": "application/json",
                },
                timeout=8000,
            )

            if request.status_code == status.HTTP_200_OK:
                st.info(
                    "A new fund raising has been started, the Fund is called:"
                    f" '{fund_name}' and the Fund Manager is {fund_administrators}",
                    icon="ℹ️",
                )
                st.rerun()

    if st.session_state.get("role", UserRole.INVESTOR) == UserRole.ADMINISTRATOR:
        investor_expander = st.sidebar.expander(
            label="Investor",
        )
        investor_form = investor_expander.form(
            key="investor_form", clear_on_submit=True
        )
        investor_first_name = investor_form.text_input(
            label="Investor - First Name",
            placeholder="First Name",
            label_visibility="hidden",
        )
        investor_second_name = investor_form.text_input(
            label="Investor - Second Name",
            placeholder="Second Name",
            label_visibility="hidden",
        )
        investor_email_address = investor_form.text_input(
            label="Investor - E-mail Address",
            placeholder="E-mail Address",
            label_visibility="hidden",
        )
        investor_policies = investor_form.multiselect(
            label="Investor - Policies",
            placeholder="Select policies (these are additional)",
            options=InvestorPolicies.list(),
            label_visibility="hidden",
        )
        if investor_form.form_submit_button(
            "Create New Investor",
            use_container_width=True,
        ):
            if (
                not investor_email_address
                or not investor_first_name
                or not investor_second_name
            ):
                st.error(
                    "Unable to create a new investor, not enough information specified",
                    icon="🚨",
                )

            password = "".join(
                [
                    random.choice(
                        list(
                            set(string.ascii_letters)
                            .union(string.ascii_lowercase)
                            .union(string.ascii_uppercase)
                        )
                    )
                    for _ in range(12)
                ]
            )

            request = requests.post(
                url="http://localhost:44444/api/v1/create_investor",
                json={
                    "first_name": investor_first_name,
                    "second_name": investor_second_name,
                    "email_address": investor_email_address,
                    "policies": investor_policies,
                    "password": password,
                },
                headers={
                    "Content-Type": "application/json",
                    "x-token": st.session_state.get("token"),
                },
                timeout=8000,
            )

            if request.status_code == status.HTTP_200_OK:
                st.info(
                    "A new investor account has been created. These are the"
                    f" credentials: E-mail Address {investor_email_address} - Password:"
                    f" {password}",
                    icon="ℹ️",
                )

    if st.session_state.get("role", UserRole.INVESTOR) == UserRole.ADMINISTRATOR:
        administrator_expander = st.sidebar.expander(label="Administrator")
        administrator_form = administrator_expander.form(
            key="administration_form", clear_on_submit=True
        )
        administrator_form.title("Create New Administrator")
        administrator_first_name = administrator_form.text_input(
            label="Administrator First Name",
            placeholder="First Name",
            label_visibility="hidden",
        )
        administrator_second_name = administrator_form.text_input(
            label="Administrator Second Name",
            placeholder="Second Name",
            label_visibility="hidden",
        )
        administrator_email_address = administrator_form.text_input(
            label="Adminitrator E-mail Address",
            placeholder="E-mail Address",
            label_visibility="hidden",
        )
        administrator_policies = administrator_form.multiselect(
            label="Administrator Policies",
            placeholder="Select policies (these are additional)",
            options=AdministratorPolicies.list(),
            label_visibility="hidden",
        )
        if administrator_form.form_submit_button(
            "Create New Admininistrator",
            use_container_width=True,
        ):
            eligible = False
            if (
                not administrator_email_address
                or not administrator_first_name
                or not administrator_second_name
            ):
                st.error(
                    "Unable to create a new administrator, not enough information"
                    " specified",
                    icon="🚨",
                )
            else:
                eligible = True

            if not administrator_policies:
                st.warning(
                    "No policies have been specified",
                    icon="⚠️",
                )

            if eligible:
                password = generate_id(10)

                request = requests.post(
                    url="http://localhost:44444/api/v1/create_administrator",
                    json={
                        "first_name": administrator_first_name,
                        "second_name": administrator_second_name,
                        "email_address": administrator_email_address,
                        "policies": administrator_policies,
                        "password": password,
                    },
                    headers={
                        "Content-Type": "application/json",
                        "x-token": st.session_state.get("token"),
                    },
                    timeout=8000,
                )

                if request.status_code == status.HTTP_200_OK:
                    st.info(
                        "A new administrator account has been created. These are the"
                        f" credentials: E-mail Address {administrator_email_address} -"
                        f" Password: {password}",
                        icon="ℹ️",
                    )

        administrator_add_form = administrator_expander.form(
            key="administration_add_form", clear_on_submit=True
        )
        administrator_add_form.title("Add Administrator")
        administrator_add_account = administrator_add_form.selectbox(
            label="Administrator Selection",
            options=request_fund_managers_available.json().keys(),
            placeholder="List of available administrators",
        )
        if administrator_add_form.form_submit_button(
            "Add Admininistrator",
            use_container_width=True,
        ):
            request = requests.post(
                url="http://localhost:44444/api/v1/add_administrator",
                json={
                    "administrator_id": request_fund_managers_available.json().get(
                        administrator_add_account,
                        None,
                    ),
                    "fund": fund_selected,
                },
                headers={
                    "Content-Type": "application/json",
                    "x-token": st.session_state.get("token"),
                },
                timeout=8000,
            )

            if request.status_code == status.HTTP_200_OK:
                st.info(
                    "Administrator correctly added",
                    icon="ℹ️",
                )

    if st.session_state.get("role", UserRole.INVESTOR) == UserRole.ADMINISTRATOR:
        ats_expander = st.sidebar.expander(label="Algorithmic Trading Strategy")
        ats_form = ats_expander.form(key="ats_form")
        ats_form.markdown(
            "<p>Generated ID</p>"
            f"<p><strong>{st.session_state.get('generate_id', '-')}</strong></p>",
            unsafe_allow_html=True,
        )

        if ats_form.form_submit_button(
            "Update ID",
            use_container_width=True,
        ):
            st.session_state["generate_id"] = generate_id(16)

        strategy_name = ats_form.text_input(
            label="Strategy Name",
            placeholder="Strategy Name",
            label_visibility="hidden",
        )

        strategy_category = ats_form.selectbox(
            label="Category",
            placeholder="Select Category",
            label_visibility="hidden",
            options=CategoriesATS.list(),
        )

        if ats_form.form_submit_button(
            "Add ATS",
            use_container_width=True,
        ):
            request = requests.post(
                url="http://localhost:44444/api/v1/create_ats",
                json={
                    "id": st.session_state.get("generate_id", 0),
                    "administrator_id": st.session_state.get("", 0),
                    "fund_name": fund_selected,
                    "category": strategy_category,
                    "name": strategy_name,
                },
                headers={
                    "Content-Type": "application/json",
                    "x-token": st.session_state.get("token"),
                },
                timeout=8000,
            )

            if request.status_code == status.HTTP_200_OK:
                results = request.json()
            else:
                st.error(
                    "Unable to correctly deposit funds",
                    icon="🚨",
                )

    if (
        st.session_state.get("role", UserRole.INVESTOR) == UserRole.ADMINISTRATOR
        and not fund_information.raising_funds
    ):
        open_position = st.sidebar.expander(label="Open Position")
        open_position_form = open_position.form(
            key="Open Position Form",
            clear_on_submit=True,
        )
        ticker_selection = open_position_form.selectbox(
            label="Tickers Selection",
            options=get_trading_tickers(),
            placeholder="Select Financial Instrument",
            label_visibility="hidden",
        )
        operation_selection = open_position_form.selectbox(
            label="Operation",
            options=Position.list(),
            placeholder="Select Position",
            label_visibility="hidden",
        )
        if open_position_form.form_submit_button(
            "Open Position", use_container_width=True
        ):
            request = requests.post(
                url="http://localhost:44444/api/v1/trading/position",
                json={
                    "fund_name": fund_selected,
                    "market_order": "market_order",
                    "operation": operation_selection,
                    "ticker": ticker_selection,
                },
                headers={
                    "Content-Type": "application/json",
                },
                timeout=8000,
            )

            if request.status_code == status.HTTP_200_OK:
                st.info(
                    body="Position correctly opened",
                    icon="ℹ️",
                )
            else:
                st.error(
                    body="Unable to correctly open the position",
                    icon="🚨",
                )

    if st.sidebar.button(
        "Backtesting Platform",
        use_container_width=True,
    ):
        open_page(f"http://localhost:8502/?token={st.session_state.get('token', '-')}")

    if (
        st.session_state.get("role", UserRole.INVESTOR) == UserRole.INVESTOR
        and fund_information.raising_funds
    ):
        deposit_expander = st.sidebar.expander(label="Deposit Fund")
        deposit: float = deposit_expander.number_input(
            label="Deposit fund",
            placeholder="Euro Currency",
            label_visibility="hidden",
        )

        if deposit_expander.button("Deposit Fund"):
            request = requests.post(
                url="http://localhost:44444/api/v1/deposit_fund",
                json={
                    "investor_id": st.session_state.get("id", 0),
                    "deposit": deposit,
                    "fund_name": fund_selected,
                },
                headers={
                    "Content-Type": "application/json",
                    "x-token": st.session_state.get("token"),
                },
                timeout=8000,
            )

            if request.status_code == status.HTTP_200_OK:
                if not request.json().get("result", False):
                    st.error(
                        "Unable to correctly add funds",
                        icon="🚨",
                    )
                else:
                    st.info(
                        "Fund correctly deposited",
                        icon="ℹ️",
                    )
            else:
                st.error(
                    "Unable to correctly deposit funds",
                    icon="🚨",
                )

    request = requests.post(
        url="http://localhost:44444/api/v1/returns",
        json={
            "fund_name": fund_selected,
            "date_from": datetime.strftime(
                datetime.today() - timedelta(days=30), "%d/%m/%Y"
            ),
            "date_to": datetime.strftime(datetime.today(), "%d/%m/%Y"),
        },
        headers={
            "Content-Type": "application/json",
            "x-token": st.session_state.get("token"),
        },
        timeout=8000,
    )

    if request.status_code != status.HTTP_200_OK:
        st.error("Unable to fetch returns from the selected fund")
    else:
        st.title("Chart Returns")

        chart_data = pd.DataFrame(
            request.json().get("raw_returns", {}).items(),
            columns=["Dates", "Returns"],
        )
        copy_data = chart_data.copy()
        chart_data = chart_data.rename(columns={"Dates": "index"}).set_index("index")

        copy_data.index = copy_data["Dates"]
        copy_data.drop(columns=["Dates"], inplace=True)
        copy_data["Returns"] = copy_data["Returns"].apply(
            lambda x: "{:.2f} €".format((x))
        )

        initial_capital = request.json().get(
            "initial_capital",
            "-",
        )
        cumulative_commissions_fund = request.json().get(
            "cumulative_commissions_fund",
            "-",
        )
        cumulative_commissions_broker = request.json().get(
            "cumulative_commissions_broker",
            "-",
        )
        absolute_returns = request.json().get(
            "absolute_returns",
            "-",
        )

        st.line_chart(
            chart_data,
            color=["#FF0000"],
        )

        st.title("Capitals Table")
        st.table(copy_data)

        st.title("Fund Returns")

        match st.session_state.get("role"):
            case UserRole.INVESTOR:
                st.markdown(
                    f"""
                    <p>Initial Capital <strong>{initial_capital}</strong></p>
                    <p>Capital Gain <strong>{absolute_returns}</strong></p>
                    """,
                    unsafe_allow_html=True,
                )
            case UserRole.ADMINISTRATOR:
                st.markdown(
                    f"""
                    <p>Initial Capital <strong>{initial_capital}</strong></p>
                    <p>Cumululative Commission Fund <strong>
                     {cumulative_commissions_fund}</strong></p>
                    <p>Capital Gain <strong>{absolute_returns}</strong></p>
                    """,
                    unsafe_allow_html=True,
                )
            case _:
                ...


else:
    st.markdown(
        "<h1 style='text-align: center;'>Inkosi Login</h1>",
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        The current page let both investor and admistrator to *view* and *manage*
        __funds__.
        <br>
        <br>
        It is important to highlight the different authentication methods available for
        _Administrator_ and _Investors_.
        <br>
        <br>
        In particular, for the first, the __only authentication method__ *allowed*
        accept the respective Administrator. Whereas, the __Investor authentication
        method__ refers to the respective *E-Mail Address*.
        """,
        unsafe_allow_html=True,
    )

    username = st.text_input(
        label="E-Mail Address",
        placeholder="E-Mail Address / Administrator ID",
        label_visibility="collapsed",
    )
    password = st.text_input(
        label="Password",
        placeholder="Password",
        type="password",
        label_visibility="collapsed",
    )

    if st.button("Login", use_container_width=True):
        r = requests.get(
            url="http://localhost:44444/api/v1/login",
            json={
                "email_address": username,
                "password": password,
            },
            headers={
                "Content-Type": "application/json",
            },
            timeout=8000,
        )

        if r.status_code == status.HTTP_200_OK:
            st.session_state.token = r.json().get("token", "")
            st.session_state.policies = r.json().get("policies", [])
            st.session_state.role = r.json().get("role", "")
            st.session_state.id = r.json().get("id", 0)

            set_policies(st.session_state.policies)
            set_token(st.session_state.token)
            set_role(st.session_state.role)
            set_id(st.session_state.id)

            st.rerun()
        else:
            st.error(f"Server Response - {r.json().get('detail', '')}")
