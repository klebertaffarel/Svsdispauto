import splunklib.results as results
import splunklib.client as client



DEBUG_MODE=True


class SvsSpkExecutor:
    def __init__(self, spk_host, spk_user, spk_password):
        self._spk_host = spk_host
        self._spk_user = spk_user
        self._spk_passwd = spk_password
        self._service = None
        #Conecta ao Splunk
        self._conecta()


    def _conecta(self):
        print 'Connectin to Splunk, please wait'
        self._service = client.connect(
            host=self._spk_host,
            username=self._spk_user,
            password=self._spk_passwd
        )
        print 'Conectado ao Splunk!!'


    def exec_export_search(self, str_search, earliest_time=None, latest_time=None):
        #Monta os cabecalhos
        kwargs_export = {
            "search_mode": "normal",
            "preview": False
        }
        if earliest_time != None:
            kwargs_export.update({"earliest_time": earliest_time})
        if latest_time != None:
            kwargs_export.update({"latest_time": latest_time})
        if DEBUG_MODE: print kwargs_export

        #Executa a busca
        exportsearch_results = self._service.jobs.export(str_search, **kwargs_export)
        resultados_processados = []
        # Get the results and display them using the ResultsReader
        reader = results.ResultsReader(exportsearch_results)
        print "***************===================*********************===================******************"
        for result in reader:
            if isinstance(result, dict):
                if DEBUG_MODE: print "Result: %s" % result
                #Adiciona nos resultados
                resultados_processados.append(result)

            elif isinstance(result, results.Message):
                # Diagnostic messages may be returned in the results
                print "Message: %s" % result


        if DEBUG_MODE: print 'len_resultados:', len(resultados_processados)

        return resultados_processados


