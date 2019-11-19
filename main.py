import argparse
import csv
import glob
import requests
import os
from typing import List
from bs4 import BeautifulSoup

parser = argparse.ArgumentParser()
parser.add_argument("--out", help="nome do arquivo que conterá o resultado")
args = parser.parse_args()

def extract_data(page: requests.Response, column_cnpj: str = '') -> list:
    soup = BeautifulSoup(page.text, 'html.parser').find('div', class_='box-tabela-completa inner')
    if not soup: return []

    soup = soup.find_all('td')
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

if __name__ == "__main__":
    URI = lambda cnpj: f'http://www.portaltransparencia.gov.br/busca/pessoa-juridica/{cnpj}'

    files_paths: List[str] = glob.glob("./csv/*/*.csv")
    out: str = args.out if args.out else "out.csv"

    with open(out, 'w') as file_out: #TODO(Fábio): 'file_out' é um péssimo nome
        writer = csv.writer(file_out)

        for file_path in files_paths:
            with open(file_path, 'r', encoding="ISO-8859-1") as file: #TODO(Fábio): 'file' tb é um péssimo nome
                csvfile = csv.DictReader(file, delimiter=';')

                try:
                    header = next(csvfile)
                except StopIteration:
                    continue

                if cpf_column_name := [x for x in header if 'cnpj' in x.lower()]:
                    print('-', file_path)
                    for row in csvfile:
                        CNPJ: str = row[cpf_column_name[0]]

                        if not CNPJ:
                            continue
                        
                        page: requests.Response = requests.get(URI(CNPJ))
                        if page.status_code != 200:
                            print(f'    *.* {URI(CNPJ)} - {page.status_code}')
                            continue

                        writer.writerows(extract_data(page, CNPJ))
