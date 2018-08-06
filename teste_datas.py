import datetime

from dateutil import relativedelta

from svs_gerador_subperiodos import gera_subperiodos_from_mask

report_ini = datetime.datetime.strptime('2017-09-03 00:00:00', '%Y-%m-%d %H:%M:%S')
report_end = datetime.datetime.strptime('2018-04-15 23:59:59', '%Y-%m-%d %H:%M:%S')

#---------CONFIGURACAO--------------------------------------
CFG_TIME_MASK = "%Y_%m"
CFG_COMPLEMENT_VALUE = '_01 00:00:00'
CFG_TIME_DELTA = relativedelta.relativedelta(months=1)



periodos = gera_subperiodos_from_mask(periodo_ini=report_ini, periodo_end=report_end, time_mask=CFG_TIME_MASK, mask_complement_value=CFG_COMPLEMENT_VALUE, time_delta=CFG_TIME_DELTA)
#print 'periodos:', periodos






periodos = gera_subperiodos_from_mask(periodo_ini=report_ini, periodo_end=report_end, time_mask="%Y_%m_%d", mask_complement_value=" 00:00:00", time_delta=relativedelta.relativedelta(days=1))
print 'periodos:', periodos


