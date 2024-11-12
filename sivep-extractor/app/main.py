import requests

def salvar_html(url, nome_arquivo='pagina.html'):
    try:
        # Fazer a requisição para obter o conteúdo HTML
        resposta = requests.get(url)
        resposta.raise_for_status()  # Verifica se houve algum erro na requisição

        # Salvar o conteúdo HTML em um arquivo
        with open(nome_arquivo, 'w', encoding='utf-8') as arquivo:
            arquivo.write(resposta.text)

        print(f'O HTML foi salvo em "{nome_arquivo}".')

    except requests.exceptions.RequestException as e:
        print(f'Ocorreu um erro ao obter o HTML: {e}')

# Exemplo de uso
# class="resource-item"
#   href <a> data-format="csv"

url = 'https://opendatasus.saude.gov.br/dataset/srag-2021-a-2024'  # Substitua pela URL desejada
salvar_html(url, 'pagina.html')
print("oi oi oi oi")
print("oi oi oi oi")
print("oi oi oi oi")
print("oi oi oi oi")
