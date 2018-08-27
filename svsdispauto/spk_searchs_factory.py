
CFG_SPK_ZAB_INDEX='zabbix'
CFG_SPK_ZAB_SOURCETYPE='zabdb_history'



def search_operstatus_semcoleta(host_swl3, trunk, trunk_bkp, spk_index=CFG_SPK_ZAB_INDEX, spk_sourcetype=CFG_SPK_ZAB_SOURCETYPE, spk_source=None):
    str_search = """
        search index="<<<%SPK_INDEX%>>>" sourcetype=<<<%SPK_SOURCETYPE%>>> source="<<<%SPK_SOURCE%>>>"
        | lookup tstrod_lookups_items.csv itemid
        | lookup tstrod_lookups_hosts.csv hostid  
        | search host_name="*<<<%HOST%>>>*" AND item_key=*Trunk*Port*ID*<<<%TRUNK%>>>* OR item_key=*Trunk32<<<%TRUNK_BKP%>>>*
        | sort 0 _time
        | streamstats current=true window=2 earliest(clock) as last_clock, earliest(itemid) as last_itemid, earliest(datetime) as last_datetime
        | eval diff_itemid=last_itemid - itemid
        | eval last_clock = last_clock
        | eval delta_tempo = (clock - last_clock) 
        | eval is_faltacoleta = IF((_time > strptime("2017-09-20 19:50", "%Y-%m-%d %H:%M") AND delta_tempo >= 2.5*60) OR (_time <= strptime("2017-09-20 19:50", "%Y-%m-%d %H:%M") AND delta_tempo > 2.5*300), 1, 0)
        | eval is_faltacoleta = IF(delta_tempo > 3500 AND delta_tempo <= 3800 AND (strftime(_time, "%Y-%m-%d %H")="2018-02-17 23" OR strftime(_time, "%Y-%m-%d %H")="2018-02-18 00"),0,is_faltacoleta) 
        | where  is_faltacoleta=1
        | table last_datetime, datetime, host_name, item_key, delta_tempo
        | rename last_datetime AS dh_inicio, datetime as dh_termino, host_name AS Equipamento, item_key AS Trunk
        """
    str_search = str_search.replace("<<<%SPK_INDEX%>>>", str(spk_index))
    str_search = str_search.replace("<<<%SPK_SOURCETYPE%>>>", str(spk_sourcetype))
    str_search = str_search.replace("<<<%SPK_SOURCE%>>>", str(spk_source))

    str_search = str_search.replace("<<<%HOST%>>>", host_swl3 + "_SWL3")
    str_search = str_search.replace("<<<%TRUNK%>>>", str(trunk))
    str_search = str_search.replace("<<<%TRUNK_BKP%>>>", str(trunk_bkp))


    return str_search



