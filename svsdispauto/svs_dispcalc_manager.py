import os
import shutil

import datetime

from dateutil.relativedelta import relativedelta

from svs_gerador_subperiodos import gera_subperiodos_from_mask
from svsdispauto import spk_searchs_factory, SvsCsvsMergerUtils, SvsSCP
from svsdispauto.SvsDateRangesTable import SvsDateRangesTable
from svsdispauto.spk_executor import SvsSpkExecutor
from svsdispauto.svs_cvswriter import svscsv_from_listdict
from svsdispauto.svs_dispcalc_enlace import extrai_dados_enlace, extrai_dados_sitio, extrai_base_chamados

#====================== CONFIGURACOES ========================================================================
DEBUG_MODE=True

DIR_BASE = os.path.join('.', 'base-20mar31-20mai01')

CSV_MATRIZ_OUTFILE = 'consolidacao_disponibilidade_2020mar31_2020mai01.csv'
CSV_MATRIZ_DELIMITADOR = ','



#--CONFIG DOS CHAMADOS---------------------------
CSV_CHAMADOS = 'base_chamados.csv'
#CHAMADOS_LISTA_IDS = [468, 559, 570, 1034,1042, 1106, 1128, 1245 ,1251, 1166, 1265, 1276, 1371, 1372, 1417, 1433, 1459, 1471, 1482, 1509,1520,1523,1526,1531,1542,1543,1624,1692,1715,1719,1720,1721,1722,1727,1732,1735,1748,1749]
CHAMADOS_LISTA_IDS = [1749]
#--CSV com Info dos Enlaces------------------------
CSV_ENLACES_FILEPATH = os.path.join('..', 'enlaces_base.csv')
#CSV_ENLACES_FILEPATH = os.path.join('..', 'enlaces_teste.csv')
#CSV_ENLACES_FILEPATH = os.path.join('..', 'enlac_corrig.csv')
CSV_FIELD_SITIO_A = 'SITE A'
CSV_FIELD_SITIO_B = 'SITE B'
CSV_FIELD_SITIO_TRUNK = 'TRUNK'
CSV_FIELD_SITIO_VERT_A = 'VERT. A'
CSV_FIELD_SITIO_VERT_B = 'VERT. B'
CSV_FIELD_SITIO_HORIZ_A = 'HORIZ. A'
CSV_FIELD_SITIO_HORIZ_B = 'HORIZ. B'
CSV_FIELD_DATA_ATIVACAO = 'DATA ATIVACAO'


#Periodo desejado dos dados
report_ini = datetime.datetime.strptime('2020-03-31 00:00:00', '%Y-%m-%d %H:%M:%S')
report_end = datetime.datetime.strptime('2020-05-01 23:59:59', '%Y-%m-%d %H:%M:%S')
CFG_MATRIZ_QUEBRAPOR_MES = True
CFG_MATRIZ_QUEBRAPOR_DIA = True


#Splunk
SPK_HOST = '10.254.22.79'
SPK_USER = 'admin'
SPK_PASSWD = 'SplunkN0c'

#Splunk - Fontes de dados
#zabdb_history
#--zab_hist_operststrunk_0001
#--zab_hist_operststrunk_0002
#--zab_hist_operststrunk_0003
#--zab_hist_operststrunk_0004
#--zab_hist_sysuptime

#novo_zabdb_history
#-FEITO POR TAFFAREL PARA RELATORIO RSR DE JAN-FEV-MAR
#--novo_import_statusoper_0001
#--novo_import_statusoper_0002
#--novo_import_statusoper_0003
#--novo_import_statusoper_0004

#novo_zabdbhistory
#-FEITO POR RODRIGO PARA RELATORIO RSR DE OUT-NOV-DEZ
#--novohist_opstatus_trk0001
#--novohist_opstatus_trk0002
#--novohist_opstatus_trk0003
#--novohist_opstatus_trk0004
#--novohist_system_upt

#--OperStatus
SPK_OPERSTATUS_SOURCE='novo_import*'
SPK_OPERSTATUS_SOURCETYPE='novo_zabdb_history*'
#--SysUp Times
#SPK_SYSUPS_SOURCE='zab_hist_sysuptime'
#SPK_SYSUPS_SOURCETYPE='zabdb_history'

#Envio da Matriz ao Splunk
dest_mat_scp_host='10.254.22.79'
dest_mat_scp_user='root'
dest_mat_scp_pwd ='s@visn0c'
dest_mat_scp_dir = '/opt/splunk/var/run/splunk/csv/'



#====================== INICIALIZACAO ========================================================================
#if os.path.exists(DIR_BASE):
#   shutil.rmtree(DIR_BASE)

