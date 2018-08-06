import os

from svsdispauto import spk_searchs_factory
from svsdispauto.svs_cvswriter import svscsv_from_listdict


DEBUG_MODE=True


def extrai_dados_enlace(sitio_A, sitio_B, trunk, trunk_bkp, dir_base=None, spk_executor_ref=None, spk_earliest=None, spk_latest=None, spk_operstatus_sourcetype=None, spk_operstatus_source=None):
    if DEBUG_MODE: print 'Enlace:', sitio_A, 'x', sitio_B, ' - Trunk', trunk
    if DEBUG_MODE: print 'salvando dados em:', dir_base


    sitios = [sitio_A, sitio_B]
    for sit in sitios:
        #OPERSTATUS - SEM COLETA Extrai a falta de coleta de OperStatus ------------------------------------------------
        str_search_swl3 = spk_searchs_factory.search_operstatus_semcoleta(host_swl3=sit, trunk=trunk, trunk_bkp=trunk_bkp, spk_index='zabbix',
                                                                          spk_sourcetype=spk_operstatus_sourcetype,
                                                                          spk_source=spk_operstatus_source)
        if DEBUG_MODE: print 'str_search:', str_search_swl3

        # Obtem os dados
        dados = spk_executor_ref.exec_export_search(str_search_swl3, earliest_time=spk_earliest, latest_time=spk_latest)

        # Salva o CSV
        arq_nome = sit + '_semColeta_' + trunk + '.csv'
        arq_path = os.path.join(dir_base, arq_nome)
        svscsv_from_listdict(list_dicts=dados,
                             list_headers=['dh_inicio', 'dh_termino', 'delta_tempo', 'Equipamento', 'Trunk', 'item_key'],
                             output_file=arq_path)

        #OPERSTATUS - COM COLETA, mas Nao-OK ---------------------------------------------------------------------------
        str_search_nok = spk_searchs_factory.search_operstatus_nok(host_swl3=sit, trunk=trunk, spk_index='zabbix',
                                                                          spk_sourcetype=spk_operstatus_sourcetype,
                                                                          spk_source=spk_operstatus_source)
        if DEBUG_MODE: print 'str_search:', str_search_nok

        # Obtem os dados
        dados = spk_executor_ref.exec_export_search(str_search_nok, earliest_time=spk_earliest, latest_time=spk_latest)

        # Salva o CSV
        arq_nome = sit + '_operNok_' + trunk + '.csv'
        arq_path = os.path.join(dir_base, arq_nome)
        svscsv_from_listdict(list_dicts=dados,
                             list_headers=['dh_inicio', 'dh_termino', 'tempo_periodo', 'tempo_opersts_nOk', 'delta_value', 'is_periodo'],
                             output_file=arq_path)









def extrai_dados_sitio(sitio, dir_base=None, spk_executor_ref=None, spk_earliest=None, spk_latest=None, spk_sysups_sourcetype=None, spk_sysups_source=None):
    if DEBUG_MODE: print 'Informacoes do sitio:', sitio
    if DEBUG_MODE: print 'salvando dados em:', dir_base


    #SysUpTimes - Extrai as janelas de reinicio de equipamentos ------------------------------------------------
    str_search_sysups = spk_searchs_factory.search_sysuptimes(host_sitio=sitio, spk_index='zabbix',
                                                                          spk_sourcetype=spk_sysups_sourcetype,
                                                                          spk_source=spk_sysups_source)
    if DEBUG_MODE: print 'str_search:', str_search_sysups

    # Obtem os dados
    dados = spk_executor_ref.exec_export_search(str_search_sysups, earliest_time=spk_earliest, latest_time=spk_latest)

    # Salva o CSV
    arq_nome = sitio + '_sysUps' + '.csv'
    arq_path = os.path.join(dir_base, arq_nome)
    svscsv_from_listdict(list_dicts=dados,
                        list_headers=['dh_ultima_coleta', 'dh_equip_ligado', 'dh_primeira_coleta', 'TempoIndisponivel', 'TempoIndispAjustado', 'Equipamento', 'Uptime', 'UltimoUptime'],
                        output_file=arq_path)







def extrai_base_chamados(lista_chamados, dir_base=None, csv_output=None, spk_executor_ref=None, spk_earliest=None, spk_latest=None):
    if DEBUG_MODE: print 'Extraindo lista de chamados:', lista_chamados
    if DEBUG_MODE: print 'salvando dados em:', dir_base, csv_output


    #Base de Chamados  ------------------------------------------------
    str_search_chamados = spk_searchs_factory.search_base_chamados(lista_chamados=lista_chamados)
    if DEBUG_MODE: print 'str_search:', str_search_chamados

    # Obtem os dados
    dados = spk_executor_ref.exec_export_search(str_search_chamados, earliest_time=spk_earliest, latest_time=spk_latest)

    # Salva o CSV
    arq_nome = csv_output
    arq_path = os.path.join(dir_base, arq_nome)
    svscsv_from_listdict(list_dicts=dados,
                        list_headers=['dh_inicio', 'dh_termino', 'ID', 'chamados', 'localidade_id'],
                        output_file=arq_path)




