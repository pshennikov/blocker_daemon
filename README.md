# blocker_daemon

blocker_daemon подписывается в ESL Freeswitch на eventы о неуспешности регистрации учетки, при достижении лимита неуспешных попыток регистрации | REGISTRATION_FILURE_LIMIT за время наблюдения | OBSERV_PERIOD данная SIP учетка блокируется

## описание переменных:
- OPERATOR_LIST - список Hostов операторов которые должны блокироваться с первой неуспешной попытки регистрации

Необходимо создать конфигурационный файл config.py с след содержимым:

### # paths:
LOG_PATH = '/var/log/freeswitch/'
SIP_ACCOUNT_PATH = '/etc/freeswitch/directory/default/'
SIP_ACCOUNT_FILE_TYPE = '.xml'
SIP_CLIENT_TRUNK_PATH = '/etc/freeswitch/directory/client_trunk/'
SIP_CLIENT_TRUNK_PREFIX = 'client_trunk'
BLOCKED_ACCOUNT_PATH = '/etc/freeswitch/directory/blocked'
BLOCKED_CLIENT_TRUNK_PATH = '/etc/freeswitch/directory/client_trunk_blocked'

### # mysql:
db_host = '' # str  
db_port = # int  
db_user = '' # str  
db_password = '' # str  
db_database = '' # str

### # other:
OBSERV_PERIOD = 30  # minutes  
REGISTRATION_FAILURE_LIMIT = 3  # count  
OPERATOR_LIST = ['']  # list  
ESL_IP = ''  # str  
LOG_FORMAT = '%(asctime)s | %(levelname)s | %(message)s [%(filename)s:%(lineno)d]'  
