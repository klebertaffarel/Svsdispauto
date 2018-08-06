import os

DEBUG_MODE=False

class SvsDateRangesTable:
    def __init__(self):
        self._dados = []


    def sort_dados(self):
        has_changed = None
        while has_changed != False:
            has_changed = False
            i=0
            while i < (len(self._dados)-1):
                d = self._dados[i]
                d_next = self._dados[i+1]
                if d['date_start'] > d_next['date_start']:
                    #Reordena (troca os dois de posicao
                    aux = self._dados[i]
                    self._dados[i] = self._dados[i+1]
                    self._dados[i+1] = aux
                    if DEBUG_MODE: print 'REORDENADO'
                    has_changed = True
                    break
                i+=1





    def _insert_into_position(self, date_start, date_end, dict_data):
        #Insere os dados na posicao inicial correta (considera apenas o Date Start)
        idx_insert = 0
        i=0
        for d in self._dados:
            if date_start >= d['date_start']:
                idx_insert = i+1
            i+=1
        #Insere no indice especificado
        self._dados.insert(idx_insert, SvsDateRangesTable.aux_gera_dict_final(date_start, date_end, dict_data))



    def _find_first_overlap_index(self):
        #Varre a tabela atual verificando se ha interseccao de horarios de tempo
        #Primeiramente, sempre garante que a tabela estara ordenada
        self.sort_dados()
        i=0
        overlap_first_idx = None
        for d in self._dados:
            #Verifica se ha um proximo
            if i < (len(self._dados)-1):
                #Recupera o proximo slot
                d_next = self._dados[i+1]
                #Realiza a checagem
                if d['date_end'] > d_next['date_start']:
                    #Ha overlap!!
                    overlap_first_idx = i
                    break
            i+=1
        #Verifica se houve overlap
        #print 'overlap index:', overlap_first_idx
        return overlap_first_idx

    def _break_overlap(self, idx_start):
        #Recupera os itens
        d_1 = self._dados[idx_start]
        d_2 = self._dados[idx_start+1]
        #Trata a situacao que os horarios de inicio NAO sao iguais
        if d_1['date_start'] < d_2['date_start']:
            if d_1['date_end'] < d_2['date_end']:
                #Os 2 slots serao quebrados em 3
                if DEBUG_MODE: print 'Tratando quebra de 2 p/ 3'
                #--SLOT 1
                sl_1_date_start = d_1['date_start']
                sl_1_date_end = d_2['date_start']
                sl_1_data = d_1['data'].copy()
                sl_2_date_start = sl_1_date_end
                sl_2_date_end = d_1['date_end']
                sl_2_data = SvsDateRangesTable.mescla_informacoes(d_1['data'], d_2['data'])
                sl_3_date_start = sl_2_date_end
                sl_3_date_end = d_2['date_end']
                sl_3_data = d_2['data'].copy()
                #Remove os 2 slots atuais
                self._dados.pop(idx_start+1)
                self._dados.pop(idx_start)
                #Insere (reversamente para ficar ordenado) os novos slots
                self._dados.insert(idx_start, SvsDateRangesTable.aux_gera_dict_final(sl_3_date_start, sl_3_date_end, sl_3_data))
                self._dados.insert(idx_start, SvsDateRangesTable.aux_gera_dict_final(sl_2_date_start, sl_2_date_end, sl_2_data))
                self._dados.insert(idx_start, SvsDateRangesTable.aux_gera_dict_final(sl_1_date_start, sl_1_date_end, sl_1_data))
            else:
                #TODO
                if DEBUG_MODE: print 'Tratando data de termino do primeiro eh maior do que o termino do segundo!'
                #Tratando o caso de que o overlap com termindo do primeiro sendo maior que o termino do segundo
                #Nesse caso, apenas o primeiro intervalo (que eh o que extrapola) sera quebrado em 2. A partir disso,
                #sera gerado um outro erro no qual o proximo intervalo possuira mesmo horario de inicio, e entao podera
                #ser tratado no proximo loop
                sl_1_date_start = d_1['date_start']
                sl_1_date_end = d_2['date_start']
                sl_1_data = d_1['data'].copy()
                sl_2_date_start = sl_1_date_end
                sl_2_date_end = d_1['date_end']
                #Mantem os mesmos dados pois apenas esta segregando um dos slots
                sl_2_data = d_1['data'].copy()
                #Remove apenas o primeiro slot (que sera quebrado)
                self._dados.pop(idx_start)
                #Insere (reversamente para ficar ordenado) os novos slots
                self._dados.insert(idx_start, SvsDateRangesTable.aux_gera_dict_final(sl_2_date_start, sl_2_date_end, sl_2_data))
                self._dados.insert(idx_start, SvsDateRangesTable.aux_gera_dict_final(sl_1_date_start, sl_1_date_end, sl_1_data))


        else:
                #TODO
                if DEBUG_MODE: print 'Tratando - datas de inicio iguais'
                #Continuara quebrado em 2, mas verifica qual a menor data de termino
                if d_1['date_end'] > d_2['date_end']:
                    #Inverte ambos
                    aux = d_1
                    d_1 = d_2
                    d_2 = aux
                #Quebra em dois, ja assumindo que o primeiro eh o menos por conta da ordenacao acima
                sl_1_date_start = d_1['date_start']
                sl_1_date_end = d_1['date_end']
                sl_1_data = SvsDateRangesTable.mescla_informacoes(d_1['data'],d_2['data'])
                sl_2_date_start = d_1['date_end']
                sl_2_date_end = d_2['date_end']
                #Ja o segundo, que eh o maior, contem entao apenas informacao dele mesmo
                sl_2_data = d_2['data'].copy()
                #Remove os 2 slots atuais
                self._dados.pop(idx_start+1)
                self._dados.pop(idx_start)
                #Insere (reversamente para ficar ordenado) os novos slots
                self._dados.insert(idx_start, SvsDateRangesTable.aux_gera_dict_final(sl_2_date_start, sl_2_date_end, sl_2_data))
                self._dados.insert(idx_start, SvsDateRangesTable.aux_gera_dict_final(sl_1_date_start, sl_1_date_end, sl_1_data))

    def do_one_pass_overlap_break(self):
        had_overlap = False
        idx_overlap = self._find_first_overlap_index()
        if DEBUG_MODE: print 'has_overlap at:', idx_overlap
        if idx_overlap != None:
            had_overlap = True
            self._break_overlap(idx_overlap)
        return had_overlap

    def _remove_zero_duration_slots(self):
        #Realiza verificacao na ordem INVERSA, para nao ter que atualizar indices e fazer tudo em uma passada apenas
        i= len(self._dados)-1
        while i >=0:
            #Verifica se trata-se de um duration-zero
            if self._dados[i]['date_start'] == self._dados[i]['date_end']:
                if DEBUG_MODE: print 'DURATION ZERO========================'
                #Remove o duration zero:
                self._dados.pop(i)
            i-=1

    def add_data(self, date_start, date_end, dict_data):
        #Insere (posiciona) no vetor
        self._insert_into_position(date_start, date_end, dict_data)
        # while self._find_first_overlap_index() != None:
        #     idx_overlap = self._find_first_overlap_index()
        #     print 'has_overlap at:', idx_overlap
        #     self._break_overlap(idx_overlap)
        #Verifica se gerou overlaps e trata-os ate limpar tudo
        while self.do_one_pass_overlap_break() == True:
            pass
        #Realiza uma limpeza eliminando slots de tempo "zero" (horario inicio igual horario de termino)
        self._remove_zero_duration_slots()



    # def add_data(self, date_start, date_end, dict_data):
    #     idx_start_after = None
    #     idx_end_before = None
    #     #Verifica qual a posicao de inicio
    #     i=0
    #     for d in self._dados:
    #         if date_start >= d['date_start']:
    #             idx_start_after = i
    #             break
    #         i+=1
    #     #Verifica a posicao de termino
    #     i=0
    #     for d in self._dados:
    #         if date_end > d['date_end']:
    #             idx_end_before = i-1
    #             break
    #         i+=1
    #     print 'add_indexes - idx_start_after:', idx_start_after, ' idx_end_before:', idx_end_before
    #
    #     #Analisa a insercao
    #     idx_ini = None
    #     idx_last = None
    #     #--Inicio
    #     #Caso seja NONE, deve adicionar no indice zero mesmo
    #     idx_ini = idx_start_after
    #     if idx_start_after==None:
    #         idx_ini = 0
    #     #--Ultimo
    #     idx_last = idx_end_before
    #     if idx_end_before == None:
    #         idx_last = 0
    #     print 'insert_indexes - idx_ini:', idx_ini, ' idx_last:', idx_last
    #     #Realiza as insercoes
    #     if len(self._dados)==0:
    #         #Apenas insere, pois eh o primeiro
    #         self._dados.append(SvsDateRangesTable.aux_gera_dict_final(date_start, date_end, dict_data))
    #     else:
    #         #Processo recursivo, ate que o date_start seja igual o date_end
    #         while (date_start < date_end):
    #             print 'ENTRANDO NO WHILE'
    #             #Verifica a posicao inicial de insercao
    #             i=0
    #             x_idx_insert = None
    #             print 'len:', len(self._dados)
    #             while i < len(self._dados):
    #                 #Caso o dado sendo inserido seja maior do que o start da posicao atual, insere-o
    #                 d = self._dados[i]
    #                 if date_start >= d['date_start']:
    #                     #Aqui deve ser o inicio
    #                     x_idx_insert = i
    #                     break
    #                 i+=1
    #             #Caso nao tenha sido maior que nenhuma das entradas, deve ser colocado no inicio
    #             if x_idx_insert==None:
    #                 x_idx_insert=0
    #             #Caso o idx de insercao seja maior que o tamanho do vetor de dados, entao deve acrescentar por ultimo (append)
    #             if x_idx_insert >= len(self._dados):
    #                 #Acrescenta por ultimo
    #                 self._dados.append(SvsDateRangesTable.aux_gera_dict_final(date_start, date_end, dict_data))
    #                 #Atualiza os valores
    #                 date_start = date_end
    #             else:
    #                 #Verifica se o final do slot sendo inserido intersecciona com o proximo
    #                 if date_end <= d['date_start']:
    #                     #SEM interseccao
    #                     #Nao ha problema, basta criar um novo slot e acrescenta-lo
    #                     self._dados.insert(x_idx_insert, SvsDateRangesTable.aux_gera_dict_final(date_start, date_end, dict_data))
    #                     #Atualiza a data ja inserida
    #                     date_start = date_end
    #                 #TODO elif date_end == d['date_']
    #                 #elif


    @staticmethod
    def mescla_informacoes(dict_1, dict_2):
        resultado = {}
        if dict_1 != None:
            resultado.update(dict_1.copy())
        if dict_2 != None:
            resultado.update(dict_2.copy())
        return resultado


    @staticmethod
    def aux_gera_dict_final(date_start, date_end, dict_data):
        dict_final = {'date_start': date_start, 'date_end': date_end, 'data': dict_data}
        return dict_final

    def print_list(self, include_cols=False):
        print '=====TIME TABLES====================================='
        i=0
        for r in self._dados:
            if include_cols==False:
                print i, r['date_start'], '-', r['date_end']
            else:
                print i, r['date_start'], '-', r['date_end'], ' ', r['data']
            i+=1

    def export_csv(self, output_file, delimitador=';'):
        csv_matriz = []
        NONE_VALUE = ' '
        #--MONTA O CABECALHO--------------------------------------------------
        all_keys_set = set()
        for d in self._dados:
            all_keys_set.update(d['data'].keys())
        print 'all_keys:', all_keys_set
        cabecalhos = ['time_ini', 'time_end', 'duration_seg', 'duration_percent']
        cabecalhos.extend(all_keys_set)
        print 'cabecalhos:', cabecalhos
        csv_matriz.append(cabecalhos)
        #--EXTRAI OS DADOS----------------------------------------------------
        #--Estatisticas e campos auxiliares
        duracao_periodo_total = (self._dados[-1]['date_end'] - self._dados[0]['date_start']).total_seconds()
        for d in self._dados:
            duracao = (d['date_end']-d['date_start']).total_seconds()
            duracao_porcent = duracao/duracao_periodo_total
            list_linha = ['"'+str(d['date_start'])+'"', '"'+str(d['date_end'])+'"', str(duracao), str(duracao_porcent).upper()]
            for k in all_keys_set:
                list_linha.append(str(d['data'].get(k, NONE_VALUE)))
            #Salva a linha
            csv_matriz.append(list_linha)
        #--IMPRIME NA TELA O CSV FINAL
        for l in csv_matriz:
            print l
        #--Monta e escreve no arquivo
        output_file = os.path.join(output_file)
        f = open(output_file, 'w')
        for l in csv_matriz:
            f.write(delimitador.join(l) + "\n")
        f.close()
