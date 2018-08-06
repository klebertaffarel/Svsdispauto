import os
import shutil

import datetime

from svsdispauto import spk_searchs_factory, SvsCsvsMergerUtils, SvsSCP
from svsdispauto.SvsDateRangesTable import SvsDateRangesTable
from svsdispauto.spk_executor import SvsSpkExecutor
from svsdispauto.svs_cvswriter import svscsv_from_listdict
from svsdispauto.svs_dispcalc_enlace import extrai_dados_enlace, extrai_dados_sitio




#====================== CONFIGURACOES ========================================================================
DEBUG_MODE=True

DIR_BASE = os.path.join('.', 'base-17set01-18jun29')

CSV_MATRIZ_OUTFILE = 'consolidacao_disponibilidade_2017set01_2018jun29.csv'
CSV_MATRIZ_DELIMITADOR = ','

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
    CSV_FIELD_SITIO_VERT_B: aux_enlaces_headers.index(CSV_FIELD_SITIO_VERT_B)
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



#====================== GERACAO DE CONSULTA-BASE PRE-CONSOLIDANDO DADOS DA MATRIZ NO SPLUNK==========================
str_search = spk_searchs_factory.search_matriz_disponibilidade(lista_enlaces=lista_enlaces, lista_sitios=lista_sitios, arquivo_matriz=CSV_MATRIZ_OUTFILE)

print 'str_search:', str_search



