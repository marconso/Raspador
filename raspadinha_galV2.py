from datetime import datetime
import csv
from selenium import webdriver #inclui selenium+urllib3+setuptools+certifi
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, NoSuchElementException #para saber qual erro no try/except
from selenium.webdriver.common.action_chains import ActionChains
import logging #para criar arquivo de log

#Início do programa
A = str(input("Digite 1 para Gal Hemoce ou 2 para Gal Fiocruz: "))
if A == "1":
	Ref = "https://gal.saude.ce.gov.br/"
if A == "2":
	Ref = "https://gal.fiocruz.sus.gov.br/"

#tempos em segundos
TEMPO_ESPERAR_LOGIN = 180
TEMPO_ESPERAR_ABRIR_PASTA = 10
TEMPO_ESPERAR_APARECER_ELEMENTO = 10
TEMPO_ESPERAR_ABRIR_FRAME = 15
TEMPO_ESPERAR_ABRIR_JANELA = 15
TEMPO_ESPERAR_ELEMENTO_SER_CLICAVEL = 15

	

class Navegador:
    def __init__(self, caminho_navegador='.//chromedriver.exe'):
        servc = webdriver.chrome.service.Service(caminho_navegador)
        logging.debug('Caminho do navegador = %s', caminho_navegador)
        opcoes = webdriver.ChromeOptions()
        opcoes.add_argument("start-maximized")
        opcoes.add_argument("disable-infobars")
        opcoes.add_argument("--disable-extensions")
        opcoes.add_argument('--no-sandbox')
        opcoes.add_argument('--disable-application-cache')
        opcoes.add_argument('--disable-gpu')
        opcoes.add_argument("--disable-dev-shm-usage")
        #opcoes.add_argument('headless') #para o selenium nao abrir o navegador, e rodar em segundo plano
        self.navegador = webdriver.Chrome(service=servc, options=opcoes)
        self.actions = ActionChains(self.navegador)
        hoje=datetime.today().strftime("%Y%m%d%H%M%S")
        self.nome_arquivo = "dados_"+str(hoje)+".csv"

    def iniciar_gal(self):
        self.navegador.get(Ref)
        try:
            WebDriverWait(self.navegador, TEMPO_ESPERAR_LOGIN).until(EC.visibility_of_element_located(('xpath', '/html/body/div[4]/div[2]/div/div/div/div/ul/div/li[2]/div/img[1]')))
        except TimeoutException:
            logging.critical('ERRO CRÍTICO: O login no GAL não foi realizado em menos de %s segundos. Reinicie a aplicação.', str(TEMPO_ESPERAR_LOGIN))
            self.navegador.quit()
        try: 
            self.navegador.find_element(By.XPATH, '/html/body/div[13]/div[2]/div[2]/div/div/div/div/div/table/tbody/tr/td/table/tbody/tr/td[2]/em/button').click() #fechar noticias
        except NoSuchElementException:
            logging.warning('Alerta: Não foi possível localizar o elemento de Notícias ao abrir o GAL. Confira se está tudo OK.')
        self.abrir_pasta_biologia_medica()
        self.abrir_pasta_consultas()
        janela_principal = self.navegador.window_handles[0]

        with open('amostras.csv', 'r', newline='', encoding='ISO-8859-1') as csvfile:
            leitor_csv = csv.reader(csvfile, delimiter=',') #primeiro ele abre o csv com os programas/ies
            for linha in leitor_csv:
                print("LINHA: ", linha)
                logging.info('Iniciando raspagem da requisicao  %s', linha[0])
                with open(self.nome_arquivo, 'a') as csv2:
                    csv2.write(linha[0] + ";")
                self.clicar_consultar_exame()
                self.iniciar_nova_consulta_exame(linha[0], janela_principal)
                with open(self.nome_arquivo, 'a') as csv2:
                    csv2.write("\n")
        logging.info('Fim da raspagem de dados...')
        logging.info('Os dados foram salvos no arquivo dados.csv')
        logging.info('Agradecr srs.:L.D., C.A., P.J., S.A.')
        self.navegador.quit()

    def abrir_pasta_biologia_medica(self):
        logging.info('Abrindo pasta biologia médica...')
        WebDriverWait(self.navegador, TEMPO_ESPERAR_ABRIR_PASTA).until(EC.visibility_of_element_located(('xpath', '/html/body/div[4]/div[2]/div/div/div/div/ul/div/li[2]/div/img[1]')))
        pasta_biologia = self.navegador.find_element(By.XPATH, '/html/body/div[4]/div[2]/div/div/div/div/ul/div/li[2]/div/img[1]') #procurar pasta 'Biologia Medica'
        self.actions.double_click(pasta_biologia).perform()

    def abrir_pasta_consultas(self):
        logging.info('Abrindo pasta consultas...')
        WebDriverWait(self.navegador, TEMPO_ESPERAR_ABRIR_PASTA).until(EC.visibility_of_element_located(('xpath', '/html/body/div[4]/div[2]/div/div/div/div/ul/div/li[2]/ul/li[5]')))
        pasta_consulta = self.navegador.find_element(By.XPATH, '/html/body/div[4]/div[2]/div/div/div/div/ul/div/li[2]/ul/li[5]') #procurar pasta 'Consultas'
        self.actions.double_click(pasta_consulta).perform()

    def clicar_consultar_exame(self):
        logging.info('Abrindo frame de consulta ao exame...')
        WebDriverWait(self.navegador, TEMPO_ESPERAR_APARECER_ELEMENTO).until(EC.visibility_of_element_located(('xpath', '/html/body/div[4]/div[2]/div/div/div/div/ul/div/li[2]/ul/li[5]/ul/li[3]/div')))
        consultar_exame = self.navegador.find_element(By.XPATH, '/html/body/div[4]/div[2]/div/div/div/div/ul/div/li[2]/ul/li[5]/ul/li[3]/div') #procurar o botao 'consultar exame'
        self.actions.double_click(consultar_exame).perform()
        #210149002653
        self.navegador.switch_to.frame(self.navegador.find_element(By.NAME, "content-panel"))
        WebDriverWait(self.navegador, TEMPO_ESPERAR_ABRIR_FRAME).until(EC.visibility_of_element_located(('xpath', '/html/body/div[6]/div[2]/div[1]/div/div/div/div/div/div/table/tbody/tr[1]/td[2]/div/div/div/div/div[1]/input')))

    def iniciar_nova_consulta_exame(self, numero_amostra, janela):
        logging.info('Buscando exame com requisição %s...', numero_amostra)
        campo_amostra = self.navegador.find_element(By.XPATH, '/html/body/div[6]/div[2]/div[1]/div/div/div/div/div/div/table/tbody/tr[1]/td[2]/div/div/div/div/div[1]/input') #procurar o campo do numero de requisicao Não conseguiu achar /html/body/div[6]/div[2]/div[1]/div/div/div/div/div/div/table/tbody/tr[1]/td[1]/div/div/div/div/div[1]/input
        campo_amostra.click()
        campo_amostra.send_keys(numero_amostra)
        input_residencia = self.navegador.find_element(By.XPATH, '/html/body/div[6]/div[2]/div[1]/div/div/div/div/div/div/table/tbody/tr[4]/td[1]/div/div/div/div/div[1]/div/input')
        WebDriverWait(self.navegador, TEMPO_ESPERAR_ELEMENTO_SER_CLICAVEL).until(EC.element_to_be_clickable(('xpath', '/html/body/div[6]/div[2]/div[1]/div/div/div/div/div/div/table/tbody/tr[4]/td[1]/div/div/div/div/div[1]/div/input')))
        input_requisitante = self.navegador.find_element(By.XPATH, '/html/body/div[6]/div[2]/div[1]/div/div/div/div/div/div/table/tbody/tr[4]/td[2]/div/div/div/div/div[1]/div/input')
        WebDriverWait(self.navegador, TEMPO_ESPERAR_ELEMENTO_SER_CLICAVEL).until(EC.element_to_be_clickable(('xpath', '/html/body/div[6]/div[2]/div[1]/div/div/div/div/div/div/table/tbody/tr[4]/td[2]/div/div/div/div/div[1]/div/input')))
        input_exame = self.navegador.find_element(By.XPATH, '/html/body/div[6]/div[2]/div[1]/div/div/div/div/div/div/table/tbody/tr[5]/td[1]/div/div/div/div/div[1]/div/input')
        WebDriverWait(self.navegador, TEMPO_ESPERAR_ELEMENTO_SER_CLICAVEL).until(EC.element_to_be_clickable(('xpath', '/html/body/div[6]/div[2]/div[1]/div/div/div/div/div/div/table/tbody/tr[5]/td[1]/div/div/div/div/div[1]/div/input')))
        input_status = self.navegador.find_element(By.XPATH, '/html/body/div[6]/div[2]/div[1]/div/div/div/div/div/div/table/tbody/tr[5]/td[2]/div/div/div/div/div[1]/div/input')
        WebDriverWait(self.navegador, TEMPO_ESPERAR_ELEMENTO_SER_CLICAVEL).until(EC.element_to_be_clickable(('xpath', '/html/body/div[6]/div[2]/div[1]/div/div/div/div/div/div/table/tbody/tr[5]/td[2]/div/div/div/div/div[1]/div/input')))
        self.navegador.find_element(By.XPATH, '/html/body/div[6]/div[2]/div[2]/div/div/div/div/div/table/tbody/tr/td/table/tbody/tr/td[2]/em/button').click()
        try:
            WebDriverWait(self.navegador, TEMPO_ESPERAR_APARECER_ELEMENTO).until(EC.visibility_of_element_located(('xpath', '/html/body/div[1]/div/div/div/div/div[2]/div/div[1]/div[2]/div')))
        except TimeoutException:
            logging.error('ERRO: Número da amostra %s não encontrada no GAL. Iniciando a busca para número da amostra seguinte...', numero_amostra)
            self.navegador.switch_to.window(janela)
        else:
            logging.info('SUCESSO: Número da amostra %s encontrada no GAL.', numero_amostra)
            primeira_pessoa_encontrada = self.navegador.find_element(By.XPATH, '/html/body/div[1]/div/div/div/div/div[2]/div/div[1]/div[2]/div') #verificar se alguem eh encontrado pelo numero de requisicao
            primeira_pessoa_encontrada.click()
            self.coletar_informacoes_consulta_exame(numero_amostra)

    def coletar_informacoes_consulta_exame(self, numero_amostra):
        infos_consulta = []
        logging.info('Iniciando coleta de informações do exame com número da amostra %s...', numero_amostra)
        janela_principal = self.navegador.window_handles[0] #atribuir objeto (janela principal) em variavel
        botao_visualizar_resultado = self.navegador.find_element(By.XPATH, '/html/body/div[1]/div/div/div/div/div[1]/div/table/tbody/tr/td[1]/table/tbody/tr/td[2]/em/button')
        botao_visualizar_resultado.click()
        janela_info_exame = self.navegador.window_handles[1] #atribuir objeto (janela das infos do exame) em variavel
        self.navegador.switch_to.window(janela_info_exame) #alterar foco do selenium para janela_info_exame
        #try:
        WebDriverWait(self.navegador, TEMPO_ESPERAR_APARECER_ELEMENTO).until(EC.visibility_of_element_located(('xpath', '/html/body/div/div/table/tbody/tr[2]/td[1]')))
        infos_consulta.append(self.navegador.find_element(By.XPATH, '/html/body/div/div/table/tbody/tr[2]/td[1]').get_attribute("innerHTML")) #requisição
        self.navegador.close() #fechar janela_info_exame
        self.navegador.switch_to.window(janela_principal) #alterar foco do selenium para janela_principal
        #except TimeoutException:
        #	pass
        #except selenium.common.exceptions.NoSuchElementException:
        #	pass
        with open(self.nome_arquivo, 'a') as csvfile:
            infos_str = ';'.join(infos_consulta)
            csvfile.write(infos_str)
            # escritor_csv = csv.writer(csvfile, delimiter=';')
            # escritor_csv.writerow(infos_consulta)

if __name__ == '__main__':
	logging.basicConfig(filename='acontecimentos.log', filemode = 'w', encoding='iso8859-1', level=logging.INFO)
	abrir = Navegador()
	abrir.iniciar_gal()