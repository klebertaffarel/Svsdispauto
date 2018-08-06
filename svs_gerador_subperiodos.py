import datetime

from dateutil import relativedelta

DEBUG_MODE=False
CFG_COMPLETE_MASK = '%Y_%m_%d %H:%M:%S'
def gera_subperiodos_from_mask(periodo_ini=None, periodo_end=None, time_mask="%Y-%m", mask_complement_value="-01 00:00:00", time_delta=relativedelta.relativedelta(months=1)):

    # Calcula os limites
    dtini_minimo = periodo_ini.strftime(time_mask)
    dtend_maximo = periodo_end.strftime(time_mask)
    if DEBUG_MODE: print 'minimo_base:', dtini_minimo
    if DEBUG_MODE: print 'maximo_base:', dtend_maximo

    aux_data_mask = dtini_minimo
    lista_datas_inicio = []
    while aux_data_mask <= dtend_maximo:
        if DEBUG_MODE: print 'aux_data_mask:', aux_data_mask
        aux_dt = datetime.datetime.strptime(aux_data_mask + mask_complement_value, CFG_COMPLETE_MASK)
        lista_datas_inicio.append(aux_dt)
        if DEBUG_MODE: print 'aux_dt:', aux_dt
        prox_data = aux_dt + time_delta
        if DEBUG_MODE: print 'prox_data:', prox_data
        aux_data_mask = prox_data.strftime(time_mask)

    # Varre os meses gerando os intervalos
        if DEBUG_MODE: print 'gerando periodos'
    periodos = []
    for m in lista_datas_inicio:
        anomes_str = m.strftime(time_mask)
        if DEBUG_MODE: print 'anomes_str:', anomes_str
        # Monta o periodo
        per_ini = m
        per_end = m + time_delta - datetime.timedelta(seconds=1)

        if anomes_str == dtini_minimo:
            per_ini = max(periodo_ini, per_ini)
            print 'DATA INICIO:', per_ini

        if anomes_str == dtend_maximo:
            per_end = min(periodo_end, per_end)
            print 'DATA MAXIMO:', per_end
        aux_periodo = [per_ini, per_end]
        print 'periodo:', aux_periodo
        periodos.append(aux_periodo)

    return periodos

