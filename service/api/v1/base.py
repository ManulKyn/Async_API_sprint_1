from typing import Optional

from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    query: Optional[dict] = Field(title='тело запроса для эластика', default={"match_all": {}})
    sort: Optional[dict] = Field(title='Параметры сортировки')
    page_size: Optional[int] = Field(title='размер страницы поиска', gt=1, default=5000, alias='size')
    page_number: Optional[int] = Field(title='страница поиска', gt=0, default=1, alias='from')
