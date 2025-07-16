import json

def format_sabin_data_json(sabin_data):
    """
    Format Sabin data to JSON format.

    Args:
        sabin_data (SabinDataList): The data to be formatted.

    Returns:
        str: The formatted JSON string.
    """

    # Transform SabinDataList to a list of dictionaries
    data_list = [data.dict() for data in sabin_data.data]

    # DataAtendimento, DataNascimento, DataAssinatura format dd/mm/yyyy
    for data in data_list:
        data['DataAtendimento'] = data['DataAtendimento'].strftime('%d/%m/%Y')
        data['DataNascimento'] = data['DataNascimento'].strftime('%d/%m/%Y')
        data['DataAssinatura'] = data['DataAssinatura'].strftime('%d/%m/%Y')

    return data_list

def save_sabin_data_one_json_file_by_date(sabin_data):
    """
    Save the Sabin data to a JSON file, one file per date.

    Args:
        sabin_data (list of dict): The data to be saved by date.
    """

    # Retrieve all dates from the sabin data
    all_dates = set(data['DataAtendimento'] for data in sabin_data)

    for date in all_dates:

        # Filter data for the specific date
        date_data = [
            data
            for data in sabin_data
            if data['DataAtendimento'] == date
        ]

        # Save JSON in /data/sabin/sabin_<date>.json
        file_path = f"/data/sabin/sabin_{date.replace('/', '-')}.json"
        with open(file_path, "w") as file:
            file.write( json.dumps(date_data, ensure_ascii=False) )

def save_sabin_data(sabin_data):
    """
    Save the Sabin data to the database.

    Args:
        sabin_data (SabinDataList): The data to be saved.
    """

    # Transform SabinDataList to a list of dictionaries
    data_list = format_sabin_data_json(sabin_data)

    # Save one JSON file per date
    save_sabin_data_one_json_file_by_date(data_list)