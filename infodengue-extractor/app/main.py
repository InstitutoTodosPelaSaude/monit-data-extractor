
import pandas as pd
from datetime import datetime, timedelta
from epiweeks import Week, Year

from itertools import product

GEOCODE_TO_UF = {
    1200401: "AC",
    2704302: "AL",
    1302603: "AM",
    1600303: "AP",
    2927408: "BA",
    2304400: "CE",
    5300108: "DF",
    3205309: "ES",
    5208707: "GO",
    2111300: "MA",
    5103403: "MT",
    5002704: "MS",
    3106200: "MG",
    1501402: "PA",
    2507507: "PB",
    4115200: "PR",
    2611606: "PE",
    2207702: "PI",
    3304557: "RJ",
    2408102: "RN",
    4314902: "RS",
    1100023: "RO",
    1400100: "RR",
    4205407: "SC",
    3550308: "SP",
    2800308: "SE",
    1721000: "TO"
}

UF_TO_NAME = {
    "AC": "Acre",              "AL": "Alagoas",              "AM": "Amazonas",
    "AP": "Amapá",             "BA": "Bahia",                "CE": "Ceará",
    "DF": "Distrito Federal",  "ES": "Espírito Santo",       "GO": "Goiás",
    "MA": "Maranhão",          "MT": "Mato Grosso",          "MS": "Mato Grosso do Sul",   
    "MG": "Minas Gerais",      "PA": "Pará",                 "PB": "Paraíba",
    "PR": "Paraná",            "PE": "Pernambuco",           "PI": "Piauí",
    "RJ": "Rio de Janeiro",    "RN": "Rio Grande do Norte",  "RS": "Rio Grande do Sul",
    "RO": "Rondônia",          "RR": "Roraima",              "SC": "Santa Catarina",
    "SP": "São Paulo",         "SE": "Sergipe",              "TO": "Tocantins"
}

UF_TO_REGION = {
    "AC": "Norte", "AP": "Norte", "AM": "Norte", "PA": "Norte", "RO": "Norte", "RR": "Norte", "TO": "Norte",
    "AL": "Nordeste", "BA": "Nordeste", "CE": "Nordeste", "MA": "Nordeste", "PB": "Nordeste",
    "PE": "Nordeste", "PI": "Nordeste", "RN": "Nordeste", "SE": "Nordeste",
    "DF": "Centro-Oeste", "GO": "Centro-Oeste", "MT": "Centro-Oeste", "MS": "Centro-Oeste",
    "ES": "Sudeste", "MG": "Sudeste", "RJ": "Sudeste", "SP": "Sudeste",
    "PR": "Sul", "RS": "Sul", "SC": "Sul"
}

BASE_URL = "https://info.dengue.mat.br/api/alertcity?geocode=2408102&disease=dengue&format=csv&ew_start=1&ew_end=2&ey_start=2024&ey_end=2024"

def get_data_infodengue(geocode, disease, ew_start, ew_end, ey_start, ey_end):
    
    columns = ['data_iniSE', 'SE', 'casos_est', 'casos_est_min', 'casos_est_max', 'casos']
    url = (
        f"{BASE_URL}?geocode={geocode}&disease={disease}&format=csv"
        f"&ew_start={ew_start}&ew_end={ew_end}&ey_start={ey_start}&ey_end={ey_end}"
    )
    
    try:
        infodengue_df = pd.read_csv(url)
        infodengue_df = infodengue_df[columns]
        return infodengue_df
    except Exception as e:
        # Em caso de erro, exibe uma mensagem de erro
        print(f"Erro ao obter ou processar os dados: {e}")
        return None

def get_week_end_date(date_str):
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    end_date_obj = date_obj + timedelta(days=6)
    return end_date_obj.strftime('%Y-%m-%d')

def get_current_epiweek():
    current_date = datetime.now().date()
    current_year = int(datetime.now().year)
    all_epiweeks = list(range(1, 53+1))

    for epiweek_number in all_epiweeks:
        epiweek = Week(current_year, epiweek_number)
        if current_date >= epiweek.startdate() and current_date <= epiweek.enddate():
            return epiweek_number


if __name__ == "__main__":

    current_year = int(datetime.now().year)
    current_epiweek = get_current_epiweek()
    diseases = ["dengue"]

    all_epiweeks = list(range(1, 53+1))
    all_years = list(range(2022, current_year+1))

    for geocode, uf in GEOCODE_TO_UF.items():
        infodengue_df = get_data_infodengue(geocode, "dengue", 1, 2, 2024, 2024)
        infodengue_df['state_code'] = uf
        infodengue_df['state'] = infodengue_df['state_code'].map(UF_TO_NAME)
        infodengue_df['region'] = infodengue_df['state_code'].map(UF_TO_REGION)
        infodengue_df['data_fimSE'] = infodengue_df['data_iniSE'].apply(get_week_end_date)
        
        print(infodengue_df)