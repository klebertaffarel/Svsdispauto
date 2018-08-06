import paramiko
from scp import SCPClient


def envia_arquivo(path_file, dest_dir, host, user, passwd, port=22):
    print 'enviando arquivo por scp: ', path_file

    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(host, port=port, username=user, password=passwd)
    print 'ssh-conectado'
    scp_client = SCPClient(client.get_transport())
    print 'scp-conectado'
    scp_client.put([path_file], remote_path=dest_dir, preserve_times=True)
    print 'arquivo enviado'
