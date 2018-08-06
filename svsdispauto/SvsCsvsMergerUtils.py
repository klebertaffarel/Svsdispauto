import os

import datetime


def add_csvfile_to_drt(drt, csv_path, delimitador=';', datestr_fmt='%Y-%m-%d %H:%M:%S', sufixo=None, onlycols=None, create_constant_cols=[], create_cols_from_values_for_cols=[]):
    #Abre o arquivo passado
    csv_path = os.path.join(csv_path)
    print 'add_csvfile_to_drt:', csv_path, datetime.datetime.now()
    f = open(csv_path, 'r')
    linhas = f.readlines()
    #Extrai os nomes dos cabecalhos
    cabecalhos = linhas[0].strip().split(delimitador)
    #Monta uma lista de todos as colunas do CSV que devem ser importadas, atualizando tambem a lista de cabecalhos
    lista_cabecalhos = []
    lista_colunas = []
    i=2
    for col in cabecalhos[2:]:
        #Verifica se deve adicionar
        if onlycols==None or col in onlycols:
            lista_cabecalhos.extend([col])
            lista_colunas.extend([i])
        i+=1
    print 'lista_cabecalhos:', lista_cabecalhos
    print 'lista_colunas:', lista_colunas
    #Varre os dados:
    for linha in linhas[1:]:
        #Extrai todos os dados da linha
        list_linha = linha.strip().split(delimitador)
        if len(list_linha) > 2:
            #Extrai as datas de inicio/termino
            date_start = datetime.datetime.strptime(list_linha[0].strip('"'), datestr_fmt)
            date_end = datetime.datetime.strptime(list_linha[1].strip('"'), datestr_fmt)
            dict_data = {}

            #Extrai cada uma das colunas da lista filtrada
            i=0
            for c in lista_cabecalhos:
                chave_name = None
                valor = None
                #Checa se eh uma coluna que precisa utilizar valor como chave
                if c in create_cols_from_values_for_cols:
                    chave_name = c + "_" + str(list_linha[lista_colunas[i]])
                    valor = '1'
                else:
                    chave_name = c
                    valor = list_linha[lista_colunas[i]]
                if sufixo != None:
                    chave_name = sufixo + chave_name
                dict_data.update({chave_name: valor})
                i+=1

            #Adiciona colunas de constantes
            for const_col in create_constant_cols:
                chave_name = const_col[0]
                if sufixo != None:
                    chave_name = sufixo + chave_name
                dict_data.update({chave_name:const_col[1]})
            #Adiciona no objeto DateRangesTable
            drt.add_data(date_start, date_end, dict_data)
    return drt
