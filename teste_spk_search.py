import splunklib.results as results
import splunklib.client as client




#Conectando ao Splunk
from svsdispauto.svs_cvswriter import svscsv_from_listdict

print 'Connectin to Splunk, please wait'
service = client.connect(
    host='10.254.22.79',
    username='admin',
    password='nocnoc'
)
print 'Conectado ao Splunk!!'



# Run an export search and display the results using the results reader.

# Set the parameters for the search:
# - Search everything in the last hour
# - Run a normal-mode search
# - Search internal index
kwargs_export = {"earliest_time": "-4mon",
                 "latest_time": "-3mon",
                 "search_mode": "normal"}
searchquery_export = "search index=zabbix source=*_ret*"

searchquery_export = "search index=zabbix source=*_ret* |table _time, itemid, clock, value"


searchquery_export = """
search index="zabbix" sourcetype=novo_zabdbhistory source="novohist_opstatus_trk*"
| lookup tstrod_lookups_items.csv itemid
| lookup tstrod_lookups_hosts.csv hostid  
| search host_name="*OMIGT_SWL3" AND item_key=*Trunk*Port*ID*0001*
| sort 0 itemid, _time
| streamstats current=true window=2 earliest(clock) as last_clock, earliest(itemid) as last_itemid, earliest(datetime) as last_datetime by itemid
| eval diff_itemid=last_itemid - itemid
| eval last_clock = last_clock
| eval delta_tempo = (clock - last_clock) 
| eval is_faltacoleta = IF(delta_tempo >= 2.5*60, 1, 0)
| eval tempo_semcoleta = IF(is_faltacoleta=1,delta_tempo-60,"")
| where  is_faltacoleta=1
| table last_datetime, datetime, tempo_semcoleta, host_name, item_key, delta_tempo
| rename last_datetime AS Inicio, datetime as Termino, tempo_semcoleta AS TempoSemColeta, host_name AS Equipamento, item_key AS Trunk
"""


exportsearch_results = service.jobs.export(searchquery_export, **kwargs_export)
resultados_processados = []
# Get the results and display them using the ResultsReader
reader = results.ResultsReader(exportsearch_results)
print "***************===================*********************===================******************"
for result in reader:
    if isinstance(result, dict):
        print "Result: %s" % result
        aux_dict = {
            't_ini': result.get('Inicio'),
            't_fim': result.get('Termino'),
            'TempoSemColeta': result.get('TempoSemColeta'),
            'Equipamento': result.get('Equipamento'),
            'Trunk': result.get('Trunk'),
            'delta_tempo': result.get('delta_tempo')
        }
        #Adiciona nos resultados
        resultados_processados.append(aux_dict)


    elif isinstance(result, results.Message):
        # Diagnostic messages may be returned in the results
        print "Message: %s" % result

# Print whether results are a preview from a running search
print "is_preview = %s " % reader.is_preview

print 'len_resultados:', len(resultados_processados)

print ''
print ''
print ''
print '======================= ************************** ============================= ************************'



#for r in resultados_processados:
#    print r

#Gera um CSV
svscsv_from_listdict(list_dicts=resultados_processados, list_headers=['t_ini', 't_fim', 'TempoSemColeta', 'delta_tempo', 'Equipamento', 'Trunk'], output_file='teste.csv')
