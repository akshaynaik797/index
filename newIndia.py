import pdftotext
import sqlite3
import datetime
import pandas as pd
import tabula

# file="C:\\Users\\91798\\Desktop\\varun sir\\index\\newIndia\\PAYMENT_DETAIL_1000002021474140378.pdf"
# table=tabula.read_pdf(file,lattice=True,pages='all',pandas_options={'header': None})
# print(table[0])
# print(table[1])
# df=table[0]
# tempDic={}
# for i in range(len(df)) : 
# 		key=df.loc[i, 0]
# 		value=df.loc[i, 1]
# 		tempDic[key]=value
# 		# key=df.loc[i, 2]
# 		# value=df.loc[i, 3]
# 		# tempDic[key]=value

# print(tempDic)
try:
	conn=None
	conn=sqlite3.connect("database1.db")
	cur = conn.cursor()

	file=r"C:\Users\Administrator\Downloads\PAYMENT_DETAIL_1000002021607772111.pdf"
	table=tabula.read_pdf(file,lattice=True,pages='all',pandas_options={'header': None})
	print(table[0])
	df=table[0]
	print(df.columns)
	tempDic={}
	for i in range(len(df)) : 
			key=df.loc[i, 0]
			value=df.loc[i, 1]
			tempDic[key]=value

	refrenceNo=tempDic["Transaction Reference no"]

	with open(r"C:\Users\Administrator\Downloads\PAYMENT_DETAIL_1000002021607772111.pdf") as f:
		pdf = pdftotext.PDF(f)

	with open('newIndia/output1.txt', 'w') as f:
		f.write(" ".join(pdf))   

	with open('newIndia/output1.txt', 'r') as myfile:
		f = myfile.read()

	w=f.find("on")+len('on')
	k=f[w:]
	u=k.find(".")+w
	g=f[w:u]
	g=g.strip()
	g=g.replace(',','')
	date_time_obj = datetime.datetime.strptime(g, '%d %b %Y')
	mdate = str(date_time_obj.strftime("%d-%m-%Y"))
	print('Date:', mdate)
    		
	query = """insert into NIC(TPA_Name,Transaction_Reference_No,Amount,Date_on_attachment) values \
		('%s','%s','%s','%s')""" %(tempDic['TPA Name'],tempDic['Transaction Reference no'],tempDic['Amount'],mdate)
	print(query)
	cur.execute (query)
	conn.commit()


	table=tabula.read_pdf(file,lattice=True,pages='all')
	# print(table[1])
	df=table[1]
	newcoldic={}
	colList=[]
	for col in df.columns: 
		col1=col.replace('\r',' ')
		newcoldic[col]=col1
		colList.append(col1)

	
	df=table[1]
	df1=df.rename(columns = newcoldic, inplace = False)
	print(df1.columns)
	for i in range(len(df1)) : 
		policyNo=df1.loc[i, "Policy Number"]
		claimNo=df1.loc[i, "Claim Number"]
		tpa=claimNo[0:5]
		patientName=df1.loc[i, "Name of Patient"]
		grossAmount=df1.loc[i, "Gross Amount"]
		tdsAmount=df1.loc[i, "TDS Amount"]
		netAmount=df1.loc[i, "Net Amount"]
		query = """insert into NIC_Records(Transaction_Reference_No,Policy_Number,Claim_Number,Name_Of_Patient,Gross_Amounts,tds,Net_Amount,tpa_No) values \
		('%s','%s','%s','%s','%s','%s','%s','%s')""" %(refrenceNo,policyNo,claimNo,patientName,grossAmount,tdsAmount,netAmount,tpa)
		print(query)
		cur.execute(query)
        
	if len(table) >2:
		df=table[2]
	if len(table[2].columns) == len(table[1].columns):
		tempDic={}
		tempDic1={}
		i=0
		for col in df.columns: 
			tempDic[colList[i]]=col
			tempDic1[col]=colList[i]
			i=i+1
		df2=df.rename(columns = tempDic1, inplace = False)
		df1=df2.append(tempDic,ignore_index=True)
		print(df1)

		for i in range(len(df1)) : 
			policyNo=df1.loc[i, "Policy Number"]
			claimNo=df1.loc[i, "Claim Number"]
			tpa=claimNo[0:5]
			patientName=df1.loc[i, "Name of Patient"]
			grossAmount=df1.loc[i, "Gross Amount"]
			tdsAmount=df1.loc[i, "TDS Amount"]
			netAmount=df1.loc[i, "Net Amount"]
			query = """insert into NIC_Records(Transaction_Reference_No,Policy_Number,Claim_Number,Name_Of_Patient,Gross_Amounts,tds,Net_Amount,tpa_No) values \
			('%s','%s','%s','%s','%s','%s','%s','%s')""" %(refrenceNo,policyNo,claimNo,patientName,grossAmount,tdsAmount,netAmount,tpa)
			print(query)
			cur.execute(query)

	conn.commit()
	cur.close()	
	conn.close()
except Exception as e:
		print(e.__str__())
