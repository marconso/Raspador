#encoding: iso8859-1
#Algoritmo em selenium para raspar dados do Gerenciador de Ambiente Laboratorial
#Necessário fazer login manualmente antes do início da raspagem
#Agradeça a: 
#License: MIT

#!pip install selenium
# branch suzana

A = str(input("Digite 1 para Gal Hemoce ou 2 para Gal Fiocruz: "))
if A == "1":
	Ref = "https://gal.saude.ce.gov.br/"
if A == "2":
	Ref = "https://gal.fiocruz.sus.gov.br/"
	
from datetime import datetime
import csv
from selenium import webdriver #inclui selenium+urllib3+setuptools+certifi
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, NoSuchElementException #para saber qual erro no try/except
from selenium.webdriver.common.action_chains import ActionChains
import logging #para criar arquivo de log
import unidecode

#tempos em segundos
TEMPO_ESPERAR_LOGIN = 120
TEMPO_ESPERAR_ABRIR_PASTA = 10
TEMPO_ESPERAR_APARECER_ELEMENTO = 10
TEMPO_ESPERAR_ABRIR_FRAME = 15
TEMPO_ESPERAR_ABRIR_JANELA = 15
TEMPO_ESPERAR_ELEMENTO_SER_CLICAVEL = 15

INFORMACOES = {
	"REQUISICAO":{
		'botao_categoria':"/html/body/div[10]/div[2]/div[1]/div/div/div/div/div[1]/div[1]/ul/li[1]",
		'num_requisicao':'/html/body/div[10]/div[2]/div[1]/div/div/div/div/div[2]/div/div[1]/div/form/div[1]/div/div/div/div[1]/div/div/div/div[1]/input',
		'requisitante':'/html/body/div[10]/div[2]/div[1]/div/div/div/div/div[2]/div/div[1]/div/form/div[1]/div/div/div/div[2]/div/div/div/div[1]/input',
		'cnes_requisitante':'/html/body/div[10]/div[2]/div[1]/div/div/div/div/div[2]/div/div[1]/div/form/div[1]/div/div/div/div[3]/div/div/div/div[1]/input',
		'municipio_requisitante':'/html/body/div[10]/div[2]/div[1]/div/div/div/div/div[2]/div/div[1]/div/form/div[2]/div/div/div/div[1]/div/div/div/div[1]/input',
		'cod_ibge_requisitante':'/html/body/div[10]/div[2]/div[1]/div/div/div/div/div[2]/div/div[1]/div/form/div[2]/div/div/div/div[2]/div/div/div/div[1]/input',
		'uf_requisitante':'/html/body/div[10]/div[2]/div[1]/div/div/div/div/div[2]/div/div[1]/div/form/div[2]/div/div/div/div[3]/div/div/div/div[1]/input',
		'cns_prof_saude_requisitante':'/html/body/div[10]/div[2]/div[1]/div/div/div/div/div[2]/div/div[1]/div/form/div[3]/div/div/div/div[1]/div/div/div/div[1]/input',
		'nome_prof_saude_requisitante':'/html/body/div[10]/div[2]/div[1]/div/div/div/div/div[2]/div/div[1]/div/form/div[3]/div/div/div/div[2]/div/div/div/div[1]/input',
		'registro_prof_saude_requisitante':'/html/body/div[10]/div[2]/div[1]/div/div/div/div/div[2]/div/div[1]/div/form/div[3]/div/div/div/div[3]/div/div/div/div[1]/input',
		'data_requisicao':'/html/body/div[10]/div[2]/div[1]/div/div/div/div/div[2]/div/div[1]/div/form/div[4]/div/div/div/div[1]/div/div/div/div[1]/input',
		'finalidade_requisicao':'/html/body/div[10]/div[2]/div[1]/div/div/div/div/div[2]/div/div[1]/div/form/div[4]/div/div/div/div[2]/div/div/div/div[1]/input',
		'descricao_requisicao':'/html/body/div[10]/div[2]/div[1]/div/div/div/div/div[2]/div/div[1]/div/form/div[4]/div/div/div/div[3]/div/div/div/div[1]/input'},
	"PACIENTE": {
		'botao_categoria':"/html/body/div[10]/div[2]/div[1]/div/div/div/div/div[1]/div[1]/ul/li[2]",
		'cns_paciente':'/html/body/div[10]/div[2]/div[1]/div/div/div/div/div[2]/div/div[2]/div/form/table/tbody/tr[1]/td/div/div/div/div/div[1]/div/div/div/div[1]/input',
		'nome_paciente':'/html/body/div[10]/div[2]/div[1]/div/div/div/div/div[2]/div/div[2]/div/form/table/tbody/tr[1]/td/div/div/div/div/div[2]/div/div/div/div[1]/input',
		'data_nasc_paciente':'/html/body/div[10]/div[2]/div[1]/div/div/div/div/div[2]/div/div[2]/div/form/table/tbody/tr[2]/td/div/div/div/div/div[1]/div/div/div/div[1]/input',
		'idade_paciente':'/html/body/div[10]/div[2]/div[1]/div/div/div/div/div[2]/div/div[2]/div/form/table/tbody/tr[2]/td/div/div/div/div/div[2]/div/div/div/div[1]/input',
		'sexo_paciente':'/html/body/div[10]/div[2]/div[1]/div/div/div/div/div[2]/div/div[2]/div/form/table/tbody/tr[2]/td/div/div/div/div/div[3]/div/div/div/div[1]/input',
		'nacionalidade_paciente':'/html/body/div[10]/div[2]/div[1]/div/div/div/div/div[2]/div/div[2]/div/form/table/tbody/tr[2]/td/div/div/div/div/div[4]/div/div/div/div[1]/input',
		'raca_paciente':'/html/body/div[10]/div[2]/div[1]/div/div/div/div/div[2]/div/div[2]/div/form/table/tbody/tr[3]/td/div/div/div/div/div[1]/div/div/div/div[1]/input',
		'etnia_paciente':'/html/body/div[10]/div[2]/div[1]/div/div/div/div/div[2]/div/div[2]/div/form/table/tbody/tr[3]/td/div/div/div/div/div[2]/div/div/div/div[1]/input',
		'nome_mae_paciente':'/html/body/div[10]/div[2]/div[1]/div/div/div/div/div[2]/div/div[2]/div/form/table/tbody/tr[3]/td/div/div/div/div/div[3]/div/div/div/div[1]/input',
		'documento_1_paciente':'/html/body/div[10]/div[2]/div[1]/div/div/div/div/div[2]/div/div[2]/div/form/table/tbody/tr[4]/td/div/div/div/div/div[1]/div/div/div/div[1]/input',
		'documento_2_paciente':'/html/body/div[10]/div[2]/div[1]/div/div/div/div/div[2]/div/div[2]/div/form/table/tbody/tr[4]/td/div/div/div/div/div[2]/div/div/div/div[1]/input',
		'logradouro_residencia_paciente':'/html/body/div[10]/div[2]/div[1]/div/div/div/div/div[2]/div/div[2]/div/form/table/tbody/tr[5]/td/div/div/div/div/div[1]/div/div/div/div[1]/input',
		'numero_residencia_paciente':'/html/body/div[10]/div[2]/div[1]/div/div/div/div/div[2]/div/div[2]/div/form/table/tbody/tr[5]/td/div/div/div/div/div[2]/div/div/div/div[1]/input',
		'complemento_residencia_paciente':'/html/body/div[10]/div[2]/div[1]/div/div/div/div/div[2]/div/div[2]/div/form/table/tbody/tr[5]/td/div/div/div/div/div[3]/div/div/div/div[1]/input',
		'ponto_ref_residencia_paciente':'/html/body/div[10]/div[2]/div[1]/div/div/div/div/div[2]/div/div[2]/div/form/table/tbody/tr[5]/td/div/div/div/div/div[4]/div/div/div/div[1]/input',
		'bairro_residencia_paciente':'/html/body/div[10]/div[2]/div[1]/div/div/div/div/div[2]/div/div[2]/div/form/table/tbody/tr[5]/td/div/div/div/div/div[5]/div/div/div/div[1]/input',
		'municipio_residencia_paciente':'/html/body/div[10]/div[2]/div[1]/div/div/div/div/div[2]/div/div[2]/div/form/table/tbody/tr[7]/td/div/div/div/div/div[1]/div/div/div/div[1]/input',
		'cod_ibge_residencia_paciente':'/html/body/div[10]/div[2]/div[1]/div/div/div/div/div[2]/div/div[2]/div/form/table/tbody/tr[7]/td/div/div/div/div/div[2]/div/div/div/div[1]/input',
		'uf_residencia_paciente':'/html/body/div[10]/div[2]/div[1]/div/div/div/div/div[2]/div/div[2]/div/form/table/tbody/tr[7]/td/div/div/div/div/div[3]/div/div/div/div[1]/input',
		'cep_residencia_paciente':'/html/body/div[10]/div[2]/div[1]/div/div/div/div/div[2]/div/div[2]/div/form/table/tbody/tr[7]/td/div/div/div/div/div[4]/div/div/div/div[1]/input',
		'telefone_paciente':'/html/body/div[10]/div[2]/div[1]/div/div/div/div/div[2]/div/div[2]/div/form/table/tbody/tr[7]/td/div/div/div/div/div[5]/div/div/div/div[1]/input',
		'zona_residencia_paciente':'/html/body/div[10]/div[2]/div[1]/div/div/div/div/div[2]/div/div[2]/div/form/table/tbody/tr[7]/td/div/div/div/div/div[6]/div/div/div/div[1]/input',
		'pais_residencia_paciente':'/html/body/div[10]/div[2]/div[1]/div/div/div/div/div[2]/div/div[2]/div/form/table/tbody/tr[8]/td/div/div/div/div/div[1]/div/div/div/div[1]/input'},
	"INF_CLINICA":{
		'botao_categoria':"/html/body/div[10]/div[2]/div[1]/div/div/div/div/div[1]/div[1]/ul/li[3]",
		'agravo_info_clinica':'/html/body/div[10]/div[2]/div[1]/div/div/div/div/div[2]/div/div[3]/div/form/table/tbody/tr[1]/td/div/div/div/div/div[1]/div/div/div/div[1]/input',
		'data_primeiros_sintomas':'/html/body/div[10]/div[2]/div[1]/div/div/div/div/div[2]/div/div[3]/div/form/table/tbody/tr[1]/td/div/div/div/div/div[2]/div/div/div/div[1]/input',
		'idade_gestacional':'/html/body/div[10]/div[2]/div[1]/div/div/div/div/div[2]/div/div[3]/div/form/table/tbody/tr[1]/td/div/div/div/div/div[3]/div/div/div/div[1]/input',
		'caso_info_clinica':'/html/body/div[10]/div[2]/div[1]/div/div/div/div/div[2]/div/div[3]/div/form/table/tbody/tr[2]/td/div/div/div/div/div/div/table/tbody/tr[1]/td[1]/div/div/div/div/div[1]/input',
		'tratamento_info_clinica':'/html/body/div[10]/div[2]/div[1]/div/div/div/div/div[2]/div/div[3]/div/form/table/tbody/tr[2]/td/div/div/div/div/div/div/table/tbody/tr[1]/td[2]/div/div/div/div/div[1]/input',
		'etapa_info_clinica':'/html/body/div[10]/div[2]/div[1]/div/div/div/div/div[2]/div/div[3]/div/form/table/tbody/tr[2]/td/div/div/div/div/div/div/table/tbody/tr[1]/td[3]/div/div/div/div/div[1]/input',
		'paciente_tomou_vacina':'/html/body/div[10]/div[2]/div[1]/div/div/div/div/div[2]/div/div[3]/div/form/table/tbody/tr[2]/td/div/div/div/div/div/div/table/tbody/tr[2]/td[1]/div/div/div/div/div[1]/input',
		'qual_vacina_paciente_tomou':'/html/body/div[10]/div[2]/div[1]/div/div/div/div/div[2]/div/div[3]/div/form/table/tbody/tr[2]/td/div/div/div/div/div/div/table/tbody/tr[2]/td[2]/div/div/div/div/div[1]/input',
		'data_ultima_dose_vacina':'/html/body/div[10]/div[2]/div[1]/div/div/div/div/div[2]/div/div[3]/div/form/table/tbody/tr[2]/td/div/div/div/div/div/div/table/tbody/tr[2]/td[3]/div/div/div/div/div[1]/input'},
	"EXAME":{
		'botao_categoria':"/html/body/div[10]/div[2]/div[1]/div/div/div/div/div[1]/div[1]/ul/li[5]",
		'num_exame':'/html/body/div[10]/div[2]/div[1]/div/div/div/div/div[2]/div/div[5]/div/div[2]/div/div[1]/div[2]/div/div/div[2]/div/table/tbody/tr/td[1]/div',
		'tipo_exame':'/html/body/div[10]/div[2]/div[1]/div/div/div/div/div[2]/div/div[5]/div/div[2]/div/div[1]/div[2]/div/div/div[2]/div/table/tbody/tr/td[2]/div',
		'metodo_exame':'/html/body/div[10]/div[2]/div[1]/div/div/div/div/div[2]/div/div[5]/div/div[2]/div/div[1]/div[2]/div/div/div[2]/div/table/tbody/tr/td[3]/div',
		'num_interno_exame':'/html/body/div[10]/div[2]/div[1]/div/div/div/div/div[2]/div/div[5]/div/div[2]/div/div[1]/div[2]/div/div/div[2]/div/table/tbody/tr/td[4]/div',
		'num_amostra':'/html/body/div[10]/div[2]/div[1]/div/div/div/div/div[2]/div/div[5]/div/div[2]/div/div[1]/div[2]/div/div/div[2]/div/table/tbody/tr/td[5]/div',
		'tipo_amostra':'/html/body/div[10]/div[2]/div[1]/div/div/div/div/div[2]/div/div[5]/div/div[2]/div/div[1]/div[2]/div/div/div[2]/div/table/tbody/tr/td[6]/div',
		'restricao_amostra':'/html/body/div[10]/div[2]/div[1]/div/div/div/div/div[2]/div/div[5]/div/div[2]/div/div[1]/div[2]/div/div/div[2]/div/table/tbody/tr/td[7]/div',
		'status_amostra':'/html/body/div[10]/div[2]/div[1]/div/div/div/div/div[2]/div/div[5]/div/div[2]/div/div[1]/div[2]/div/div/div[2]/div/table/tbody/tr/td[8]/div/span',
		'lab_responsavel_amostra':'/html/body/div[10]/div[2]/div[1]/div/div/div/div/div[2]/div/div[5]/div/div[2]/div/div[1]/div[2]/div/div/div[2]/div/table/tbody/tr/td[9]/div',
		'data_coleta_amostra':'/html/body/div/div/table[2]/tbody/tr[2]/td[4]'}, #outra pagina web /html/body/div/div/div[2]/div[6]/div[1]/strong
	"OBSERVACAO": {
		'botao_categoria':"/html/body/div[10]/div[2]/div[1]/div/div/div/div/div[1]/div[1]/ul/li[6]",
		'observacoes':'/html/body'} #iframe_name = ext-gen987
}



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
		with open(self.nome_arquivo, 'w', newline='') as csvfile:
			escritor_csv = csv.writer(csvfile, delimiter=';')
			escritor_csv.writerow([
				'cpf','num_requisicao','requisitante','cnes_requisitante','municipio_requisitante','cod_ibge_requisitante','uf_requisitante','cns_prof_saude_requisitante','nome_prof_saude_requisitante','registro_prof_saude_requisitante','data_requisicao','finalidade_requisicao','descricao_requisicao',
				'cns_paciente','nome_paciente','data_nasc_paciente','idade_paciente','sexo_paciente','nacionalidade_paciente','raca_paciente','etnia_paciente','nome_mae_paciente','documento_1_paciente','documento_2_paciente','logradouro_residencia_paciente','numero_residencia_paciente','complemento_residencia_paciente','ponto_ref_residencia_paciente','bairro_residencia_paciente','municipio_residencia_paciente','cod_ibge_residencia_paciente','uf_residencia_paciente','cep_residencia_paciente','telefone_paciente','zona_residencia_paciente','pais_residencia_paciente',
				'agravo_info_clinica','data_primeiros_sintomas','idade_gestacional','caso_info_clinica','tratamento_info_clinica','etapa_info_clinica','paciente_tomou_vacina','qual_vacina_paciente_tomou','data_ultima_dose_vacina',
				'num_exame','tipo_exame','metodo_exame','num_interno_exame','num_amostra','tipo_amostra','restricao_amostra','status_amostra','lab_responsavel_amostra','data_coleta_amostra',
				'observacoes','resultado'])

	def _contar_caracteres(self, string):
		return len(string)

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

	def clicar_consultar_paciente(self):
		logging.info('Abrindo frame de consulta ao paciente...')
		try:
			WebDriverWait(self.navegador, TEMPO_ESPERAR_APARECER_ELEMENTO).until(EC.visibility_of_element_located(('xpath', '/html/body/div[4]/div[2]/div/div/div/div/ul/div/li[2]/ul/li[5]/ul/li[2]')))
			consultar_paciente = self.navegador.find_element(By.XPATH, '/html/body/div[4]/div[2]/div/div/div/div/ul/div/li[2]/ul/li[5]/ul/li[2]') #procurar o botao 'consultar paciente'
			self.actions.double_click(consultar_paciente).perform()
			#210149002653
			self.navegador.switch_to.frame(self.navegador.find_element(By.NAME, "content-panel"))
			WebDriverWait(self.navegador, TEMPO_ESPERAR_ABRIR_FRAME).until(EC.visibility_of_element_located(('xpath', '/html/body/div[6]/div[2]/div[1]/div/div/div/div[1]/div[1]/input')))
		except TimeoutException:
			print('erro ao clicar em consultar paciente')

	def iniciar_nova_consulta(self, numero_requisicao):
		logging.info('Buscando paciente com requisição %s...', numero_requisicao)
		campo_requisicao = self.navegador.find_element(By.XPATH, '/html/body/div[6]/div[2]/div[1]/div/div/div/div[1]/div[1]/input') #procurar o campo do numero de requisicao
		campo_requisicao.click()
		campo_requisicao.send_keys(numero_requisicao)
		input_residencia = self.navegador.find_element(By.XPATH, '/html/body/div[6]/div[2]/div[1]/div/div/div/div[5]/div[1]/div/input')
		WebDriverWait(self.navegador, TEMPO_ESPERAR_ELEMENTO_SER_CLICAVEL).until(EC.element_to_be_clickable(('xpath', '/html/body/div[6]/div[2]/div[1]/div/div/div/div[5]/div[1]/div/input')))
		self.navegador.find_element(By.XPATH, '/html/body/div[6]/div[2]/div[2]/div/div/div/div/div/table/tbody/tr/td/table/tbody/tr/td[2]/em/button').click()
		try:
			WebDriverWait(self.navegador, TEMPO_ESPERAR_APARECER_ELEMENTO).until(EC.visibility_of_element_located(('xpath', '/html/body/div[1]/div/div/div/div/div[2]/div/div[1]/div[2]/div')))
		except TimeoutException:
			logging.error('ERRO: Requisição %s não encontrada no GAL. Iniciando a busca para requisição seguinte...', numero_requisicao)
		else:
			logging.info('SUCESSO: Requisição %s encontrada no GAL.', numero_requisicao)
			primeira_pessoa_encontrada = self.navegador.find_element(By.XPATH, '/html/body/div[1]/div/div/div/div/div[2]/div/div[1]/div[2]/div') #verificar se alguem eh encontrado pelo numero de requisicao
			self.actions.double_click(primeira_pessoa_encontrada).perform()
			info = self.coletar_informacoes_consulta_paciente(numero_requisicao)
            #self.coletar_informacoes_consulta_paciente(numero_requisicao)

			return info
		finally:
			self.navegador.switch_to.default_content()
	def coletar_informacoes_consulta_paciente(self, numero_requisicao):
		infos_consulta = []
		logging.info('Iniciando coleta de informações do paciente com requisição %s...', numero_requisicao)
		infos_consulta.append(self.navegador.find_element(By.XPATH,"/html/body/div[1]/div/div/div/div/div[2]/div/div[1]/div[2]/div/div/table/tbody/tr/td[4]/div").get_attribute("innerHTML").strip("&nbsp;"))
		for TIPO_INFO in INFORMACOES:
			for info in INFORMACOES[TIPO_INFO]:
				if(info=="botao_categoria"): #ao mudar de categoria, preciso clicar no botao da categoria correspondente
					try:
						WebDriverWait(self.navegador, TEMPO_ESPERAR_APARECER_ELEMENTO).until(EC.visibility_of_element_located(('xpath', INFORMACOES[TIPO_INFO][info])))
					except TimeoutException:
						logging.critical('ERRO CRÍTICO: Não foi possível localizar o elemento [%s] da requisição [%s] na nova pagina aberta. Talvez não haja resultados da categoria [%s].', info, numero_requisicao, TIPO_INFO)
					else:
						self.navegador.find_element(By.XPATH, INFORMACOES[TIPO_INFO][info]).click()
				else:
					if(TIPO_INFO == "EXAME"):
						if(info == "data_coleta_amostra"): #se for data_coleta_amostra, precisa abrir uma nova janela clicando em 'Consultar Amostra'
							janela_principal = self.navegador.window_handles[0] #atribuir objeto (janela principal) em variavel
							self.navegador.find_element(By.XPATH, "/html/body/div[10]/div[2]/div[1]/div/div/div/div/div[2]/div/div[5]/div/div[2]/div/div[1]/div[2]/div/div/div[2]/div/table/tbody/tr").click() #clicar na amostra
							self.navegador.find_element(By.XPATH, "/html/body/div[10]/div[2]/div[1]/div/div/div/div/div[2]/div/div[5]/div/div[1]/div/div/div/div[1]/table/tbody/tr/td[3]/table/tbody/tr/td[2]/em/button").click() #clicar em abrir amostra
							janela_info_coleta = self.navegador.window_handles[1] #atribuir objeto (janela das infos da amostra) em variavel
							self.navegador.switch_to.window(janela_info_coleta) #alterar foco do selenium para janela_info_coleta
							WebDriverWait(self.navegador, TEMPO_ESPERAR_APARECER_ELEMENTO).until(EC.visibility_of_element_located(('xpath', INFORMACOES[TIPO_INFO][info])))
							infos_consulta.append(self.navegador.find_element(By.XPATH, INFORMACOES[TIPO_INFO][info]).get_attribute("innerHTML")) #data da coleta da amostra
							self.navegador.close() #fechar janela_info_coleta
							self.navegador.switch_to.window(janela_principal) #alterar foco do selenium para janela_principal
							self.navegador.switch_to.frame(self.navegador.find_element(By.NAME, "content-panel")) #alterar foco do selenium para o frame principal (content-panel) da janela_principal
						else:
							try:
								WebDriverWait(self.navegador, TEMPO_ESPERAR_APARECER_ELEMENTO).until(EC.visibility_of_element_located(('xpath', INFORMACOES[TIPO_INFO][info])))
							except TimeoutException:
								logging.error('ERRO: Não foi possível localizar o elemento [%s] da requisição [%s] na nova pagina aberta. Iniciando coleta no elemento seguinte...', info, numero_requisicao)
							else:
								infos_consulta.append(self.navegador.find_element(By.XPATH, INFORMACOES[TIPO_INFO][info]).get_attribute("innerHTML"))
					elif(TIPO_INFO == "OBSERVACAO"): #se for observacao, precisa abrir o frame de observacao
						try:
							self.navegador.switch_to.frame(self.navegador.find_element(By.NAME, "ext-gen979"))
						except NoSuchElementException:
							try:
								self.navegador.switch_to.frame(self.navegador.find_element(By.NAME, "ext-gen981"))
							except NoSuchElementException:
								logging.error('ERRO: Não foi possível localizar o frame [OBSERVACAO] da requisição [%s] na nova pagina aberta. Iniciando coleta no elemento seguinte...', numero_requisicao)
						try:
							WebDriverWait(self.navegador, TEMPO_ESPERAR_ABRIR_FRAME).until(EC.visibility_of_element_located(('xpath', INFORMACOES[TIPO_INFO][info])))
						except TimeoutException:
							logging.error('ERRO: Não foi possível localizar o elemento [%s] da requisição [%s] na nova pagina aberta. Iniciando coleta no elemento seguinte...', info, numero_requisicao)
						else:
							infos_consulta.append(self.navegador.find_element(By.XPATH, INFORMACOES[TIPO_INFO][info]).get_attribute("innerHTML"))
						finally:
							self.navegador.switch_to.default_content()
					else:
						try:
							WebDriverWait(self.navegador, TEMPO_ESPERAR_APARECER_ELEMENTO).until(EC.visibility_of_element_located(('xpath', INFORMACOES[TIPO_INFO][info])))
						except TimeoutException:
							logging.error('ERRO: Não foi possível localizar o elemento [%s] da requisição [%s] na nova pagina aberta. Iniciando coleta no elemento seguinte...', info, numero_requisicao)
						else:
							infos_consulta.append(self.navegador.find_element(By.XPATH, INFORMACOES[TIPO_INFO][info]).get_attribute("value"))
		return infos_consulta
		#with open(self.nome_arquivo, 'a', newline='') as csvfile:
			#csvfile.write('\t'.join(infos_consulta)+'\t')
            #escritor_csv = csv.writer(csvfile, delimiter='\t')
			#escritor_csv.writerow(infos_consulta)

	def clicar_consultar_exame(self):
		logging.info('Abrindo frame de consulta ao exame...')
		try:
			WebDriverWait(self.navegador, TEMPO_ESPERAR_APARECER_ELEMENTO).until(EC.visibility_of_element_located(('xpath', '/html/body/div[4]/div[2]/div/div/div/div/ul/div/li[2]/ul/li[5]/ul/li[3]/div')))
			consultar_exame = self.navegador.find_element(By.XPATH, '/html/body/div[4]/div[2]/div/div/div/div/ul/div/li[2]/ul/li[5]/ul/li[3]/div') #procurar o botao 'consultar exame'
			self.actions.double_click(consultar_exame).perform()
			#210149002653
			self.navegador.switch_to.frame(self.navegador.find_element(By.NAME, "content-panel"))
			WebDriverWait(self.navegador, TEMPO_ESPERAR_ABRIR_FRAME).until(EC.visibility_of_element_located(('xpath', '/html/body/div[6]/div[2]/div[1]/div/div/div/div/div/div/table/tbody/tr[1]/td[1]/div/div/div/div/div[1]/input')))
		except TimeoutException:
			pass
	def iniciar_nova_consulta_exame(self, numero_requisicao, infos_consulta):
		logging.info('Buscando exame com requisição %s...', numero_requisicao)
		try:
			campo_requisicao = self.navegador.find_element(By.XPATH, '/html/body/div[6]/div[2]/div[1]/div/div/div/div/div/div/table/tbody/tr[1]/td[1]/div/div/div/div/div[1]/input') #procurar o campo do numero de requisicao Não conseguiu achar /html/body/div[6]/div[2]/div[1]/div/div/div/div/div/div/table/tbody/tr[1]/td[1]/div/div/div/div/div[1]/input
			campo_requisicao.click()
			campo_requisicao.send_keys(numero_requisicao)
			input_residencia = self.navegador.find_element(By.XPATH, '/html/body/div[6]/div[2]/div[1]/div/div/div/div/div/div/table/tbody/tr[4]/td[1]/div/div/div/div/div[1]/div/input')
			WebDriverWait(self.navegador, TEMPO_ESPERAR_ELEMENTO_SER_CLICAVEL).until(EC.element_to_be_clickable(('xpath', '/html/body/div[6]/div[2]/div[1]/div/div/div/div/div/div/table/tbody/tr[4]/td[1]/div/div/div/div/div[1]/div/input')))
			input_requisitante = self.navegador.find_element(By.XPATH, '/html/body/div[6]/div[2]/div[1]/div/div/div/div/div/div/table/tbody/tr[4]/td[2]/div/div/div/div/div[1]/div/input')
			WebDriverWait(self.navegador, TEMPO_ESPERAR_ELEMENTO_SER_CLICAVEL).until(EC.element_to_be_clickable(('xpath', '/html/body/div[6]/div[2]/div[1]/div/div/div/div/div/div/table/tbody/tr[4]/td[2]/div/div/div/div/div[1]/div/input')))
			input_exame = self.navegador.find_element(By.XPATH, '/html/body/div[6]/div[2]/div[1]/div/div/div/div/div/div/table/tbody/tr[5]/td[1]/div/div/div/div/div[1]/div/input')
			WebDriverWait(self.navegador, TEMPO_ESPERAR_ELEMENTO_SER_CLICAVEL).until(EC.element_to_be_clickable(('xpath', '/html/body/div[6]/div[2]/div[1]/div/div/div/div/div/div/table/tbody/tr[5]/td[1]/div/div/div/div/div[1]/div/input')))
			input_status = self.navegador.find_element(By.XPATH, '/html/body/div[6]/div[2]/div[1]/div/div/div/div/div/div/table/tbody/tr[5]/td[2]/div/div/div/div/div[1]/div/input')
			WebDriverWait(self.navegador, TEMPO_ESPERAR_ELEMENTO_SER_CLICAVEL).until(EC.element_to_be_clickable(('xpath', '/html/body/div[6]/div[2]/div[1]/div/div/div/div/div/div/table/tbody/tr[5]/td[2]/div/div/div/div/div[1]/div/input')))
			self.navegador.find_element(By.XPATH, '/html/body/div[6]/div[2]/div[2]/div/div/div/div/div/table/tbody/tr/td/table/tbody/tr/td[2]/em/button').click()
		except NoSuchElementException:
			pass
		try:
			WebDriverWait(self.navegador, TEMPO_ESPERAR_APARECER_ELEMENTO).until(EC.visibility_of_element_located(('xpath', '/html/body/div[1]/div/div/div/div/div[2]/div/div[1]/div[2]/div')))
		except TimeoutException:
			logging.error('ERRO: Requisição %s não encontrada no GAL. Iniciando a busca para requisição seguinte...', numero_requisicao)
		else:
			logging.info('SUCESSO: Requisição %s encontrada no GAL.', numero_requisicao)
			primeira_pessoa_encontrada = self.navegador.find_element(By.XPATH, '/html/body/div[1]/div/div/div/div/div[2]/div/div[1]/div[2]/div') #verificar se alguem eh encontrado pelo numero de requisicao
			primeira_pessoa_encontrada.click()
			self.coletar_informacoes_consulta_exame(numero_requisicao, infos_consulta)
		finally:
			self.navegador.switch_to.default_content()
            
	def coletar_informacoes_consulta_exame(self, numero_requisicao, infos_consulta):
		
		logging.info('Iniciando coleta de informações do exame com requisição %s...', numero_requisicao)
		janela_principal = self.navegador.window_handles[0] #atribuir objeto (janela principal) em variavel
		botao_visualizar_resultado = self.navegador.find_element(By.XPATH, '/html/body/div[1]/div/div/div/div/div[1]/div/table/tbody/tr/td[1]/table/tbody/tr/td[2]/em/button')
		botao_visualizar_resultado.click()
		janela_info_exame = self.navegador.window_handles[1] #atribuir objeto (janela das infos do exame) em variavel
		self.navegador.switch_to.window(janela_info_exame) #alterar foco do selenium para janela_info_exame
		try:
			WebDriverWait(self.navegador, TEMPO_ESPERAR_APARECER_ELEMENTO).until(EC.visibility_of_element_located(('xpath', '/html/body')))
			infos_consulta.append(self.navegador.find_element(By.XPATH, '/html/body').get_attribute("innerHTML")) #resultado do exame
			self.navegador.close() #fechar janela_info_exame
			self.navegador.switch_to.window(janela_principal) #alterar foco do selenium para janela_principal
		except TimeoutException:
			pass
		except selenium.common.exceptions.NoSuchElementException:
			pass
		infos_consulta[-1] = unidecode.unidecode(infos_consulta[-1])
		
		if "Detectavel" in infos_consulta[-1]:
			if "Nao Detectavel" in infos_consulta[-1]:
				infos_consulta[-1] = "Não Detectável"
			else:
				infos_consulta[-1] = "Detectável"
		else:
			infos_consulta[-1] = "Análise manual"
		with open(self.nome_arquivo, 'a', newline='') as csvfile:
			#csvfile.write(infos_consulta+'\n')
			escritor_csv = csv.writer(csvfile, delimiter=';')
			escritor_csv.writerow(infos_consulta)    
           
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
		#campo_requisicao.clear()
		with open('requisicoes.csv', 'r', newline='', encoding='ISO-8859-1') as csvfile:
			leitor_csv = csv.reader(csvfile, delimiter=',') #primeiro ele abre o csv com os programas/ies
			for linha in leitor_csv:

				logging.info('Iniciando raspagem da requisicao  %s', linha[0])
				self.clicar_consultar_paciente()
				info_write = self.iniciar_nova_consulta(linha[0])
				self.clicar_consultar_exame()
				self.iniciar_nova_consulta_exame(linha[0], info_write)
				

                
		logging.info('Fim da raspagem de dados...')
		logging.info('Os dados foram salvos no arquivo dados.csv')
		logging.info('Agradecr srs.: L.D, C.A, S.A, P.J')
		self.navegador.quit()

if __name__ == '__main__':
	logging.basicConfig(filename='acontecimentos.log', filemode = 'w', encoding='iso8859-1', level=logging.INFO)
	abrir = Navegador()
	abrir.iniciar_gal() 
	
    
