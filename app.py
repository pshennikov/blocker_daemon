#!/usr/bin/python
# coding=utf-8


import os
import ESL
import json
import logging
import MySQLdb

from config import *
from shutil import copyfile
from datetime import datetime, timedelta


logging.basicConfig(filename=LOG_PATH + 'blocker_daemon/' + 'debug.log', level=logging.DEBUG, format=LOG_FORMAT)


def now():
    return str(datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3])


def date_now():
    return str(datetime.now().strftime('%Y-%m-%d'))


def last_hour(minutes_period):
    return str((datetime.now() - timedelta(minutes=minutes_period)).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3])


def copy_file(path, block_path,  sip_account):
    logging.info('copy_file | try copy file: {} to {}'.format(path + sip_account, block_path))

    if os.path.exists(path + sip_account):
        copyfile(path + sip_account, block_path + sip_account)
        logging.debug("copy_file | file {} copied".format(sip_account))
    else:
        logging.debug("copy_file | {} - file don't exist".format(sip_account))


def remove_file(path, sip_account):
    logging.info('remove_file | try remove file: {}'.format(path + sip_account))

    if os.path.exists(path + sip_account):
        os.remove(path + sip_account)
        logging.debug("remove_file | file {} removed".format(sip_account))
    else:
        logging.debug("remove_file | file {} doesn't exist".format(sip_account))


def add_alarm(alarm, message, priority, alarm_type):
    logging.info('add_alarm | try add alarm, message: {}'.format(message))
    conn = MySQLdb.connect(host=db_host, port=db_port, user=db_user, passwd=db_password, db=db_database, charset='utf8')
    x = conn.cursor()

    try:
        sql_insert_request = "insert into alarms (alarm,message,priority,type,created_at) values " \
                             "('{}','{}',{},{},'{}');".format(alarm, message, priority, alarm_type, now())

        logging.debug('add_alarm | sql_insert_request: {}'.format(sql_insert_request))

        x.execute(sql_insert_request)
        conn.commit()

    except (IOError, Exception) as e:
        logging.debug("add_alarm | some except: {}".format(e))

        conn.rollback()
#        conn.close()

    conn.close()
    logging.info('add_alarm | db conn.close()')


def add_event(account):
    logging.info('add_event | try add event, gateway: {}'.format(account))
    conn = MySQLdb.connect(host=db_host, port=db_port, user=db_user, passwd=db_password, db=db_database, charset='utf8')
    x = conn.cursor()

    try:
        sql_insert_request = "insert into events (gateway,happened_at) values " \
                             "('{}','{}');".format(account, now())

        logging.debug('add_event | sql_insert_request: {}'.format(sql_insert_request))

        x.execute(sql_insert_request)
        conn.commit()

    except (IOError, Exception) as e:
        logging.debug("add_event | some except: {}".format(e))

        conn.rollback()
        # conn.close()

    conn.close()
    logging.debug('add_event | db conn.close()')


def check_event(account):
    logging.info('check_event | try check event, gateway: {}'.format(account))
    conn = MySQLdb.connect(host=db_host, port=db_port, user=db_user, passwd=db_password, db=db_database, charset='utf8')
    x = conn.cursor()
    sql_select_result = None

    try:
        sql_select_request = "select count(id) from events where gateway = '{}' and happened_at between '{}' and" \
                             " '{}';".format(account, last_hour(OBSERV_PERIOD), now())

        logging.debug('check_event | sql_select_request: {}'.format(sql_select_request))
        
        x.execute(sql_select_request)
        sql_select_result = x.fetchone()

        logging.debug('check_event | select return: {}'.format(sql_select_result))

        conn.commit()

    except (IOError, Exception) as e:
        logging.debug("check_event | except: {}".format(e))

        conn.rollback()
        # conn.close()

    logging.debug('check_event | function will return: {}'.format(sql_select_result))

    conn.close()
    logging.debug('check_event | db conn.close()')

    return sql_select_result


