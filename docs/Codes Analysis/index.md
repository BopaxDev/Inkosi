## __Codes Analysis__

### _Introduction_

Through this _section_ will be able to __dive in__ most of the _documentation_ related to the _current version_ __Inkosi__.
<br><br>
I kindly suggest you to have a _direct look_ to the code since, some part of the code are __not available yet__.
<br>

### _Authentication_

A __well-structured authentication__ _system_ has been implemented in the platform.
<br>
In particular, 3 particular __types of security__ _layers_ have been developed:

- __IP Address Restriction__
- __Access Token__
- __Policies__
    - __Investors__
        - INVESTOR_DASHBOARD_VISUALISATION
            - It allows investor to visualise the Dashboard
        - INVESTOR_SAMPLING_SCENARIOS_
            - It allows investor to sample new scenarios
        - INVESTOR_BACKTEST_ALL
            - It allows investor to perform backtests
    - __Administrators__
        - ADMINISTRATOR_IFM_FULL_ACCESS
            - It allows administrator to have full access to the Investment Firm Management
        - ADMINISTRATOR_FM_FULL_ACCESS
            - It allows administrator to have full access to the Fund Management
        - ADMINISTRATOR_PM_FULL_ACCESS
            - It allows administrator to have relative access to the Fund Managemen, being it a Portfolio Management


### _Modules_

- API
- App
- Backtest
- Database
- Log
- Mailing _(Under development)_
- Portfolio _(Under development)_
- Scheduler _(Under development)_
- Utils
- Web

