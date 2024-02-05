import pandas as pd
from numpy.typing import NDArray

from inkosi.backtest.operation.asset import Asset
from inkosi.backtest.operation.models import SourceType
from inkosi.database.postgresql.database import PostgreSQLInstance


class Dataset:
    """
    A class for loading datasets from various sources.

    Parameters:
        source (str or Asset): The data source, which can be a string representing a SQL
            table, a file path for CSV, HDF, or Parquet,
            or an Asset object for custom data.
        source_type (SourceType): The type of the data source.
        **kwargs: Additional keyword arguments passed to the specific data loading
            function.

    Attributes:
        postgres_instance (PostgreSQLInstance): An instance of PostgreSQLInstance used
            for SQL data loading.
        dataset (pd.DataFrame): The loaded dataset as a Pandas DataFrame.
        np_dataset (NDArray): The dataset converted to a NumPy array.

    Methods:
        get_dataset(): Returns the NumPy array representation of the loaded dataset.
    """

    def __init__(
        self,
        source: str | Asset,
        source_type: SourceType,
        **kwargs,
    ) -> None:
        """
        Constructor for the Dataset class.

        Parameters:
            source (str | Asset): The data source, which can be a string representing a
                SQL table, a file path for CSV, HDF, or Parquet, or an Asset object for
                custom data.
            source_type (SourceType): The type of the data source.
            **kwargs: Additional keyword arguments passed to the specific data loading
                function.
        """

        self.postgres_instance = PostgreSQLInstance()

        if isinstance(source, str) or isinstance(source, Asset):
            self.dataset: None = None

        match source_type:
            case SourceType.SQL:
                with self.postgres_instance.engine.connect() as conn, conn.begin():
                    self.dataset: pd.DataFrame = pd.read_sql_table(
                        table_name=source,
                        con=conn,
                        **kwargs,
                    )
            case SourceType.CSV:
                self.dataset: pd.DataFrame = pd.read_csv(
                    filepath_or_buffer=source,
                    **kwargs,
                )
            case SourceType.HDF:
                self.dataset: pd.DataFrame = pd.read_hdf(
                    path_or_buf=source,
                    **kwargs,
                )
            case SourceType.PARQUET:
                self.dataset: pd.DataFrame = pd.read_parquet(
                    path=source,
                    **kwargs,
                )
            case SourceType.ASSET:
                self.dataset: pd.DataFrame = pd.DataFrame(
                    {
                        0: source.dates(),
                        1: source.close_prices(),
                        2: source.open_prices(),
                    }
                )

        self.np_dataset: NDArray = self.dataset.to_numpy()

    def get_dataset(
        self,
    ) -> NDArray | None:
        """
        Returns the NumPy array representation of the loaded dataset.

        Returns:
            (NDArray | None): The NumPy array representing the dataset or None if the
                dataset is not loaded.
        """

        return self.np_dataset
