import sqlite3

import requests

from make_log import log_exceptions
from push_api import api_update_trigger


def get_update_log(row_no):
    response = ""
    ref_no, comment, status = "", "", ""
    local_dict = {}
    try:
        with sqlite3.connect("database1.db") as con:
            cur = con.cursor()
            b = f"select  preauthid,policyno,memberid,comment,hos_id,status  from updation_detail_log where row_no = '{row_no}'"
            cur.execute(b)
            r = cur.fetchone()
            #handle null row
            if r is not None:
                preauthid, policyno, memberid, comment, hos_id, status = r[0], r[1], r[2], r[3], r[4], r[5]
            else:
                preauthid, policyno, memberid, comment, hos_id, status = "", "", "", "", "", ""
                return

        if hos_id == 'Max':
            url = 'https://vnusoftware.com/iclaimmax/api/preauth/vnupatientsearch'
        else:
            url = 'https://vnusoftware.com/iclaimportal/api/preauth/vnupatientsearch'
        payload = {
            'memberid': memberid,
            'preauthid': preauthid,
            'policyno': policyno,
            'comment': comment
        }

        temp = {}
        for i, j in payload.items():
            if j is None:
                temp[i] = ''
            else:
                temp[i] = j

        payload = temp

        response = requests.post(url, data=payload)
        result = response.json()
        print(result)
        # log_api_data('result', result)
        if result['status'] == '1':
            local_dict['searchdata'] = result['searchdata']
        else:
            local_dict["searchdata"] = {
                "refno": "",
                "approve_amount": "",
                "current_status": "",
                "process": "",
                "InsurerId": "",
                "insname": "",
                "Cumulative_flag": ""
            }
        ref_no = local_dict['searchdata']['refno']
        api_update_trigger(ref_no, comment, status)
        #return ref_no, comment, status
    except Exception as e:
        log_exceptions(payload=payload, url=url, response=response)
        print(e)
        # log_api_data('e', e)
        local_dict["searchdata"] = {
            "refno": "",
            "approve_amount": "",
            "current_status": "",
            "process": "",
            "InsurerId": "",
            "insname": ""
        }
        #return ref_no, comment, status


if __name__ == '__main__':
    a = get_update_log('7555')
    pass