def search_operstatus_nok(host_swl3, trunk, trunk_bkp, spk_index=CFG_SPK_ZAB_INDEX,
                                    spk_sourcetype=CFG_SPK_ZAB_SOURCETYPE, spk_source=None):
        str_search = """
        search index="<<<%SPK_INDEX%>>>" sourcetype=<<<%SPK_SOURCETYPE%>>> source="<<<%SPK_SOURCE%>>>"
            | lookup tstrod_lookups_items.csv itemid
            | lookup tstrod_lookups_hosts.csv hostid  
            | search host_name="*<<<%HOST%>>>" AND item_key="*Trunk*Port*ID*<<<%TRUNK%>>>*"
            | sort 0 itemid, _time
            | streamstats current=true window=2 earliest(clock) as last_clock, earliest(itemid) as last_itemid, earliest(datetime) as last_datetime, earliest(value) as last_value by itemid
            | eval diff_itemid=last_itemid - itemid
            | eval delta_value = last_value - value
            | eval last_clock = last_clock
            | eval delta_tempo = (clock - last_clock) 
            | eval is_opersts_nOk = IF(value=1,0,1)
            | eval tempo_opersts_nOk = IF(is_opersts_nOk=1,
                                                   IF(_time > strptime("2017-09-20 19:50", "%Y-%m-%d %H:%M"),60, 300),
                                             "")
            |search delta_value!=0 
            |streamstats current=true window=2 earliest(delta_value) AS perini_delta_value, earliest(datetime) as perini_datetime, earliest(clock) as perini_clock
            |eval is_periodo = IF(perini_delta_value=-4 AND delta_value=4, 1, 0) 
            |eval tempo_periodo = (clock - perini_clock)
            |search is_periodo=1
            |table perini_datetime, datetime, tempo_periodo, tempo_opersts_nOk, delta_value, is_periodo
            |rename perini_datetime AS dh_inicio, datetime AS dh_termino
            """
        str_search = str_search.replace("<<<%SPK_INDEX%>>>", str(spk_index))
        str_search = str_search.replace("<<<%SPK_SOURCETYPE%>>>", str(spk_sourcetype))
        str_search = str_search.replace("<<<%SPK_SOURCE%>>>", str(spk_source))

        str_search = str_search.replace("<<<%HOST%>>>", host_swl3 + "_SWL3")
        str_search = str_search.replace("<<<%TRUNK%>>>", str(trunk))
        str_search = str_search.replace("<<<%TRUNK_BKP%>>>", str(trunk_bkp))

        return str_search





def search_sysuptimes(host_sitio, spk_index=CFG_SPK_ZAB_INDEX,
                                    spk_sourcetype=CFG_SPK_ZAB_SOURCETYPE, spk_source=None):
        str_search = """
        search index="<<<%SPK_INDEX%>>>" sourcetype=<<<%SPK_SOURCETYPE%>>> source="<<<%SPK_SOURCE%>>>"
            | lookup tstrod_lookups_items.csv itemid
            | lookup tstrod_lookups_hosts.csv hostid  
            | search (host_name="*<<<%HOST%>>>" OR host_name="*<<<%HOST%>>>_SWL3") 
            | eval is_uptime_ms=IF(match(substr(host_name,1,3),"SW0") OR match(substr(host_name,1,3),"RD0"), 1,0)
            | eval value=IF(is_uptime_ms==1, value/100,value)
            | sort 0 itemid, _time
            | streamstats current=true window=2 earliest(clock) as last_clock, earliest(itemid) as last_itemid, earliest(datetime) as last_datetime, earliest(value) as last_value by itemid
            | eval diff_itemid=last_itemid - itemid
            | search diff_itemid=0
            | eval last_clock = last_clock
            | eval delta_tempo = (clock - last_clock)
            | eval delta_uptime = (value - last_value) 
            | eval razao_tempoUptime = delta_uptime/delta_tempo
            | eval ligado_desde_timestamp = (clock - value)
            | eval ligado_desde_datetime = strftime(ligado_desde_timestamp, "%F %T.%1N")
            | eval tempo_indisponivel_ajustado = delta_tempo - value
            | eval is_resincronismo_tempo_proxy = IF(tempo_indisponivel_ajustado < 0,1,0)
            | search (razao_tempoUptime < 0.95) AND (value <= delta_tempo) AND is_resincronismo_tempo_proxy=0
            | table last_datetime, ligado_desde_datetime, datetime, host_name, value, last_value, delta_tempo, tempo_indisponivel_ajustado, is_resincronismo_tempo_proxy, razao_tempoUptime, diff_itemid, itemid, last_itemid, is_uptime_ms
            | rename datetime AS HoraDeteccao, value AS Uptime, last_value AS UltimoUptime, last_datetime as UltimoUptimeData, delta_tempo as TempoIndisponivel, host_name as Equipamento, tempo_indisponivel_ajustado AS TempoIndispAjustado, ligado_desde_datetime AS LigadoAs, is_resincronismo_tempo_proxy AS ProvavelResincHorarioProxy
            | rename UltimoUptimeData AS dh_ultima_coleta, LigadoAs AS dh_equip_ligado, HoraDeteccao AS dh_primeira_coleta
            """
        str_search = str_search.replace("<<<%SPK_INDEX%>>>", str(spk_index))
        str_search = str_search.replace("<<<%SPK_SOURCETYPE%>>>", str(spk_sourcetype))
        str_search = str_search.replace("<<<%SPK_SOURCE%>>>", str(spk_source))

        str_search = str_search.replace("<<<%HOST%>>>", host_sitio)

        return str_search


