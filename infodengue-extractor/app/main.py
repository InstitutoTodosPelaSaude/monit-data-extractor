
import pandas as pd
from datetime import datetime, timedelta
from epiweeks import Week, Year

import os
import io

from itertools import product

# Save and handle logs
from log import ManagerInterface

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

BASE_URL = "https://info.dengue.mat.br/api/alertcity"

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

    API_ENPOINT = os.getenv("MANAGER_ENDPOINT")
    APP_NAME    = 'infodengue'

    if API_ENPOINT is None:
        print(f"ERROR! API_ENPOINT is None")
        exit(1)

    current_year = int(datetime.now().year)
    current_epiweek = get_current_epiweek()
    diseases = ["dengue", "chikungunya", "zika"]

    all_epiweeks = list(range(1, 53+1))
    all_years = list(range(2022, current_year+1))
    

    # ===================================
    # Logger configuration
    # ===================================
    manager_interface = ManagerInterface(APP_NAME, API_ENPOINT )
    logger = manager_interface.logger
    

    # Application
    # ==================================
    NUMBER_OF_PREVIOUS_EPIWEEKS_TO_COLLECT = 8
    all_epiweeks = [current_epiweek-i for i in range(0, NUMBER_OF_PREVIOUS_EPIWEEKS_TO_COLLECT+1)]
    all_years    = [current_year]
    all_ufs_dataframes = []
    for disease in diseases:
        logger.info(f"Running for {disease}")
        for year, epiweek in product(all_years, all_epiweeks):
            for geocode, uf in GEOCODE_TO_UF.items():
                logger.info(f"Requesting {disease} SE{epiweek:02d} - {year} {uf}")
                infodengue_df = get_data_infodengue(geocode, disease, epiweek, epiweek, year, year)
                
                if infodengue_df is None:
                    logger.warning(f"API returned 'None' {disease} SE{epiweek:02d} - {year} {uf}")
                    continue

                if infodengue_df.shape[0] < 1:
                    logger.warning(f"No data found for {disease} SE{epiweek:02d} - {year} {uf}")
                    continue
            
                infodengue_df['disease'] = disease
                infodengue_df['state_code'] = uf
                infodengue_df['state'] = infodengue_df['state_code'].map(UF_TO_NAME)
                infodengue_df['region'] = infodengue_df['state_code'].map(UF_TO_REGION)
                infodengue_df['data_fimSE'] = infodengue_df['data_iniSE'].apply(get_week_end_date)

                all_ufs_dataframes.append(infodengue_df)
                
            if len(all_ufs_dataframes) == 0:
                logger.warning(f"No data found for {disease} SE{epiweek:02d} - {year}")
                all_ufs_dataframes = []
                continue
            
            all_ufs_infodengue_df = pd.concat(all_ufs_dataframes)
            all_ufs_dataframes = []
            filename = f"INFODENGUE_{year}_SE_{epiweek:02d}_{disease}.csv"
            
            logger.info(f"Finished extracting data for {disease} SE{epiweek:02d} - {year}")
            logger.info(f"Saving file {filename}...")

            buffer = io.BytesIO()
            all_ufs_infodengue_df.to_csv(buffer, index=False)
            buffer.seek(0)  # Move to the beginning of the buffer

            manager_interface.upload_file(
                organization="InfoDengue",
                project="arbo",
                file_content=buffer,
                file_name=filename
            )

            logger.info(f"Finished uploading file {filename}!")

    logger.info("Finished extracting all data")
    manager_interface.close_session()

    logger.info("Finished pipeline.")

        
