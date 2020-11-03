from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
import sys
import re
import subprocess
#from xvfbwrapper import Xvfb
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.proxy import Proxy, ProxyType
import time
if sys.argv[6]== 'Max PPT':
    un = 'Hos-5419'
elif sys.argv[6]=='inamdar hospital':
    un = 'Hos-7466'
try:
    '''display = Xvfb()
    display.start()'''
    chromeOptions = webdriver.ChromeOptions()
    chromeOptions.add_argument("--headless")
    '''chromeOptions = webdriver.ChromeOptions()
    chromeOptions.add_argument("--headless")
    chromeOptions.add_argument("--remote-debugging-port=9222")
    chromeOptions.add_argument('--no-sandbox')'''
    driver = webdriver.Chrome(r'C:\Users\Administrator\Downloads\chromedriver_win32\chromedriver.exe',options=chromeOptions)
    driver.get("https://portal.starhealth.in/hospital/")
    time.sleep(5)
    driver.find_element_by_id("txtLoginID").clear()
    driver.find_element_by_id("txtLoginID").clear()
    driver.find_element_by_id("txtLoginID").send_keys(un)
    driver.find_element_by_id("txtPassword").click()
    driver.find_element_by_id("txtPassword").clear()
    driver.find_element_by_id("txtPassword").send_keys(un)
    driver.find_element_by_id("btnLogin").click()
    driver.find_element_by_id("ctl00_ContentPlaceHolder1_txtIntimationNo").send_keys(sys.argv[1]) 
    driver.find_element_by_id("ctl00_ContentPlaceHolder1_btnSearch").click()
    '''menu = driver.find_element_by_xpath("//*[@id='ctl00_ContentPlaceHolder1_dg_DashBoard']/tbody/tr[2]/td[8]")

    #menu = driver.find_element_by_id("sub-menu") #Create the object for Action Chains 
    actions = ActionChains(driver) 
    actions.move_to_element(menu).click().perform() # perform the operation on the element
    '''
    driver.execute_script("__doPostBack('ctl00$ContentPlaceHolder1$dg_DashBoard','Sort$CHD_PREMIA_RES')")
    driver.execute_script("__doPostBack('ctl00$ContentPlaceHolder1$dg_DashBoard','Sort$CHD_PREMIA_RES')")
    driver.execute_script("__doPostBack('ctl00$ContentPlaceHolder1$dg_DashBoard$ctl02$lnkEdit')")
    time.sleep(5)
    child = driver.window_handles[1] 
    driver.switch_to.window(child)
    url = driver.current_url
    #print(url)

    menu = driver.find_element_by_xpath("//iframe[@src]")
    file1=menu.get_attribute("src")
    #print (file1)
    import os

    list1 = os.listdir("star/attachments_pdf_"+sys.argv[5]) # dir is your directory path
    number_files = len(list1)
    import requests
    pdf_resp = requests.get(file1)
    with open("star/attachments_pdf_"+sys.argv[5]+"/"+str(number_files+1)+".pdf", "wb") as f:
        f.write(pdf_resp.content)

    driver.quit()
    #display.stop()
    #subprocess.run(["python", "updation.py","1","max","15",''])
    subprocess.run(["python", "star_"+sys.argv[5]+".py","star/attachments_pdf_"+sys.argv[5]+"/"+str(number_files+1)+".pdf",sys.argv[4],'star',sys.argv[5],sys.argv[2],sys.argv[3]])
    dirFiles = os.listdir('star/attachments_pdf_'+sys.argv[5])
    detach_dir=(os.getcwd()+'/star/attachments_pdf_'+sys.argv[5]+'/')
    dirFiles.sort(key=lambda l: int(re.sub('\D', '', l)))

    filePath=os.path.join(detach_dir, str(number_files+1)+'.pdf')
    subprocess.run(["python", "updation.py","1","max","19",filePath])
except Exception as e:
	subprocess.run(["python", "updation.py","1","max","15",e+' error while downloading in driver'])
	driver.quit()