#Checa se o diretorio existe
#if os.path.exists(DIR_BASE):
#   raise Exception("Erro, apague o diretorio para iniciar a geracao!")

#Cria o diretorio
#os.mkdir(DIR_BASE)

#Inicializa um gerenciador da interacao com Splunk
spk_executor = SvsSpkExecutor(SPK_HOST, SPK_USER, SPK_PASSWD)

#Inicializa uma tabela (Matriz) de DateRanges
drt = SvsDateRangesTable()



#====================== PREPARACAO ========================================================================
#Formata os periodos de filtro no Splunk
spk_periodo_ini = report_ini.strftime('%Y-%m-%dT%H:%M:%S.000')
spk_periodo_fim = report_end.strftime('%Y-%m-%dT%H:%M:%S.999')
if DEBUG_MODE: print 'SplunkPeriod - Earliest:', spk_periodo_ini
if DEBUG_MODE: print 'SplunkPeriod - Latest:', spk_periodo_fim

#Garante que havera uma quebra exata por mes, bem como uma coluna referenciando o periodo contemplado pelo relatorio
periodos_referencia = [
    [report_ini, report_end, {'ref_Periodo':1}]
]
#--Cria as quebras por mes
if CFG_MATRIZ_QUEBRAPOR_MES:
    timedelta_mes = relativedelta(months=1)
    lista_periodos_meses = gera_subperiodos_from_mask(periodo_ini=report_ini, periodo_end=report_end, time_mask="%Y_%m", mask_complement_value="_01 00:00:00", time_delta=timedelta_mes)
    for per in lista_periodos_meses:
        periodos_referencia.append([
            per[0],
            per[1],
            {'ref_' + per[0].strftime("%Y_%m"):1}
        ])

if CFG_MATRIZ_QUEBRAPOR_DIA:
    timedelta_dia = relativedelta(days=1)
    lista_periodos_dias = gera_subperiodos_from_mask(periodo_ini=report_ini, periodo_end=report_end, time_mask="%Y_%m_%d", mask_complement_value=" 00:00:00", time_delta=timedelta_dia)
    for per in lista_periodos_dias:
        periodos_referencia.append([
            per[0],
            per[1],
            {'ref_' + per[0].strftime("%Y_%m_%d"):1}
        ])


#Adiciona na matriz
for period in periodos_referencia:
    drt.add_data(period[0], period[1], period[2])


#====================== CARREGA DADOS DOS ENLACES ============================================================
f = open(CSV_ENLACES_FILEPATH, 'r')
aux_linhas = f.readlines()
aux_linhas_list = []
for li in aux_linhas:
    aux_linhas_list.append(li.strip().split(','))

#--Headers
aux_enlaces_headers = aux_linhas_list[0]
if DEBUG_MODE: print 'aux_enlaces_headers:', aux_enlaces_headers
aux_enlace_headers_dict = {
    CSV_FIELD_SITIO_A: aux_enlaces_headers.index(CSV_FIELD_SITIO_A),
    CSV_FIELD_SITIO_B: aux_enlaces_headers.index(CSV_FIELD_SITIO_B),
    CSV_FIELD_SITIO_TRUNK: aux_enlaces_headers.index(CSV_FIELD_SITIO_TRUNK),
    CSV_FIELD_SITIO_HORIZ_A: aux_enlaces_headers.index(CSV_FIELD_SITIO_HORIZ_A),
    CSV_FIELD_SITIO_HORIZ_B: aux_enlaces_headers.index(CSV_FIELD_SITIO_HORIZ_B),
    CSV_FIELD_SITIO_VERT_A: aux_enlaces_headers.index(CSV_FIELD_SITIO_VERT_A),
    CSV_FIELD_SITIO_VERT_B: aux_enlaces_headers.index(CSV_FIELD_SITIO_VERT_B),
    CSV_FIELD_DATA_ATIVACAO: aux_enlaces_headers.index(CSV_FIELD_DATA_ATIVACAO)
}
if DEBUG_MODE: print aux_enlace_headers_dict


aux_enlaces = aux_linhas_list[1:]

#Monta uma lista estruturada dos enlaces
lista_enlaces = []
lista_sitios = set()
for li in aux_enlaces:
    dict_enlace = {
        'sitio_A': li[aux_enlace_headers_dict.get(CSV_FIELD_SITIO_A)],
        'sitio_B': li[aux_enlace_headers_dict.get(CSV_FIELD_SITIO_B)],
        'trunk': li[aux_enlace_headers_dict.get(CSV_FIELD_SITIO_TRUNK)].zfill(4),
        'trunk_bkp': li[aux_enlace_headers_dict.get(CSV_FIELD_SITIO_TRUNK)],
        'data_ativacao': li[aux_enlace_headers_dict.get(CSV_FIELD_DATA_ATIVACAO)]
    }
    lista_enlaces.append(dict_enlace)
    lista_sitios.add(li[aux_enlace_headers_dict.get(CSV_FIELD_SITIO_A)])
    lista_sitios.add(li[aux_enlace_headers_dict.get(CSV_FIELD_SITIO_B)])

