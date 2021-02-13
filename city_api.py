import mysql.connector

from custom_parallel import conn_data


city_records_fields = ["Advice_No", 'Insurer_name', 'City_Transaction_Reference', 'Payer_Reference_No',
                       'Payment_Amount', 'Processing_Date', 'City_Claim_No', 'City_Patient_name', 'City_Admission_Date',
                       'City_TPA', 'Payment_Details', 'NIA_Transaction_Reference']
nic_fields = ['SrNo', 'MailId', 'Date_Of_Mail', 'Amount_In_Mail', 'TPA_Name', 'Date_on_attachment',
              'Transaction_Reference_No',
              'Amount']
nic_records_fields = ['Transaction_Reference_No', 'Policy_Number', 'Claim_Number', 'Name_Of_Patient', 'Gross_Amounts',
                      'tds', 'Net_Amount', 'tpa_No']



def get_from_db(var):
    city, nic, nic_records = dict(), dict(), dict()
    with mysql.connector.connect(**conn_data) as con:
        cur = con.cursor()
        q = f"SELECT * from City_Records where City_Transaction_Reference='{var}'"
        cur.execute(q)
        r = cur.fetchone()
        if r is not None and len(r) == len(city_records_fields):
            for key, value in zip(city_records_fields, r):
                city[key] = value
            city['nic'] = nic
            search_key = city['NIA_Transaction_Reference']
            q = f"SELECT * from NIC where Transaction_Reference_No='{search_key}'"
            cur.execute(q)
            q1 = cur.fetchone()
            if q1 is not None and len(q1) == len(nic_fields):
                for key, value in zip(nic_fields, q1):
                    nic[key] = value
                nic['nic_records'] = {}
                search_key = nic['Transaction_Reference_No']
                q = f"SELECT * from NIC_Records where Transaction_Reference_No='{search_key}'"
                cur.execute(q)
                q2 = cur.fetchall()
                if q2 is not None:
                    for i, j in enumerate(q2):
                        if j is not None and len(j) == len(nic_records_fields):
                            for key, value in zip(nic_records_fields, j):
                                nic_records[key] = value
                        city['nic']['nic_records'][i] = nic_records
        elif r is None:
            return f'No record found for {var}'
    return city

if __name__ == '__main__':
    print(get_from_db('CITIN20125407328'))