def search_base_chamados(lista_chamados):
    str_search = """
        |savedsearch RepSlaNocInput 
            |fields ID, _Atendimento, _ReestabSistema, _SolucaoDefinitiva, Localidade
            |where """
    aux_lista = []
    for chamado in lista_chamados:
        aux_lista.append("ID==" + str(chamado))
    str_search+= " OR ".join(aux_lista)
    str_search+= """
            |eval dh_inicio=strftime(_Atendimento, "%Y-%m-%d %H:%M:%S")
            |eval dh_termino=strftime(IF(isnull(_ReestabSistema),_SolucaoDefinitiva, _ReestabSistema), "%Y-%m-%d %H:%M:%S")
            |eval localidade_id=Localidade."_".ID
            |fields dh_inicio, dh_termino, ID, Localidade, localidade_id
            |rename Localidade AS chamados
            """

    return str_search



def search_matriz_disponibilidade(lista_enlaces, lista_sitios, arquivo_matriz=None, ranges_indisp=[5,10,30,60,240,480]):
    #Monta uma grande SEARCH responsavel por fornecer todos os dados e indicadores de disponibilidade
    str_search = " | inputcsv " + arquivo_matriz
    str_search+= """
        |eval CFG_THRESH_DISP=2*65
        |eval CFG_THRESH_INTERMIT=5*60
        |eval ano_mes=substr(time_ini,1,7)
        |eval ano_mes_dia=substr(time_ini,1,10)
        |fields time_ini, time_end, duration_seg, ano_mes, * """
    #Aqui esta baseado no campo binario de janela de indisponibilidade
    #template_sitio_indisp = "| eval <<<%HOST%>>>_<<<%TRUNK%>>>_indisp=IF(<<<%HOST%>>>_SCol_<<<%TRUNK%>>>==1 OR <<<%HOST%>>>_nOk_<<<%TRUNK%>>>==1,1,0)"
    #--Aqui calculado com um threshold em cima do valor minimo de threshold da janela de disponibilidade------
    #- HOST_TRUNK_indisp
    template_sitio_indisp = "| eval <<<%HOST%>>>_<<<%TRUNK%>>>_indisp=IF(<<<%HOST%>>>_SColTempo_<<<%TRUNK%>>>_delta_tempo > CFG_THRESH_DISP OR <<<%HOST%>>>_nOk_<<<%TRUNK%>>>==1,1,0)"
    #- HOST_TRUNK_intermit
    template_sitio_intermit = '| eval <<<%HOST_A%>>>_<<<%TRUNK%>>>_intermit=IF(<<<%HOST_A%>>>_<<<%TRUNK%>>>_sysup_deslig==0 AND (<<<%HOST_A%>>>_SColTempo_<<<%TRUNK%>>>_delta_tempo <= CFG_THRESH_INTERMIT) AND !(<<<%HOST_B%>>>_nOk_<<<%TRUNK%>>>==1),1,0)'
    #- HOST_TRUNK_chamados
    template_sitio_chamados = '| eval <<<%HOST%>>>_<<<%TRUNK%>>>_chamados=IF(chamados_MS<<<%HOST%>>>==1 OR chamados_PR<<<%HOST%>>>==1,1,0)'
    #--Calcula a indisponibilidade do enlace
    #- HOST_AxHOST_B_indisp
    template_enlace_indisp = "| eval <<<%HOST_A%>>>x<<<%HOST_B%>>>_indisp=IF(<<<%HOST_A%>>>_<<<%TRUNK%>>>_indisp==1 OR <<<%HOST_B%>>>_<<<%TRUNK%>>>_indisp==1,1,0)"
    #- HOST_AxHOST_B_classifind_tempo
    template_enlace_classifind_tempo = '| eval <<<%HOST_A%>>>x<<<%HOST_B%>>>_classifind_tempo=IF(<<<%HOST_A%>>>x<<<%HOST_B%>>>_indisp==1, max(<<<%HOST_A%>>>_SColTempo_<<<%TRUNK%>>>_delta_tempo,<<<%HOST_B%>>>_SColTempo_<<<%TRUNK%>>>_delta_tempo),"")'
    #- HOST_AxHOST_B_classifind
    template_enlace_classifind = '| eval <<<%HOST_A%>>>x<<<%HOST_B%>>>_classifind=CASE(<<<%HOST_A%>>>x<<<%HOST_B%>>>_classifind_tempo=="",""'
    if ranges_indisp!=None and len(ranges_indisp)>1:
        for rng in ranges_indisp:
            template_enlace_classifind += ',<<<%HOST_A%>>>x<<<%HOST_B%>>>_classifind_tempo <= 60*' + str(rng) + ', "'+str(rng)+ '"'
        template_enlace_classifind += ',<<<%HOST_A%>>>x<<<%HOST_B%>>>_classifind_tempo > 60*' + str(max(ranges_indisp)) + ',"' + str(max(ranges_indisp)) + '_mais"'
    template_enlace_classifind+= ')'
    #--Calcula os periodos onde nao eh possivel afirmar que os equipamentos estavam ligados, por TRUNK
    #- HOST_TRUNK_sysup_deslig
    template_sitio_sysup_deslig_trunk ="| eval <<<%HOST%>>>_<<<%TRUNK%>>>_sysup_deslig=IF(Equipamento_MS<<<%HOST%>>>_SWL3==1 OR Equipamento_PR<<<%HOST%>>>_SWL3==1,1,0) "
    #--Calcula pro enlace os periodos onde nao eh possivel afirmar que todos os equipamentos estavam ligados
    #- HOST_AxHOST_B_sysup_deslig =
    template_enlace_sysup_deslig = "|eval <<<%HOST_A%>>>x<<<%HOST_B%>>>_sysup_deslig=IF(<<<%HOST_A%>>>_<<<%TRUNK%>>>_sysup_deslig==1 OR <<<%HOST_B%>>>_<<<%TRUNK%>>>_sysup_deslig==1,1,0)"
    #--Calcula a disponibilidade ajustada, descontando os periodos onde pode-se afirmar que os equipamentos estavam LIGADOS e nao houve coleta do tipo "Nao-OK"
    #- HOST_AxHOST_B_sombra