lista_sitios = list(lista_sitios)
if DEBUG_MODE: print 'lista_enlaces:', lista_enlaces
#-Filtros temporarios de TESTE - Pode Remover!
#lista_enlaces = lista_enlaces[0:2]
#lista_sitios = lista_sitios[0:5]
print lista_enlaces

#====================== EXTRACAO DADOS ENLACES ============================================================
#for enl in lista_enlaces:
#   #Extrai os dados de gerais do enlace
#     extrai_dados_enlace(sitio_A=enl['sitio_A'], sitio_B=enl['sitio_B'], trunk=enl['trunk'],trunk_bkp=enl['trunk_bkp'], dir_base=DIR_BASE,
#                         spk_executor_ref=spk_executor, spk_earliest=spk_periodo_ini, spk_latest=spk_periodo_fim,
#                         spk_operstatus_sourcetype=SPK_OPERSTATUS_SOURCETYPE,
#                         spk_operstatus_source=SPK_OPERSTATUS_SOURCE)



#====================== EXTRACAO DADOS SITIOS ============================================================
#for sit in lista_sitios:
#     #Extrai dados especificos do sitio
#     extrai_dados_sitio(sitio=sit, dir_base=DIR_BASE, spk_executor_ref=spk_executor,
#                        spk_earliest=spk_periodo_ini, spk_latest=spk_periodo_fim,
#                        spk_sysups_sourcetype=SPK_SYSUPS_SOURCETYPE,
#                        spk_sysups_source=SPK_SYSUPS_SOURCE)


#====================== EXTRACAO DOS CHAMADOS ============================================================
#extrai_base_chamados(lista_chamados=CHAMADOS_LISTA_IDS, dir_base=DIR_BASE, csv_output=CSV_CHAMADOS,
#                     spk_executor_ref=spk_executor, spk_earliest=spk_periodo_ini, spk_latest=spk_periodo_fim)


