from datetime import datetime
import csv
import pathlib
import re
import time
from selenium.common.exceptions import TimeoutException
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from unidecode import unidecode


REF = {
    1: 'https://gal.saude.ce.gov.br/',
    2: 'https://gal.fiocruz.sus.gov.br/',
}


def entrada_do_usuario():
    c = int(input('Digite [1] para Homece ou [2] para Fiocruz: '))
    return REF[c]


def abre_consulta(navegador):
    plus = 'x-tree-ec-icon.x-tree-elbow-plus'

    WebDriverWait(navegador, 180).until(
        EC.visibility_of_element_located((By.ID, 'ext-gen87'))
    )
    navegador.find_element(by='id', value='ext-gen87').click()

    WebDriverWait(navegador, 5).until(
        EC.visibility_of_element_located((By.CLASS_NAME, plus))
    )
    navegador.find_element(By.CLASS_NAME, plus).click()

    WebDriverWait(navegador, 5).until(
        EC.visibility_of_element_located((By.CLASS_NAME, plus))
    )

    navegador.find_elements(By.CLASS_NAME, plus)[2].click()

    WebDriverWait(navegador, 5).until(
        EC.visibility_of_element_located((By.LINK_TEXT, 'Consultar Exame'))
    )

    return navegador


def faz_consulta(navegador, amostra, encontrados, nao_encontrados):
    navegador.switch_to.default_content()
    navegador.find_element(By.LINK_TEXT, 'Consultar Exame').click()

    navegador.switch_to.frame(navegador.find_element(By.TAG_NAME, 'iframe'))
    navegador.find_element(By.TAG_NAME, 'input').send_keys(amostra)
    navegador.find_element(By.TAG_NAME, 'button').click()

    grid_amostra = 'x-grid3-cell-inner.x-grid3-col-2'

    try:
        WebDriverWait(navegador, 10).until(EC.visibility_of_element_located((
            By.CLASS_NAME, grid_amostra)
        ))

        [td.click()
         for td in navegador.find_elements(By.TAG_NAME, 'td')
         if td.text == amostra]

        [bt.click()
         for bt in navegador.find_elements(By.TAG_NAME, 'button')
         if bt.text == 'Visualizar Resultado']

        navegador.switch_to.window(navegador.window_handles[1])
        linhas = [
            linha.text.lstrip().rstrip()
            for linha in navegador.find_elements(By.CLASS_NAME, 'linha')
        ]

        data_coleta = re.search(
            r'Data da Coleta: \d{2}/\d{2}/\d{4}',
            linhas[1]
        )

        if data_coleta is not None:
            data_coleta = re.search(
                r'\d{2}/\d{2}/\d{4}', data_coleta.group()
            ).group()

        resultado = linhas[5]

        encontrados.writerow({'Requisicao': amostra,
                              'Data Coleta': data_coleta,
                              'Resultado': unidecode(resultado)})

        navegador.switch_to.window(navegador.window_handles[1])
        navegador.close()
        navegador.switch_to.window(navegador.window_handles[0])

    except TimeoutException:
        nao_encontrados.write(amostra)


def faz_login(navegador, email, psswd, mod, lab):
    navegador.find_element(By.ID, 'ext-comp-1008').send_keys(email)
    navegador.find_element(By.ID, 'ext-comp-1009').send_keys(psswd)
    navegador.find_element(By.ID, 'ext-comp-1010').send_keys(mod)

    navegador.find_element(By.ID, 'ext-comp-1010').click()
    navegador.find_element(By.ID, 'ext-comp-1010').send_keys(Keys.ENTER)

    time.sleep(3)
    navegador.find_element(By.ID, 'ext-comp-1011').click()
    time.sleep(3)
    navegador.find_element(By.ID, 'ext-comp-1011').send_keys(lab)
    navegador.find_element(By.ID, 'ext-comp-1011').send_keys(Keys.ENTER)
    navegador.find_element(By.ID, 'ext-gen68').click()

    return navegador


def cria_navegador(url, caminho_do_navegador):
    opcoes = webdriver.ChromeOptions()
    opcoes.binary_location = caminho_do_navegador
    opcoes.add_experimental_option('detach', True)

    navegador = webdriver.Chrome(options=opcoes)
    navegador.get(url)

    WebDriverWait(navegador, 5).until(
        EC.visibility_of_element_located((By.ID, 'ext-comp-1008'))
    )

    return navegador


def main():
    local_navegador = '/usr/bin/chromium-browser'

    opcao_do_usuario = entrada_do_usuario()
    navegador = cria_navegador(
        opcao_do_usuario, local_navegador
    )

    navegador = abre_consulta(navegador)

    colunas = ['Requisicao', 'Data Coleta', 'Resultado']

    now = datetime.now().strftime('%Y-%m-%d')

    encontrados = pathlib.Path().home() / f'encontrados_{now}.csv'
    encontrados.touch(exist_ok=True)
    n_encontrados = pathlib.Path().home() / f'nao_encontrados_{now}.csv'
    n_encontrados.touch(exist_ok=True)

    with (open(encontrados, 'w') as fe,
          open(n_encontrados, 'w') as fn):

        encontrados = csv.DictWriter(fe, fieldnames=colunas)
        encontrados.writeheader()
        n_encontrados = csv.writer(fn)

        with open('requisicoes.csv', 'r') as requisicoes:
            req = csv.DictReader(requisicoes)
            for linha in req:
                faz_consulta(
                    navegador, linha['Requisição'], encontrados, n_encontrados
                )
    navegador.close()


if __name__ == '__main__':
    driver = main()