#    template_enlace_sombra = "|eval <<<%HOST_A%>>>x<<<%HOST_B%>>>_sombra=IF(<<<%HOST_A%>>>x<<<%HOST_B%>>>_indisp==1 AND <<<%HOST_A%>>>_nOk_<<<%TRUNK%>>>!=1 AND <<<%HOST_B%>>>_nOk_<<<%TRUNK%>>>!=1 AND <<<%HOST_A%>>>x<<<%HOST_B%>>>_sysup_deslig==0,1,0)"
    template_enlace_sombra = "|eval <<<%HOST_A%>>>x<<<%HOST_B%>>>_sombra=IF( (<<<%HOST_A%>>>_SColTempo_<<<%TRUNK%>>>_delta_tempo > CFG_THRESH_DISP) AND (<<<%HOST_B%>>>_SColTempo_<<<%TRUNK%>>>_delta_tempo > CFG_THRESH_DISP) AND <<<%HOST_A%>>>x<<<%HOST_B%>>>_sysup_deslig==0,1,0)"
    #- HOST_AxHOST_B_intermitencia
    template_enlace_intermitencia = "|eval <<<%HOST_A%>>>x<<<%HOST_B%>>>_intermitencia=IF(<<<%HOST_A%>>>_<<<%TRUNK%>>>_intermit==1 OR <<<%HOST_B%>>>_<<<%TRUNK%>>>_intermit==1,1,0)"
    #- HOST_AxHOST_B_indisp
    template_enlace_indisp_intermit = "| eval <<<%HOST_A%>>>x<<<%HOST_B%>>>_indisp_intermit=IF(<<<%HOST_A%>>>x<<<%HOST_B%>>>_indisp==1 AND <<<%HOST_A%>>>x<<<%HOST_B%>>>_intermitencia==0,1,0)"
    #- HOST_AxHOST_B_chamados
    template_enlace_chamados = "|eval <<<%HOST_A%>>>x<<<%HOST_B%>>>_chamados=IF(<<<%HOST_A%>>>_<<<%TRUNK%>>>_chamados==1 OR <<<%HOST_B%>>>_<<<%TRUNK%>>>_chamados==1,1,0)"
    #- HOST_AxHOST_B_indisp_sombras
    template_enlace_indisp_sombras = "|eval <<<%HOST_A%>>>x<<<%HOST_B%>>>_indisp_sombras=IF(<<<%HOST_A%>>>x<<<%HOST_B%>>>_indisp_intermit==1 AND <<<%HOST_A%>>>x<<<%HOST_B%>>>_sombra==0,1,0)"
    #- HOST_AxHOST_B_indisp_chamados
    template_enlace_indisp_chamados = "|eval <<<%HOST_A%>>>x<<<%HOST_B%>>>_indisp_chamados=IF(<<<%HOST_A%>>>x<<<%HOST_B%>>>_indisp_intermit==1 AND <<<%HOST_A%>>>x<<<%HOST_B%>>>_chamados==0,1,0)"
    #- HOST_AxHOST_B_indisp_ajustada
    template_enlace_indisp_ajustada = "|eval <<<%HOST_A%>>>x<<<%HOST_B%>>>_indisp_ajustada=IF(<<<%HOST_A%>>>x<<<%HOST_B%>>>_indisp_intermit==1 AND <<<%HOST_A%>>>x<<<%HOST_B%>>>_sombra==0 AND <<<%HOST_A%>>>x<<<%HOST_B%>>>_chamados==0,1,0)"

    #--Calcula os tempos em segundos
    template_enlace_indisp_segundos="|eval <<<%HOST_A%>>>x<<<%HOST_B%>>>_indisp_segundos=duration_seg*<<<%HOST_A%>>>x<<<%HOST_B%>>>_indisp"
    template_enlace_deslig_segundos="|eval <<<%HOST_A%>>>x<<<%HOST_B%>>>_deslig_segundos=duration_seg*<<<%HOST_A%>>>x<<<%HOST_B%>>>_sysup_deslig"
    template_enlace_sombra_segundos="|eval <<<%HOST_A%>>>x<<<%HOST_B%>>>_sombra_segundos=duration_seg*<<<%HOST_A%>>>x<<<%HOST_B%>>>_sombra"
    template_enlace_intermit_segundos="|eval <<<%HOST_A%>>>x<<<%HOST_B%>>>_intermit_segundos=duration_seg*<<<%HOST_A%>>>x<<<%HOST_B%>>>_intermit"
    template_enlace_chamados_segundos="|eval <<<%HOST_A%>>>x<<<%HOST_B%>>>_chamados_segundos=duration_seg*<<<%HOST_A%>>>x<<<%HOST_B%>>>_chamados"
    template_enlace_indisp_intermit_segundos="|eval <<<%HOST_A%>>>x<<<%HOST_B%>>>_indisp_intermit_segundos=duration_seg*<<<%HOST_A%>>>x<<<%HOST_B%>>>_indisp_intermit"
    template_enlace_indisp_sombras_segundos="|eval <<<%HOST_A%>>>x<<<%HOST_B%>>>_indisp_sombras_segundos=duration_seg*<<<%HOST_A%>>>x<<<%HOST_B%>>>_indisp_sombras"
    template_enlace_indisp_ajustada_segundos="|eval <<<%HOST_A%>>>x<<<%HOST_B%>>>_indisp_ajustada_segundos=duration_seg*<<<%HOST_A%>>>x<<<%HOST_B%>>>_indisp_ajustada"
    template_enlace_indisp_chamados_segundos="|eval <<<%HOST_A%>>>x<<<%HOST_B%>>>_indisp_chamados_segundos=duration_seg*<<<%HOST_A%>>>x<<<%HOST_B%>>>_indisp_chamados"


    #Consolida informacoes para cada enlace
    for enl in lista_enlaces:
        #-Indisponibilidade com base em Coletas
        str_search+= template_sitio_indisp.replace('<<<%HOST%>>>', enl['sitio_A']).replace('<<<%TRUNK%>>>', enl['trunk'])
        str_search+= template_sitio_indisp.replace('<<<%HOST%>>>', enl['sitio_B']).replace('<<<%TRUNK%>>>', enl['trunk'])
        str_search+= template_sitio_chamados.replace('<<<%HOST%>>>', enl['sitio_A']).replace('<<<%TRUNK%>>>', enl['trunk'])
        str_search+= template_sitio_chamados.replace('<<<%HOST%>>>', enl['sitio_B']).replace('<<<%TRUNK%>>>', enl['trunk'])
        str_search+= template_enlace_indisp.replace('<<<%HOST_A%>>>', enl['sitio_A']).replace('<<<%HOST_B%>>>', enl['sitio_B']).replace('<<<%TRUNK%>>>', enl['trunk'])
        str_search+= template_enlace_chamados.replace('<<<%HOST_A%>>>', enl['sitio_A']).replace('<<<%HOST_B%>>>', enl['sitio_B']).replace('<<<%TRUNK%>>>', enl['trunk'])
        str_search+= template_enlace_classifind_tempo.replace('<<<%HOST_A%>>>', enl['sitio_A']).replace('<<<%HOST_B%>>>', enl['sitio_B']).replace('<<<%TRUNK%>>>', enl['trunk'])
        str_search+= template_enlace_classifind.replace('<<<%HOST_A%>>>', enl['sitio_A']).replace('<<<%HOST_B%>>>', enl['sitio_B']).replace('<<<%TRUNK%>>>', enl['trunk'])

        #-Calculos de SysUp Times
        str_search+= template_sitio_sysup_deslig_trunk.replace('<<<%HOST%>>>', enl['sitio_A']).replace('<<<%TRUNK%>>>', enl['trunk'])
        str_search+= template_sitio_sysup_deslig_trunk.replace('<<<%HOST%>>>', enl['sitio_B']).replace('<<<%TRUNK%>>>', enl['trunk'])
        str_search+= template_enlace_sysup_deslig.replace('<<<%HOST_A%>>>', enl['sitio_A']).replace('<<<%HOST_B%>>>', enl['sitio_B']).replace('<<<%TRUNK%>>>', enl['trunk'])
        #Aqui precisa calcular duas vezes, uma para cada lado do enlace, mas considerando ambos os sitios
        str_search+= template_sitio_intermit.replace('<<<%HOST_A%>>>', enl['sitio_A']).replace('<<<%HOST_B%>>>', enl['sitio_B']).replace('<<<%TRUNK%>>>', enl['trunk'])
        str_search+= template_sitio_intermit.replace('<<<%HOST_A%>>>', enl['sitio_B']).replace('<<<%HOST_B%>>>', enl['sitio_A']).replace('<<<%TRUNK%>>>', enl['trunk'])
        #-Ajuste Disponibilidade por Sombras, Intermitencia e chamados
        str_search+= template_enlace_sombra.replace('<<<%HOST_A%>>>', enl['sitio_A']).replace('<<<%HOST_B%>>>', enl['sitio_B']).replace('<<<%TRUNK%>>>', enl['trunk'])
        str_search+= template_enlace_intermitencia.replace('<<<%HOST_A%>>>', enl['sitio_A']).replace('<<<%HOST_B%>>>', enl['sitio_B']).replace('<<<%TRUNK%>>>', enl['trunk'])
        str_search+= template_enlace_indisp_intermit.replace('<<<%HOST_A%>>>', enl['sitio_A']).replace('<<<%HOST_B%>>>', enl['sitio_B']).replace('<<<%TRUNK%>>>', enl['trunk'])
        str_search+= template_enlace_indisp_sombras.replace('<<<%HOST_A%>>>', enl['sitio_A']).replace('<<<%HOST_B%>>>', enl['sitio_B']).replace('<<<%TRUNK%>>>', enl['trunk'])
        str_search+= template_enlace_indisp_chamados.replace('<<<%HOST_A%>>>', enl['sitio_A']).replace('<<<%HOST_B%>>>', enl['sitio_B']).replace('<<<%TRUNK%>>>', enl['trunk'])
        str_search+= template_enlace_indisp_ajustada.replace('<<<%HOST_A%>>>', enl['sitio_A']).replace('<<<%HOST_B%>>>', enl['sitio_B']).replace('<<<%TRUNK%>>>', enl['trunk'])

        #-Calculo em Segundos
        str_search+= template_enlace_indisp_segundos.replace('<<<%HOST_A%>>>', enl['sitio_A']).replace('<<<%HOST_B%>>>', enl['sitio_B']).replace('<<<%TRUNK%>>>', enl['trunk'])
        str_search+= template_enlace_deslig_segundos.replace('<<<%HOST_A%>>>', enl['sitio_A']).replace('<<<%HOST_B%>>>', enl['sitio_B']).replace('<<<%TRUNK%>>>', enl['trunk'])
        str_search+= template_enlace_sombra_segundos.replace('<<<%HOST_A%>>>', enl['sitio_A']).replace('<<<%HOST_B%>>>', enl['sitio_B']).replace('<<<%TRUNK%>>>', enl['trunk'])
        str_search+= template_enlace_intermit_segundos.replace('<<<%HOST_A%>>>', enl['sitio_A']).replace('<<<%HOST_B%>>>', enl['sitio_B']).replace('<<<%TRUNK%>>>', enl['trunk'])
        str_search+= template_enlace_chamados_segundos.replace('<<<%HOST_A%>>>', enl['sitio_A']).replace('<<<%HOST_B%>>>', enl['sitio_B']).replace('<<<%TRUNK%>>>', enl['trunk'])
        str_search+= template_enlace_indisp_sombras_segundos.replace('<<<%HOST_A%>>>', enl['sitio_A']).replace('<<<%HOST_B%>>>', enl['sitio_B']).replace('<<<%TRUNK%>>>', enl['trunk'])
        str_search+= template_enlace_indisp_chamados_segundos.replace('<<<%HOST_A%>>>', enl['sitio_A']).replace('<<<%HOST_B%>>>', enl['sitio_B']).replace('<<<%TRUNK%>>>', enl['trunk'])
        str_search+= template_enlace_indisp_ajustada_segundos.replace('<<<%HOST_A%>>>', enl['sitio_A']).replace('<<<%HOST_B%>>>', enl['sitio_B']).replace('<<<%TRUNK%>>>', enl['trunk'])
        str_search+= template_enlace_indisp_intermit_segundos.replace('<<<%HOST_A%>>>', enl['sitio_A']).replace('<<<%HOST_B%>>>', enl['sitio_B']).replace('<<<%TRUNK%>>>', enl['trunk'])


    return str_search









