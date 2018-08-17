import csv
from xml.etree.ElementTree import Element, SubElement, Comment, tostring
import datetime
import re
import sys


debug = True

input_filename = sys.argv[1]
acct_id = sys.argv[2]
is_bank = sys.argv[3]

with open(input_filename) as csvfile:
	#csvfile.readline() #absorb excess lines before column headers

	reader = csv.DictReader(csvfile)
	count = 0
	end_date = ""
	start_date = ""
	trans_list = []
	balance_amount = 0


	#read CSV row by row and build up container of formatted transaction strings
	for row in reader:

		date_string = row['Date'][:10]
		amount = row['Amount']

		if not date_string or not amount:
			if debug:
				print "null values"
			continue
		

		c_name = row['Name'][:40]
		c_name = c_name.replace("&","and")
		c_name = c_name.replace("amp;","n")
		memo = row['Memo'][:40]
		memo = memo.replace("&","and")
		memo = memo.replace("amp;","n")
		
		if not c_name:
			c_name = memo
		if not memo:
			memo = c_name
		c_name = c_name[:30]
		if not c_name and not memo: 
			c_name = "UNKNOWN"
			memo = "UNKNOWN"

		
	 	date_string = (datetime.datetime.strptime(date_string, '%m/%d/%Y')).strftime('%Y%m%d')
	 	if count==0:
	 		#trans_string = "<STMTTRNRS>"
	 		end_date = date_string
	 	start_date = date_string

		
		negative =  amount[0]=='-'
		num_amount = re.sub("[^\d\.\-]","",amount)
		balance_amount+=float(num_amount)


		fitid_amount = re.sub("[^\d]", "", amount)

	 	fitid = "{}{:04d}{}".format(date_string,count,fitid_amount)

	 	credit_debit = "CREDIT"
	 	if negative:
	 		#fitid+='M'
	 		credit_debit = "DEBIT"
	 		num_amount = num_amount[1:]
	 	else:
	 		num_amount = "-"+num_amount

	 	indent = "\t\t\t\t\t"

	 	trans_string = "<STMTTRN>"
	 	trans_string = indent+trans_string + "\n"
	 	credit_debit = "\t{}<TRNTYPE>{}</TRNTYPE>\n".format(indent,credit_debit)
	 	posted_date_string = "\t{}<DTPOSTED>{}040000.000</DTPOSTED>\n".format(indent,date_string)
	 	user_date_string = "\t{}<DTUSER>{}040000.000</DTUSER>\n".format(indent,date_string)
	 	num_amount_string = "\t{}<TRNAMT>{}</TRNAMT>\n".format(indent,num_amount)
	 	fitid = "\t{}<FITID>{}</FITID>\n".format(indent,fitid)
	 	c_name = "\t{}<NAME>{}</NAME>\n".format(indent,c_name)
	 	cc_acct = "\t{}<CCACCTTO>\n\t\t{}<ACCTID>{}</ACCTID>\n\t{}</CCACCTTO>\n".format(indent,indent,acct_id,indent)
	 	memo = "\t{}<MEMO>{}</MEMO>\n".format(indent,memo)
	 	end_trans = "{}</STMTTRN>\n".format(indent)
	 	
	 	trans_string = trans_string + credit_debit + posted_date_string + user_date_string +num_amount_string + fitid + c_name + cc_acct + memo + end_trans

	 	trans_list.append(trans_string)

	 	count = count + 1

	# balance_amount = -balance_amount;

	output_filename = re.sub("\.csv",".qbo",input_filename)
	output_filename = re.sub("\.CSV",".qbo",input_filename)
	output = open(output_filename, 'w')
	with open("qbo_template_CC.qbo") as template:
		for _ in range(33):
			output.write(template.readline())


	output.write("\n{}<ACCTID>{}</ACCTID>\n\t\t\t\t</CCACCTFROM>\n\t\t\t\t<BANKTRANLIST>\n\t\t\t\t\t<DTSTART>{}040000.000</DTSTART>\n\t\t\t\t\t<DTEND>{}040000.000</DTEND>\n".format(indent,acct_id,start_date,end_date))
	for trans_string in trans_list:
		output.write(trans_string)
	output.write("\t\t\t\t</BANKTRANLIST>\n\t\t\t\t<LEDGERBAL>\n\t\t\t\t\t<BALAMT>{}</BALAMT>\n\t\t\t\t\t<DTASOF>{}</DTASOF>\n\t\t\t\t</LEDGERBAL>\n\t\t\t</CCSTMTRS>\n\t\t</CCSTMTTRNRS>\n\t</CREDITCARDMSGSRSV1>\n</OFX>\n".format(balance_amount,end_date))

	if debug:
		print "finished."

	#between LEDGERBAL end tag and CCSTMTRS
	# <AVAILBAL>
	# 				<BALAMT>16010.2</BALAMT>
	# 				<DTASOF>20180613142940.708</DTASOF>
	# 			</AVAILBAL>


	


