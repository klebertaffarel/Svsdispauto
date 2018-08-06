# -*- coding: utf-8 -*-
import os
import datetime

DEBUG_MODE=False

def addconvert_csvcolumn_to_drt(drt, csv_path, delimitador=';', datestr_fmt='%Y-%m-%d %H:%M:%S', list_slots_from_columns=[]):
    #Abre o arquivo passado
    csv_path = os.path.join(csv_path)
    f = open(csv_path, 'r')
    linhas = f.readlines()
    #Extrai os nomes dos cabecalhos
    cabecalhos = linhas[0].strip().split(delimitador)
    print 'cabecalhos:', cabecalhos
    #Varre as linhas, quebrando cada uma delas nos SlotTimes definidos
    for linha in linhas[1:]:
        if DEBUG_MODE: print 'PROCESSANDO Linha ================================================================================='
        #Quebra a linha em um vetor
        linha = linha.strip().split(delimitador)
        #Cria e adiciona cada um dos Slot Times
        for st in list_slots_from_columns:
            # Identifica o nome da coluna
            # Extrai o indice da coluna que contera o nome da coluna nova nos Slots Times
            column_name = ''
            if st.get('column_name_sufix', None) != None:
                column_name += st.get('column_name_sufix')
            if st.get('column_name_from_column', None) != None:
                idx_slots_column_name = cabecalhos.index(st['column_name_from_column'])
                if DEBUG_MODE: print 'idx_slots_column_name:', idx_slots_column_name
                if idx_slots_column_name >= 0:
                    column_name += linha[idx_slots_column_name]

            #Extrai as datas de inicio e termino
            idx_date_start = cabecalhos.index(st['date_start_column'])
            idx_date_end = cabecalhos.index(st['date_end_column'])
            if DEBUG_MODE: print 'teste:', linha[idx_date_start]
            str_date_start = linha[idx_date_start]
            str_date_end = linha[idx_date_end]
            #Checa se possue as datas
            date_start = None
            date_end = None
            if (str_date_start!='' and str_date_end!=''):
                date_start = datetime.datetime.strptime(str_date_start, datestr_fmt)
                date_end = datetime.datetime.strptime(str_date_end, datestr_fmt)
            #Decide se deve ignorar ranges sem data/hora
            if (date_start!=None and date_end!=None) or st.get('ignore_when_no_date',False)==False:
                if DEBUG_MODE: print 'column_name:', column_name, 'data_start:', date_start, 'date_end:', date_end
                #Adiciona na tabela
                drt.add_data(date_start, date_end, {column_name:st['value_constant']})


    return drt