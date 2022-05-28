import datetime
from typing import Tuple, Union

from .strategy import (FilmWorkTableStrategyFabric, GenreTableStrategyFabric,
                       GenreTableStrategyGenreIndexFabric,
                       PersonTableStrategyFabric,
                       PersonTableStrategyPersonIndexFabric)


class Manager:
    def __init__(self):
        self.chain = (
            FilmWorkTableStrategyFabric,
            GenreTableStrategyFabric,
            PersonTableStrategyFabric,
            GenreTableStrategyGenreIndexFabric,
            PersonTableStrategyPersonIndexFabric
        )
        self.strategy_index = 0
        self._strategy = self.chain[self.strategy_index]()

    @property
    def table(self) -> Union[
        PersonTableStrategyFabric,
        FilmWorkTableStrategyFabric,
        GenreTableStrategyFabric,
        PersonTableStrategyPersonIndexFabric
    ]:
        """Логика процесса для различных таблиц БД"""
        return self._strategy

    @table.setter
    def table(
            self,
            value: Union[
                PersonTableStrategyFabric,
                FilmWorkTableStrategyFabric,
                GenreTableStrategyFabric,
                PersonTableStrategyPersonIndexFabric
            ]
    ):
        self._strategy = value

    def switch_table(self):
        """Переключение таблицы и запрашиваемого временного промежутка"""
        self.strategy_index = (self.strategy_index + 1)

        if self.strategy_index == len(self.chain):
            self.strategy_index %= len(self.chain)
            is_done_time = True
        else:
            is_done_time = False

        self.table = self.chain[self.strategy_index]()
        return is_done_time

    def start(
            self,
            reference_date_start: datetime.datetime,
            reference_date_end: datetime.datetime,
            query_limit: int,
            offset: int
    ) -> Tuple[bool, bool]:
        """Процесс получения данных из БД, обработки и загрузки в Elasticsearch"""
        qs = self.table.extract(
            reference_date_start=reference_date_start,
            reference_date_end=reference_date_end,
            query_limit=query_limit,
            offset=offset
        )

        if not qs:
            is_done_time = self.switch_table()
            is_done_table = True
        else:
            result = self.table.transform(qs)
            self.table.load(qs=result)
            is_done_time = False
            is_done_table = False

        return is_done_table, is_done_time
