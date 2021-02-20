import subprocess


def run():
    ins = "tata"
    ct = "General"
    fpath = "/home/akshay/temp/6888_2021021300048.pdf"
    subject = "Claim Query Letter- MemberID:-N90A0175TODAY	Claim No:-90222021477211"
    l_time = "07/12/2020 18:22:25"
    hid = "test"
    mail_id = 'asdasdasda'
    subprocess.run(
              ["python", ins + "_" + ct + ".py", fpath, str(999999), ins,
               ct, subject, l_time, hid, mail_id])

if __name__ == '__main__':
    run()