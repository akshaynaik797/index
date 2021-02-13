from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
#from xvfbwrapper import Xvfb
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.proxy import Proxy, ProxyType
import time

chromeOptions = webdriver.ChromeOptions()
chromeOptions.add_argument("--headless")
driver = webdriver.Chrome(r'C:\Users\Administrator\Downloads\chromedriver_win32\chromedriver.exe',options=chromeOptions)

driver.get("https://portal.starhealth.in/hospital/")
time.sleep(5)
driver.find_element_by_xpath("//*[@id='txtLoginID']").click()
driver.find_element_by_xpath("//*[@id='txtLoginID']").clear()
driver.find_element_by_xpath("//*[@id='txtLoginID']").send_keys("Hos-5419")
driver.find_element_by_id("txtPassword").click()
driver.find_element_by_id("txtPassword").clear()
driver.find_element_by_id("txtPassword").send_keys("Hos-5419")
driver.find_element_by_id("btnLogin").click()
#driver.find_element_by_id("ctl00_ContentPlaceHolder1_lnkApproved").click()
#driver.find_element_by_id("btnLogin").click()
#driver.find_element_by_id("ctl00_ContentPlaceHolder1_lnkApproved").click()
driver.find_element_by_id("ctl00_ContentPlaceHolder1_txtIntimationNo").send_keys("CLI/2021/161100/0173568") 
driver.find_element_by_id("ctl00_ContentPlaceHolder1_btnSearch").click()
'''menu = driver.find_element_by_xpath("//*[@id='ctl00_ContentPlaceHolder1_dg_DashBoard']/tbody/tr[2]/td[8]")

#menu = driver.find_element_by_id("sub-menu") #Create the object for Action Chains 
actions = ActionChains(driver) 
actions.move_to_element(menu).click().perform() # perform the operation on the element
'''
driver.execute_script("__doPostBack('ctl00$ContentPlaceHolder1$dg_DashBoard','Sort$CHD_PREMIA_RES')")
driver.execute_script("__doPostBack('ctl00$ContentPlaceHolder1$dg_DashBoard','Sort$CHD_PREMIA_RES')")
driver.execute_script("__doPostBack('ctl00$ContentPlaceHolder1$dg_DashBoard$ctl02$lnkEdit')")
time.sleep(10)
child = driver.window_handles[1] 
driver.switch_to.window(child)
url = driver.current_url
print(url)
time.sleep(10)
menu = driver.find_element_by_xpath("//iframe[@src]")
file1=menu.get_attribute("src")
#print (file1)
import requests
pdf_resp = requests.get(file1)
with open("save.pdf", "wb") as f:
    f.write(pdf_resp.content)

driver.quit()



