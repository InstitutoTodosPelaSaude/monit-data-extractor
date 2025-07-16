from pydantic import BaseModel
from datetime import date
from typing import Optional

class SabinData(BaseModel):

    OS: str
    CodigoPosto: str
    Estado: str
    Municipio: str
    DataAtendimento: date
    DataNascimento: date
    Sexo: str
    Descricao: str
    Parametro: str
    Resultado: str
    DataAssinatura: date

class SabinDataList(BaseModel):
    data: list[SabinData]