#====================== CONSOLIDACAO DE MATRIZ COMPLETA ============================================================
#---Dados dos Enlaces--
for enl in lista_enlaces:
    #Add Rodrigo/Taffarel 24/jan/2019 - Coluna informando (com 0 e 1) o periodo que o enlace estava ATIVO. Considera-se a data "final" como a data final do relatorio sendo gerado.
    #--Gera um objeto Datetime com a data de inicio
    enlace_ativ_inicio = datetime.datetime.strptime(enl['data_ativacao'], '%Y-%m-%d %H:%M:%S')
    #--Para definir o INICIO, compara os periodos que o Relatorio esta sendo gerado com o do enlace, de modo a obter uma INTERSECAO dos periodos. Isto pode ser feito pegando a MAIOR data entre os dois
    enlace_ativ_inicio = max(enlace_ativ_inicio, report_ini)
    #--Recupera objeto Datetime com o periodo final do relatorio
    enlace_ativ_termino = report_end
    #Apenas acrescenta valores caso a data de ativacao seja MENOR do que a data final do Relatorio. Caso contrario, acrescenta uma coluna em branco


    enlace_ativo_nome_coluna = enl['sitio_A'] + 'x' + enl['sitio_B'] + "_ativado"
    if enlace_ativ_inicio <= report_end:
        #--Acrescenta uma coluna na matriz indicando com "1" este periodo que o enlace esteve ativo
        #--Nome da Coluna: SITIO_Ax_Sitio_B_ativo
        #enlace_ativo_nome_coluna = enl['sitio_A'] + 'x' + enl['sitio_B'] + "_ativado"
        #--Acrescenta na Matriz Completa
        drt.add_data(enlace_ativ_inicio, enlace_ativ_termino, {enlace_ativo_nome_coluna: 1})
    else:
        #Apenas acrescenta uma coluna vazia
        drt.add_data(report_ini, report_end, {enlace_ativo_nome_coluna: ""})

    # # --OperStatus SemColeta Periodos BINARIOS - Sitio A
    # SvsCsvsMergerUtils.add_csvfile_to_drt(drt, os.path.join(DIR_BASE, enl['sitio_A']+'_semColeta_'+ enl['trunk'] +'.csv'), delimitador=",",
    #                                       create_constant_cols=[[enl['sitio_A']+'_SCol_'+enl['trunk'], 1]], onlycols=[],
    #                                       datestr_fmt='%Y-%m-%d %H:%M:%S.%f')
    # # --OperStatus SemColeta Periodos BINARIOS - Sitio B
    # SvsCsvsMergerUtils.add_csvfile_to_drt(drt, os.path.join(DIR_BASE, enl['sitio_B']+'_semColeta_'+ enl['trunk'] +'.csv'), delimitador=",",
    #                                       create_constant_cols=[[enl['sitio_B']+'_SCol_'+enl['trunk'], 1]], onlycols=[],
    #                                       datestr_fmt='%Y-%m-%d %H:%M:%S.%f')

    # --OperStatus SemColeta Periodos COM VALOR DO DELTA - Sitio A
    SvsCsvsMergerUtils.add_csvfile_to_drt(drt, os.path.join(DIR_BASE, enl['sitio_A']+'_semColeta_'+ enl['trunk'] +'.csv'), delimitador=",",
                                          onlycols=['delta_tempo'],
                                          sufixo=enl['sitio_A']+"_SColTempo_"+enl['trunk']+'_',
                                          datestr_fmt='%Y-%m-%d %H:%M:%S.%f')
    # --OperStatus SemColeta Periodos COM VALOR DO DELTA - Sitio B
    SvsCsvsMergerUtils.add_csvfile_to_drt(drt, os.path.join(DIR_BASE, enl['sitio_B']+'_semColeta_'+ enl['trunk'] +'.csv'), delimitador=",",
                                          onlycols=['delta_tempo'],
                                          sufixo=enl['sitio_B']+"_SColTempo_"+enl['trunk']+'_',
                                          datestr_fmt='%Y-%m-%d %H:%M:%S.%f')


    # --OperStatus nOK - Sitio A
    SvsCsvsMergerUtils.add_csvfile_to_drt(drt, os.path.join(DIR_BASE, enl['sitio_A'] + '_operNok_'+enl['trunk'] + '.csv'), delimitador=",",
                                          create_constant_cols=[[enl['sitio_A']+ '_nOK_'+enl['trunk'], 1]], onlycols=[],
                                          datestr_fmt='%Y-%m-%d %H:%M:%S.%f')
    # --OperStatus nOK - Sitio B
    SvsCsvsMergerUtils.add_csvfile_to_drt(drt, os.path.join(DIR_BASE, enl['sitio_B'] + '_operNok_' + enl['trunk'] + '.csv'),
                                          delimitador=",",
                                          create_constant_cols=[[enl['sitio_B'] + '_nOK_' + enl['trunk'], 1]], onlycols=[],
                                          datestr_fmt='%Y-%m-%d %H:%M:%S.%f')

#---Dados dos SysUp Times--
#for sit in lista_sitios:
#    #--SysUp Times----
#    SvsCsvsMergerUtils.add_csvfile_to_drt(drt, os.path.join(DIR_BASE, sit+'_sysUps.csv'), delimitador=",",
#                                          create_constant_cols=[[sit+'_SysUpDeslig', 1]], onlycols=['Equipamento'],
#                                          create_cols_from_values_for_cols=['Equipamento'],
#                                          datestr_fmt='%Y-%m-%d %H:%M:%S.%f')

#---Dados dos Chamados--
#Chamados por Sitio  e tambem por SITIO_ID
SvsCsvsMergerUtils.add_csvfile_to_drt(drt, os.path.join(DIR_BASE, CSV_CHAMADOS), delimitador=",",
                                          create_constant_cols=[['Chamados_Desconto', 1]], onlycols=['chamados', 'localidade_id'],
                                          create_cols_from_values_for_cols=['chamados', 'localidade_id'],
                                          datestr_fmt='%Y-%m-%d %H:%M:%S')


drt.print_list(include_cols=True)

aux_filepath_saida = os.path.join(DIR_BASE,CSV_MATRIZ_OUTFILE)
drt.export_csv(aux_filepath_saida, delimitador=CSV_MATRIZ_DELIMITADOR)


#====================== ENVIO AO SPLUNK ============================================================
SvsSCP.envia_arquivo(aux_filepath_saida, dest_mat_scp_dir, dest_mat_scp_host, dest_mat_scp_user, dest_mat_scp_pwd)




#====================== GERACAO DE CONSULTA-BASE PRE-CONSOLIDANDO DADOS DA MATRIZ NO SPLUNK==========================
str_search = spk_searchs_factory.search_matriz_disponibilidade(lista_enlaces=lista_enlaces, lista_sitios=lista_sitios, arquivo_matriz=CSV_MATRIZ_OUTFILE)

#TODO Executa a consulta-base e gera um CSV com todos os detalhes
print 'str_search:', str_search
