


def svscsv_from_listdict(list_dicts=None,  list_headers=[], output_file=None, null_value="", delimitador=','):
    #Monta a lista de linhas em strings
    lista_linhas_str = []

    #Monta os cabecalhos
    str_headers = delimitador.join(list_headers)
    lista_linhas_str.append(str_headers)

    #Monta as linhas
    for d in list_dicts:
        #Monta uma lista temporaria para conter os campos desta linha
        list_linha = []
        #Recupera o valor de cada um dos headers
        for h in list_headers:
            list_linha.append(d.get(h, null_value))
        #Monta a string da linha
        str_linha = delimitador.join(list_linha)
        #Salva a string da linha
        lista_linhas_str.append(str_linha)

    #Abre e salva o arquivo
    f = open(output_file, 'w')
    for str_li in lista_linhas_str:
        print str_li
        f.write(str_li + "\n")
    f.close()





