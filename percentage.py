from make_log import log_exceptions, log_data
# a = "RE:Service ID=038-068-050 [EXT] INTERIM BILL FOR SURESH CHANDER MITTAL, CLAIM NO- RC-HS20-11314215"
# b = "RE:'Service ID=038-068-050' [EXT] INTERIM BILL FOR SURESH CHANDER MITTAL, CLAIM NO- RC-HS20-11314215"
a = "RE:Service ID=038-068-050 [EXT] INTERIM BILL FOR SURESH CHANDER MITTAL, CLAIM NO- RC-HS20-11314215"
b = "RE:Service ID=038-068-050 [EXT]'@^& INTERIM BILL FOR SURESH CHANDER MITTAL, CLAIM NO- RC-HS20-11314215"

def get_percentage(string1, string2):
    try:
        if isinstance(string1, str) and isinstance(string2, str):
            a, b = set(string1), set(string2)
            temp = [a, b]
            smax = max(temp, key=len)
            smin = min(temp, key=len)
            c = smax.difference(smin)
            percentage = round(100-(len(c)/(len(a)+len(b))*100))
            return percentage
        else:
            log_data(msg='no string parmas', subject=string1, dbsubject=string2)
    except:
        log_exceptions(subject=string1, dbsubject=string2)
        return 0
if __name__ == "__main__":
    get_percentage(a, '')