def set_block_status(sip_account):
    logging.info('set_block_status | try set block status, gateway: {}'.format(sip_account))

    conn = MySQLdb.connect(host=db_host, port=db_port, user=db_user, passwd=db_password, db=db_database, charset='utf8')
    x = conn.cursor()
    try:
        sql_update_is_blocked = 'update ext_sip_accounts set is_blocked = true where name = {};'.format(sip_account)

        logging.debug('set_block_status | sql_update_is_blocked: {}'.format(sql_update_is_blocked))

        x.execute(sql_update_is_blocked)
        conn.commit()

        logging.debug('set_block_status | sip account id: {} is blocked'.format(sip_account))

    except (IOError, Exception) as e:
        logging.debug("set_block_status | some except: {}".format(e))
        conn.rollback()
        # conn.close()

    conn.close()
    logging.debug('set_block_status | db conn.close()')


def get_operator_address(account):
    logging.info('check_event | try get operator address, gateway: {}'.format(account))
    conn = MySQLdb.connect(host=db_host, port=db_port, user=db_user, passwd=db_password, db=db_database, charset='utf8')
    x = conn.cursor()
    sql_select_result = None

    try:
        sql_select_request = "select server from ext_sip_accounts where name = '{}';".format(account)

        logging.debug('check_event | sql_select_request: {}'.format(sql_select_request))

        x.execute(sql_select_request)
        sql_select_result = x.fetchone()

        logging.debug('check_event | select return: {}'.format(sql_select_result))

        conn.commit()

    except (IOError, Exception) as e:
        logging.debug("check_event | except: {}".format(e))

        conn.rollback()
        # conn.close()

    logging.debug('check_event | function will return: {}'.format(sql_select_result))

    conn.close()
    logging.debug('check_event | db conn.close()')

    if sql_select_result is None:
        sql_select_result = ['null']

    return sql_select_result


def execute_esl_command(cmd, ip, password):
    con = ESL.ESLconnection(ip, '8021', password)

    if not con.connected():
        return 'Not Connected'

    e = con.api(cmd)

    if e:
        return e.getBody()


if __name__ == '__main__':
    print('blocker daemon started!')

    con = ESL.ESLconnection(ESL_IP, '8021', 'ClueCon')
    logging.info('con.connected():{}'.format(con.connected()))

    if con.connected():
        con.events('plain', 'all')
        con.filter('Ping-Status', 'DOWN')

        while 1:
            e = con.recvEvent()
            if e:
                event_dict = json.loads(e.serialize("json"))

                logging.debug('event received: {} | {} | {}'.format(event_dict.get('Gateway'),
                                                                    event_dict.get('Ping-Status'),
                                                                    event_dict.get('State')))

                if event_dict.get('Ping-Status') == 'DOWN' and event_dict.get('State') == 'FAILED':
                    account = event_dict.get('Gateway')

                    logging.debug('gateway: {}'.format(account))

                    add_event(account)
                    count = check_event(account)[0]

                    logging.debug('{} | count: {}'.format(account, count))

                    operator = get_operator_address(account)[0]

                    logging.debug('{} | operator: {}'.format(account, operator))

                    if count >= REGISTRATION_FAILURE_LIMIT or operator in OPERATOR_LIST:
                        logging.debug('blocking gateway: {}'.format(account))

                        add_alarm('blocked_sip_account', 'blocked external sip accounts ' + str(account), '3', '1')

                        blocking_path = BLOCKED_ACCOUNT_PATH + '_' + date_now() + '/'
                        logging.debug('path: {}/{}'.format(blocking_path, account))

                        if not os.path.exists(blocking_path):
                            logging.debug('make path: {}'.format(blocking_path))
                            os.makedirs(blocking_path)
                        else:
                            logging.info('path: {} - exists!'.format(blocking_path))

                        copy_file(SIP_ACCOUNT_PATH, blocking_path, account + SIP_ACCOUNT_FILE_TYPE)
                        remove_file(SIP_ACCOUNT_PATH, account + SIP_ACCOUNT_FILE_TYPE)

                        cmd = 'sofia profile external killgw {}'.format(account)
                        logging.info('cmd: {}'.format(cmd))

                        logging.debug(execute_esl_command(cmd, '127.0.0.1', 'ClueCon'))

                        set_block_status(account)
                    else:
                        logging.debug('condition for {} is false'.format(account))
    else:
        logging.warning("can't connect to esl")
