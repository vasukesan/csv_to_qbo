import csv
from xml.etree.ElementTree import Element, SubElement, Comment, tostring
import datetime
import re
import sys
debug = True

input_filename = sys.argv[1]
with open(input_filename) as csvfile:
	csvfile.readline()
	reader = csv.DictReader(csvfile)
	count = 0
	end_date = ""
	start_date = ""
	trans_list = []
	balance_amount = 0
	for row in reader:

		#verify essential values are present, otherwise skip
		date_string = row['Date'][:10]
		amount = row['Amount']
		if not date_string or not amount:
			if debug:
				print "null values"
			continue

		amount = amount.replace("$","")

		trans_string = "<STMTTRN>"

		description = row['Description'][:32]

		
	 	date_string = (datetime.datetime.strptime(date_string, '%m/%d/%Y')).strftime('%Y%m%d')

	 	if count==0:
	 		#trans_string = "<STMTTRNRS>"
	 		end_date = date_string
	 	start_date = date_string

		negative =  amount[0]=='-'
		num_amount = re.sub("[^\d\.\-]","",amount)
		fitid_amount = re.sub("[^\d]", "", amount)

	 	fitid = "T{}{:04d}{}".format(date_string,count,fitid_amount)
	 	


	 	if negative:
	 		fitid+='M'
	 		trans_string = "\t\t\t\t\t{}\n\t\t\t\t\t\t<TRNTYPE>DEBIT\n\t\t\t\t\t\t<DTPOSTED>{}\n\t\t\t\t\t\t<TRNAMT>{}\n\t\t\t\t\t\t<FITID>{}\n\t\t\t\t\t\t<NAME>{}\n\t\t\t\t\t</STMTTRN>\n".format(trans_string,date_string,num_amount,fitid,description)
	 	else:
	 		trans_string = "\t\t\t\t\t{}\n\t\t\t\t\t\t<TRNTYPE>CREDIT\n\t\t\t\t\t\t<DTPOSTED>{}\n\t\t\t\t\t\t<TRNAMT>{}\n\t\t\t\t\t\t<FITID>{}\n\t\t\t\t\t\t<NAME>{}\n\t\t\t\t\t</STMTTRN>\n".format(trans_string,date_string,num_amount,fitid,description)

	 	trans_list.append(trans_string)

	 	#transaction = Element("STMTTRN")
	 	balance_amount+=float(num_amount)
	 	count = count + 1



	output_filename = re.sub("\.csv",".qbo",input_filename)
	output_filename = re.sub("\.CSV",".qbo",input_filename)
	output = open(output_filename, 'w')
	with open("qbo_template.qbo") as template:
		for _ in range(40):
			output.write(template.readline())


	output.write("\t\t\t\t<BANKTRANLIST>\n\t\t\t\t\t<DTSTART>{}\n\t\t\t\t\t<DTEND>{}\n".format(start_date,end_date))
	for trans_string in trans_list:
		output.write(trans_string)
	output.write("\t\t\t\t</BANKTRANLIST>\n\t\t\t\t<LEDGERBAL>\n\t\t\t\t\t<BALAMT>{}\n\t\t\t\t\t<DTASOF>{}\n\t\t\t\t</LEDGERBAL>\n\t\t\t</STMTRS>\n\t\t</STMTTRNRS>\n\t</BANKMSGSRSV1>\n</OFX>\n".format(balance_amount,end_date))


	


