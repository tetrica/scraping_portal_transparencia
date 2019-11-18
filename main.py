import argparse
import csv
import requests
from bs4 import BeautifulSoup

parser = argparse.ArgumentParser()
parser.add_argument("cnpj", help="cnpj da empresa que se deseja obter os sócios")
parser.add_argument("--out", help="nome do arquivo que conterá o resultado")
args = parser.parse_args()

def extract_data(page: requests.Response, column_cnpj: str = '') -> list:
    if soup := BeautifulSoup(page.text, 'html.parser').find('div', class_='box-tabela-completa inner').find_all('td'):
        return (
            [
                column_cnpj,
                *[
                    f := soup[i].text.split(' - '),
                    f[0].strip(),
                    f[1].replace("CPF:", "").replace("CNPJ:", "").strip()
                ][1:], 
                soup[i+1].text.strip()
            ]
            for i in range(0, len(soup), 2)
        )

    return []

if __name__ == "__main__":
    URI = lambda cnpj: f'http://www.portaltransparencia.gov.br/busca/pessoa-juridica/{cnpj}'
    out = args.out if args.out else "out.csv"

    with open(out, 'w') as file:
        page: requests.Response = requests.get(URI(args.cnpj))

        writer = csv.writer(file)
        writer.writerows(extract_data(page, args.cnpj))
