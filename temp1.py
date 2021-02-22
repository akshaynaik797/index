import subprocess


def run():
    ins = "newindia"
    ct = "pay"
    fpath = "/home/akshay/temp/250.pdf"
    subject = "The New India Assurance Co. Ltd. - Health Insurance claim payment has been initiated"
    l_time = "07/12/2020 18:22:25"
    hid = "noble"
    mail_id = 'asdasdasda'
    subprocess.run(
              ["python", ins + "_" + ct + ".py", fpath, str(999999), ins,
               ct, subject, l_time, hid, mail_id])

if __name__ == '__main__':
    run()