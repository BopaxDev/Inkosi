from datetime import date

import numpy as np
import pandas as pd
from numpy.typing import NDArray

from inkosi.backtest.operation.quote import Quote
from inkosi.backtest.operation.schemas import AvailableRawColumns, SamplingMethods


class Asset:
    """
    Represents a financial asset and provides methods for data analysis and
    visualization.

    Attributes:
        asset_name (str): The name of the financial asset.
        period (str): The time period for historical data. Default is "1y" (1 year).
        time_frame (str): The time frame for data intervals. Default is "1d" (1 day).
        quote (Quote): An instance of the Quote class for downloading financial
            instrument quotes.
        result (dict): The result of downloading financial instrument quotes.
    """

    def __init__(
        self,
        asset_name: str,
        period: str = "1y",
        time_frame: str = "1d",
        start: date | None = None,
        end: date | None = None,
    ):
        """
        Initializes an Asset instance.

        Parameters:
            asset_name (str): The name of the financial asset.
            period (str, default "1y"): The time period for historical data.
                Default is "1y" (1 year).
            time_frame (str, default "1d"): The time frame for data intervals.
                Default is "1d" (1 day).
            start (date, optional, default None): The start date for historical data.
                Default is None.
            end (date, optional, default None): The end date for historical data.
                Default is None.
        """

        self.asset_name = asset_name
        self.period = period
        self.time_frame = time_frame

        self.quote = Quote(time_frame=time_frame)
        self.result = self.quote.download_quote(
            self.asset_name,
            start=start,
            end=end,
        )

    def sampling(
        self,
        sampling_method: SamplingMethods,
        steps_forward: int,
        column: str = AvailableRawColumns.CLOSE_PRICE,
        samples: int = 1,
    ) -> NDArray | None:
        """
        Generate samples based on historical data.

        Parameters:
            sampling_method (SamplingMethods): The method used for generating samples.
            steps_forward (int): The number of steps forward in time for each sample.
            column (str, default "Close Price"): The column of historical data to use
                for sampling. Default is "Close Price".
            samples (int, default 1): The number of samples to generate. Default is 1.
        """

        if not 1 < steps_forward < 255 or not isinstance(steps_forward, int):
            return None

        if not 1 <= samples < 10000 or not isinstance(samples, int):
            return None

        prices = self.result.get(column, np.array([0]))
        last_prices = np.ones(shape=(samples, 1)) * prices[-1]

        match sampling_method:
            case SamplingMethods.NORMAL_DISTRIBUTION:
                sampling = np.random.normal(
                    loc=0,
                    scale=np.std(
                        self.close_prices(),
                    ),
                    size=(samples, steps_forward - 1),
                )

                cum_raw_last_prices = np.hstack((last_prices, sampling))
                cum_prices = np.cumsum(cum_raw_last_prices, axis=1)

                return self.plotting(
                    column,
                    np.hstack(
                        (
                            np.repeat(
                                np.reshape(prices, (prices.shape[0], 1)),
                                repeats=samples,
                                axis=1,
                            ).T,
                            cum_prices,
                        )
                    ),
                )
            case SamplingMethods.LAPLACE_DISTRIBUTION:
                sampling = np.random.laplace(
                    loc=0,
                    scale=np.std(
                        self.close_prices(),
                    ),
                    size=(samples, steps_forward - 1),
                )

                cum_raw_last_prices = np.hstack((last_prices, sampling))
                cum_prices = np.cumsum(cum_raw_last_prices, axis=1)

                return self.plotting(
                    column,
                    np.hstack(
                        (
                            np.repeat(
                                np.reshape(prices, (prices.shape[0], 1)),
                                repeats=samples,
                                axis=1,
                            ).T,
                            cum_prices,
                        )
                    ),
                )
            case SamplingMethods.UNIFORM_DISTRIBUTION:
                sampling = np.random.uniform(
                    low=0,
                    high=np.max(prices) - np.min(prices),
                    size=(samples, steps_forward - 1),
                )
                cum_raw_last_prices = np.hstack((last_prices, sampling))
                cum_prices = np.cumsum(cum_raw_last_prices, axis=1)

                return self.plotting(
                    column,
                    np.hstack(
                        (
                            np.repeat(
                                np.reshape(prices, (prices.shape[0], 1)),
                                repeats=samples,
                                axis=1,
                            ).T,
                            cum_prices,
                        )
                    ),
                )
            case _:
                return None

    def dates(self) -> NDArray:
        """
        Get the dates associated with the historical data.

        Returns:
            NDArray: An array of dates.
        """

        return self.result.get(AvailableRawColumns.DATES, [])

    def open_prices(self) -> NDArray:
        """
        Get the open prices from the historical data.

        Returns:
            NDArray: An array of open prices.
        """
        return self.result.get(AvailableRawColumns.OPEN_PRICE, [])

    def high_prices(self) -> NDArray:
        """
        Get the high prices from the historical data.

        Returns:
            NDArray: An array of high prices.
        """
        return self.result.get(AvailableRawColumns.HIGH_PRICE, [])

    def low_prices(self) -> NDArray:
        """
        Get the low prices from the historical data.

        Returns:
            NDArray: An array of low prices.
        """
        return self.result.get(AvailableRawColumns.LOW_PRICE, [])

    def close_prices(self) -> NDArray:
        """
        Get the close prices from the historical data.

        Returns:
            NDArray: An array of close prices.
        """
        return self.result.get(AvailableRawColumns.CLOSE_PRICE, [])

    def returns(self) -> NDArray:
        """
        Get the returns from the historical data.

        Returns:
            NDArray: An array of returns.
        """
        return self.result.get(AvailableRawColumns.RETURNS, [])

    def return_distribution(self) -> NDArray:
        """
        Get the sorted returns from the historical data.

        Returns:
            NDArray: An array of sorted returns.
        """
        return np.sort(self.result.get(AvailableRawColumns.RETURNS, []))

    def data_frame(self) -> pd.DataFrame:
        """
        Convert historical data to a pandas DataFrame.

        Returns:
            pd.DataFrame: A DataFrame containing historical data.
        """
        return pd.DataFrame(self.result)

    def plotting(
        self,
        column: AvailableRawColumns = AvailableRawColumns.CLOSE_PRICE,
        sampling: NDArray | None = None,
    ) -> tuple:
        """
        Get data for plotting.

        Parameters:
            column (AvailableRawColumns. default "Close Price"): The column of
                historical data to plot. Default is "Close Price".
            sampling (NDArray, optional, default None): An array of samples for
                plotting. Default is None.

        Returns:
            (tuple): A tuple containing data for plotting.
        """
        return (
            self.dates() if sampling is None else np.arange(0, sampling.shape[1]),
            self.result.get(column).reshape(1, self.result.get(column).shape[0])
            if sampling is None
            else sampling,
        )
