import sys
import datetime
import clr
import System.Net
from System.Text.Encoding import UTF8
from System import Convert
from SYDATABASE import SQL
import CQVLDRIFLW
import CQCPQC4CWB

clr.AddReference("System.Net")
from System.Net import CookieContainer, NetworkCredential, Mail
from System.Net.Mail import SmtpClient, MailAddress, Attachment, MailMessage

Parameter = SqlHelper.GetFirst("SELECT QUERY_CRITERIA_1 FROM SYDBQS (NOLOCK) WHERE QUERY_NAME = 'SELECT' ")
Parameter1 = SqlHelper.GetFirst("SELECT QUERY_CRITERIA_1 FROM SYDBQS (NOLOCK) WHERE QUERY_NAME = 'UPD' ")
Parameter2 = SqlHelper.GetFirst("SELECT QUERY_CRITERIA_1 FROM SYDBQS (NOLOCK) WHERE QUERY_NAME = 'DEL' ")

SYINPL_SESSION = SqlHelper.GetFirst("SELECT NEWID() AS A")

exceptinfo = ''

try:

	Stausquery = SqlHelper.GetFirst("SELECT count(*) as cnt from SYINPL(NOLOCK) WHERE INTEGRATION_NAME = 'SSCM_TO_CPQ_PRICING_DATA' AND ISNULL(STATUS,'') = 'INPROGRESS' ")	
	
	if Stausquery.cnt == 0:

		#Status Inprogress SYINPL by CPQ Table Entry ID
		
		StatusUpdateQuery = SqlHelper.GetFirst(""+ str(Parameter1.QUERY_CRITERIA_1)+ "  SYINPL SET STATUS = ''ERROR'',SESSION_ID=''"+str(SYINPL_SESSION.A)+"'' FROM SYINPL (NOLOCK)  WHERE isnull(status,'''')='''' AND INTEGRATION_NAME = ''SSCM_TO_CPQ_PRICING_DATA'' AND INTEGRATION_PAYLOAD NOT LIKE ''%QUOTE_ID%'' ' ")

		StatusUpdateQuery = SqlHelper.GetFirst(""+ str(Parameter1.QUERY_CRITERIA_1)+ "  SYINPL SET STATUS = ''INPROGRESS'',SESSION_ID=''"+str(SYINPL_SESSION.A)+"'' FROM SYINPL (NOLOCK)  WHERE isnull(status,'''')='''' AND INTEGRATION_NAME = ''SSCM_TO_CPQ_PRICING_DATA''  ' ")

		#Status Empty
		Jsonquery = SqlHelper.GetList("SELECT replace(INTEGRATION_PAYLOAD,'null','\"\"') as INTEGRATION_PAYLOAD,CpqTableEntryId from SYINPL(NOLOCK) WHERE INTEGRATION_NAME = 'SSCM_TO_CPQ_PRICING_DATA' AND ISNULL(STATUS,'') = 'INPROGRESS' AND SESSION_ID = '"+str(SYINPL_SESSION.A)+"' ")
		
		for json_data in Jsonquery:
				
			exceptinfo = str(json_data.CpqTableEntryId)
			sessiondetail = SqlHelper.GetFirst("SELECT NEWID() AS A")
			
			if "Param" in str(json_data.INTEGRATION_PAYLOAD):
				splited_list = str(json_data.INTEGRATION_PAYLOAD).split("%%")
				rebuilt_data = eval(str(splited_list[1]))
			else:
				splited_list = str(json_data.INTEGRATION_PAYLOAD)
				rebuilt_data = eval(splited_list)		
			
			primaryQuerysession =  SqlHelper.GetFirst("SELECT NEWID() AS A")
			today = datetime.datetime.now()
			Modi_date = today.strftime("%m/%d/%Y %H:%M:%S %p")


			if len(rebuilt_data) != 0:      

				rebuilt_data = rebuilt_data["CPQ_Columns"]
				Table_Names = rebuilt_data.keys()
				Check_flag = 0
				Qt_Id = ''
				Saqico_Flag = 0
				
				for tn in Table_Names:
					if tn in rebuilt_data:	
						if 1:
							if str(type(rebuilt_data[tn])) == "<type 'dict'>":
								Tbl_data = [rebuilt_data[tn]]
							else:
								Tbl_data = rebuilt_data[tn]
								
							for record_dict in Tbl_data:

								if 'HEADBUILD_QTY' not in record_dict:
									record_dict['HEADBUILD_QTY'] = ''

								primaryQueryItems = SqlHelper.GetFirst( ""+ str(Parameter.QUERY_CRITERIA_1)+ " SAQICO_INBOUND (SESSION_ID,QUOTE_ID,EQUIPMENT_ID,ASSEMBLY_ID,SERVICE_ID,COST_MODULE_AVAILABLE,ASSEMBLY_NOT_REQUIRED_FLAG,GREATER_THAN_QTLY_COST,LESS_THAN_QTLY_COST,CLEAN_COST,SEEDSTOCK_COST,METROLOGY_COST,REFURB_COST,RECOATING_COST,CM_PART_COST,PM_PART_COST,LABOUR_COST,KPI_COST,TOTAL_COST_WISEEDSTOCK,TOTAL_COST_WOSEEDSTOCK,COST_CALCULATION_STATUS,MODULE_ID,MODULE_NAME,NPI,SERVICE_COMPLEXITY,HEADREBUILD_QTY)  select ''"+str(sessiondetail.A)+ "'',''"+str(record_dict['QUOTE_ID'])+ "'',''"+str(record_dict['EQUIPMENT_ID'])+ "'',''"+str(record_dict['ASSEMBLY_ID'])+ "'',''"+ str(record_dict['SERVICE_ID'])+ "'',''"+ str(record_dict['COST_MODULE_AVAILABLE'])+ "'',''"+ str(record_dict['ASSEMBLY_NOT_REQUIRED_FLAG'])+ "'',''"+ str(record_dict['GREATER_THAN_QTLY_COST'])+ "'',''"+ str(record_dict['LESS_THAN_QTLY_COST'])+ "'',''"+str(record_dict['CLEAN_COST'])+ "'',''"+str(record_dict['SEEDSTOCK_COST'])+ "'',''"+str(record_dict['METROLOGY_COST'])+ "'',''"+str(record_dict['REFURB_COST'])+ "'',''"+str(record_dict['RECOATING_COST'])+ "'',''"+str(record_dict['CM_PART_COST'])+ "'',''"+str(record_dict['PM_PART_COST'])+ "'',''"+str(record_dict['LABOR_COST'])+ "'',''"+str(record_dict['KPI_COST'])+ "'',''"+str(record_dict['TOTAL_COST_WISEEDSTOCK'])+ "'',''"+str(record_dict['TOTAL_COST_WOSEEDSTOCK'])+ "'',''"+str(record_dict['COST_CALCULATION_STATUS'])+ "'',''"+str(record_dict['MODULE_ID'])+ "'',''"+str(record_dict['MODULE_NAME'])+ "'',''"+str(record_dict['NPI'])+ "'',''"+str(record_dict['SERVICE_COMPLEXITY'])+ "'',CASE WHEN ISNULL(''"+str(record_dict['HEADBUILD_QTY'])+ "'','''')='''' THEN NULL ELSE ''"+str(record_dict['HEADBUILD_QTY'])+ "'' END ' ")
								
								
								Check_flag = 1
				
				primaryQueryItems = SqlHelper.GetFirst(
									""
									+ str(Parameter1.QUERY_CRITERIA_1)
									+ "  SAQICO_INBOUND SET QUOTE_ID = B.QUOTE_ID,REVISION_ID = B.QTEREV_ID FROM SAQICO_INBOUND (NOLOCK) A JOIN SAQTRV B(NOLOCK) ON A.QUOTE_ID = B.QUOTE_ID+''-''+CONVERT(VARCHAR,QTEREV_ID)  WHERE ISNULL(PROCESS_STATUS,'''')='''' AND ISNULL(SESSION_ID,'''')=''"+str(sessiondetail.A)+ "'' '")
				
				primaryQueryItems = SqlHelper.GetFirst(
									""
									+ str(Parameter1.QUERY_CRITERIA_1)
									+ "  SAQICO_INBOUND SET LINE = B.LINE FROM SAQICO_INBOUND (NOLOCK) A JOIN SAQRIT B(NOLOCK) ON A.QUOTE_ID = B.QUOTE_ID AND A.REVISION_ID = B.QTEREV_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID = B.OBJECT_ID WHERE ISNULL(PROCESS_STATUS,'''')='''' AND ISNULL(SESSION_ID,'''')=''"+str(sessiondetail.A)+ "'' AND B.OBJECT_TYPE=''EQUIPMENT'' '")
				
				primaryQueryItems = SqlHelper.GetFirst(
									""
									+ str(Parameter1.QUERY_CRITERIA_1)
									+ "  SAQICO_INBOUND SET TOTAL_COST_WISEEDSTOCK = TOTAL_COST_WOSEEDSTOCK FROM SAQICO_INBOUND (NOLOCK) A WHERE ISNULL(PROCESS_STATUS,'''')='''' AND ISNULL(SESSION_ID,'''')=''"+str(sessiondetail.A)+ "'' AND ISNULL(CONVERT(FLOAT,TOTAL_COST_WISEEDSTOCK),0)<=0 '")
								
				Qt_Id = SqlHelper.GetFirst("select QUOTE_ID,REVISION_ID from SAQICO_INBOUND(Nolock) where ISNULL(SESSION_ID,'')='"+str(sessiondetail.A)+ "' ")
				
				Saqicoquery = SqlHelper.GetFirst("select count(*) as cnt from SAQICO(Nolock) where QUOTE_ID = '"+str(Qt_Id.QUOTE_ID)+"' AND SAQICO.QTEREV_ID = '"+str(Qt_Id.REVISION_ID)+"' ")
				
				if Saqicoquery.cnt >0:
					Saqico_Flag = 1
				
				if Check_flag == 1 and Saqico_Flag == 1:
					
					Emailinfo = SqlHelper.GetFirst("SELECT QUOTE_ID,SSCM,0 as REMANING,QUOTE_RECORD_ID FROM (SELECT SAQICO.QUOTE_ID,COUNT(DISTINCT SAQICO.EQUIPMENT_ID) AS SSCM,SAQICO.QUOTE_RECORD_ID  FROM SAQICO (NOLOCK) WHERE SAQICO.QUOTE_ID = '"+str(Qt_Id.QUOTE_ID)+"' AND SAQICO.QTEREV_ID = '"+str(Qt_Id.REVISION_ID)+"' AND ISNULL(STATUS,'') not in ('','Assembly is missing') group by SAQICO.Quote_ID,SAQICO.QUOTE_RECORD_ID )SUB_SAQICO ")  
					
					ToEml = SqlHelper.GetFirst("SELECT ISNULL(OWNER_ID,'X0116954') as OWNER_ID FROM SAQTMT (NOLOCK) WHERE SAQTMT.QUOTE_ID = '"+str(Qt_Id.QUOTE_ID)+"'  ")  
					
					Emailinfo1 = SqlHelper.GetFirst("SELECT QUOTE_ID,CPQ FROM (SELECT SAQICO_INBOUND.QUOTE_ID,COUNT(DISTINCT SAQICO_INBOUND.EQUIPMENT_ID) AS CPQ FROM SAQICO_INBOUND (NOLOCK) WHERE SAQICO_INBOUND.QUOTE_ID = '"+str(Qt_Id.QUOTE_ID)+"' AND SAQICO_INBOUND.REVISION_ID = '"+str(Qt_Id.REVISION_ID)+"' AND ISNULL(SESSION_ID,'')='"+str(sessiondetail.A)+ "' group by SAQICO_INBOUND.Quote_ID )SUB_SAQICO ")  
				
					# Mail system				
					Header = "<!DOCTYPE html><html><head><style>table {font-family: Calibri, sans-serif; border-collapse: collapse; width: 75%}td, th {  border: 1px solid #dddddd;  text-align: left; padding: 8px;}.im {color: #222;}tr:nth-child(even) {background-color: #dddddd;} #grey{background: rgb(245,245,245);} #bd{color : 'black';} </style></head><body id = 'bd'>"

					Table_start = "<p>Hi Team,<br><br>Cost data has been received from SSCM for the below Quote ID and the CPQ price calculation has been initiated. Will let you know shortly about the pricing status.</p><table class='table table-bordered'><tr><th id = 'grey'>Quote ID</th><th id = 'grey'>Tools sent (CPQ-SSCM)</th><th id = 'grey'>Tools received (SSCM-CPQ)</th><th id = 'grey'>Price Calculation Status</th></tr><tr><td >"+str(Qt_Id.QUOTE_ID)+"</td><td>"+str(Emailinfo.SSCM)+"</td ><td>"+str(Emailinfo1.CPQ)+"</td><td>Initiated</td></tr>"

					Table_info = ""
					Table_End = "</table><p><strong>Note : </strong>Please do not reply to this email.</p></body></html>"

					Error_Info = Header + Table_start + Table_info + Table_End

					LOGIN_CRE = SqlHelper.GetFirst("SELECT USER_NAME as Username,Password FROM SYCONF where Domain ='SUPPORT_MAIL'")

					# Create new SmtpClient object
					mailClient = SmtpClient()

					# Set the host and port (eg. smtp.gmail.com)
					mailClient.Host = "smtp.gmail.com"
					mailClient.Port = 587
					mailClient.EnableSsl = "true"

					# Setup NetworkCredential
					mailCred = NetworkCredential()
					mailCred.UserName = str(LOGIN_CRE.Username)
					mailCred.Password = str(LOGIN_CRE.Password)
					mailClient.Credentials = mailCred

					UserEmail = SqlHelper.GetFirst("SELECT isnull(email,'"+str(LOGIN_CRE.Username)+"') as email FROM saempl (nolock) where employee_id  = '"+str(ToEml.OWNER_ID)+"'")

					# Create two mail adresses, one for send from and the another for recipient
					if UserEmail is None:
						toEmail = MailAddress("suresh.muniyandi@bostonharborconsulting.com")
					else:
						toEmail = MailAddress(UserEmail.email)
					fromEmail = MailAddress(str(LOGIN_CRE.Username))

					# Create new MailMessage object
					msg = MailMessage(fromEmail, toEmail)

					# Set message subject and body
					msg.Subject = "Pricing Initiated - AMAT CPQ(X-Tenant)"
					msg.IsBodyHtml = True
					msg.Body = Error_Info

					# Bcc Emails	
					copyEmail4 = MailAddress("baji.baba@bostonharborconsulting.com")
					msg.Bcc.Add(copyEmail4)

					copyEmail6 = MailAddress("suresh.muniyandi@bostonharborconsulting.com")
					msg.Bcc.Add(copyEmail6) 

					# Send the message
					mailClient.Send(msg)

					#Calculation code started	
					sessionid = SqlHelper.GetFirst("SELECT NEWID() AS A")
					timestamp_sessionid = "'" + str(sessionid.A) + "'"	
					
					CRMQT = SqlHelper.GetFirst("select convert(varchar(100),c4c_quote_id) as c4c_quote_id from SAQTMT(nolock) WHERE QUOTE_ID = '"+str(Qt_Id.QUOTE_ID)+"' ") 
					
					primaryQueryItems = SqlHelper.GetFirst(
						""
						+ str(Parameter1.QUERY_CRITERIA_1)
						+ "  SAQICO_INBOUND SET TIMESTAMP = '"+str(timestamp_sessionid)+"',PROCESS_STATUS = ''INPROGRESS'' FROM SAQICO_INBOUND (NOLOCK)  WHERE ISNULL(PROCESS_STATUS,'''')='''' AND ISNULL(SESSION_ID,'''')=''"+str(sessiondetail.A)+ "'' '")
					
					#Entitlement Temp		
					sess = SqlHelper.GetFirst("select left(convert(varchar(100),newid()),5) as sess  ")

					SAQIEN = "SAQIEN_BKP_"+str(CRMQT.c4c_quote_id)+str(sess.sess)
					CRMTMP = "CRMTMP_BKP_"+str(CRMQT.c4c_quote_id)+str(sess.sess)
					SAQSCE = "SAQSCE_BKP_"+str(CRMQT.c4c_quote_id)+str(sess.sess)
					
					SAQIEN_DRP = SqlHelper.GetFirst("sp_executesql @T=N'IF EXISTS (SELECT ''X'' FROM SYS.OBJECTS WHERE NAME= ''"+str(SAQIEN)+"'' ) BEGIN DROP TABLE "+str(SAQIEN)+" END  ' ")
					
					CRMTMP_DRP = SqlHelper.GetFirst("sp_executesql @T=N'IF EXISTS (SELECT ''X'' FROM SYS.OBJECTS WHERE NAME= ''"+str(CRMTMP)+"'' ) BEGIN DROP TABLE "+str(CRMTMP)+" END  ' ")
					
					SAQSCE_DRP = SqlHelper.GetFirst("sp_executesql @T=N'IF EXISTS (SELECT ''X'' FROM SYS.OBJECTS WHERE NAME= ''"+str(SAQSCE)+"'' ) BEGIN DROP TABLE "+str(SAQSCE)+" END  ' ")
					
					#Exchange Rate
					roundcurr1 = SqlHelper.GetFirst("select distinct CASE WHEN ROUNDING_DECIMAL_PLACES = '' THEN 0  ELSE ROUNDING_DECIMAL_PLACES END  AS DECIMAL_PLACES,CASE WHEN ROUNDING_METHOD='ROUND DOWN' THEN 1 ELSE 0 END AS ROUNDING_METHOD from prcurr (nolock) where currency= 'USD' ")
					
					roundcurr = SqlHelper.GetFirst("select distinct CASE WHEN ROUNDING_DECIMAL_PLACES = '' THEN 0  ELSE ROUNDING_DECIMAL_PLACES END  AS DECIMAL_PLACES,CASE WHEN ROUNDING_METHOD='ROUND DOWN' THEN 1 ELSE 0 END AS ROUNDING_METHOD from SAQRIT(nolock) a join prcurr (nolock) on a.DOC_CURRENCY = prcurr.currency where QUOTE_ID = '"+str(Qt_Id.QUOTE_ID)+"' AND QTEREV_ID = '"+str(Qt_Id.REVISION_ID)+"' ")
						
					primaryQueryItems = SqlHelper.GetFirst(
					""
					+ str(Parameter1.QUERY_CRITERIA_1)
					+ "  SAQICO_INBOUND SET EXCHANGE_RATE = SAQTRV.EXCHANGE_RATE FROM SAQICO_INBOUND (NOLOCK) JOIN SAQTRV (NOLOCK) ON SAQICO_INBOUND.QUOTE_ID = SAQTRV.QUOTE_ID AND SAQICO_INBOUND.REVISION_ID = SAQTRV.QTEREV_ID WHERE ISNULL(PROCESS_STATUS,'''')=''INPROGRESS'' AND TIMESTAMP = '"+str(timestamp_sessionid)+"'   ' ")
					
					#Quote Item Covered Object Assembly Update 
					primaryQueryItems = SqlHelper.GetFirst(
						""
						+ str(Parameter1.QUERY_CRITERIA_1)
						+ "  A SET CM_PART_COST=CONVERT(FLOAT,B.CM_PART_COST),PM_PART_COST = CONVERT(FLOAT,B.PM_PART_COST),ASSEMBLY_NOT_MAPPED = B.ASSEMBLY_NOT_REQUIRED_FLAG,CLEANING_COST = CONVERT(FLOAT,B.CLEAN_COST),COST_MODULE_AVAILABLE = B.COST_MODULE_AVAILABLE,COST_MODULE_STATUS = B.COST_CALCULATION_STATUS,GREATER_THAN_QTLY_PM_COST = CONVERT(FLOAT,B.GREATER_THAN_QTLY_COST),KPI_COST = CONVERT(FLOAT,B.KPI_COST),LABOR_COST = CONVERT(FLOAT,B.LABOUR_COST),LESS_THAN_QTLY_PM_COST= CONVERT(FLOAT,B.LESS_THAN_QTLY_COST),METROLOGY_COST=CONVERT(FLOAT, B.METROLOGY_COST),RECOATING_COST = CONVERT(FLOAT,B.RECOATING_COST),REFURB_COST = CONVERT(FLOAT,B.REFURB_COST),SEEDSTOCK_COST = CONVERT(FLOAT,B.SEEDSTOCK_COST),TOTAL_COST_WOSEEDSTOCK = CONVERT(FLOAT,B.TOTAL_COST_WOSEEDSTOCK),TOTAL_COST_WSEEDSTOCK = CONVERT(FLOAT,TOTAL_COST_WISEEDSTOCK),NPI = B.NPI,SERVICE_COMPLEXITY = B.SERVICE_COMPLEXITY FROM SAQICA A(NOLOCK) JOIN SAQICO_INBOUND B(NOLOCK) ON A.QUOTE_ID = B.QUOTE_ID AND A.QTEREV_ID = B.REVISION_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID = B.EQUIPMENT_ID AND A.ASSEMBLY_ID = B.ASSEMBLY_ID WHERE ISNULL(PROCESS_STATUS,'''')=''INPROGRESS'' AND TIMESTAMP = '"+str(timestamp_sessionid)+"' AND A.QUOTE_ID =''"+str(Qt_Id.QUOTE_ID)+"'' ' ")
					
					#Quote Item Covered Object Roll Up Cost
					primaryQueryItems = SqlHelper.GetFirst(
						""
						+ str(Parameter1.QUERY_CRITERIA_1)
						+ "  A SET CM_PART_COST=B.CM_PART_COST,PM_PART_COST = B.PM_PART_COST,CLEANING_COST = B.CLEAN_COST,GREATER_THAN_QTLY_PM_COST = B.GREATER_THAN_QTLY_COST,KPI_COST = B.KPI_COST,LABOR_COST = B.LABOUR_COST,LESS_THAN_QTLY_PM_COST= B.LESS_THAN_QTLY_COST,METROLOGY_COST= B.METROLOGY_COST,RECOATING_COST = B.RECOATING_COST,REFURB_COST = B.REFURB_COST,SEEDSTOCK_COST = B.SEEDSTOCK_COST,TOTAL_COST_WOSEEDSTOCK = B.TOTAL_COST_WOSEEDSTOCK,TOTAL_COST_WSEEDSTOCK = TOTAL_COST_WISEEDSTOCK,HEAD_REBUILD_QTY= B.HEADREBUILD_QTY FROM SAQICO A(NOLOCK) JOIN (SELECT QUOTE_ID,SERVICE_ID,EQUIPMENT_ID,SUM(CONVERT(FLOAT,CM_PART_COST)) AS CM_PART_COST,SUM(CONVERT(FLOAT,PM_PART_COST)) AS PM_PART_COST,SUM(CONVERT(FLOAT,CLEAN_COST)) AS CLEAN_COST, SUM(CONVERT(FLOAT,GREATER_THAN_QTLY_COST)) AS GREATER_THAN_QTLY_COST,SUM(CONVERT(FLOAT,KPI_COST)) AS KPI_COST,SUM(CONVERT(FLOAT,LABOUR_COST)) AS LABOUR_COST,SUM(CONVERT(FLOAT,LESS_THAN_QTLY_COST)) AS LESS_THAN_QTLY_COST,SUM(CONVERT(FLOAT,METROLOGY_COST)) AS METROLOGY_COST,SUM(CONVERT(FLOAT,RECOATING_COST)) AS RECOATING_COST,SUM(CONVERT(FLOAT,REFURB_COST)) AS REFURB_COST, SUM(CONVERT(FLOAT,SEEDSTOCK_COST)) AS SEEDSTOCK_COST,SUM(CONVERT(FLOAT,TOTAL_COST_WOSEEDSTOCK)) AS TOTAL_COST_WOSEEDSTOCK,SUM(CONVERT(FLOAT,TOTAL_COST_WISEEDSTOCK)) AS TOTAL_COST_WISEEDSTOCK,REVISION_ID,MIN(HEADREBUILD_QTY) AS HEADREBUILD_QTY  FROM SAQICO_INBOUND B(NOLOCK) WHERE ISNULL(PROCESS_STATUS,'''')=''INPROGRESS'' AND TIMESTAMP = '"+str(timestamp_sessionid)+"' GROUP BY QUOTE_ID,SERVICE_ID,EQUIPMENT_ID,REVISION_ID  )B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID = B.EQUIPMENT_ID AND A.QTEREV_ID = B.REVISION_ID ' ")
						
					primaryQueryItems = SqlHelper.GetFirst(
						""
						+ str(Parameter1.QUERY_CRITERIA_1)
						+ "  A SET MODULE_ID=B.MODULE_ID,MODULE_NAME = B.MODULE_NAME,MODULE_RECORD_ID=COST_MODULE_RECORD_ID FROM SAQICO A(NOLOCK) JOIN (SELECT  DISTINCT QUOTE_ID,SERVICE_ID,EQUIPMENT_ID,REVISION_ID,MODULE_ID,MODULE_NAME  FROM SAQICO_INBOUND B(NOLOCK) WHERE ISNULL(PROCESS_STATUS,'''')=''INPROGRESS'' AND TIMESTAMP = '"+str(timestamp_sessionid)+"'  )B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID = B.EQUIPMENT_ID AND A.QTEREV_ID = B.REVISION_ID LEFT JOIN MACMDL (NOLOCK) ON B.MODULE_ID = MACMDL.MODULE_ID  ' ")
					
					#NPI
					
					primaryQueryItems = SqlHelper.GetFirst(
						""
						+ str(Parameter1.QUERY_CRITERIA_1)
						+ "  A SET TOOL_NPI = ''Yes'' FROM SAQICO_INBOUND A(NOLOCK) JOIN (SELECT QUOTE_ID,SERVICE_ID,EQUIPMENT_ID,TIMESTAMP,SESSION_ID FROM SAQICO_INBOUND (NOLOCK) WHERE ISNULL(PROCESS_STATUS,'''')=''INPROGRESS'' AND TIMESTAMP = '"+str(timestamp_sessionid)+"' AND NPI = ''TRUE'' )B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID = B.EQUIPMENT_ID AND A.TIMESTAMP = B.TIMESTAMP AND A.SESSION_ID = B.SESSION_ID  ' ")

					primaryQueryItems = SqlHelper.GetFirst(
											""
											+ str(Parameter1.QUERY_CRITERIA_1)
											+ "  SAQICO_INBOUND SET TOOL_NPI = ''No'' FROM SAQICO_INBOUND (NOLOCK) WHERE ISNULL(PROCESS_STATUS,'''')=''INPROGRESS'' AND TIMESTAMP = '"+str(timestamp_sessionid)+"' AND ISNULL(TOOL_NPI,'''') = ''''  ' ")
					
					#Z0091
					primaryQueryItems = SqlHelper.GetFirst(
												""
												+ str(Parameter1.QUERY_CRITERIA_1)
												+ "  A SET NPI_COEFFICIENT = CONVERT(VARCHAR,ENTITLEMENT_COEFFICIENT),NPI_CODE = ENTITLEMENT_VALUE_CODE FROM SAQICO_INBOUND (NOLOCK) A JOIN PRENVL B(NOLOCK) ON A.TOOL_NPI = B.ENTITLEMENT_DISPLAY_VALUE WHERE ISNULL(PROCESS_STATUS,'''')=''INPROGRESS'' AND TIMESTAMP = '"+str(timestamp_sessionid)+"' AND ISNULL(TOOL_NPI,'''') <> '''' AND ENTITLEMENT_ID = ''AGS_Z0091_VAL_NPIREC'' AND A.SERVICE_ID = ''Z0091'' ' ")
					
					#Z0092
					primaryQueryItems = SqlHelper.GetFirst(
					""
					+ str(Parameter1.QUERY_CRITERIA_1)
					+ "  A SET NPI_COEFFICIENT = CONVERT(VARCHAR,ENTITLEMENT_COEFFICIENT),NPI_CODE = ENTITLEMENT_VALUE_CODE FROM SAQICO_INBOUND (NOLOCK) A JOIN PRENVL B(NOLOCK) ON A.TOOL_NPI = B.ENTITLEMENT_DISPLAY_VALUE WHERE ISNULL(PROCESS_STATUS,'''')=''INPROGRESS'' AND TIMESTAMP = '"+str(timestamp_sessionid)+"' AND ISNULL(TOOL_NPI,'''') <> '''' AND ENTITLEMENT_ID = ''AGS_Z0092_VAL_NPIREC'' AND A.SERVICE_ID = ''Z0092'' ' ")
					
					#Z0004
					primaryQueryItems = SqlHelper.GetFirst(
					""
					+ str(Parameter1.QUERY_CRITERIA_1)
					+ "  A SET NPI_COEFFICIENT = CONVERT(VARCHAR,ENTITLEMENT_COEFFICIENT),NPI_CODE = ENTITLEMENT_VALUE_CODE FROM SAQICO_INBOUND (NOLOCK) A JOIN PRENVL B(NOLOCK) ON A.TOOL_NPI = B.ENTITLEMENT_DISPLAY_VALUE WHERE ISNULL(PROCESS_STATUS,'''')=''INPROGRESS'' AND TIMESTAMP = '"+str(timestamp_sessionid)+"' AND ISNULL(TOOL_NPI,'''') <> '''' AND ENTITLEMENT_ID = ''AGS_Z0004_VAL_NPIREC'' AND A.SERVICE_ID = ''Z0004'' ' ")
					
					#Z0099
					primaryQueryItems = SqlHelper.GetFirst(
					""
					+ str(Parameter1.QUERY_CRITERIA_1)
					+ "  A SET NPI_COEFFICIENT = CONVERT(VARCHAR,ENTITLEMENT_COEFFICIENT),NPI_CODE = ENTITLEMENT_VALUE_CODE FROM SAQICO_INBOUND (NOLOCK) A JOIN PRENVL B(NOLOCK) ON A.TOOL_NPI = B.ENTITLEMENT_DISPLAY_VALUE WHERE ISNULL(PROCESS_STATUS,'''')=''INPROGRESS'' AND TIMESTAMP = '"+str(timestamp_sessionid)+"' AND ISNULL(TOOL_NPI,'''') <> '''' AND ENTITLEMENT_ID = ''AGS_Z0099_VAL_NPIREC'' AND A.SERVICE_ID = ''Z0099'' ' ")
					
					#Z0035
					primaryQueryItems = SqlHelper.GetFirst(
					""
					+ str(Parameter1.QUERY_CRITERIA_1)
					+ "  A SET NPI_COEFFICIENT = CONVERT(VARCHAR,ENTITLEMENT_COEFFICIENT),NPI_CODE = ENTITLEMENT_VALUE_CODE FROM SAQICO_INBOUND (NOLOCK) A JOIN PRENVL B(NOLOCK) ON A.TOOL_NPI = B.ENTITLEMENT_DISPLAY_VALUE WHERE ISNULL(PROCESS_STATUS,'''')=''INPROGRESS'' AND TIMESTAMP = '"+str(timestamp_sessionid)+"' AND ISNULL(TOOL_NPI,'''') <> '''' AND ENTITLEMENT_ID = ''AGS_Z0035_VAL_NPIREC'' AND A.SERVICE_ID = ''Z0035'' ' ")
					
					#Z0009
					primaryQueryItems = SqlHelper.GetFirst(
					""
					+ str(Parameter1.QUERY_CRITERIA_1)
					+ "  A SET NPI_COEFFICIENT = CONVERT(VARCHAR,ENTITLEMENT_COEFFICIENT),NPI_CODE = ENTITLEMENT_VALUE_CODE FROM SAQICO_INBOUND (NOLOCK) A JOIN PRENVL B(NOLOCK) ON A.TOOL_NPI = B.ENTITLEMENT_DISPLAY_VALUE WHERE ISNULL(PROCESS_STATUS,'''')=''INPROGRESS'' AND TIMESTAMP = '"+str(timestamp_sessionid)+"' AND ISNULL(TOOL_NPI,'''') <> '''' AND ENTITLEMENT_ID = ''AGS_Z0009_VAL_NPIREC'' AND A.SERVICE_ID = ''Z0009'' ' ")

					#Service Complexity									
					primaryQueryItems = SqlHelper.GetFirst(
						""
						+ str(Parameter1.QUERY_CRITERIA_1)
						+ " A SET GREENBOOK = B.GREENBOOK FROM SAQICO_INBOUND (NOLOCK) A JOIN SAQICO (NOLOCK) B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID = B.EQUIPMENT_ID AND A.REVISION_ID = B.QTEREV_ID WHERE ISNULL(PROCESS_STATUS,'''')=''INPROGRESS'' AND TIMESTAMP = '"+str(timestamp_sessionid)+"' '")
						
					primaryQueryItems = SqlHelper.GetFirst(
											""
											+ str(Parameter1.QUERY_CRITERIA_1)
											+ " A SET TOOL_SERVICE_COMPLEXITY = B.SERVICE_COMPLEXITY FROM SAQICO_INBOUND A(NOLOCK) JOIN (SELECT A.QUOTE_ID,A.SERVICE_ID,A.EQUIPMENT_ID,A.REVISION_ID AS QTEREV_ID,CASE WHEN A.SERVICE_COMPLEXITY = ''DIFFICULT'' THEN ''Difficult'' ELSE A.SERVICE_COMPLEXITY END AS SERVICE_COMPLEXITY FROM SAQICO_INBOUND (NOLOCK) A JOIN SAQICA (NOLOCK) B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID = B.EQUIPMENT_ID AND A.REVISION_ID = B.QTEREV_ID AND A.ASSEMBLY_ID = B.ASSEMBLY_ID WHERE ISNULL(PROCESS_STATUS,'''')=''INPROGRESS'' AND TIMESTAMP = '"+str(timestamp_sessionid)+"' AND B.EQUIPMENTTYPE_ID=''MAINFRAME'' AND A.GREENBOOK IN (''CMP'',''PDC'',''MPS'',''IMPLANT'') )B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID = B.EQUIPMENT_ID AND A.REVISION_ID = B.QTEREV_ID   '")

					primaryQueryItems = SqlHelper.GetFirst(
																""
																+ str(Parameter1.QUERY_CRITERIA_1)
																+ " A SET TOOL_SERVICE_COMPLEXITY = ''Difficult'' FROM SAQICO_INBOUND A(NOLOCK) JOIN (SELECT A.QUOTE_ID,A.SERVICE_ID,A.EQUIPMENT_ID,A.REVISION_ID AS QTEREV_ID,COUNT(*) AS SERVICE_COMPLEXITY FROM SAQICO_INBOUND (NOLOCK) A WHERE ISNULL(PROCESS_STATUS,'''')=''INPROGRESS'' AND TIMESTAMP = '"+str(timestamp_sessionid)+"' AND A.SERVICE_COMPLEXITY = ''Difficult'' AND A.GREENBOOK NOT IN (''CMP'',''PDC'',''MPS'',''IMPLANT'') GROUP BY A.QUOTE_ID,A.SERVICE_ID,A.EQUIPMENT_ID,A.REVISION_ID )B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID = B.EQUIPMENT_ID AND A.REVISION_ID = B.QTEREV_ID WHERE B.SERVICE_COMPLEXITY >= 2  '")

					primaryQueryItems = SqlHelper.GetFirst( ""+ str(Parameter1.QUERY_CRITERIA_1)+ " A SET TOOL_SERVICE_COMPLEXITY = CASE WHEN WA>=75 THEN ''Difficult'' WHEN WA>=25 AND WA<75 THEN ''MEDIUM'' WHEN WA<25 THEN ''EASY'' ELSE NULL END  FROM SAQICO_INBOUND A(NOLOCK) JOIN (SELECT QUOTE_ID,SERVICE_ID,EQUIPMENT_ID,QTEREV_ID,SCORE/SERVICE_COMPLEXITY AS WA FROM (SELECT A.QUOTE_ID,A.SERVICE_ID,A.EQUIPMENT_ID,A.REVISION_ID AS QTEREV_ID,COUNT(CASE WHEN ISNULL(SERVICE_COMPLEXITY,'''')='''' THEN NULL ELSE 1 END) AS SERVICE_COMPLEXITY,SUM(CASE WHEN ISNULL(SERVICE_COMPLEXITY,'''')=''DIFFICULT'' THEN 100 WHEN ISNULL(SERVICE_COMPLEXITY,'''')=''MEDIUM'' THEN 50 ELSE 0 END) AS SCORE FROM SAQICO_INBOUND (NOLOCK) A WHERE ISNULL(PROCESS_STATUS,'''')=''INPROGRESS'' AND TIMESTAMP = '"+str(timestamp_sessionid)+"' AND A.GREENBOOK NOT IN (''CMP'',''PDC'',''MPS'',''IMPLANT'') GROUP BY A.QUOTE_ID,A.SERVICE_ID,A.EQUIPMENT_ID,A.REVISION_ID)B WHERE EQUIPMENT_ID IN (SELECT DISTINCT EQUIPMENT_ID FROM (SELECT A.QUOTE_ID,A.SERVICE_ID,A.EQUIPMENT_ID,A.REVISION_ID AS QTEREV_ID,COUNT(CASE WHEN ISNULL(SERVICE_COMPLEXITY,'''')=''DIFFICULT'' THEN 1 ELSE NULL END) AS SERV_COMP  FROM SAQICO_INBOUND (NOLOCK) A  WHERE ISNULL(PROCESS_STATUS,'''')=''INPROGRESS'' AND TIMESTAMP = '"+str(timestamp_sessionid)+"' AND ISNULL(TOOL_SERVICE_COMPLEXITY,'''')='''' AND A.GREENBOOK NOT IN (''CMP'',''PDC'',''MPS'',''IMPLANT'') GROUP BY A.QUOTE_ID,A.SERVICE_ID,A.EQUIPMENT_ID,A.REVISION_ID ) A WHERE SERV_COMP<2) AND ISNULL(SERVICE_COMPLEXITY,0)>0 )B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID = B.EQUIPMENT_ID AND A.REVISION_ID = B.QTEREV_ID    '")
					
					#Z0091
					primaryQueryItems = SqlHelper.GetFirst(
																	""
																	+ str(Parameter1.QUERY_CRITERIA_1)
																	+ "  A SET SERVICECOMPLEXITY_COEFFICIENT = CONVERT(VARCHAR,ENTITLEMENT_COEFFICIENT),SERVICE_COMPLEXITY_CODE = ENTITLEMENT_VALUE_CODE FROM SAQICO_INBOUND (NOLOCK) A JOIN PRENVL B(NOLOCK) ON A.TOOL_SERVICE_COMPLEXITY = B.ENTITLEMENT_DISPLAY_VALUE WHERE ISNULL(PROCESS_STATUS,'''')=''INPROGRESS'' AND TIMESTAMP = '"+str(timestamp_sessionid)+"' AND ISNULL(TOOL_SERVICE_COMPLEXITY,'''') <> '''' AND ENTITLEMENT_ID = ''AGS_Z0091_VAL_SCCCDF'' AND A.SERVICE_ID = ''Z0091'' ' ")
					
					#Z0092					
					primaryQueryItems = SqlHelper.GetFirst(
										""
										+ str(Parameter1.QUERY_CRITERIA_1)
										+ "  A SET SERVICECOMPLEXITY_COEFFICIENT = CONVERT(VARCHAR,ENTITLEMENT_COEFFICIENT),SERVICE_COMPLEXITY_CODE = ENTITLEMENT_VALUE_CODE FROM SAQICO_INBOUND (NOLOCK) A JOIN PRENVL B(NOLOCK) ON A.TOOL_SERVICE_COMPLEXITY = B.ENTITLEMENT_DISPLAY_VALUE WHERE ISNULL(PROCESS_STATUS,'''')=''INPROGRESS'' AND TIMESTAMP = '"+str(timestamp_sessionid)+"' AND ISNULL(TOOL_SERVICE_COMPLEXITY,'''') <> '''' AND ENTITLEMENT_ID = ''AGS_Z0092_VAL_SCCCDF'' AND A.SERVICE_ID = ''Z0092'' ' ")
					
					#Z0004					
					primaryQueryItems = SqlHelper.GetFirst(
										""
										+ str(Parameter1.QUERY_CRITERIA_1)
										+ "  A SET SERVICECOMPLEXITY_COEFFICIENT = CONVERT(VARCHAR,ENTITLEMENT_COEFFICIENT),SERVICE_COMPLEXITY_CODE = ENTITLEMENT_VALUE_CODE FROM SAQICO_INBOUND (NOLOCK) A JOIN PRENVL B(NOLOCK) ON A.TOOL_SERVICE_COMPLEXITY = B.ENTITLEMENT_DISPLAY_VALUE WHERE ISNULL(PROCESS_STATUS,'''')=''INPROGRESS'' AND TIMESTAMP = '"+str(timestamp_sessionid)+"' AND ISNULL(TOOL_SERVICE_COMPLEXITY,'''') <> '''' AND ENTITLEMENT_ID = ''AGS_Z0004_VAL_SCCCDF'' AND A.SERVICE_ID = ''Z0004'' ' ")
					
					#Z0099					
					primaryQueryItems = SqlHelper.GetFirst(
										""
										+ str(Parameter1.QUERY_CRITERIA_1)
										+ "  A SET SERVICECOMPLEXITY_COEFFICIENT = CONVERT(VARCHAR,ENTITLEMENT_COEFFICIENT),SERVICE_COMPLEXITY_CODE = ENTITLEMENT_VALUE_CODE FROM SAQICO_INBOUND (NOLOCK) A JOIN PRENVL B(NOLOCK) ON A.TOOL_SERVICE_COMPLEXITY = B.ENTITLEMENT_DISPLAY_VALUE WHERE ISNULL(PROCESS_STATUS,'''')=''INPROGRESS'' AND TIMESTAMP = '"+str(timestamp_sessionid)+"' AND ISNULL(TOOL_SERVICE_COMPLEXITY,'''') <> '''' AND ENTITLEMENT_ID = ''AGS_Z0099_VAL_SCCCDF'' AND A.SERVICE_ID = ''Z0099'' ' ")
					
					#Z0035					
					primaryQueryItems = SqlHelper.GetFirst(
										""
										+ str(Parameter1.QUERY_CRITERIA_1)
										+ "  A SET SERVICECOMPLEXITY_COEFFICIENT = CONVERT(VARCHAR,ENTITLEMENT_COEFFICIENT),SERVICE_COMPLEXITY_CODE = ENTITLEMENT_VALUE_CODE FROM SAQICO_INBOUND (NOLOCK) A JOIN PRENVL B(NOLOCK) ON A.TOOL_SERVICE_COMPLEXITY = B.ENTITLEMENT_DISPLAY_VALUE WHERE ISNULL(PROCESS_STATUS,'''')=''INPROGRESS'' AND TIMESTAMP = '"+str(timestamp_sessionid)+"' AND ISNULL(TOOL_SERVICE_COMPLEXITY,'''') <> '''' AND ENTITLEMENT_ID = ''AGS_Z0035_VAL_SCCCDF'' AND A.SERVICE_ID = ''Z0035'' ' ")
					
					#Z0009					
					primaryQueryItems = SqlHelper.GetFirst(
										""
										+ str(Parameter1.QUERY_CRITERIA_1)
										+ "  A SET SERVICECOMPLEXITY_COEFFICIENT = CONVERT(VARCHAR,ENTITLEMENT_COEFFICIENT),SERVICE_COMPLEXITY_CODE = ENTITLEMENT_VALUE_CODE FROM SAQICO_INBOUND (NOLOCK) A JOIN PRENVL B(NOLOCK) ON A.TOOL_SERVICE_COMPLEXITY = B.ENTITLEMENT_DISPLAY_VALUE WHERE ISNULL(PROCESS_STATUS,'''')=''INPROGRESS'' AND TIMESTAMP = '"+str(timestamp_sessionid)+"' AND ISNULL(TOOL_SERVICE_COMPLEXITY,'''') <> '''' AND ENTITLEMENT_ID = ''AGS_Z0009_VAL_SCCCDF'' AND A.SERVICE_ID = ''Z0009'' ' ")
						
					SAQIEN_INSERT = SqlHelper.GetFirst(
							"sp_executesql @T=N'SELECT A.QUOTE_ID,A.QTEREV_ID,A.LINE,A.ENTITLEMENT_XML,B.EQUIPMENT_ID,A.SERVICE_ID INTO "+str(SAQIEN)+" FROM SAQITE(NOLOCK) A JOIN SAQRIO B(NOLOCK) ON A.QUOTE_ID = B.QUOTE_ID AND A.QTEREV_ID = B.QTEREV_ID WHERE A.QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND A.QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"''  '")
							
					start12 = 1
					end12 = 300

					Check_flag12 = 1
					while Check_flag12 == 1:

						table12 = SqlHelper.GetFirst(
									"SELECT DISTINCT equipment_id FROM (SELECT DISTINCT equipment_id, ROW_NUMBER()OVER(ORDER BY equipment_id) AS SNO FROM (SELECT DISTINCT equipment_id FROM SAQICO_INBOUND (NOLOCK) WHERE ISNULL(PROCESS_STATUS,'')='INPROGRESS' AND TIMESTAMP = "+str(timestamp_sessionid)+" )A ) A WHERE SNO>= "+str(start12)+" AND SNO<="+str(end12)+""
								)
								
						CRMTMP12 = SqlHelper.GetFirst("sp_executesql @T=N'IF NOT EXISTS (SELECT ''X'' FROM SYS.OBJECTS WHERE NAME= ''"+str(CRMTMP)+"'' ) BEGIN CREATE TABLE "+str(CRMTMP)+" (EQUIPMENT_IDD VARCHAR(100)) END  ' ")
						
						table_ins = SqlHelper.GetFirst(
							"sp_executesql @T=N'INSERT "+str(CRMTMP)+" SELECT DISTINCT equipment_id FROM (SELECT DISTINCT equipment_id, ROW_NUMBER()OVER(ORDER BY equipment_id) AS SNO FROM (SELECT DISTINCT equipment_id FROM SAQICO_INBOUND (NOLOCK) WHERE ISNULL(PROCESS_STATUS,'''')=''INPROGRESS'' AND TIMESTAMP = '"+str(timestamp_sessionid)+"' )A ) A WHERE SNO>= "+str(start12)+" AND SNO<="+str(end12)+"  '")
							
						start12 = start12 + 300
						end12 = end12 + 300

						if str(table12) != "None":
						
							#SAQIEN
							primaryQueryItems = SqlHelper.GetFirst("sp_executesql @t=N'UPDATE A SET ENTITLEMENT_XML = replace(replace(entitlement_xml,''	'',''''),''\n'','''')  FROM "+str(SAQIEN)+"(NOLOCK) A JOIN "+str(CRMTMP)+" C ON A.EQUIPMENT_ID = C.EQUIPMENT_IDD  WHERE A.QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND A.QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' '")
							
							table_inrt = SqlHelper.GetFirst(
							"sp_executesql @T=N'SELECT * INTO "+str(SAQSCE)+" FROM "+str(SAQIEN)+"(NOLOCK) JOIN "+str(CRMTMP)+"  ON EQUIPMENT_ID = EQUIPMENT_IDD  WHERE QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"''  '")
							
							#SAQIEN NPI
							#Z0091
							primaryQueryItems = SqlHelper.GetFirst("sp_executesql @t=N'UPDATE A SET ENTITLEMENT_XML = CASE WHEN charindex( ''<ENTITLEMENT_ID>AGS_Z0091_VAL_NPIREC</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'',replace(replace(entitlement_xml,''	'',''''),''\n'','''')) >0 THEN REPLACE(entitlement_xml ,  substring(entitlement_xml,charindex(''<ENTITLEMENT_ID>AGS_Z0091_VAL_NPIREC</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'' ,entitlement_xml),charindex(''</ENTITLEMENT_VALUE_CODE>''  ,substring(entitlement_xml,charindex(''<ENTITLEMENT_ID>AGS_Z0091_VAL_NPIREC</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'' ,entitlement_xml) , 1000 ))-1  ), ''<ENTITLEMENT_ID>AGS_Z0091_VAL_NPIREC</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>''+NPI_CODE) ELSE ENTITLEMENT_XML END FROM "+str(SAQIEN)+"(NOLOCK) A JOIN (SELECT DISTINCT QUOTE_ID ,SERVICE_ID,EQUIPMENT_ID,REVISION_ID,NPI_CODE FROM SAQICO_INBOUND B(NOLOCK) JOIN "+str(CRMTMP)+" C ON B.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE ISNULL(PROCESS_STATUS,'''')=''INPROGRESS'' AND TIMESTAMP = '"+str(timestamp_sessionid)+"' AND SERVICE_ID = ''Z0091'' ) B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID  = B.EQUIPMENT_ID AND A.QTEREV_ID = B.REVISION_ID  WHERE A.QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND A.QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND ISNULL(NPI_CODE,'''')<>''''  '")
							
							primaryQueryItems = SqlHelper.GetFirst("sp_executesql @t=N'UPDATE A SET ENTITLEMENT_XML = CASE WHEN charindex( ''<ENTITLEMENT_ID>AGS_Z0091_VAL_NPIREC</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'',replace(replace(entitlement_xml,''	'',''''),''\n'','''')) >0 THEN REPLACE(entitlement_xml ,  substring(entitlement_xml,charindex(''<ENTITLEMENT_ID>AGS_Z0091_VAL_NPIREC</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'' ,entitlement_xml),charindex(''</ENTITLEMENT_DISPLAY_VALUE>''  ,substring(entitlement_xml,charindex(''<ENTITLEMENT_ID>AGS_Z0091_VAL_NPIREC</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'' ,entitlement_xml) , 1000 ))-1  ), replace(substring(entitlement_xml,charindex(''<ENTITLEMENT_ID>AGS_Z0091_VAL_NPIREC</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'' ,entitlement_xml),charindex(''<ENTITLEMENT_DISPLAY_VALUE>''  ,substring(entitlement_xml,charindex(''<ENTITLEMENT_ID>AGS_Z0091_VAL_NPIREC</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'' ,entitlement_xml) , 1000 ))-1  ),''select'','''') +''<ENTITLEMENT_DISPLAY_VALUE>'' + TOOL_NPI  ) ELSE ENTITLEMENT_XML END FROM "+str(SAQIEN)+"(NOLOCK) A JOIN (SELECT DISTINCT QUOTE_ID ,SERVICE_ID,EQUIPMENT_ID,REVISION_ID,TOOL_NPI FROM SAQICO_INBOUND B(NOLOCK) JOIN "+str(CRMTMP)+" C ON B.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE ISNULL(PROCESS_STATUS,'''')=''INPROGRESS'' AND TIMESTAMP = '"+str(timestamp_sessionid)+"' AND SERVICE_ID = ''Z0091'' ) B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID  = B.EQUIPMENT_ID AND A.QTEREV_ID = B.REVISION_ID  WHERE A.QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND A.QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND ISNULL(TOOL_NPI,'''')<>''''  '")
							
							#Z0092
							primaryQueryItems = SqlHelper.GetFirst("sp_executesql @t=N'UPDATE A SET ENTITLEMENT_XML = CASE WHEN charindex( ''<ENTITLEMENT_ID>AGS_Z0092_VAL_NPIREC</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'',replace(replace(entitlement_xml,''	'',''''),''\n'','''')) >0 THEN REPLACE(entitlement_xml ,  substring(entitlement_xml,charindex(''<ENTITLEMENT_ID>AGS_Z0092_VAL_NPIREC</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'' ,entitlement_xml),charindex(''</ENTITLEMENT_VALUE_CODE>''  ,substring(entitlement_xml,charindex(''<ENTITLEMENT_ID>AGS_Z0092_VAL_NPIREC</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'' ,entitlement_xml) , 1000 ))-1  ), ''<ENTITLEMENT_ID>AGS_Z0092_VAL_NPIREC</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>''+NPI_CODE ) ELSE ENTITLEMENT_XML END FROM "+str(SAQIEN)+"(NOLOCK) A JOIN (SELECT DISTINCT QUOTE_ID ,SERVICE_ID,EQUIPMENT_ID,REVISION_ID,NPI_CODE FROM SAQICO_INBOUND B(NOLOCK) JOIN "+str(CRMTMP)+" C ON B.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE ISNULL(PROCESS_STATUS,'''')=''INPROGRESS'' AND TIMESTAMP = '"+str(timestamp_sessionid)+"' AND SERVICE_ID = ''Z0092'' ) B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID  = B.EQUIPMENT_ID AND A.QTEREV_ID = B.REVISION_ID  WHERE A.QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND A.QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND ISNULL(NPI_CODE,'''')<>''''  '")
							
							primaryQueryItems = SqlHelper.GetFirst("sp_executesql @t=N'UPDATE A SET ENTITLEMENT_XML = CASE WHEN charindex( ''<ENTITLEMENT_ID>AGS_Z0092_VAL_NPIREC</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'',replace(replace(entitlement_xml,''	'',''''),''\n'','''')) >0 THEN REPLACE(entitlement_xml ,  substring(entitlement_xml,charindex(''<ENTITLEMENT_ID>AGS_Z0092_VAL_NPIREC</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'' ,entitlement_xml),charindex(''</ENTITLEMENT_DISPLAY_VALUE>''  ,substring(entitlement_xml,charindex(''<ENTITLEMENT_ID>AGS_Z0092_VAL_NPIREC</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'' ,entitlement_xml) , 1000 ))-1  ), replace(substring(entitlement_xml,charindex(''<ENTITLEMENT_ID>AGS_Z0092_VAL_NPIREC</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'' ,entitlement_xml),charindex(''<ENTITLEMENT_DISPLAY_VALUE>''  ,substring(entitlement_xml,charindex(''<ENTITLEMENT_ID>AGS_Z0092_VAL_NPIREC</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'' ,entitlement_xml) , 1000 ))-1  ),''select'','''') + ''<ENTITLEMENT_DISPLAY_VALUE>'' + TOOL_NPI  ) ELSE ENTITLEMENT_XML END FROM "+str(SAQIEN)+"(NOLOCK) A JOIN (SELECT DISTINCT QUOTE_ID ,SERVICE_ID,EQUIPMENT_ID,REVISION_ID,TOOL_NPI FROM SAQICO_INBOUND B(NOLOCK) JOIN "+str(CRMTMP)+" C ON B.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE ISNULL(PROCESS_STATUS,'''')=''INPROGRESS'' AND TIMESTAMP = '"+str(timestamp_sessionid)+"' AND SERVICE_ID = ''Z0092'' ) B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID  = B.EQUIPMENT_ID AND A.QTEREV_ID = B.REVISION_ID  WHERE A.QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND A.QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND ISNULL(TOOL_NPI,'''')<>''''  '")
							
							#Z0004
							primaryQueryItems = SqlHelper.GetFirst("sp_executesql @t=N'UPDATE A SET ENTITLEMENT_XML = CASE WHEN charindex( ''<ENTITLEMENT_ID>AGS_Z0004_VAL_NPIREC</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'',replace(replace(entitlement_xml,''	'',''''),''\n'','''')) >0  THEN REPLACE(entitlement_xml ,  substring(entitlement_xml,charindex(''<ENTITLEMENT_ID>AGS_Z0004_VAL_NPIREC</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'' ,entitlement_xml),charindex(''</ENTITLEMENT_VALUE_CODE>''  ,substring(entitlement_xml,charindex(''<ENTITLEMENT_ID>AGS_Z0004_VAL_NPIREC</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'' ,entitlement_xml) , 1000 ))-1  ), ''<ENTITLEMENT_ID>AGS_Z0004_VAL_NPIREC</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>''+NPI_CODE ) ELSE ENTITLEMENT_XML END FROM "+str(SAQIEN)+"(NOLOCK) A JOIN (SELECT DISTINCT QUOTE_ID ,SERVICE_ID,EQUIPMENT_ID,REVISION_ID,NPI_CODE FROM SAQICO_INBOUND B(NOLOCK) JOIN "+str(CRMTMP)+" C ON B.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE ISNULL(PROCESS_STATUS,'''')=''INPROGRESS'' AND TIMESTAMP = '"+str(timestamp_sessionid)+"' AND SERVICE_ID = ''Z0004'' ) B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID  = B.EQUIPMENT_ID AND A.QTEREV_ID = B.REVISION_ID  WHERE A.QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND A.QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND ISNULL(NPI_CODE,'''')<>''''  '")
							
							primaryQueryItems = SqlHelper.GetFirst("sp_executesql @t=N'UPDATE A SET ENTITLEMENT_XML = CASE WHEN charindex( ''<ENTITLEMENT_ID>AGS_Z0004_VAL_NPIREC</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'',replace(replace(entitlement_xml,''	'',''''),''\n'','''')) >0 THEN REPLACE(entitlement_xml ,  substring(entitlement_xml,charindex(''<ENTITLEMENT_ID>AGS_Z0004_VAL_NPIREC</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'' ,entitlement_xml),charindex(''</ENTITLEMENT_DISPLAY_VALUE>''  ,substring(entitlement_xml,charindex(''<ENTITLEMENT_ID>AGS_Z0004_VAL_NPIREC</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'' ,entitlement_xml) , 1000 ))-1  ), replace(substring(entitlement_xml,charindex(''<ENTITLEMENT_ID>AGS_Z0004_VAL_NPIREC</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'' ,entitlement_xml),charindex(''<ENTITLEMENT_DISPLAY_VALUE>''  ,substring(entitlement_xml,charindex(''<ENTITLEMENT_ID>AGS_Z0004_VAL_NPIREC</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'' ,entitlement_xml) , 1000 ))-1  ),''select'','''') +''<ENTITLEMENT_DISPLAY_VALUE>'' + TOOL_NPI  ) ELSE ENTITLEMENT_XML END FROM "+str(SAQIEN)+"(NOLOCK) A JOIN (SELECT DISTINCT QUOTE_ID ,SERVICE_ID,EQUIPMENT_ID,REVISION_ID,TOOL_NPI FROM SAQICO_INBOUND B(NOLOCK) JOIN "+str(CRMTMP)+" C ON B.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE ISNULL(PROCESS_STATUS,'''')=''INPROGRESS'' AND TIMESTAMP = '"+str(timestamp_sessionid)+"' AND SERVICE_ID = ''Z0004'' ) B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID  = B.EQUIPMENT_ID AND A.QTEREV_ID = B.REVISION_ID  WHERE A.QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND A.QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND ISNULL(TOOL_NPI,'''')<>''''  '")
							
							
							#Z0099
							primaryQueryItems = SqlHelper.GetFirst("sp_executesql @t=N'UPDATE A SET ENTITLEMENT_XML = CASE WHEN charindex( ''<ENTITLEMENT_ID>AGS_Z0099_VAL_NPIREC</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'',replace(replace(entitlement_xml,''	'',''''),''\n'','''')) >0 THEN REPLACE(entitlement_xml ,  substring(entitlement_xml,charindex(''<ENTITLEMENT_ID>AGS_Z0099_VAL_NPIREC</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'' ,entitlement_xml),charindex(''</ENTITLEMENT_VALUE_CODE>''  ,substring(entitlement_xml,charindex(''<ENTITLEMENT_ID>AGS_Z0099_VAL_NPIREC</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'' ,entitlement_xml) , 1000 ))-1  ), ''<ENTITLEMENT_ID>AGS_Z0099_VAL_NPIREC</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>''+NPI_CODE ) ELSE ENTITLEMENT_XML END FROM "+str(SAQIEN)+"(NOLOCK) A JOIN (SELECT DISTINCT QUOTE_ID ,SERVICE_ID,EQUIPMENT_ID,REVISION_ID,NPI_CODE FROM SAQICO_INBOUND B(NOLOCK) JOIN "+str(CRMTMP)+" C ON B.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE ISNULL(PROCESS_STATUS,'''')=''INPROGRESS'' AND TIMESTAMP = '"+str(timestamp_sessionid)+"' AND SERVICE_ID = ''Z0099'' ) B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID  = B.EQUIPMENT_ID AND A.QTEREV_ID = B.REVISION_ID  WHERE A.QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND A.QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND ISNULL(NPI_CODE,'''')<>''''   '")
							
							primaryQueryItems = SqlHelper.GetFirst("sp_executesql @t=N'UPDATE A SET ENTITLEMENT_XML = CASE WHEN charindex( ''<ENTITLEMENT_ID>AGS_Z0099_VAL_NPIREC</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'',replace(replace(entitlement_xml,''	'',''''),''\n'','''')) >0 THEN REPLACE(entitlement_xml ,  substring(entitlement_xml,charindex(''<ENTITLEMENT_ID>AGS_Z0099_VAL_NPIREC</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'' ,entitlement_xml),charindex(''</ENTITLEMENT_DISPLAY_VALUE>''  ,substring(entitlement_xml,charindex(''<ENTITLEMENT_ID>AGS_Z0099_VAL_NPIREC</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'' ,entitlement_xml) , 1000 ))-1  ), replace(substring(entitlement_xml,charindex(''<ENTITLEMENT_ID>AGS_Z0099_VAL_NPIREC</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'' ,entitlement_xml),charindex(''<ENTITLEMENT_DISPLAY_VALUE>''  ,substring(entitlement_xml,charindex(''<ENTITLEMENT_ID>AGS_Z0099_VAL_NPIREC</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'' ,entitlement_xml) , 1000 ))-1  ),''select'','''') +''<ENTITLEMENT_DISPLAY_VALUE>'' + TOOL_NPI  ) ELSE ENTITLEMENT_XML END FROM "+str(SAQIEN)+"(NOLOCK) A JOIN (SELECT DISTINCT QUOTE_ID ,SERVICE_ID,EQUIPMENT_ID,REVISION_ID,TOOL_NPI FROM SAQICO_INBOUND B(NOLOCK) JOIN "+str(CRMTMP)+" C ON B.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE ISNULL(PROCESS_STATUS,'''')=''INPROGRESS'' AND TIMESTAMP = '"+str(timestamp_sessionid)+"' AND SERVICE_ID = ''Z0099'' ) B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID  = B.EQUIPMENT_ID AND A.QTEREV_ID = B.REVISION_ID  WHERE A.QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND A.QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND ISNULL(TOOL_NPI,'''')<>''''  '")
							
							#Z0035
							primaryQueryItems = SqlHelper.GetFirst("sp_executesql @t=N'UPDATE A SET ENTITLEMENT_XML = CASE WHEN charindex( ''<ENTITLEMENT_ID>AGS_Z0035_VAL_NPIREC</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'',replace(replace(entitlement_xml,''	'',''''),''\n'','''')) >0 THEN REPLACE(entitlement_xml ,  substring(entitlement_xml,charindex(''<ENTITLEMENT_ID>AGS_Z0035_VAL_NPIREC</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'' ,entitlement_xml),charindex(''</ENTITLEMENT_VALUE_CODE>''  ,substring(entitlement_xml,charindex(''<ENTITLEMENT_ID>AGS_Z0035_VAL_NPIREC</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'' ,entitlement_xml) , 1000 ))-1  ), ''<ENTITLEMENT_ID>AGS_Z0035_VAL_NPIREC</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>''+NPI_CODE ) ELSE ENTITLEMENT_XML END FROM "+str(SAQIEN)+"(NOLOCK) A JOIN (SELECT DISTINCT QUOTE_ID ,SERVICE_ID,EQUIPMENT_ID,REVISION_ID,NPI_CODE FROM SAQICO_INBOUND B(NOLOCK) JOIN "+str(CRMTMP)+" C ON B.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE ISNULL(PROCESS_STATUS,'''')=''INPROGRESS'' AND TIMESTAMP = '"+str(timestamp_sessionid)+"' AND SERVICE_ID = ''Z0035'' ) B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID  = B.EQUIPMENT_ID AND A.QTEREV_ID = B.REVISION_ID  WHERE A.QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND A.QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND ISNULL(NPI_CODE,'''')<>''''   '")
							
							primaryQueryItems = SqlHelper.GetFirst("sp_executesql @t=N'UPDATE A SET ENTITLEMENT_XML = CASE WHEN charindex( ''<ENTITLEMENT_ID>AGS_Z0035_VAL_NPIREC</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'',replace(replace(entitlement_xml,''	'',''''),''\n'','''')) >0  THEN REPLACE(entitlement_xml ,  substring(entitlement_xml,charindex(''<ENTITLEMENT_ID>AGS_Z0035_VAL_NPIREC</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'' ,entitlement_xml),charindex(''</ENTITLEMENT_DISPLAY_VALUE>''  ,substring(entitlement_xml,charindex(''<ENTITLEMENT_ID>AGS_Z0035_VAL_NPIREC</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'' ,entitlement_xml) , 1000 ))-1  ), replace(substring(entitlement_xml,charindex(''<ENTITLEMENT_ID>AGS_Z0035_VAL_NPIREC</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'' ,entitlement_xml),charindex(''<ENTITLEMENT_DISPLAY_VALUE>''  ,substring(entitlement_xml,charindex(''<ENTITLEMENT_ID>AGS_Z0035_VAL_NPIREC</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'' ,entitlement_xml) , 1000 ))-1  ),''select'','''') + ''<ENTITLEMENT_DISPLAY_VALUE>'' + TOOL_NPI  ) ELSE ENTITLEMENT_XML END FROM "+str(SAQIEN)+"(NOLOCK) A JOIN (SELECT DISTINCT QUOTE_ID ,SERVICE_ID,EQUIPMENT_ID,REVISION_ID,TOOL_NPI FROM SAQICO_INBOUND B(NOLOCK) JOIN "+str(CRMTMP)+" C ON B.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE ISNULL(PROCESS_STATUS,'''')=''INPROGRESS'' AND TIMESTAMP = '"+str(timestamp_sessionid)+"' AND SERVICE_ID = ''Z0035'' ) B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID  = B.EQUIPMENT_ID AND A.QTEREV_ID = B.REVISION_ID  WHERE A.QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND A.QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND ISNULL(TOOL_NPI,'''')<>'''' '")
							
							#Z0009
							primaryQueryItems = SqlHelper.GetFirst("sp_executesql @t=N'UPDATE A SET ENTITLEMENT_XML =CASE WHEN charindex( ''<ENTITLEMENT_ID>AGS_Z0009_VAL_NPIREC</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'',replace(replace(entitlement_xml,''	'',''''),''\n'','''')) >0  THEN REPLACE(entitlement_xml ,  substring(entitlement_xml,charindex(''<ENTITLEMENT_ID>AGS_Z0009_VAL_NPIREC</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'' ,entitlement_xml),charindex(''</ENTITLEMENT_VALUE_CODE>''  ,substring(entitlement_xml,charindex(''<ENTITLEMENT_ID>AGS_Z0009_VAL_NPIREC</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'' ,entitlement_xml) , 1000 ))-1  ), ''<ENTITLEMENT_ID>AGS_Z0009_VAL_NPIREC</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>''+NPI_CODE ) ELSE ENTITLEMENT_XML END FROM "+str(SAQIEN)+"(NOLOCK) A JOIN (SELECT DISTINCT QUOTE_ID ,SERVICE_ID,EQUIPMENT_ID,REVISION_ID,NPI_CODE FROM SAQICO_INBOUND B(NOLOCK) JOIN "+str(CRMTMP)+" C ON B.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE ISNULL(PROCESS_STATUS,'''')=''INPROGRESS'' AND TIMESTAMP = '"+str(timestamp_sessionid)+"' AND SERVICE_ID = ''Z0009'' ) B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID  = B.EQUIPMENT_ID AND A.QTEREV_ID = B.REVISION_ID  WHERE A.QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND A.QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND ISNULL(NPI_CODE,'''')<>''''  '")
							
							primaryQueryItems = SqlHelper.GetFirst("sp_executesql @t=N'UPDATE A SET ENTITLEMENT_XML = CASE WHEN charindex( ''<ENTITLEMENT_ID>AGS_Z0009_VAL_NPIREC</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'',replace(replace(entitlement_xml,''	'',''''),''\n'','''')) >0  THEN REPLACE(entitlement_xml ,  substring(entitlement_xml,charindex(''<ENTITLEMENT_ID>AGS_Z0009_VAL_NPIREC</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'' ,entitlement_xml),charindex(''</ENTITLEMENT_DISPLAY_VALUE>''  ,substring(entitlement_xml,charindex(''<ENTITLEMENT_ID>AGS_Z0009_VAL_NPIREC</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'' ,entitlement_xml) , 1000 ))-1  ), replace(substring(entitlement_xml,charindex(''<ENTITLEMENT_ID>AGS_Z0009_VAL_NPIREC</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'' ,entitlement_xml),charindex(''<ENTITLEMENT_DISPLAY_VALUE>''  ,substring(entitlement_xml,charindex(''<ENTITLEMENT_ID>AGS_Z0009_VAL_NPIREC</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'' ,entitlement_xml) , 1000 ))-1  ),''select'','''') + ''<ENTITLEMENT_DISPLAY_VALUE>'' + TOOL_NPI  ) ELSE ENTITLEMENT_XML END FROM "+str(SAQIEN)+"(NOLOCK) A JOIN (SELECT DISTINCT QUOTE_ID ,SERVICE_ID,EQUIPMENT_ID,REVISION_ID,TOOL_NPI FROM SAQICO_INBOUND B(NOLOCK) JOIN "+str(CRMTMP)+" C ON B.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE ISNULL(PROCESS_STATUS,'''')=''INPROGRESS'' AND TIMESTAMP = '"+str(timestamp_sessionid)+"' AND SERVICE_ID = ''Z0009'' ) B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID  = B.EQUIPMENT_ID AND A.QTEREV_ID = B.REVISION_ID  WHERE A.QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND A.QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND ISNULL(TOOL_NPI,'''')<>'''' '")
															
							#SAQIEN NPI Coefficent
							#Z0091
							primaryQueryItems = SqlHelper.GetFirst("sp_executesql @t=N'UPDATE A SET ENTITLEMENT_XML =CASE WHEN charindex( ''<ENTITLEMENT_ID>AGS_Z0091_VAL_NPICOF</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'',replace(replace(entitlement_xml,''	'',''''),''\n'','''')) >0  THEN  REPLACE(entitlement_xml ,  substring(entitlement_xml,charindex(''<ENTITLEMENT_ID>AGS_Z0091_VAL_NPICOF</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'' ,entitlement_xml),charindex(''</ENTITLEMENT_VALUE_CODE>''  ,substring(entitlement_xml,charindex(''<ENTITLEMENT_ID>AGS_Z0091_VAL_NPICOF</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'' ,entitlement_xml) , 1000 ))-1  ), ''<ENTITLEMENT_ID>AGS_Z0091_VAL_NPICOF</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>''+CONVERT(VARCHAR,NPI_COEFFICIENT) ) ELSE ENTITLEMENT_XML END FROM "+str(SAQIEN)+"(NOLOCK) A JOIN (SELECT DISTINCT QUOTE_ID ,SERVICE_ID,EQUIPMENT_ID,REVISION_ID,NPI_COEFFICIENT FROM SAQICO_INBOUND B(NOLOCK) JOIN "+str(CRMTMP)+" C ON B.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE ISNULL(PROCESS_STATUS,'''')=''INPROGRESS'' AND TIMESTAMP = '"+str(timestamp_sessionid)+"' AND SERVICE_ID = ''Z0091'')B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID  = B.EQUIPMENT_ID AND A.QTEREV_ID = B.REVISION_ID  WHERE A.QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND A.QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"''   '")
							
							#Z0092 
							primaryQueryItems = SqlHelper.GetFirst("sp_executesql @t=N'UPDATE A SET ENTITLEMENT_XML = CASE WHEN charindex( ''<ENTITLEMENT_ID>AGS_Z0092_VAL_NPICOF</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'',replace(replace(entitlement_xml,''	'',''''),''\n'','''')) >0  THEN REPLACE(entitlement_xml ,  substring(entitlement_xml,charindex(''<ENTITLEMENT_ID>AGS_Z0092_VAL_NPICOF</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'' ,entitlement_xml),charindex(''</ENTITLEMENT_VALUE_CODE>''  ,substring(entitlement_xml,charindex(''<ENTITLEMENT_ID>AGS_Z0092_VAL_NPICOF</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'' ,entitlement_xml) , 1000 ))-1  ), ''<ENTITLEMENT_ID>AGS_Z0092_VAL_NPICOF</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>''+CONVERT(VARCHAR,NPI_COEFFICIENT) ) ELSE ENTITLEMENT_XML END FROM "+str(SAQIEN)+"(NOLOCK) A JOIN (SELECT DISTINCT QUOTE_ID ,SERVICE_ID,EQUIPMENT_ID,REVISION_ID,NPI_COEFFICIENT FROM SAQICO_INBOUND B(NOLOCK) JOIN "+str(CRMTMP)+" C ON B.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE ISNULL(PROCESS_STATUS,'''')=''INPROGRESS'' AND TIMESTAMP = '"+str(timestamp_sessionid)+"' AND SERVICE_ID = ''Z0092'')B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID  = B.EQUIPMENT_ID AND A.QTEREV_ID = B.REVISION_ID  WHERE A.QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND A.QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"''  '")
							
							#Z0004
							primaryQueryItems = SqlHelper.GetFirst("sp_executesql @t=N'UPDATE A SET ENTITLEMENT_XML = CASE WHEN charindex( ''<ENTITLEMENT_ID>AGS_Z0004_VAL_NPICOF</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'',replace(replace(entitlement_xml,''	'',''''),''\n'','''')) >0  THEN REPLACE(entitlement_xml ,  substring(entitlement_xml,charindex(''<ENTITLEMENT_ID>AGS_Z0004_VAL_NPICOF</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'' ,entitlement_xml),charindex(''</ENTITLEMENT_VALUE_CODE>''  ,substring(entitlement_xml,charindex(''<ENTITLEMENT_ID>AGS_Z0004_VAL_NPICOF</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'' ,entitlement_xml) , 1000 ))-1  ), ''<ENTITLEMENT_ID>AGS_Z0004_VAL_NPICOF</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>''+CONVERT(VARCHAR,NPI_COEFFICIENT) ) ELSE ENTITLEMENT_XML END FROM "+str(SAQIEN)+"(NOLOCK) A JOIN (SELECT DISTINCT QUOTE_ID ,SERVICE_ID,EQUIPMENT_ID,REVISION_ID,NPI_COEFFICIENT FROM SAQICO_INBOUND B(NOLOCK) JOIN "+str(CRMTMP)+" C ON B.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE ISNULL(PROCESS_STATUS,'''')=''INPROGRESS'' AND TIMESTAMP = '"+str(timestamp_sessionid)+"' AND SERVICE_ID = ''Z0004'')B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID  = B.EQUIPMENT_ID AND A.QTEREV_ID = B.REVISION_ID  WHERE A.QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND A.QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"''   '")
							
							#Z0099
							primaryQueryItems = SqlHelper.GetFirst("sp_executesql @t=N'UPDATE A SET ENTITLEMENT_XML = CASE WHEN  charindex( ''<ENTITLEMENT_ID>AGS_Z0099_VAL_NPICOF</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'',replace(replace(entitlement_xml,''	'',''''),''\n'','''')) >0  THEN REPLACE(entitlement_xml ,  substring(entitlement_xml,charindex(''<ENTITLEMENT_ID>AGS_Z0099_VAL_NPICOF</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'' ,entitlement_xml),charindex(''</ENTITLEMENT_VALUE_CODE>''  ,substring(entitlement_xml,charindex(''<ENTITLEMENT_ID>AGS_Z0099_VAL_NPICOF</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'' ,entitlement_xml) , 1000 ))-1  ), ''<ENTITLEMENT_ID>AGS_Z0099_VAL_NPICOF</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>''+CONVERT(VARCHAR,NPI_COEFFICIENT) ) ELSE ENTITLEMENT_XML END FROM "+str(SAQIEN)+"(NOLOCK) A JOIN (SELECT DISTINCT QUOTE_ID ,SERVICE_ID,EQUIPMENT_ID,REVISION_ID,NPI_COEFFICIENT FROM SAQICO_INBOUND B(NOLOCK) JOIN "+str(CRMTMP)+" C ON B.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE ISNULL(PROCESS_STATUS,'''')=''INPROGRESS'' AND TIMESTAMP = '"+str(timestamp_sessionid)+"' AND SERVICE_ID = ''Z0099'')B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID  = B.EQUIPMENT_ID AND A.QTEREV_ID = B.REVISION_ID  WHERE A.QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND A.QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"''  '")
							
							#Z0035
							primaryQueryItems = SqlHelper.GetFirst("sp_executesql @t=N'UPDATE A SET ENTITLEMENT_XML = CASE WHEN  charindex( ''<ENTITLEMENT_ID>AGS_Z0035_VAL_NPICOF</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'',replace(replace(entitlement_xml,''	'',''''),''\n'','''')) >0 THEN REPLACE(entitlement_xml ,  substring(entitlement_xml,charindex(''<ENTITLEMENT_ID>AGS_Z0035_VAL_NPICOF</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'' ,entitlement_xml),charindex(''</ENTITLEMENT_VALUE_CODE>''  ,substring(entitlement_xml,charindex(''<ENTITLEMENT_ID>AGS_Z0035_VAL_NPICOF</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'' ,entitlement_xml) , 1000 ))-1  ), ''<ENTITLEMENT_ID>AGS_Z0035_VAL_NPICOF</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>''+CONVERT(VARCHAR,NPI_COEFFICIENT) ) ELSE ENTITLEMENT_XML END FROM "+str(SAQIEN)+"(NOLOCK) A JOIN (SELECT DISTINCT QUOTE_ID ,SERVICE_ID,EQUIPMENT_ID,REVISION_ID,NPI_COEFFICIENT FROM SAQICO_INBOUND B(NOLOCK) JOIN "+str(CRMTMP)+" C ON B.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE ISNULL(PROCESS_STATUS,'''')=''INPROGRESS'' AND TIMESTAMP = '"+str(timestamp_sessionid)+"' AND SERVICE_ID = ''Z0035'')B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID  = B.EQUIPMENT_ID AND A.QTEREV_ID = B.REVISION_ID  WHERE A.QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND A.QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"''    '")
							
							#Z0009
							primaryQueryItems = SqlHelper.GetFirst("sp_executesql @t=N'UPDATE A SET ENTITLEMENT_XML = CASE WHEN charindex( ''<ENTITLEMENT_ID>AGS_Z0009_VAL_NPICOF</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'',replace(replace(entitlement_xml,''	'',''''),''\n'','''')) >0  THEN REPLACE(entitlement_xml ,  substring(entitlement_xml,charindex(''<ENTITLEMENT_ID>AGS_Z0009_VAL_NPICOF</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'' ,entitlement_xml),charindex(''</ENTITLEMENT_VALUE_CODE>''  ,substring(entitlement_xml,charindex(''<ENTITLEMENT_ID>AGS_Z0009_VAL_NPICOF</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'' ,entitlement_xml) , 1000 ))-1  ), ''<ENTITLEMENT_ID>AGS_Z0009_VAL_NPICOF</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>''+CONVERT(VARCHAR,NPI_COEFFICIENT) ) ELSE ENTITLEMENT_XML END FROM "+str(SAQIEN)+"(NOLOCK) A JOIN (SELECT DISTINCT QUOTE_ID ,SERVICE_ID,EQUIPMENT_ID,REVISION_ID,NPI_COEFFICIENT FROM SAQICO_INBOUND B(NOLOCK) JOIN "+str(CRMTMP)+" C ON B.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE ISNULL(PROCESS_STATUS,'''')=''INPROGRESS'' AND TIMESTAMP = '"+str(timestamp_sessionid)+"' AND SERVICE_ID = ''Z0009'')B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID  = B.EQUIPMENT_ID AND A.QTEREV_ID = B.REVISION_ID  WHERE A.QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND A.QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"''   '")
														
							#SAQIEN Service Complexity
							#Z0091
							primaryQueryItems = SqlHelper.GetFirst("sp_executesql @t=N'UPDATE A SET ENTITLEMENT_XML = CASE WHEN charindex( ''<ENTITLEMENT_ID>AGS_Z0091_VAL_SCCCDF</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'',replace(replace(entitlement_xml,''	'',''''),''\n'','''')) >0  THEN REPLACE(entitlement_xml ,  substring(entitlement_xml,charindex(''<ENTITLEMENT_ID>AGS_Z0091_VAL_SCCCDF</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'' ,entitlement_xml),charindex(''</ENTITLEMENT_VALUE_CODE>''  ,substring(entitlement_xml,charindex(''<ENTITLEMENT_ID>AGS_Z0091_VAL_SCCCDF</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'' ,entitlement_xml) , 1000 ))-1  ), ''<ENTITLEMENT_ID>AGS_Z0091_VAL_SCCCDF</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>''+SERVICE_COMPLEXITY_CODE ) ELSE ENTITLEMENT_XML END FROM "+str(SAQIEN)+"(NOLOCK) A JOIN (SELECT DISTINCT QUOTE_ID ,SERVICE_ID,EQUIPMENT_ID,REVISION_ID,SERVICE_COMPLEXITY_CODE FROM SAQICO_INBOUND B(NOLOCK) JOIN "+str(CRMTMP)+" C ON B.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE ISNULL(PROCESS_STATUS,'''')=''INPROGRESS'' AND TIMESTAMP = '"+str(timestamp_sessionid)+"' AND SERVICE_ID = ''Z0091'' )B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID  = B.EQUIPMENT_ID AND A.QTEREV_ID = B.REVISION_ID  WHERE A.QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND A.QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND ISNULL(SERVICE_COMPLEXITY_CODE,'''')<>''''    '")
							
							primaryQueryItems = SqlHelper.GetFirst("sp_executesql @t=N'UPDATE A SET ENTITLEMENT_XML = CASE WHEN charindex( ''<ENTITLEMENT_ID>AGS_Z0091_VAL_SCCCDF</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'',replace(replace(entitlement_xml,''	'',''''),''\n'','''')) >0 THEN REPLACE(entitlement_xml ,  substring(entitlement_xml,charindex(''<ENTITLEMENT_ID>AGS_Z0091_VAL_SCCCDF</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'' ,entitlement_xml),charindex(''</ENTITLEMENT_DISPLAY_VALUE>''  ,substring(entitlement_xml,charindex(''<ENTITLEMENT_ID>AGS_Z0091_VAL_SCCCDF</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'' ,entitlement_xml) , 1000 ))-1  ), replace(substring(entitlement_xml,charindex(''<ENTITLEMENT_ID>AGS_Z0091_VAL_SCCCDF</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'' ,entitlement_xml),charindex(''<ENTITLEMENT_DISPLAY_VALUE>''  ,substring(entitlement_xml,charindex(''<ENTITLEMENT_ID>AGS_Z0091_VAL_SCCCDF</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'' ,entitlement_xml) , 1000 ))-1  ),''select'','''') + ''<ENTITLEMENT_DISPLAY_VALUE>'' + TOOL_SERVICE_COMPLEXITY  ) ELSE ENTITLEMENT_XML END FROM "+str(SAQIEN)+"(NOLOCK) A JOIN (SELECT DISTINCT QUOTE_ID ,SERVICE_ID,EQUIPMENT_ID,REVISION_ID,TOOL_SERVICE_COMPLEXITY FROM SAQICO_INBOUND B(NOLOCK) JOIN "+str(CRMTMP)+" C ON B.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE ISNULL(PROCESS_STATUS,'''')=''INPROGRESS'' AND TIMESTAMP = '"+str(timestamp_sessionid)+"' AND SERVICE_ID = ''Z0091'' ) B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID  = B.EQUIPMENT_ID AND A.QTEREV_ID = B.REVISION_ID  WHERE A.QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND A.QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND ISNULL(TOOL_SERVICE_COMPLEXITY,'''')<>''''  '")
							
							#Z0092
							primaryQueryItems = SqlHelper.GetFirst("sp_executesql @t=N'UPDATE A SET ENTITLEMENT_XML = CASE WHEN charindex( ''<ENTITLEMENT_ID>AGS_Z0092_VAL_SCCCDF</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'',replace(replace(entitlement_xml,''	'',''''),''\n'','''')) >0 THEN  REPLACE(entitlement_xml ,  substring(entitlement_xml,charindex(''<ENTITLEMENT_ID>AGS_Z0092_VAL_SCCCDF</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'' ,entitlement_xml),charindex(''</ENTITLEMENT_VALUE_CODE>''  ,substring(entitlement_xml,charindex(''<ENTITLEMENT_ID>AGS_Z0092_VAL_SCCCDF</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'' ,entitlement_xml) , 1000 ))-1  ), ''<ENTITLEMENT_ID>AGS_Z0092_VAL_SCCCDF</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>''+SERVICE_COMPLEXITY_CODE ) ELSE ENTITLEMENT_XML END FROM "+str(SAQIEN)+"(NOLOCK) A JOIN (SELECT DISTINCT QUOTE_ID ,SERVICE_ID,EQUIPMENT_ID,REVISION_ID,SERVICE_COMPLEXITY_CODE FROM SAQICO_INBOUND B(NOLOCK) JOIN "+str(CRMTMP)+" C ON B.EQUIPMENT_ID = C.EQUIPMENT_IDD  WHERE ISNULL(PROCESS_STATUS,'''')=''INPROGRESS'' AND TIMESTAMP = '"+str(timestamp_sessionid)+"' AND SERVICE_ID = ''Z0092'' )B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID  = B.EQUIPMENT_ID AND A.QTEREV_ID = B.REVISION_ID  WHERE A.QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND A.QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND ISNULL(SERVICE_COMPLEXITY_CODE,'''')<>''''  '")
							
							primaryQueryItems = SqlHelper.GetFirst("sp_executesql @t=N'UPDATE A SET ENTITLEMENT_XML =CASE WHEN charindex( ''<ENTITLEMENT_ID>AGS_Z0092_VAL_SCCCDF</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'',replace(replace(entitlement_xml,''	'',''''),''\n'','''')) >0 THEN REPLACE(entitlement_xml ,  substring(entitlement_xml,charindex(''<ENTITLEMENT_ID>AGS_Z0092_VAL_SCCCDF</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'' ,entitlement_xml),charindex(''</ENTITLEMENT_DISPLAY_VALUE>''  ,substring(entitlement_xml,charindex(''<ENTITLEMENT_ID>AGS_Z0092_VAL_SCCCDF</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'' ,entitlement_xml) , 1000 ))-1  ), replace(substring(entitlement_xml,charindex(''<ENTITLEMENT_ID>AGS_Z0092_VAL_SCCCDF</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'' ,entitlement_xml),charindex(''<ENTITLEMENT_DISPLAY_VALUE>''  ,substring(entitlement_xml,charindex(''<ENTITLEMENT_ID>AGS_Z0092_VAL_SCCCDF</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'' ,entitlement_xml) , 1000 ))-1  ),''select'','''') + ''<ENTITLEMENT_DISPLAY_VALUE>'' + TOOL_SERVICE_COMPLEXITY  ) ELSE ENTITLEMENT_XML END FROM "+str(SAQIEN)+"(NOLOCK) A JOIN (SELECT DISTINCT QUOTE_ID ,SERVICE_ID,EQUIPMENT_ID,REVISION_ID,TOOL_SERVICE_COMPLEXITY FROM SAQICO_INBOUND B(NOLOCK) JOIN "+str(CRMTMP)+" C ON B.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE ISNULL(PROCESS_STATUS,'''')=''INPROGRESS'' AND TIMESTAMP = '"+str(timestamp_sessionid)+"' AND SERVICE_ID = ''Z0092'' ) B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID  = B.EQUIPMENT_ID AND A.QTEREV_ID = B.REVISION_ID  WHERE A.QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND A.QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND ISNULL(TOOL_SERVICE_COMPLEXITY,'''')<>''''  '")
							
							#Z0004
							primaryQueryItems = SqlHelper.GetFirst("sp_executesql @t=N'UPDATE A SET ENTITLEMENT_XML = CASE WHEN charindex( ''<ENTITLEMENT_ID>AGS_Z0004_VAL_SCCCDF</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'',replace(replace(entitlement_xml,''	'',''''),''\n'','''')) >0 THEN REPLACE(entitlement_xml ,  substring(entitlement_xml,charindex(''<ENTITLEMENT_ID>AGS_Z0004_VAL_SCCCDF</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'' ,entitlement_xml),charindex(''</ENTITLEMENT_VALUE_CODE>''  ,substring(entitlement_xml,charindex(''<ENTITLEMENT_ID>AGS_Z0004_VAL_SCCCDF</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'' ,entitlement_xml) , 1000 ))-1  ), ''<ENTITLEMENT_ID>AGS_Z0004_VAL_SCCCDF</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>''+SERVICE_COMPLEXITY_CODE ) ELSE ENTITLEMENT_XML END FROM "+str(SAQIEN)+"(NOLOCK) A JOIN (SELECT DISTINCT QUOTE_ID ,SERVICE_ID,EQUIPMENT_ID,REVISION_ID,SERVICE_COMPLEXITY_CODE FROM SAQICO_INBOUND B(NOLOCK) JOIN "+str(CRMTMP)+" C ON B.EQUIPMENT_ID = C.EQUIPMENT_IDD  WHERE ISNULL(PROCESS_STATUS,'''')=''INPROGRESS'' AND TIMESTAMP = '"+str(timestamp_sessionid)+"' AND SERVICE_ID = ''Z0004'' )B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID  = B.EQUIPMENT_ID AND A.QTEREV_ID = B.REVISION_ID  WHERE A.QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND A.QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND ISNULL(SERVICE_COMPLEXITY_CODE,'''')<>''''  '")
							
							primaryQueryItems = SqlHelper.GetFirst("sp_executesql @t=N'UPDATE A SET ENTITLEMENT_XML =CASE WHEN charindex( ''<ENTITLEMENT_ID>AGS_Z0004_VAL_SCCCDF</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'',replace(replace(entitlement_xml,''	'',''''),''\n'','''')) >0 THEN REPLACE(entitlement_xml ,  substring(entitlement_xml,charindex(''<ENTITLEMENT_ID>AGS_Z0004_VAL_SCCCDF</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'' ,entitlement_xml),charindex(''</ENTITLEMENT_DISPLAY_VALUE>''  ,substring(entitlement_xml,charindex(''<ENTITLEMENT_ID>AGS_Z0004_VAL_SCCCDF</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'' ,entitlement_xml) , 1000 ))-1  ), replace(substring(entitlement_xml,charindex(''<ENTITLEMENT_ID>AGS_Z0004_VAL_SCCCDF</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'' ,entitlement_xml),charindex(''<ENTITLEMENT_DISPLAY_VALUE>''  ,substring(entitlement_xml,charindex(''<ENTITLEMENT_ID>AGS_Z0004_VAL_SCCCDF</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'' ,entitlement_xml) , 1000 ))-1  ),''select'','''') +''<ENTITLEMENT_DISPLAY_VALUE>'' + TOOL_SERVICE_COMPLEXITY  ) ELSE ENTITLEMENT_XML END FROM "+str(SAQIEN)+"(NOLOCK) A JOIN (SELECT DISTINCT QUOTE_ID ,SERVICE_ID,EQUIPMENT_ID,REVISION_ID,TOOL_SERVICE_COMPLEXITY FROM SAQICO_INBOUND B(NOLOCK) JOIN "+str(CRMTMP)+" C ON B.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE ISNULL(PROCESS_STATUS,'''')=''INPROGRESS'' AND TIMESTAMP = '"+str(timestamp_sessionid)+"' AND SERVICE_ID = ''Z0004'' ) B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID  = B.EQUIPMENT_ID AND A.QTEREV_ID = B.REVISION_ID  WHERE A.QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND A.QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND ISNULL(TOOL_SERVICE_COMPLEXITY,'''')<>''''  '")
							
							#Z0099
							primaryQueryItems = SqlHelper.GetFirst("sp_executesql @t=N'UPDATE A SET ENTITLEMENT_XML = CASE WHEN charindex( ''<ENTITLEMENT_ID>AGS_Z0099_VAL_SCCCDF</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'',replace(replace(entitlement_xml,''	'',''''),''\n'','''')) >0 THEN REPLACE(entitlement_xml ,  substring(entitlement_xml,charindex(''<ENTITLEMENT_ID>AGS_Z0099_VAL_SCCCDF</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'' ,entitlement_xml),charindex(''</ENTITLEMENT_VALUE_CODE>''  ,substring(entitlement_xml,charindex(''<ENTITLEMENT_ID>AGS_Z0099_VAL_SCCCDF</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'' ,entitlement_xml) , 1000 ))-1  ), ''<ENTITLEMENT_ID>AGS_Z0099_VAL_SCCCDF</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>''+SERVICE_COMPLEXITY_CODE ) ELSE ENTITLEMENT_XML END FROM "+str(SAQIEN)+"(NOLOCK) A JOIN (SELECT DISTINCT QUOTE_ID ,SERVICE_ID,EQUIPMENT_ID,REVISION_ID,SERVICE_COMPLEXITY_CODE FROM SAQICO_INBOUND B(NOLOCK) JOIN "+str(CRMTMP)+" C ON B.EQUIPMENT_ID = C.EQUIPMENT_IDD  WHERE ISNULL(PROCESS_STATUS,'''')=''INPROGRESS'' AND TIMESTAMP = '"+str(timestamp_sessionid)+"' AND SERVICE_ID = ''Z0099'' )B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID  = B.EQUIPMENT_ID AND A.QTEREV_ID = B.REVISION_ID  WHERE A.QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND A.QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND ISNULL(SERVICE_COMPLEXITY_CODE,'''')<>''''  '")
							
							primaryQueryItems = SqlHelper.GetFirst("sp_executesql @t=N'UPDATE A SET ENTITLEMENT_XML = CASE WHEN charindex( ''<ENTITLEMENT_ID>AGS_Z0099_VAL_SCCCDF</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'',replace(replace(entitlement_xml,''	'',''''),''\n'','''')) >0 THEN REPLACE(entitlement_xml ,  substring(entitlement_xml,charindex(''<ENTITLEMENT_ID>AGS_Z0099_VAL_SCCCDF</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'' ,entitlement_xml),charindex(''</ENTITLEMENT_DISPLAY_VALUE>''  ,substring(entitlement_xml,charindex(''<ENTITLEMENT_ID>AGS_Z0099_VAL_SCCCDF</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'' ,entitlement_xml) , 1000 ))-1  ), replace(substring(entitlement_xml,charindex(''<ENTITLEMENT_ID>AGS_Z0099_VAL_SCCCDF</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'' ,entitlement_xml),charindex(''<ENTITLEMENT_DISPLAY_VALUE>''  ,substring(entitlement_xml,charindex(''<ENTITLEMENT_ID>AGS_Z0099_VAL_SCCCDF</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'' ,entitlement_xml) , 1000 ))-1  ),''select'','''') +''<ENTITLEMENT_DISPLAY_VALUE>'' + TOOL_SERVICE_COMPLEXITY  ) ELSE ENTITLEMENT_XML END FROM "+str(SAQIEN)+"(NOLOCK) A JOIN (SELECT DISTINCT QUOTE_ID ,SERVICE_ID,EQUIPMENT_ID,REVISION_ID,TOOL_SERVICE_COMPLEXITY FROM SAQICO_INBOUND B(NOLOCK) JOIN "+str(CRMTMP)+" C ON B.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE ISNULL(PROCESS_STATUS,'''')=''INPROGRESS'' AND TIMESTAMP = '"+str(timestamp_sessionid)+"' AND SERVICE_ID = ''Z0099'' ) B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID  = B.EQUIPMENT_ID AND A.QTEREV_ID = B.REVISION_ID  WHERE A.QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND A.QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND ISNULL(TOOL_SERVICE_COMPLEXITY,'''')<>''''  '")
							
							#Z0035
							primaryQueryItems = SqlHelper.GetFirst("sp_executesql @t=N'UPDATE A SET ENTITLEMENT_XML =CASE WHEN charindex( ''<ENTITLEMENT_ID>AGS_Z0035_VAL_SCCCDF</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'',replace(replace(entitlement_xml,''	'',''''),''\n'','''')) >0 THEN REPLACE(entitlement_xml ,  substring(entitlement_xml,charindex(''<ENTITLEMENT_ID>AGS_Z0035_VAL_SCCCDF</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'' ,entitlement_xml),charindex(''</ENTITLEMENT_VALUE_CODE>''  ,substring(entitlement_xml,charindex(''<ENTITLEMENT_ID>AGS_Z0035_VAL_SCCCDF</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'' ,entitlement_xml) , 1000 ))-1  ), ''<ENTITLEMENT_ID>AGS_Z0035_VAL_SCCCDF</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>''+SERVICE_COMPLEXITY_CODE ) ELSE ENTITLEMENT_XML END FROM "+str(SAQIEN)+"(NOLOCK) A JOIN (SELECT DISTINCT QUOTE_ID ,SERVICE_ID,EQUIPMENT_ID,REVISION_ID,SERVICE_COMPLEXITY_CODE FROM SAQICO_INBOUND B(NOLOCK) JOIN "+str(CRMTMP)+" C ON B.EQUIPMENT_ID = C.EQUIPMENT_IDD  WHERE ISNULL(PROCESS_STATUS,'''')=''INPROGRESS'' AND TIMESTAMP = '"+str(timestamp_sessionid)+"' AND SERVICE_ID = ''Z0035'' )B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID  = B.EQUIPMENT_ID AND A.QTEREV_ID = B.REVISION_ID  WHERE A.QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND A.QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND ISNULL(SERVICE_COMPLEXITY_CODE,'''')<>''''  '")
							
							primaryQueryItems = SqlHelper.GetFirst("sp_executesql @t=N'UPDATE A SET ENTITLEMENT_XML =CASE WHEN charindex( ''<ENTITLEMENT_ID>AGS_Z0035_VAL_SCCCDF</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'',replace(replace(entitlement_xml,''	'',''''),''\n'','''')) >0 THEN REPLACE(entitlement_xml ,  substring(entitlement_xml,charindex(''<ENTITLEMENT_ID>AGS_Z0035_VAL_SCCCDF</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'' ,entitlement_xml),charindex(''</ENTITLEMENT_DISPLAY_VALUE>''  ,substring(entitlement_xml,charindex(''<ENTITLEMENT_ID>AGS_Z0035_VAL_SCCCDF</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'' ,entitlement_xml) , 1000 ))-1  ), replace(substring(entitlement_xml,charindex(''<ENTITLEMENT_ID>AGS_Z0035_VAL_SCCCDF</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'' ,entitlement_xml),charindex(''<ENTITLEMENT_DISPLAY_VALUE>''  ,substring(entitlement_xml,charindex(''<ENTITLEMENT_ID>AGS_Z0035_VAL_SCCCDF</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'' ,entitlement_xml) , 1000 ))-1  ),''select'','''') + ''<ENTITLEMENT_DISPLAY_VALUE>'' + TOOL_SERVICE_COMPLEXITY  ) ELSE ENTITLEMENT_XML END FROM "+str(SAQIEN)+"(NOLOCK) A JOIN (SELECT DISTINCT QUOTE_ID ,SERVICE_ID,EQUIPMENT_ID,REVISION_ID,TOOL_SERVICE_COMPLEXITY FROM SAQICO_INBOUND B(NOLOCK) JOIN "+str(CRMTMP)+" C ON B.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE ISNULL(PROCESS_STATUS,'''')=''INPROGRESS'' AND TIMESTAMP = '"+str(timestamp_sessionid)+"' AND SERVICE_ID = ''Z0035'' ) B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID  = B.EQUIPMENT_ID AND A.QTEREV_ID = B.REVISION_ID  WHERE A.QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND A.QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND ISNULL(TOOL_SERVICE_COMPLEXITY,'''')<>''''  '")
							
							#Z0009
							primaryQueryItems = SqlHelper.GetFirst("sp_executesql @t=N'UPDATE A SET ENTITLEMENT_XML =CASE WHEN charindex( ''<ENTITLEMENT_ID>AGS_Z0009_VAL_SCCCDF</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'',replace(replace(entitlement_xml,''	'',''''),''\n'','''')) >0 THEN REPLACE(entitlement_xml ,  substring(entitlement_xml,charindex(''<ENTITLEMENT_ID>AGS_Z0009_VAL_SCCCDF</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'' ,entitlement_xml),charindex(''</ENTITLEMENT_VALUE_CODE>''  ,substring(entitlement_xml,charindex(''<ENTITLEMENT_ID>AGS_Z0009_VAL_SCCCDF</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'' ,entitlement_xml) , 1000 ))-1  ), ''<ENTITLEMENT_ID>AGS_Z0009_VAL_SCCCDF</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>''+SERVICE_COMPLEXITY_CODE ) ELSE ENTITLEMENT_XML END FROM "+str(SAQIEN)+"(NOLOCK) A JOIN (SELECT DISTINCT QUOTE_ID ,SERVICE_ID,EQUIPMENT_ID,REVISION_ID,SERVICE_COMPLEXITY_CODE FROM SAQICO_INBOUND B(NOLOCK) JOIN "+str(CRMTMP)+" C ON B.EQUIPMENT_ID = C.EQUIPMENT_IDD  WHERE ISNULL(PROCESS_STATUS,'''')=''INPROGRESS'' AND TIMESTAMP = '"+str(timestamp_sessionid)+"' AND SERVICE_ID = ''Z0009'' )B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID  = B.EQUIPMENT_ID AND A.QTEREV_ID = B.REVISION_ID  WHERE A.QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND A.QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND ISNULL(SERVICE_COMPLEXITY_CODE,'''')<>''''  '")
							
							primaryQueryItems = SqlHelper.GetFirst("sp_executesql @t=N'UPDATE A SET ENTITLEMENT_XML =CASE WHEN charindex( ''<ENTITLEMENT_ID>AGS_Z0009_VAL_SCCCDF</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'',replace(replace(entitlement_xml,''	'',''''),''\n'','''')) >0 THEN REPLACE(entitlement_xml ,  substring(entitlement_xml,charindex(''<ENTITLEMENT_ID>AGS_Z0009_VAL_SCCCDF</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'' ,entitlement_xml),charindex(''</ENTITLEMENT_DISPLAY_VALUE>''  ,substring(entitlement_xml,charindex(''<ENTITLEMENT_ID>AGS_Z0009_VAL_SCCCDF</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'' ,entitlement_xml) , 1000 ))-1  ), replace(substring(entitlement_xml,charindex(''<ENTITLEMENT_ID>AGS_Z0009_VAL_SCCCDF</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'' ,entitlement_xml),charindex(''<ENTITLEMENT_DISPLAY_VALUE>''  ,substring(entitlement_xml,charindex(''<ENTITLEMENT_ID>AGS_Z0009_VAL_SCCCDF</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'' ,entitlement_xml) , 1000 ))-1  ),''select'','''') + ''<ENTITLEMENT_DISPLAY_VALUE>'' + TOOL_SERVICE_COMPLEXITY  ) ELSE ENTITLEMENT_XML END FROM "+str(SAQIEN)+"(NOLOCK) A JOIN (SELECT DISTINCT QUOTE_ID ,SERVICE_ID,EQUIPMENT_ID,REVISION_ID,TOOL_SERVICE_COMPLEXITY FROM SAQICO_INBOUND B(NOLOCK) JOIN "+str(CRMTMP)+" C ON B.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE ISNULL(PROCESS_STATUS,'''')=''INPROGRESS'' AND TIMESTAMP = '"+str(timestamp_sessionid)+"' AND SERVICE_ID = ''Z0009'' ) B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID  = B.EQUIPMENT_ID AND A.QTEREV_ID = B.REVISION_ID  WHERE A.QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND A.QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND ISNULL(TOOL_SERVICE_COMPLEXITY,'''')<>''''  '")
							
							#SAQIEN Service Complexity Coefficent
							#Z0091
							primaryQueryItems = SqlHelper.GetFirst("sp_executesql @t=N'UPDATE A SET ENTITLEMENT_XML = CASE WHEN charindex( ''<ENTITLEMENT_ID>AGS_Z0091_VAL_SCCCCO</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'',replace(replace(entitlement_xml,''	'',''''),''\n'','''')) >0  THEN REPLACE(entitlement_xml ,  substring(entitlement_xml,charindex(''<ENTITLEMENT_ID>AGS_Z0091_VAL_SCCCCO</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'' ,entitlement_xml),charindex(''</ENTITLEMENT_VALUE_CODE>''  ,substring(entitlement_xml,charindex(''<ENTITLEMENT_ID>AGS_Z0091_VAL_SCCCCO</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'' ,entitlement_xml) , 1000 ))-1  ), ''<ENTITLEMENT_ID>AGS_Z0091_VAL_SCCCCO</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>''+SERVICECOMPLEXITY_COEFFICIENT ) ELSE ENTITLEMENT_XML END FROM "+str(SAQIEN)+"(NOLOCK) A JOIN (SELECT DISTINCT QUOTE_ID ,SERVICE_ID,EQUIPMENT_ID,REVISION_ID,SERVICECOMPLEXITY_COEFFICIENT FROM SAQICO_INBOUND B(NOLOCK) JOIN "+str(CRMTMP)+" C ON B.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE ISNULL(PROCESS_STATUS,'''')=''INPROGRESS'' AND TIMESTAMP = '"+str(timestamp_sessionid)+"' AND SERVICE_ID=''Z0091''  )B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID  = B.EQUIPMENT_ID AND A.QTEREV_ID = B.REVISION_ID  WHERE A.QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND A.QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND ISNULL(SERVICECOMPLEXITY_COEFFICIENT,'''')<>''''  '")
							
							#Z0092
							primaryQueryItems = SqlHelper.GetFirst("sp_executesql @t=N'UPDATE A SET ENTITLEMENT_XML = CASE WHEN charindex( ''<ENTITLEMENT_ID>AGS_Z0092_VAL_SCCCCO</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'',replace(replace(entitlement_xml,''	'',''''),''\n'','''')) >0 THEN REPLACE(entitlement_xml ,  substring(entitlement_xml,charindex(''<ENTITLEMENT_ID>AGS_Z0092_VAL_SCCCCO</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'' ,entitlement_xml),charindex(''</ENTITLEMENT_VALUE_CODE>''  ,substring(entitlement_xml,charindex(''<ENTITLEMENT_ID>AGS_Z0092_VAL_SCCCCO</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'' ,entitlement_xml) , 1000 ))-1  ), ''<ENTITLEMENT_ID>AGS_Z0092_VAL_SCCCCO</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>''+SERVICECOMPLEXITY_COEFFICIENT ) ELSE ENTITLEMENT_XML END FROM "+str(SAQIEN)+"(NOLOCK) A JOIN (SELECT DISTINCT QUOTE_ID ,SERVICE_ID,EQUIPMENT_ID,REVISION_ID,SERVICECOMPLEXITY_COEFFICIENT FROM SAQICO_INBOUND B(NOLOCK) JOIN "+str(CRMTMP)+" C ON B.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE ISNULL(PROCESS_STATUS,'''')=''INPROGRESS'' AND TIMESTAMP = '"+str(timestamp_sessionid)+"' AND SERVICE_ID=''Z0092'' )B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID  = B.EQUIPMENT_ID AND A.QTEREV_ID = B.REVISION_ID  WHERE A.QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND A.QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND ISNULL(SERVICECOMPLEXITY_COEFFICIENT,'''')<>''''  '")
							
							#Z0004
							primaryQueryItems = SqlHelper.GetFirst("sp_executesql @t=N'UPDATE A SET ENTITLEMENT_XML = CASE WHEN charindex( ''<ENTITLEMENT_ID>AGS_Z0004_VAL_SCCCCO</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'',replace(replace(entitlement_xml,''	'',''''),''\n'','''')) >0 THEN REPLACE(entitlement_xml ,  substring(entitlement_xml,charindex(''<ENTITLEMENT_ID>AGS_Z0004_VAL_SCCCCO</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'' ,entitlement_xml),charindex(''</ENTITLEMENT_VALUE_CODE>''  ,substring(entitlement_xml,charindex(''<ENTITLEMENT_ID>AGS_Z0004_VAL_SCCCCO</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'' ,entitlement_xml) , 1000 ))-1  ), ''<ENTITLEMENT_ID>AGS_Z0004_VAL_SCCCCO</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>''+SERVICECOMPLEXITY_COEFFICIENT ) ELSE ENTITLEMENT_XML END FROM "+str(SAQIEN)+"(NOLOCK) A JOIN (SELECT DISTINCT QUOTE_ID ,SERVICE_ID,EQUIPMENT_ID,REVISION_ID,SERVICECOMPLEXITY_COEFFICIENT FROM SAQICO_INBOUND B(NOLOCK) JOIN "+str(CRMTMP)+" C ON B.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE ISNULL(PROCESS_STATUS,'''')=''INPROGRESS'' AND TIMESTAMP = '"+str(timestamp_sessionid)+"' AND SERVICE_ID=''Z0004'' )B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID  = B.EQUIPMENT_ID AND A.QTEREV_ID = B.REVISION_ID  WHERE A.QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND A.QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND ISNULL(SERVICECOMPLEXITY_COEFFICIENT,'''')<>''''  '")
							
							#Z0099
							primaryQueryItems = SqlHelper.GetFirst("sp_executesql @t=N'UPDATE A SET ENTITLEMENT_XML =CASE WHEN charindex( ''<ENTITLEMENT_ID>AGS_Z0099_VAL_SCCCCO</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'',replace(replace(entitlement_xml,''	'',''''),''\n'','''')) >0 THEN REPLACE(entitlement_xml ,  substring(entitlement_xml,charindex(''<ENTITLEMENT_ID>AGS_Z0099_VAL_SCCCCO</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'' ,entitlement_xml),charindex(''</ENTITLEMENT_VALUE_CODE>''  ,substring(entitlement_xml,charindex(''<ENTITLEMENT_ID>AGS_Z0099_VAL_SCCCCO</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'' ,entitlement_xml) , 1000 ))-1  ), ''<ENTITLEMENT_ID>AGS_Z0099_VAL_SCCCCO</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>''+SERVICECOMPLEXITY_COEFFICIENT ) ELSE ENTITLEMENT_XML END FROM "+str(SAQIEN)+"(NOLOCK) A JOIN (SELECT DISTINCT QUOTE_ID ,SERVICE_ID,EQUIPMENT_ID,REVISION_ID,SERVICECOMPLEXITY_COEFFICIENT FROM SAQICO_INBOUND B(NOLOCK) JOIN "+str(CRMTMP)+" C ON B.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE ISNULL(PROCESS_STATUS,'''')=''INPROGRESS'' AND TIMESTAMP = '"+str(timestamp_sessionid)+"' AND SERVICE_ID=''Z0099'' )B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID  = B.EQUIPMENT_ID AND A.QTEREV_ID = B.REVISION_ID  WHERE A.QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND A.QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND ISNULL(SERVICECOMPLEXITY_COEFFICIENT,'''')<>''''  '")
							
							#Z0035
							primaryQueryItems = SqlHelper.GetFirst("sp_executesql @t=N'UPDATE A SET ENTITLEMENT_XML =CASE WHEN charindex( ''<ENTITLEMENT_ID>AGS_Z0035_VAL_SCCCCO</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'',replace(replace(entitlement_xml,''	'',''''),''\n'','''')) >0 THEN REPLACE(entitlement_xml ,  substring(entitlement_xml,charindex(''<ENTITLEMENT_ID>AGS_Z0035_VAL_SCCCCO</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'' ,entitlement_xml),charindex(''</ENTITLEMENT_VALUE_CODE>''  ,substring(entitlement_xml,charindex(''<ENTITLEMENT_ID>AGS_Z0035_VAL_SCCCCO</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'' ,entitlement_xml) , 1000 ))-1  ), ''<ENTITLEMENT_ID>AGS_Z0035_VAL_SCCCCO</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>''+SERVICECOMPLEXITY_COEFFICIENT ) ELSE ENTITLEMENT_XML END FROM "+str(SAQIEN)+"(NOLOCK) A JOIN (SELECT DISTINCT QUOTE_ID ,SERVICE_ID,EQUIPMENT_ID,REVISION_ID,SERVICECOMPLEXITY_COEFFICIENT FROM SAQICO_INBOUND B(NOLOCK) JOIN "+str(CRMTMP)+" C ON B.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE ISNULL(PROCESS_STATUS,'''')=''INPROGRESS'' AND TIMESTAMP = '"+str(timestamp_sessionid)+"' AND SERVICE_ID=''Z0035'' )B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID  = B.EQUIPMENT_ID AND A.QTEREV_ID = B.REVISION_ID  WHERE A.QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND A.QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND ISNULL(SERVICECOMPLEXITY_COEFFICIENT,'''')<>'''' '")
							
							#Z0009
							primaryQueryItems = SqlHelper.GetFirst("sp_executesql @t=N'UPDATE A SET ENTITLEMENT_XML =CASE WHEN charindex( ''<ENTITLEMENT_ID>AGS_Z0009_VAL_SCCCCO</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'',replace(replace(entitlement_xml,''	'',''''),''\n'','''')) >0 THEN REPLACE(entitlement_xml ,  substring(entitlement_xml,charindex(''<ENTITLEMENT_ID>AGS_Z0009_VAL_SCCCCO</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'' ,entitlement_xml),charindex(''</ENTITLEMENT_VALUE_CODE>''  ,substring(entitlement_xml,charindex(''<ENTITLEMENT_ID>AGS_Z0009_VAL_SCCCCO</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'' ,entitlement_xml) , 1000 ))-1  ), ''<ENTITLEMENT_ID>AGS_Z0009_VAL_SCCCCO</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>''+SERVICECOMPLEXITY_COEFFICIENT ) ELSE ENTITLEMENT_XML END FROM "+str(SAQIEN)+"(NOLOCK) A JOIN (SELECT DISTINCT QUOTE_ID ,SERVICE_ID,EQUIPMENT_ID,REVISION_ID,SERVICECOMPLEXITY_COEFFICIENT FROM SAQICO_INBOUND B(NOLOCK) JOIN "+str(CRMTMP)+" C ON B.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE ISNULL(PROCESS_STATUS,'''')=''INPROGRESS'' AND TIMESTAMP = '"+str(timestamp_sessionid)+"' AND SERVICE_ID=''Z0009'' )B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID  = B.EQUIPMENT_ID AND A.QTEREV_ID = B.REVISION_ID  WHERE A.QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND A.QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND ISNULL(SERVICECOMPLEXITY_COEFFICIENT,'''')<>''''  '")

							#Swap Kit AMAT Provided
							#Z0004
							S3 = SqlHelper.GetFirst("sp_executesql @T=N'UPDATE A SET SWAP_KIT=ENTITLEMENT_DISPLAY_VALUE FROM SAQICO_INBOUND A(NOLOCK) JOIN (SELECT distinct quote_ID,equipment_id,service_id, replace(X.Y.value(''(ENTITLEMENT_DISPLAY_VALUE)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_DISPLAY_VALUE,replace(X.Y.value(''(ENTITLEMENT_NAME)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_NAME FROM (SELECT quote_ID,equipment_id,service_id,CONVERT(XML,''<QUOTE_ENTITLEMENT>''+substring(entitlement_xml,charindex (''<ENTITLEMENT_ID>AGS_Z0004_STT_SWKTAP'',entitlement_xml),charindex (''Swap Kits (Applied provided)</ENTITLEMENT_NAME>'',entitlement_xml)-charindex (''<ENTITLEMENT_ID>AGS_Z0004_STT_SWKTAP'',entitlement_xml)+len(''Swap Kits (Applied provided)</ENTITLEMENT_NAME>''))+''</QUOTE_ENTITLEMENT>'') as entitlement_xml FROM "+str(SAQIEN)+" (nolock)a JOIN "+str(CRMTMP)+" C ON a.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND SERVICE_ID = ''Z0004'') e OUTER APPLY e.ENTITLEMENT_XML.nodes(''QUOTE_ENTITLEMENT'') as X(Y) )B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID = B.EQUIPMENT_ID  WHERE B.ENTITLEMENT_NAME=''Swap Kits (Applied provided)''  '")
							
							#Z0091
							S3 = SqlHelper.GetFirst("sp_executesql @T=N'UPDATE A SET SWAP_KIT=ENTITLEMENT_DISPLAY_VALUE FROM SAQICO_INBOUND A(NOLOCK) JOIN (SELECT distinct quote_ID,equipment_id,service_id, replace(X.Y.value(''(ENTITLEMENT_DISPLAY_VALUE)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_DISPLAY_VALUE,replace(X.Y.value(''(ENTITLEMENT_NAME)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_NAME FROM (SELECT quote_ID,equipment_id,service_id,CONVERT(XML,''<QUOTE_ENTITLEMENT>''+substring(entitlement_xml,charindex (''<ENTITLEMENT_ID>AGS_Z0091_STT_SWKTAP'',entitlement_xml),charindex (''Swap Kits (Applied provided)</ENTITLEMENT_NAME>'',entitlement_xml)-charindex (''<ENTITLEMENT_ID>AGS_Z0091_STT_SWKTAP'',entitlement_xml)+len(''Swap Kits (Applied provided)</ENTITLEMENT_NAME>''))+''</QUOTE_ENTITLEMENT>'') as entitlement_xml FROM "+str(SAQIEN)+" (nolock)a JOIN "+str(CRMTMP)+" C ON A.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND SERVICE_ID =''Z0091'') e OUTER APPLY e.ENTITLEMENT_XML.nodes(''QUOTE_ENTITLEMENT'') as X(Y) )B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID = B.EQUIPMENT_ID  WHERE B.ENTITLEMENT_NAME=''Swap Kits (Applied provided)''  '")
							
							#Z0009
							S3 = SqlHelper.GetFirst("sp_executesql @T=N'UPDATE A SET SWAP_KIT=ENTITLEMENT_DISPLAY_VALUE FROM SAQICO_INBOUND A(NOLOCK) JOIN (SELECT distinct quote_ID,equipment_id,service_id, replace(X.Y.value(''(ENTITLEMENT_DISPLAY_VALUE)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_DISPLAY_VALUE,replace(X.Y.value(''(ENTITLEMENT_NAME)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_NAME FROM (SELECT quote_ID,equipment_id,service_id,CONVERT(XML,''<QUOTE_ENTITLEMENT>''+substring(entitlement_xml,charindex (''<ENTITLEMENT_ID>AGS_Z0009_STT_SWKTAP'',entitlement_xml),charindex (''Swap Kits (Applied provided)</ENTITLEMENT_NAME>'',entitlement_xml)-charindex (''<ENTITLEMENT_ID>AGS_Z0009_STT_SWKTAP'',entitlement_xml)+len(''Swap Kits (Applied provided)</ENTITLEMENT_NAME>''))+''</QUOTE_ENTITLEMENT>'') as entitlement_xml FROM "+str(SAQIEN)+" (nolock)a JOIN "+str(CRMTMP)+" C ON A.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND SERVICE_ID =''Z0009'') e OUTER APPLY e.ENTITLEMENT_XML.nodes(''QUOTE_ENTITLEMENT'') as X(Y) )B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID = B.EQUIPMENT_ID  WHERE B.ENTITLEMENT_NAME=''Swap Kits (Applied provided)''  '")
							
							#Z0035
							S3 = SqlHelper.GetFirst("sp_executesql @T=N'UPDATE A SET SWAP_KIT=ENTITLEMENT_DISPLAY_VALUE FROM SAQICO_INBOUND A(NOLOCK) JOIN (SELECT distinct quote_ID,equipment_id,service_id, replace(X.Y.value(''(ENTITLEMENT_DISPLAY_VALUE)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_DISPLAY_VALUE,replace(X.Y.value(''(ENTITLEMENT_NAME)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_NAME FROM (SELECT quote_ID,equipment_id,service_id,CONVERT(XML,''<QUOTE_ENTITLEMENT>''+substring(entitlement_xml,charindex (''<ENTITLEMENT_ID>AGS_Z0035_STT_SWKTAP'',entitlement_xml),charindex (''Swap Kits (Applied provided)</ENTITLEMENT_NAME>'',entitlement_xml)-charindex (''<ENTITLEMENT_ID>AGS_Z0035_STT_SWKTAP'',entitlement_xml)+len(''Swap Kits (Applied provided)</ENTITLEMENT_NAME>''))+''</QUOTE_ENTITLEMENT>'') as entitlement_xml FROM "+str(SAQIEN)+" (nolock)a JOIN "+str(CRMTMP)+" C ON A.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND SERVICE_ID =''Z0035'') e OUTER APPLY e.ENTITLEMENT_XML.nodes(''QUOTE_ENTITLEMENT'') as X(Y) )B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID = B.EQUIPMENT_ID  WHERE B.ENTITLEMENT_NAME=''Swap Kits (Applied provided)''  '")
							
							#Capital Avoidance											
							#Z0091
							primaryQueryItems = SqlHelper.GetFirst(
												""
												+ str(Parameter1.QUERY_CRITERIA_1)
												+ "  A SET CAPITALAVOIDANCE_COEFFICIENT = B.SEEDSTOCK_COST / B.TOTAL_COST_WISEEDSTOCK FROM SAQICO_INBOUND (NOLOCK) A JOIN (SELECT DISTINCT QUOTE_ID,REVISION_ID,EQUIPMENT_ID,SERVICE_ID,SUM(CONVERT(FLOAT,SEEDSTOCK_COST)) AS SEEDSTOCK_COST,SUM(CONVERT(FLOAT,TOTAL_COST_WISEEDSTOCK)) AS TOTAL_COST_WISEEDSTOCK FROM SAQICO_INBOUND(NOLOCK)B  JOIN "+str(CRMTMP)+" C ON B.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE ISNULL(PROCESS_STATUS,'''')=''INPROGRESS'' AND TIMESTAMP = '"+str(timestamp_sessionid)+"' GROUP BY QUOTE_ID,REVISION_ID,SERVICE_ID,EQUIPMENT_ID)B ON A.QUOTE_ID = B.QUOTE_ID AND A.REVISION_ID = B.REVISION_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID = B.EQUIPMENT_ID WHERE ISNULL(PROCESS_STATUS,'''')=''INPROGRESS'' AND TIMESTAMP = '"+str(timestamp_sessionid)+"' AND A.SERVICE_ID = ''Z0091'' AND ISNULL(B.TOTAL_COST_WISEEDSTOCK,0)>0 ' ")
							
							#Z0092
							primaryQueryItems = SqlHelper.GetFirst(
												""
												+ str(Parameter1.QUERY_CRITERIA_1)
												+ "  A SET CAPITALAVOIDANCE_COEFFICIENT = B.SEEDSTOCK_COST / B.TOTAL_COST_WISEEDSTOCK FROM SAQICO_INBOUND (NOLOCK) A JOIN (SELECT DISTINCT QUOTE_ID,REVISION_ID,EQUIPMENT_ID,SERVICE_ID,SUM(CONVERT(FLOAT,SEEDSTOCK_COST)) AS SEEDSTOCK_COST,SUM(CONVERT(FLOAT,TOTAL_COST_WISEEDSTOCK)) AS TOTAL_COST_WISEEDSTOCK FROM SAQICO_INBOUND(NOLOCK)B  JOIN "+str(CRMTMP)+" C ON B.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE ISNULL(PROCESS_STATUS,'''')=''INPROGRESS'' AND TIMESTAMP = '"+str(timestamp_sessionid)+"' GROUP BY QUOTE_ID,REVISION_ID,SERVICE_ID,EQUIPMENT_ID)B ON A.QUOTE_ID = B.QUOTE_ID AND A.REVISION_ID = B.REVISION_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID = B.EQUIPMENT_ID WHERE ISNULL(PROCESS_STATUS,'''')=''INPROGRESS'' AND TIMESTAMP = '"+str(timestamp_sessionid)+"' AND A.SERVICE_ID = ''Z0092'' AND ISNULL(B.TOTAL_COST_WISEEDSTOCK,0)>0 ' ")
							
							#Z0004
							primaryQueryItems = SqlHelper.GetFirst(
												""
												+ str(Parameter1.QUERY_CRITERIA_1)
												+ "  A SET CAPITALAVOIDANCE_COEFFICIENT = B.SEEDSTOCK_COST / B.TOTAL_COST_WISEEDSTOCK FROM SAQICO_INBOUND (NOLOCK) A JOIN (SELECT DISTINCT QUOTE_ID,REVISION_ID,EQUIPMENT_ID,SERVICE_ID,SUM(CONVERT(FLOAT,SEEDSTOCK_COST)) AS SEEDSTOCK_COST,SUM(CONVERT(FLOAT,TOTAL_COST_WISEEDSTOCK)) AS TOTAL_COST_WISEEDSTOCK FROM SAQICO_INBOUND(NOLOCK)B  JOIN "+str(CRMTMP)+" C ON B.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE ISNULL(PROCESS_STATUS,'''')=''INPROGRESS'' AND TIMESTAMP = '"+str(timestamp_sessionid)+"' GROUP BY QUOTE_ID,REVISION_ID,SERVICE_ID,EQUIPMENT_ID)B ON A.QUOTE_ID = B.QUOTE_ID AND A.REVISION_ID = B.REVISION_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID = B.EQUIPMENT_ID WHERE ISNULL(PROCESS_STATUS,'''')=''INPROGRESS'' AND TIMESTAMP = '"+str(timestamp_sessionid)+"' AND A.SERVICE_ID = ''Z0004'' AND ISNULL(B.TOTAL_COST_WISEEDSTOCK,0)>0 ' ")
							
							#Z0099
							primaryQueryItems = SqlHelper.GetFirst(
												""
												+ str(Parameter1.QUERY_CRITERIA_1)
												+ "  A SET CAPITALAVOIDANCE_COEFFICIENT = B.SEEDSTOCK_COST / B.TOTAL_COST_WISEEDSTOCK FROM SAQICO_INBOUND (NOLOCK) A JOIN (SELECT DISTINCT QUOTE_ID,REVISION_ID,EQUIPMENT_ID,SERVICE_ID,SUM(CONVERT(FLOAT,SEEDSTOCK_COST)) AS SEEDSTOCK_COST,SUM(CONVERT(FLOAT,TOTAL_COST_WISEEDSTOCK)) AS TOTAL_COST_WISEEDSTOCK FROM SAQICO_INBOUND(NOLOCK)B  JOIN "+str(CRMTMP)+" C ON B.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE ISNULL(PROCESS_STATUS,'''')=''INPROGRESS'' AND TIMESTAMP = '"+str(timestamp_sessionid)+"' GROUP BY QUOTE_ID,REVISION_ID,SERVICE_ID,EQUIPMENT_ID)B ON A.QUOTE_ID = B.QUOTE_ID AND A.REVISION_ID = B.REVISION_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID = B.EQUIPMENT_ID WHERE ISNULL(PROCESS_STATUS,'''')=''INPROGRESS'' AND TIMESTAMP = '"+str(timestamp_sessionid)+"' AND A.SERVICE_ID = ''Z0099'' AND ISNULL(B.TOTAL_COST_WISEEDSTOCK,0)>0 ' ")
							
							#Z0035
							primaryQueryItems = SqlHelper.GetFirst(
												""
												+ str(Parameter1.QUERY_CRITERIA_1)
												+ "  A SET CAPITALAVOIDANCE_COEFFICIENT = B.SEEDSTOCK_COST / B.TOTAL_COST_WISEEDSTOCK FROM SAQICO_INBOUND (NOLOCK) A JOIN (SELECT DISTINCT QUOTE_ID,REVISION_ID,EQUIPMENT_ID,SERVICE_ID,SUM(CONVERT(FLOAT,SEEDSTOCK_COST)) AS SEEDSTOCK_COST,SUM(CONVERT(FLOAT,TOTAL_COST_WISEEDSTOCK)) AS TOTAL_COST_WISEEDSTOCK FROM SAQICO_INBOUND(NOLOCK)B  JOIN "+str(CRMTMP)+" C ON B.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE ISNULL(PROCESS_STATUS,'''')=''INPROGRESS'' AND TIMESTAMP = '"+str(timestamp_sessionid)+"' GROUP BY QUOTE_ID,REVISION_ID,SERVICE_ID,EQUIPMENT_ID)B ON A.QUOTE_ID = B.QUOTE_ID AND A.REVISION_ID = B.REVISION_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID = B.EQUIPMENT_ID WHERE ISNULL(PROCESS_STATUS,'''')=''INPROGRESS'' AND TIMESTAMP = '"+str(timestamp_sessionid)+"' AND A.SERVICE_ID = ''Z0035'' AND ISNULL(B.TOTAL_COST_WISEEDSTOCK,0)>0 ' ")
							
							#Z0009
							primaryQueryItems = SqlHelper.GetFirst(
												""
												+ str(Parameter1.QUERY_CRITERIA_1)
												+ "  A SET CAPITALAVOIDANCE_COEFFICIENT = B.SEEDSTOCK_COST / B.TOTAL_COST_WISEEDSTOCK FROM SAQICO_INBOUND (NOLOCK) A JOIN (SELECT DISTINCT QUOTE_ID,REVISION_ID,EQUIPMENT_ID,SERVICE_ID,SUM(CONVERT(FLOAT,SEEDSTOCK_COST)) AS SEEDSTOCK_COST,SUM(CONVERT(FLOAT,TOTAL_COST_WISEEDSTOCK)) AS TOTAL_COST_WISEEDSTOCK FROM SAQICO_INBOUND(NOLOCK)B  JOIN "+str(CRMTMP)+" C ON B.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE ISNULL(PROCESS_STATUS,'''')=''INPROGRESS'' AND TIMESTAMP = '"+str(timestamp_sessionid)+"' GROUP BY QUOTE_ID,REVISION_ID,SERVICE_ID,EQUIPMENT_ID)B ON A.QUOTE_ID = B.QUOTE_ID AND A.REVISION_ID = B.REVISION_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID = B.EQUIPMENT_ID WHERE ISNULL(PROCESS_STATUS,'''')=''INPROGRESS'' AND TIMESTAMP = '"+str(timestamp_sessionid)+"' AND A.SERVICE_ID = ''Z0009'' AND ISNULL(B.TOTAL_COST_WISEEDSTOCK,0)>0 ' ")
																												
							#SAQIEN Capital Avoidance Coefficent
							#Z0091
							primaryQueryItems = SqlHelper.GetFirst("sp_executesql @t=N'UPDATE A SET ENTITLEMENT_XML =CASE WHEN charindex( ''<ENTITLEMENT_ID>AGS_Z0091_VAL_CAPACO</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'',replace(replace(entitlement_xml,''	'',''''),''\n'','''')) >0 THEN REPLACE(entitlement_xml ,  substring(entitlement_xml,charindex(''<ENTITLEMENT_ID>AGS_Z0091_VAL_CAPACO</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'' ,entitlement_xml),charindex(''</ENTITLEMENT_VALUE_CODE>''  ,substring(entitlement_xml,charindex(''<ENTITLEMENT_ID>AGS_Z0091_VAL_CAPACO</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'' ,entitlement_xml) , 1000 ))-1  ), ''<ENTITLEMENT_ID>AGS_Z0091_VAL_CAPACO</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>''+CAPITALAVOIDANCE_COEFFICIENT ) ELSE ENTITLEMENT_XML END FROM "+str(SAQIEN)+"(NOLOCK) A JOIN (SELECT DISTINCT QUOTE_ID ,SERVICE_ID,EQUIPMENT_ID,REVISION_ID,CAPITALAVOIDANCE_COEFFICIENT FROM SAQICO_INBOUND B(NOLOCK) JOIN "+str(CRMTMP)+" C ON B.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE ISNULL(PROCESS_STATUS,'''')=''INPROGRESS'' AND TIMESTAMP = '"+str(timestamp_sessionid)+"' AND B.SERVICE_ID = ''Z0091'' )B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID  = B.EQUIPMENT_ID AND A.QTEREV_ID = B.REVISION_ID  WHERE A.QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND A.QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"''  AND ISNULL(CAPITALAVOIDANCE_COEFFICIENT,'''')<>''''  '")
							
							#Z0092
							primaryQueryItems = SqlHelper.GetFirst("sp_executesql @t=N'UPDATE A SET ENTITLEMENT_XML =CASE WHEN charindex( ''<ENTITLEMENT_ID>AGS_Z0092_VAL_CAPACO</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'',replace(replace(entitlement_xml,''	'',''''),''\n'','''')) >0 THEN REPLACE(entitlement_xml ,  substring(entitlement_xml,charindex(''<ENTITLEMENT_ID>AGS_Z0092_VAL_CAPACO</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'' ,entitlement_xml),charindex(''</ENTITLEMENT_VALUE_CODE>''  ,substring(entitlement_xml,charindex(''<ENTITLEMENT_ID>AGS_Z0092_VAL_CAPACO</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'' ,entitlement_xml) , 1000 ))-1  ), ''<ENTITLEMENT_ID>AGS_Z0092_VAL_CAPACO</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>''+CAPITALAVOIDANCE_COEFFICIENT ) ELSE ENTITLEMENT_XML END FROM "+str(SAQIEN)+"(NOLOCK) A JOIN (SELECT DISTINCT QUOTE_ID ,SERVICE_ID,EQUIPMENT_ID,REVISION_ID,CAPITALAVOIDANCE_COEFFICIENT FROM SAQICO_INBOUND B(NOLOCK) JOIN "+str(CRMTMP)+" C ON B.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE ISNULL(PROCESS_STATUS,'''')=''INPROGRESS'' AND TIMESTAMP = '"+str(timestamp_sessionid)+"' AND B.SERVICE_ID = ''Z0092'')B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID  = B.EQUIPMENT_ID AND A.QTEREV_ID = B.REVISION_ID  WHERE A.QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND A.QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"''  AND ISNULL(CAPITALAVOIDANCE_COEFFICIENT,'''')<>''''  '")
							
							#Z0004
							primaryQueryItems = SqlHelper.GetFirst("sp_executesql @t=N'UPDATE A SET ENTITLEMENT_XML =CASE WHEN charindex( ''<ENTITLEMENT_ID>AGS_Z0004_VAL_CAPACO</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'',replace(replace(entitlement_xml,''	'',''''),''\n'','''')) >0  THEN REPLACE(entitlement_xml ,  substring(entitlement_xml,charindex(''<ENTITLEMENT_ID>AGS_Z0004_VAL_CAPACO</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'' ,entitlement_xml),charindex(''</ENTITLEMENT_VALUE_CODE>''  ,substring(entitlement_xml,charindex(''<ENTITLEMENT_ID>AGS_Z0004_VAL_CAPACO</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'' ,entitlement_xml) , 1000 ))-1  ), ''<ENTITLEMENT_ID>AGS_Z0004_VAL_CAPACO</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>''+CAPITALAVOIDANCE_COEFFICIENT ) ELSE ENTITLEMENT_XML END FROM "+str(SAQIEN)+"(NOLOCK) A JOIN (SELECT DISTINCT QUOTE_ID ,SERVICE_ID,EQUIPMENT_ID,REVISION_ID,CAPITALAVOIDANCE_COEFFICIENT FROM SAQICO_INBOUND B(NOLOCK) JOIN "+str(CRMTMP)+" C ON B.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE ISNULL(PROCESS_STATUS,'''')=''INPROGRESS'' AND TIMESTAMP = '"+str(timestamp_sessionid)+"' AND B.SERVICE_ID = ''Z0004'')B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID  = B.EQUIPMENT_ID AND A.QTEREV_ID = B.REVISION_ID  WHERE A.QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND A.QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"''  AND ISNULL(CAPITALAVOIDANCE_COEFFICIENT,'''')<>''''  '")
							
							#Z0099
							primaryQueryItems = SqlHelper.GetFirst("sp_executesql @t=N'UPDATE A SET ENTITLEMENT_XML =CASE WHEN charindex( ''<ENTITLEMENT_ID>AGS_Z0099_VAL_CAPACO</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'',replace(replace(entitlement_xml,''	'',''''),''\n'','''')) >0 THEN REPLACE(entitlement_xml ,  substring(entitlement_xml,charindex(''<ENTITLEMENT_ID>AGS_Z0099_VAL_CAPACO</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'' ,entitlement_xml),charindex(''</ENTITLEMENT_VALUE_CODE>''  ,substring(entitlement_xml,charindex(''<ENTITLEMENT_ID>AGS_Z0099_VAL_CAPACO</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'' ,entitlement_xml) , 1000 ))-1  ), ''<ENTITLEMENT_ID>AGS_Z0099_VAL_CAPACO</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>''+CAPITALAVOIDANCE_COEFFICIENT ) ELSE ENTITLEMENT_XML END FROM "+str(SAQIEN)+"(NOLOCK) A JOIN (SELECT DISTINCT QUOTE_ID ,SERVICE_ID,EQUIPMENT_ID,REVISION_ID,CAPITALAVOIDANCE_COEFFICIENT FROM SAQICO_INBOUND B(NOLOCK) JOIN "+str(CRMTMP)+" C ON B.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE ISNULL(PROCESS_STATUS,'''')=''INPROGRESS'' AND TIMESTAMP = '"+str(timestamp_sessionid)+"' AND B.SERVICE_ID = ''Z0099'')B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID  = B.EQUIPMENT_ID AND A.QTEREV_ID = B.REVISION_ID  WHERE A.QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND A.QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"''  AND ISNULL(CAPITALAVOIDANCE_COEFFICIENT,'''')<>''''   '")
							
							#Z0035
							primaryQueryItems = SqlHelper.GetFirst("sp_executesql @t=N'UPDATE A SET ENTITLEMENT_XML = CASE WHEN charindex( ''<ENTITLEMENT_ID>AGS_Z0035_VAL_CAPACO</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'',replace(replace(entitlement_xml,''	'',''''),''\n'','''')) >0  THEN REPLACE(entitlement_xml ,  substring(entitlement_xml,charindex(''<ENTITLEMENT_ID>AGS_Z0035_VAL_CAPACO</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'' ,entitlement_xml),charindex(''</ENTITLEMENT_VALUE_CODE>''  ,substring(entitlement_xml,charindex(''<ENTITLEMENT_ID>AGS_Z0035_VAL_CAPACO</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'' ,entitlement_xml) , 1000 ))-1  ), ''<ENTITLEMENT_ID>AGS_Z0035_VAL_CAPACO</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>''+CAPITALAVOIDANCE_COEFFICIENT ) ELSE ENTITLEMENT_XML END FROM "+str(SAQIEN)+"(NOLOCK) A JOIN (SELECT DISTINCT QUOTE_ID ,SERVICE_ID,EQUIPMENT_ID,REVISION_ID,CAPITALAVOIDANCE_COEFFICIENT FROM SAQICO_INBOUND B(NOLOCK) JOIN "+str(CRMTMP)+" C ON B.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE ISNULL(PROCESS_STATUS,'''')=''INPROGRESS'' AND TIMESTAMP = '"+str(timestamp_sessionid)+"' AND B.SERVICE_ID = ''Z0035'')B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID  = B.EQUIPMENT_ID AND A.QTEREV_ID = B.REVISION_ID  WHERE A.QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND A.QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"''  AND ISNULL(CAPITALAVOIDANCE_COEFFICIENT,'''')<>'''' '")
							
							#Z0009
							primaryQueryItems = SqlHelper.GetFirst("sp_executesql @t=N'UPDATE A SET ENTITLEMENT_XML =CASE WHEN charindex( ''<ENTITLEMENT_ID>AGS_Z0009_VAL_CAPACO</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'',replace(replace(entitlement_xml,''	'',''''),''\n'','''')) >0 THEN REPLACE(entitlement_xml ,  substring(entitlement_xml,charindex(''<ENTITLEMENT_ID>AGS_Z0009_VAL_CAPACO</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'' ,entitlement_xml),charindex(''</ENTITLEMENT_VALUE_CODE>''  ,substring(entitlement_xml,charindex(''<ENTITLEMENT_ID>AGS_Z0009_VAL_CAPACO</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>'' ,entitlement_xml) , 1000 ))-1  ), ''<ENTITLEMENT_ID>AGS_Z0009_VAL_CAPACO</ENTITLEMENT_ID><ENTITLEMENT_VALUE_CODE>''+CAPITALAVOIDANCE_COEFFICIENT ) ELSE ENTITLEMENT_XML END FROM "+str(SAQIEN)+"(NOLOCK) A JOIN (SELECT DISTINCT QUOTE_ID ,SERVICE_ID,EQUIPMENT_ID,REVISION_ID,CAPITALAVOIDANCE_COEFFICIENT FROM SAQICO_INBOUND B(NOLOCK) JOIN "+str(CRMTMP)+" C ON B.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE ISNULL(PROCESS_STATUS,'''')=''INPROGRESS'' AND TIMESTAMP = '"+str(timestamp_sessionid)+"' AND B.SERVICE_ID = ''Z0009'')B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID  = B.EQUIPMENT_ID AND A.QTEREV_ID = B.REVISION_ID  WHERE A.QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND A.QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"''  AND ISNULL(CAPITALAVOIDANCE_COEFFICIENT,'''')<>'''' '")
							
							#Customer Segment
							#Z0091
							S3 = SqlHelper.GetFirst("sp_executesql @T=N'UPDATE A SET TOTAL_COEFFICIENT= ISNULL(TOTAL_COEFFICIENT,0) + ISNULL(CONVERT(FLOAT,ENTITLEMENT_VALUE_CODE),0) FROM SAQICO_INBOUND A(NOLOCK) JOIN (SELECT distinct quote_ID,equipment_id,service_id, replace(X.Y.value(''(ENTITLEMENT_VALUE_CODE)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_VALUE_CODE,replace(X.Y.value(''(ENTITLEMENT_NAME)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_NAME FROM (SELECT quote_ID,equipment_id,service_id,CONVERT(XML,''<QUOTE_ENTITLEMENT>''+substring(entitlement_xml,charindex (''<ENTITLEMENT_ID>AGS_Z0091_VAL_CSSGCO'',entitlement_xml),charindex (''Customer Segment Coefficent</ENTITLEMENT_NAME>'',entitlement_xml)-charindex (''<ENTITLEMENT_ID>AGS_Z0091_VAL_CSSGCO'',entitlement_xml)+len(''Customer Segment Coefficent</ENTITLEMENT_NAME>''))+''</QUOTE_ENTITLEMENT>'') as entitlement_xml FROM "+str(SAQSCE)+" (nolock)a JOIN "+str(CRMTMP)+" C ON A.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND SERVICE_ID = ''Z0091'') e OUTER APPLY e.ENTITLEMENT_XML.nodes(''QUOTE_ENTITLEMENT'') as X(Y) )B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID = B.EQUIPMENT_ID  WHERE B.ENTITLEMENT_NAME=''Customer Segment Coefficent'' AND ISNULL(ENTITLEMENT_VALUE_CODE,'''') <>''''  '")
							
							#Z0092
							S3 = SqlHelper.GetFirst("sp_executesql @T=N'UPDATE A SET TOTAL_COEFFICIENT= ISNULL(TOTAL_COEFFICIENT,0) + ISNULL(CONVERT(FLOAT,ENTITLEMENT_VALUE_CODE),0) FROM SAQICO_INBOUND A(NOLOCK) JOIN (SELECT distinct quote_ID,equipment_id,service_id, replace(X.Y.value(''(ENTITLEMENT_VALUE_CODE)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_VALUE_CODE,replace(X.Y.value(''(ENTITLEMENT_NAME)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_NAME FROM (SELECT quote_ID,equipment_id,service_id,CONVERT(XML,''<QUOTE_ENTITLEMENT>''+substring(entitlement_xml,charindex (''<ENTITLEMENT_ID>AGS_Z0092_VAL_CSSGCO'',entitlement_xml),charindex (''Customer Segment Coefficent</ENTITLEMENT_NAME>'',entitlement_xml)-charindex (''<ENTITLEMENT_ID>AGS_Z0092_VAL_CSSGCO'',entitlement_xml)+len(''Customer Segment Coefficent</ENTITLEMENT_NAME>''))+''</QUOTE_ENTITLEMENT>'') as entitlement_xml FROM "+str(SAQSCE)+" (nolock)a JOIN "+str(CRMTMP)+" C ON A.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND SERVICE_ID = ''Z0092'') e OUTER APPLY e.ENTITLEMENT_XML.nodes(''QUOTE_ENTITLEMENT'') as X(Y) )B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID = B.EQUIPMENT_ID  WHERE B.ENTITLEMENT_NAME=''Customer Segment Coefficent'' AND ISNULL(ENTITLEMENT_VALUE_CODE,'''') <>''''  '")
							
							#Z0004
							S3 = SqlHelper.GetFirst("sp_executesql @T=N'UPDATE A SET TOTAL_COEFFICIENT= ISNULL(TOTAL_COEFFICIENT,0) + ISNULL(CONVERT(FLOAT,ENTITLEMENT_VALUE_CODE),0) FROM SAQICO_INBOUND A(NOLOCK) JOIN (SELECT distinct quote_ID,equipment_id,service_id, replace(X.Y.value(''(ENTITLEMENT_VALUE_CODE)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_VALUE_CODE,replace(X.Y.value(''(ENTITLEMENT_NAME)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_NAME FROM (SELECT quote_ID,equipment_id,service_id,CONVERT(XML,''<QUOTE_ENTITLEMENT>''+substring(entitlement_xml,charindex (''<ENTITLEMENT_ID>AGS_Z0004_VAL_CSSGCO'',entitlement_xml),charindex (''Customer Segment Coefficent</ENTITLEMENT_NAME>'',entitlement_xml)-charindex (''<ENTITLEMENT_ID>AGS_Z0004_VAL_CSSGCO'',entitlement_xml)+len(''Customer Segment Coefficent</ENTITLEMENT_NAME>''))+''</QUOTE_ENTITLEMENT>'') as entitlement_xml FROM "+str(SAQSCE)+" (nolock)a JOIN "+str(CRMTMP)+" C ON A.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND SERVICE_ID = ''Z0004'') e OUTER APPLY e.ENTITLEMENT_XML.nodes(''QUOTE_ENTITLEMENT'') as X(Y) )B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID = B.EQUIPMENT_ID  WHERE B.ENTITLEMENT_NAME=''Customer Segment Coefficent'' AND ISNULL(ENTITLEMENT_VALUE_CODE,'''') <>''''  '")
							
							#Z0099
							S3 = SqlHelper.GetFirst("sp_executesql @T=N'UPDATE A SET TOTAL_COEFFICIENT= ISNULL(TOTAL_COEFFICIENT,0) + ISNULL(CONVERT(FLOAT,ENTITLEMENT_VALUE_CODE),0) FROM SAQICO_INBOUND A(NOLOCK) JOIN (SELECT distinct quote_ID,equipment_id,service_id, replace(X.Y.value(''(ENTITLEMENT_VALUE_CODE)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_VALUE_CODE,replace(X.Y.value(''(ENTITLEMENT_NAME)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_NAME FROM (SELECT quote_ID,equipment_id,service_id,CONVERT(XML,''<QUOTE_ENTITLEMENT>''+substring(entitlement_xml,charindex (''<ENTITLEMENT_ID>AGS_Z0099_VAL_CSSGCO'',entitlement_xml),charindex (''Customer Segment Coefficent</ENTITLEMENT_NAME>'',entitlement_xml)-charindex (''<ENTITLEMENT_ID>AGS_Z0099_VAL_CSSGCO'',entitlement_xml)+len(''Customer Segment Coefficent</ENTITLEMENT_NAME>''))+''</QUOTE_ENTITLEMENT>'') as entitlement_xml FROM "+str(SAQSCE)+" (nolock)a JOIN "+str(CRMTMP)+" C ON A.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND SERVICE_ID = ''Z0099'') e OUTER APPLY e.ENTITLEMENT_XML.nodes(''QUOTE_ENTITLEMENT'') as X(Y) )B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID = B.EQUIPMENT_ID  WHERE B.ENTITLEMENT_NAME=''Customer Segment Coefficent'' AND ISNULL(ENTITLEMENT_VALUE_CODE,'''') <>''''  '")
							
							#Z0035
							S3 = SqlHelper.GetFirst("sp_executesql @T=N'UPDATE A SET TOTAL_COEFFICIENT= ISNULL(TOTAL_COEFFICIENT,0) + ISNULL(CONVERT(FLOAT,ENTITLEMENT_VALUE_CODE),0) FROM SAQICO_INBOUND A(NOLOCK) JOIN (SELECT distinct quote_ID,equipment_id,service_id, replace(X.Y.value(''(ENTITLEMENT_VALUE_CODE)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_VALUE_CODE,replace(X.Y.value(''(ENTITLEMENT_NAME)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_NAME FROM (SELECT quote_ID,equipment_id,service_id,CONVERT(XML,''<QUOTE_ENTITLEMENT>''+substring(entitlement_xml,charindex (''<ENTITLEMENT_ID>AGS_Z0035_VAL_CSSGCO'',entitlement_xml),charindex (''Customer Segment Coefficent</ENTITLEMENT_NAME>'',entitlement_xml)-charindex (''<ENTITLEMENT_ID>AGS_Z0035_VAL_CSSGCO'',entitlement_xml)+len(''Customer Segment Coefficent</ENTITLEMENT_NAME>''))+''</QUOTE_ENTITLEMENT>'') as entitlement_xml FROM "+str(SAQSCE)+" (nolock)a JOIN "+str(CRMTMP)+" C ON A.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND SERVICE_ID = ''Z0035'') e OUTER APPLY e.ENTITLEMENT_XML.nodes(''QUOTE_ENTITLEMENT'') as X(Y) )B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID = B.EQUIPMENT_ID  WHERE B.ENTITLEMENT_NAME=''Customer Segment Coefficent'' AND ISNULL(ENTITLEMENT_VALUE_CODE,'''') <>''''  '")
							
							#Z0009
							S3 = SqlHelper.GetFirst("sp_executesql @T=N'UPDATE A SET TOTAL_COEFFICIENT= ISNULL(TOTAL_COEFFICIENT,0) + ISNULL(CONVERT(FLOAT,ENTITLEMENT_VALUE_CODE),0) FROM SAQICO_INBOUND A(NOLOCK) JOIN (SELECT distinct quote_ID,equipment_id,service_id, replace(X.Y.value(''(ENTITLEMENT_VALUE_CODE)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_VALUE_CODE,replace(X.Y.value(''(ENTITLEMENT_NAME)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_NAME FROM (SELECT quote_ID,equipment_id,service_id,CONVERT(XML,''<QUOTE_ENTITLEMENT>''+substring(entitlement_xml,charindex (''<ENTITLEMENT_ID>AGS_Z0009_VAL_CSSGCO'',entitlement_xml),charindex (''Customer Segment Coefficent</ENTITLEMENT_NAME>'',entitlement_xml)-charindex (''<ENTITLEMENT_ID>AGS_Z0009_VAL_CSSGCO'',entitlement_xml)+len(''Customer Segment Coefficent</ENTITLEMENT_NAME>''))+''</QUOTE_ENTITLEMENT>'') as entitlement_xml FROM "+str(SAQSCE)+" (nolock)a JOIN "+str(CRMTMP)+" C ON A.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND SERVICE_ID = ''Z0009'') e OUTER APPLY e.ENTITLEMENT_XML.nodes(''QUOTE_ENTITLEMENT'') as X(Y) )B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID = B.EQUIPMENT_ID  WHERE B.ENTITLEMENT_NAME=''Customer Segment Coefficent'' AND ISNULL(ENTITLEMENT_VALUE_CODE,'''') <>''''  '")
							
							#Service Competition
							#Z0091
							S3 = SqlHelper.GetFirst("sp_executesql @T=N'UPDATE A SET TOTAL_COEFFICIENT= ISNULL(TOTAL_COEFFICIENT,0) + ISNULL(CONVERT(FLOAT,ENTITLEMENT_VALUE_CODE),0) FROM SAQICO_INBOUND A(NOLOCK) JOIN (SELECT distinct quote_ID,equipment_id,service_id, replace(X.Y.value(''(ENTITLEMENT_VALUE_CODE)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_VALUE_CODE,replace(X.Y.value(''(ENTITLEMENT_NAME)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_NAME FROM (SELECT quote_ID,equipment_id,service_id,CONVERT(XML,''<QUOTE_ENTITLEMENT>''+substring(entitlement_xml,charindex (''<ENTITLEMENT_ID>AGS_Z0091_VAL_SVCCCO'',entitlement_xml),charindex (''Service Competition Coefficien</ENTITLEMENT_NAME>'',entitlement_xml)-charindex (''<ENTITLEMENT_ID>AGS_Z0091_VAL_SVCCCO'',entitlement_xml)+len(''Service Competition Coefficien</ENTITLEMENT_NAME>''))+''</QUOTE_ENTITLEMENT>'') as entitlement_xml FROM "+str(SAQSCE)+" (nolock)a JOIN "+str(CRMTMP)+" C ON A.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND SERVICE_ID = ''Z0091'') e OUTER APPLY e.ENTITLEMENT_XML.nodes(''QUOTE_ENTITLEMENT'') as X(Y) )B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID = B.EQUIPMENT_ID  WHERE B.ENTITLEMENT_NAME=''Service Competition Coefficien'' AND ISNULL(ENTITLEMENT_VALUE_CODE,'''') <>''''  '")
							
							#Z0092
							S3 = SqlHelper.GetFirst("sp_executesql @T=N'UPDATE A SET TOTAL_COEFFICIENT= ISNULL(TOTAL_COEFFICIENT,0) + ISNULL(CONVERT(FLOAT,ENTITLEMENT_VALUE_CODE),0) FROM SAQICO_INBOUND A(NOLOCK) JOIN (SELECT distinct quote_ID,equipment_id,service_id, replace(X.Y.value(''(ENTITLEMENT_VALUE_CODE)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_VALUE_CODE,replace(X.Y.value(''(ENTITLEMENT_NAME)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_NAME FROM (SELECT quote_ID,equipment_id,service_id,CONVERT(XML,''<QUOTE_ENTITLEMENT>''+substring(entitlement_xml,charindex (''<ENTITLEMENT_ID>AGS_Z0092_VAL_SVCCCO'',entitlement_xml),charindex (''Service Competition Coefficien</ENTITLEMENT_NAME>'',entitlement_xml)-charindex (''<ENTITLEMENT_ID>AGS_Z0092_VAL_SVCCCO'',entitlement_xml)+len(''Service Competition Coefficien</ENTITLEMENT_NAME>''))+''</QUOTE_ENTITLEMENT>'') as entitlement_xml FROM "+str(SAQSCE)+" (nolock)a JOIN "+str(CRMTMP)+" C ON A.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND SERVICE_ID = ''Z0092'') e OUTER APPLY e.ENTITLEMENT_XML.nodes(''QUOTE_ENTITLEMENT'') as X(Y) )B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID = B.EQUIPMENT_ID  WHERE B.ENTITLEMENT_NAME=''Service Competition Coefficien'' AND ISNULL(ENTITLEMENT_VALUE_CODE,'''') <>''''  '")
							
							#Z0004
							S3 = SqlHelper.GetFirst("sp_executesql @T=N'UPDATE A SET TOTAL_COEFFICIENT= ISNULL(TOTAL_COEFFICIENT,0) + ISNULL(CONVERT(FLOAT,ENTITLEMENT_VALUE_CODE),0) FROM SAQICO_INBOUND A(NOLOCK) JOIN (SELECT distinct quote_ID,equipment_id,service_id, replace(X.Y.value(''(ENTITLEMENT_VALUE_CODE)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_VALUE_CODE,replace(X.Y.value(''(ENTITLEMENT_NAME)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_NAME FROM (SELECT quote_ID,equipment_id,service_id,CONVERT(XML,''<QUOTE_ENTITLEMENT>''+substring(entitlement_xml,charindex (''<ENTITLEMENT_ID>AGS_Z0004_VAL_SVCCCO'',entitlement_xml),charindex (''Service Competition Coefficien</ENTITLEMENT_NAME>'',entitlement_xml)-charindex (''<ENTITLEMENT_ID>AGS_Z0004_VAL_SVCCCO'',entitlement_xml)+len(''Service Competition Coefficien</ENTITLEMENT_NAME>''))+''</QUOTE_ENTITLEMENT>'') as entitlement_xml FROM "+str(SAQSCE)+" (nolock)a JOIN "+str(CRMTMP)+" C ON A.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND SERVICE_ID = ''Z0004'') e OUTER APPLY e.ENTITLEMENT_XML.nodes(''QUOTE_ENTITLEMENT'') as X(Y) )B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID = B.EQUIPMENT_ID  WHERE B.ENTITLEMENT_NAME=''Service Competition Coefficien'' AND ISNULL(ENTITLEMENT_VALUE_CODE,'''') <>''''  '")
							
							#Z0099
							S3 = SqlHelper.GetFirst("sp_executesql @T=N'UPDATE A SET TOTAL_COEFFICIENT= ISNULL(TOTAL_COEFFICIENT,0) + ISNULL(CONVERT(FLOAT,ENTITLEMENT_VALUE_CODE),0) FROM SAQICO_INBOUND A(NOLOCK) JOIN (SELECT distinct quote_ID,equipment_id,service_id, replace(X.Y.value(''(ENTITLEMENT_VALUE_CODE)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_VALUE_CODE,replace(X.Y.value(''(ENTITLEMENT_NAME)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_NAME FROM (SELECT quote_ID,equipment_id,service_id,CONVERT(XML,''<QUOTE_ENTITLEMENT>''+substring(entitlement_xml,charindex (''<ENTITLEMENT_ID>AGS_Z0099_VAL_SVCCCO'',entitlement_xml),charindex (''Service Competition Coefficien</ENTITLEMENT_NAME>'',entitlement_xml)-charindex (''<ENTITLEMENT_ID>AGS_Z0099_VAL_SVCCCO'',entitlement_xml)+len(''Service Competition Coefficien</ENTITLEMENT_NAME>''))+''</QUOTE_ENTITLEMENT>'') as entitlement_xml FROM "+str(SAQSCE)+" (nolock)a JOIN "+str(CRMTMP)+" C ON A.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND SERVICE_ID = ''Z0099'') e OUTER APPLY e.ENTITLEMENT_XML.nodes(''QUOTE_ENTITLEMENT'') as X(Y) )B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID = B.EQUIPMENT_ID  WHERE B.ENTITLEMENT_NAME=''Service Competition Coefficien'' AND ISNULL(ENTITLEMENT_VALUE_CODE,'''') <>''''  '")
							
							#Z0035
							S3 = SqlHelper.GetFirst("sp_executesql @T=N'UPDATE A SET TOTAL_COEFFICIENT= ISNULL(TOTAL_COEFFICIENT,0) + ISNULL(CONVERT(FLOAT,ENTITLEMENT_VALUE_CODE),0) FROM SAQICO_INBOUND A(NOLOCK) JOIN (SELECT distinct quote_ID,equipment_id,service_id, replace(X.Y.value(''(ENTITLEMENT_VALUE_CODE)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_VALUE_CODE,replace(X.Y.value(''(ENTITLEMENT_NAME)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_NAME FROM (SELECT quote_ID,equipment_id,service_id,CONVERT(XML,''<QUOTE_ENTITLEMENT>''+substring(entitlement_xml,charindex (''<ENTITLEMENT_ID>AGS_Z0035_VAL_SVCCCO'',entitlement_xml),charindex (''Service Competition Coefficien</ENTITLEMENT_NAME>'',entitlement_xml)-charindex (''<ENTITLEMENT_ID>AGS_Z0035_VAL_SVCCCO'',entitlement_xml)+len(''Service Competition Coefficien</ENTITLEMENT_NAME>''))+''</QUOTE_ENTITLEMENT>'') as entitlement_xml FROM "+str(SAQSCE)+" (nolock)a JOIN "+str(CRMTMP)+" C ON A.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND SERVICE_ID = ''Z0035'') e OUTER APPLY e.ENTITLEMENT_XML.nodes(''QUOTE_ENTITLEMENT'') as X(Y) )B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID = B.EQUIPMENT_ID  WHERE B.ENTITLEMENT_NAME=''Service Competition Coefficien'' AND ISNULL(ENTITLEMENT_VALUE_CODE,'''') <>''''  '")
							
							#Z0009
							S3 = SqlHelper.GetFirst("sp_executesql @T=N'UPDATE A SET TOTAL_COEFFICIENT= ISNULL(TOTAL_COEFFICIENT,0) + ISNULL(CONVERT(FLOAT,ENTITLEMENT_VALUE_CODE),0) FROM SAQICO_INBOUND A(NOLOCK) JOIN (SELECT distinct quote_ID,equipment_id,service_id, replace(X.Y.value(''(ENTITLEMENT_VALUE_CODE)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_VALUE_CODE,replace(X.Y.value(''(ENTITLEMENT_NAME)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_NAME FROM (SELECT quote_ID,equipment_id,service_id,CONVERT(XML,''<QUOTE_ENTITLEMENT>''+substring(entitlement_xml,charindex (''<ENTITLEMENT_ID>AGS_Z0009_VAL_SVCCCO'',entitlement_xml),charindex (''Service Competition Coefficien</ENTITLEMENT_NAME>'',entitlement_xml)-charindex (''<ENTITLEMENT_ID>AGS_Z0009_VAL_SVCCCO'',entitlement_xml)+len(''Service Competition Coefficien</ENTITLEMENT_NAME>''))+''</QUOTE_ENTITLEMENT>'') as entitlement_xml FROM "+str(SAQSCE)+" (nolock)a JOIN "+str(CRMTMP)+" C ON A.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND SERVICE_ID = ''Z0009'') e OUTER APPLY e.ENTITLEMENT_XML.nodes(''QUOTE_ENTITLEMENT'') as X(Y) )B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID = B.EQUIPMENT_ID  WHERE B.ENTITLEMENT_NAME=''Service Competition Coefficien'' AND ISNULL(ENTITLEMENT_VALUE_CODE,'''') <>''''  '")

							#Quality Required 
							#Z0091
							S3 = SqlHelper.GetFirst("sp_executesql @T=N'UPDATE A SET TOTAL_COEFFICIENT= ISNULL(TOTAL_COEFFICIENT,0) + ISNULL(CONVERT(FLOAT,ENTITLEMENT_VALUE_CODE),0) FROM SAQICO_INBOUND A(NOLOCK) JOIN (SELECT distinct quote_ID,equipment_id,service_id, replace(X.Y.value(''(ENTITLEMENT_VALUE_CODE)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_VALUE_CODE,replace(X.Y.value(''(ENTITLEMENT_NAME)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_NAME FROM (SELECT quote_ID,equipment_id,service_id,CONVERT(XML,''<QUOTE_ENTITLEMENT>''+substring(entitlement_xml,charindex (''<ENTITLEMENT_ID>AGS_Z0091_VAL_QLYRCO'',entitlement_xml),charindex (''Quality Required Coefficient</ENTITLEMENT_NAME>'',entitlement_xml)-charindex (''<ENTITLEMENT_ID>AGS_Z0091_VAL_QLYRCO'',entitlement_xml)+len(''Quality Required Coefficient</ENTITLEMENT_NAME>''))+''</QUOTE_ENTITLEMENT>'') as entitlement_xml FROM "+str(SAQSCE)+" (nolock)a JOIN "+str(CRMTMP)+" C ON A.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND SERVICE_ID = ''Z0091'') e OUTER APPLY e.ENTITLEMENT_XML.nodes(''QUOTE_ENTITLEMENT'') as X(Y) )B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID = B.EQUIPMENT_ID  WHERE B.ENTITLEMENT_NAME=''Quality Required Coefficient'' AND ISNULL(ENTITLEMENT_VALUE_CODE,'''') <>''''  '")
							
							#Z0092
							S3 = SqlHelper.GetFirst("sp_executesql @T=N'UPDATE A SET TOTAL_COEFFICIENT= ISNULL(TOTAL_COEFFICIENT,0) + ISNULL(CONVERT(FLOAT,ENTITLEMENT_VALUE_CODE),0) FROM SAQICO_INBOUND A(NOLOCK) JOIN (SELECT distinct quote_ID,equipment_id,service_id, replace(X.Y.value(''(ENTITLEMENT_VALUE_CODE)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_VALUE_CODE,replace(X.Y.value(''(ENTITLEMENT_NAME)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_NAME FROM (SELECT quote_ID,equipment_id,service_id,CONVERT(XML,''<QUOTE_ENTITLEMENT>''+substring(entitlement_xml,charindex (''<ENTITLEMENT_ID>AGS_Z0092_VAL_QLYRCO'',entitlement_xml),charindex (''Quality Required Coefficient</ENTITLEMENT_NAME>'',entitlement_xml)-charindex (''<ENTITLEMENT_ID>AGS_Z0092_VAL_QLYRCO'',entitlement_xml)+len(''Quality Required Coefficient</ENTITLEMENT_NAME>''))+''</QUOTE_ENTITLEMENT>'') as entitlement_xml FROM "+str(SAQSCE)+" (nolock)a JOIN "+str(CRMTMP)+" C ON A.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND SERVICE_ID = ''Z0092'') e OUTER APPLY e.ENTITLEMENT_XML.nodes(''QUOTE_ENTITLEMENT'') as X(Y) )B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID = B.EQUIPMENT_ID  WHERE B.ENTITLEMENT_NAME=''Quality Required Coefficient'' AND ISNULL(ENTITLEMENT_VALUE_CODE,'''') <>''''  '")
							
							#Z0004
							S3 = SqlHelper.GetFirst("sp_executesql @T=N'UPDATE A SET TOTAL_COEFFICIENT= ISNULL(TOTAL_COEFFICIENT,0) + ISNULL(CONVERT(FLOAT,ENTITLEMENT_VALUE_CODE),0) FROM SAQICO_INBOUND A(NOLOCK) JOIN (SELECT distinct quote_ID,equipment_id,service_id, replace(X.Y.value(''(ENTITLEMENT_VALUE_CODE)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_VALUE_CODE,replace(X.Y.value(''(ENTITLEMENT_NAME)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_NAME FROM (SELECT quote_ID,equipment_id,service_id,CONVERT(XML,''<QUOTE_ENTITLEMENT>''+substring(entitlement_xml,charindex (''<ENTITLEMENT_ID>AGS_Z0004_VAL_QLYRCO'',entitlement_xml),charindex (''Quality Required Coefficient</ENTITLEMENT_NAME>'',entitlement_xml)-charindex (''<ENTITLEMENT_ID>AGS_Z0004_VAL_QLYRCO'',entitlement_xml)+len(''Quality Required Coefficient</ENTITLEMENT_NAME>''))+''</QUOTE_ENTITLEMENT>'') as entitlement_xml FROM "+str(SAQSCE)+" (nolock)a JOIN "+str(CRMTMP)+" C ON A.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND SERVICE_ID = ''Z0004'') e OUTER APPLY e.ENTITLEMENT_XML.nodes(''QUOTE_ENTITLEMENT'') as X(Y) )B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID = B.EQUIPMENT_ID  WHERE B.ENTITLEMENT_NAME=''Quality Required Coefficient'' AND ISNULL(ENTITLEMENT_VALUE_CODE,'''') <>''''  '")
							
							#Z0099
							S3 = SqlHelper.GetFirst("sp_executesql @T=N'UPDATE A SET TOTAL_COEFFICIENT= ISNULL(TOTAL_COEFFICIENT,0) + ISNULL(CONVERT(FLOAT,ENTITLEMENT_VALUE_CODE),0) FROM SAQICO_INBOUND A(NOLOCK) JOIN (SELECT distinct quote_ID,equipment_id,service_id, replace(X.Y.value(''(ENTITLEMENT_VALUE_CODE)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_VALUE_CODE,replace(X.Y.value(''(ENTITLEMENT_NAME)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_NAME FROM (SELECT quote_ID,equipment_id,service_id,CONVERT(XML,''<QUOTE_ENTITLEMENT>''+substring(entitlement_xml,charindex (''<ENTITLEMENT_ID>AGS_Z0099_VAL_QLYRCO'',entitlement_xml),charindex (''Quality Required Coefficient</ENTITLEMENT_NAME>'',entitlement_xml)-charindex (''<ENTITLEMENT_ID>AGS_Z0099_VAL_QLYRCO'',entitlement_xml)+len(''Quality Required Coefficient</ENTITLEMENT_NAME>''))+''</QUOTE_ENTITLEMENT>'') as entitlement_xml FROM "+str(SAQSCE)+" (nolock)a JOIN "+str(CRMTMP)+" C ON A.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND SERVICE_ID = ''Z0099'') e OUTER APPLY e.ENTITLEMENT_XML.nodes(''QUOTE_ENTITLEMENT'') as X(Y) )B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID = B.EQUIPMENT_ID  WHERE B.ENTITLEMENT_NAME=''Quality Required Coefficient'' AND ISNULL(ENTITLEMENT_VALUE_CODE,'''') <>''''  '")
							
							#Z0035
							S3 = SqlHelper.GetFirst("sp_executesql @T=N'UPDATE A SET TOTAL_COEFFICIENT= ISNULL(TOTAL_COEFFICIENT,0) + ISNULL(CONVERT(FLOAT,ENTITLEMENT_VALUE_CODE),0) FROM SAQICO_INBOUND A(NOLOCK) JOIN (SELECT distinct quote_ID,equipment_id,service_id, replace(X.Y.value(''(ENTITLEMENT_VALUE_CODE)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_VALUE_CODE,replace(X.Y.value(''(ENTITLEMENT_NAME)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_NAME FROM (SELECT quote_ID,equipment_id,service_id,CONVERT(XML,''<QUOTE_ENTITLEMENT>''+substring(entitlement_xml,charindex (''<ENTITLEMENT_ID>AGS_Z0035_VAL_QLYRCO'',entitlement_xml),charindex (''Quality Required Coefficient</ENTITLEMENT_NAME>'',entitlement_xml)-charindex (''<ENTITLEMENT_ID>AGS_Z0035_VAL_QLYRCO'',entitlement_xml)+len(''Quality Required Coefficient</ENTITLEMENT_NAME>''))+''</QUOTE_ENTITLEMENT>'') as entitlement_xml FROM "+str(SAQSCE)+" (nolock)a JOIN "+str(CRMTMP)+" C ON A.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND SERVICE_ID = ''Z0035'') e OUTER APPLY e.ENTITLEMENT_XML.nodes(''QUOTE_ENTITLEMENT'') as X(Y) )B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID = B.EQUIPMENT_ID  WHERE B.ENTITLEMENT_NAME=''Quality Required Coefficient'' AND ISNULL(ENTITLEMENT_VALUE_CODE,'''') <>''''  '")
							
							#Z0009
							S3 = SqlHelper.GetFirst("sp_executesql @T=N'UPDATE A SET TOTAL_COEFFICIENT= ISNULL(TOTAL_COEFFICIENT,0) + ISNULL(CONVERT(FLOAT,ENTITLEMENT_VALUE_CODE),0) FROM SAQICO_INBOUND A(NOLOCK) JOIN (SELECT distinct quote_ID,equipment_id,service_id, replace(X.Y.value(''(ENTITLEMENT_VALUE_CODE)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_VALUE_CODE,replace(X.Y.value(''(ENTITLEMENT_NAME)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_NAME FROM (SELECT quote_ID,equipment_id,service_id,CONVERT(XML,''<QUOTE_ENTITLEMENT>''+substring(entitlement_xml,charindex (''<ENTITLEMENT_ID>AGS_Z0009_VAL_QLYRCO'',entitlement_xml),charindex (''Quality Required Coefficient</ENTITLEMENT_NAME>'',entitlement_xml)-charindex (''<ENTITLEMENT_ID>AGS_Z0009_VAL_QLYRCO'',entitlement_xml)+len(''Quality Required Coefficient</ENTITLEMENT_NAME>''))+''</QUOTE_ENTITLEMENT>'') as entitlement_xml FROM "+str(SAQSCE)+" (nolock)a JOIN "+str(CRMTMP)+" C ON A.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND SERVICE_ID = ''Z0009'') e OUTER APPLY e.ENTITLEMENT_XML.nodes(''QUOTE_ENTITLEMENT'') as X(Y) )B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID = B.EQUIPMENT_ID  WHERE B.ENTITLEMENT_NAME=''Quality Required Coefficient'' AND ISNULL(ENTITLEMENT_VALUE_CODE,'''') <>''''  '")

							#Intercept
							#Z0091
							S3 = SqlHelper.GetFirst("sp_executesql @T=N'UPDATE A SET INTERCEPT=  ISNULL(CONVERT(FLOAT,ENTITLEMENT_VALUE_CODE),0) FROM SAQICO_INBOUND A(NOLOCK) JOIN (SELECT distinct quote_ID,equipment_id,service_id, replace(X.Y.value(''(ENTITLEMENT_VALUE_CODE)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_VALUE_CODE,replace(X.Y.value(''(ENTITLEMENT_NAME)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_NAME FROM (SELECT quote_ID,equipment_id,service_id,CONVERT(XML,''<QUOTE_ENTITLEMENT>''+substring(entitlement_xml,charindex (''<ENTITLEMENT_ID>AGS_Z0091_VAL_INTCCO'',entitlement_xml),charindex (''Intercept Coefficient</ENTITLEMENT_NAME>'',entitlement_xml)-charindex (''<ENTITLEMENT_ID>AGS_Z0091_VAL_INTCCO'',entitlement_xml)+len(''Intercept Coefficient</ENTITLEMENT_NAME>''))+''</QUOTE_ENTITLEMENT>'') as entitlement_xml FROM "+str(SAQSCE)+" (nolock)a JOIN "+str(CRMTMP)+" C ON A.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND SERVICE_ID = ''Z0091'') e OUTER APPLY e.ENTITLEMENT_XML.nodes(''QUOTE_ENTITLEMENT'') as X(Y) )B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID = B.EQUIPMENT_ID  WHERE B.ENTITLEMENT_NAME=''Intercept Coefficient'' AND ISNULL(ENTITLEMENT_VALUE_CODE,'''') <>'''' '")
							
							#Z0092
							S3 = SqlHelper.GetFirst("sp_executesql @T=N'UPDATE A SET INTERCEPT=  ISNULL(CONVERT(FLOAT,ENTITLEMENT_VALUE_CODE),0) FROM SAQICO_INBOUND A(NOLOCK) JOIN (SELECT distinct quote_ID,equipment_id,service_id, replace(X.Y.value(''(ENTITLEMENT_VALUE_CODE)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_VALUE_CODE,replace(X.Y.value(''(ENTITLEMENT_NAME)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_NAME FROM (SELECT quote_ID,equipment_id,service_id,CONVERT(XML,''<QUOTE_ENTITLEMENT>''+substring(entitlement_xml,charindex (''<ENTITLEMENT_ID>AGS_Z0092_VAL_INTCCO'',entitlement_xml),charindex (''Intercept Coefficient</ENTITLEMENT_NAME>'',entitlement_xml)-charindex (''<ENTITLEMENT_ID>AGS_Z0092_VAL_INTCCO'',entitlement_xml)+len(''Intercept Coefficient</ENTITLEMENT_NAME>''))+''</QUOTE_ENTITLEMENT>'') as entitlement_xml FROM "+str(SAQSCE)+" (nolock)a JOIN "+str(CRMTMP)+" C ON A.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND SERVICE_ID = ''Z0092'') e OUTER APPLY e.ENTITLEMENT_XML.nodes(''QUOTE_ENTITLEMENT'') as X(Y) )B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID = B.EQUIPMENT_ID  WHERE B.ENTITLEMENT_NAME=''Intercept Coefficient'' AND ISNULL(ENTITLEMENT_VALUE_CODE,'''') <>'''' '")
							
							#Z0004
							S3 = SqlHelper.GetFirst("sp_executesql @T=N'UPDATE A SET INTERCEPT=  ISNULL(CONVERT(FLOAT,ENTITLEMENT_VALUE_CODE),0) FROM SAQICO_INBOUND A(NOLOCK) JOIN (SELECT distinct quote_ID,equipment_id,service_id, replace(X.Y.value(''(ENTITLEMENT_VALUE_CODE)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_VALUE_CODE,replace(X.Y.value(''(ENTITLEMENT_NAME)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_NAME FROM (SELECT quote_ID,equipment_id,service_id,CONVERT(XML,''<QUOTE_ENTITLEMENT>''+substring(entitlement_xml,charindex (''<ENTITLEMENT_ID>AGS_Z0004_VAL_INTCCO'',entitlement_xml),charindex (''Intercept Coefficient</ENTITLEMENT_NAME>'',entitlement_xml)-charindex (''<ENTITLEMENT_ID>AGS_Z0004_VAL_INTCCO'',entitlement_xml)+len(''Intercept Coefficient</ENTITLEMENT_NAME>''))+''</QUOTE_ENTITLEMENT>'') as entitlement_xml FROM "+str(SAQSCE)+" (nolock)a JOIN "+str(CRMTMP)+" C ON A.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND SERVICE_ID = ''Z0004'') e OUTER APPLY e.ENTITLEMENT_XML.nodes(''QUOTE_ENTITLEMENT'') as X(Y) )B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID = B.EQUIPMENT_ID  WHERE B.ENTITLEMENT_NAME=''Intercept Coefficient'' AND ISNULL(ENTITLEMENT_VALUE_CODE,'''') <>'''' '")
							
							#Z0099
							S3 = SqlHelper.GetFirst("sp_executesql @T=N'UPDATE A SET INTERCEPT=  ISNULL(CONVERT(FLOAT,ENTITLEMENT_VALUE_CODE),0) FROM SAQICO_INBOUND A(NOLOCK) JOIN (SELECT distinct quote_ID,equipment_id,service_id, replace(X.Y.value(''(ENTITLEMENT_VALUE_CODE)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_VALUE_CODE,replace(X.Y.value(''(ENTITLEMENT_NAME)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_NAME FROM (SELECT quote_ID,equipment_id,service_id,CONVERT(XML,''<QUOTE_ENTITLEMENT>''+substring(entitlement_xml,charindex (''<ENTITLEMENT_ID>AGS_Z0099_VAL_INTCCO'',entitlement_xml),charindex (''Intercept Coefficient</ENTITLEMENT_NAME>'',entitlement_xml)-charindex (''<ENTITLEMENT_ID>AGS_Z0099_VAL_INTCCO'',entitlement_xml)+len(''Intercept Coefficient</ENTITLEMENT_NAME>''))+''</QUOTE_ENTITLEMENT>'') as entitlement_xml FROM "+str(SAQSCE)+" (nolock)a JOIN "+str(CRMTMP)+" C ON A.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND SERVICE_ID = ''Z0099'') e OUTER APPLY e.ENTITLEMENT_XML.nodes(''QUOTE_ENTITLEMENT'') as X(Y) )B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID = B.EQUIPMENT_ID  WHERE B.ENTITLEMENT_NAME=''Intercept Coefficient'' AND ISNULL(ENTITLEMENT_VALUE_CODE,'''') <>'''' '")
							
							#Z0035
							S3 = SqlHelper.GetFirst("sp_executesql @T=N'UPDATE A SET INTERCEPT=  ISNULL(CONVERT(FLOAT,ENTITLEMENT_VALUE_CODE),0) FROM SAQICO_INBOUND A(NOLOCK) JOIN (SELECT distinct quote_ID,equipment_id,service_id, replace(X.Y.value(''(ENTITLEMENT_VALUE_CODE)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_VALUE_CODE,replace(X.Y.value(''(ENTITLEMENT_NAME)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_NAME FROM (SELECT quote_ID,equipment_id,service_id,CONVERT(XML,''<QUOTE_ENTITLEMENT>''+substring(entitlement_xml,charindex (''<ENTITLEMENT_ID>AGS_Z0035_VAL_INTCCO'',entitlement_xml),charindex (''Intercept Coefficient</ENTITLEMENT_NAME>'',entitlement_xml)-charindex (''<ENTITLEMENT_ID>AGS_Z0035_VAL_INTCCO'',entitlement_xml)+len(''Intercept Coefficient</ENTITLEMENT_NAME>''))+''</QUOTE_ENTITLEMENT>'') as entitlement_xml FROM "+str(SAQSCE)+" (nolock)a JOIN "+str(CRMTMP)+" C ON A.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND SERVICE_ID = ''Z0035'') e OUTER APPLY e.ENTITLEMENT_XML.nodes(''QUOTE_ENTITLEMENT'') as X(Y) )B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID = B.EQUIPMENT_ID  WHERE B.ENTITLEMENT_NAME=''Intercept Coefficient'' AND ISNULL(ENTITLEMENT_VALUE_CODE,'''') <>'''' '")
							
							#Z0009
							S3 = SqlHelper.GetFirst("sp_executesql @T=N'UPDATE A SET INTERCEPT=  ISNULL(CONVERT(FLOAT,ENTITLEMENT_VALUE_CODE),0) FROM SAQICO_INBOUND A(NOLOCK) JOIN (SELECT distinct quote_ID,equipment_id,service_id, replace(X.Y.value(''(ENTITLEMENT_VALUE_CODE)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_VALUE_CODE,replace(X.Y.value(''(ENTITLEMENT_NAME)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_NAME FROM (SELECT quote_ID,equipment_id,service_id,CONVERT(XML,''<QUOTE_ENTITLEMENT>''+substring(entitlement_xml,charindex (''<ENTITLEMENT_ID>AGS_Z0009_VAL_INTCCO'',entitlement_xml),charindex (''Intercept Coefficient</ENTITLEMENT_NAME>'',entitlement_xml)-charindex (''<ENTITLEMENT_ID>AGS_Z0009_VAL_INTCCO'',entitlement_xml)+len(''Intercept Coefficient</ENTITLEMENT_NAME>''))+''</QUOTE_ENTITLEMENT>'') as entitlement_xml FROM "+str(SAQSCE)+" (nolock)a JOIN "+str(CRMTMP)+" C ON A.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND SERVICE_ID = ''Z0009'') e OUTER APPLY e.ENTITLEMENT_XML.nodes(''QUOTE_ENTITLEMENT'') as X(Y) )B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID = B.EQUIPMENT_ID  WHERE B.ENTITLEMENT_NAME=''Intercept Coefficient'' AND ISNULL(ENTITLEMENT_VALUE_CODE,'''') <>'''' '")

							#Tool Base Coefficient
							S3 = SqlHelper.GetFirst("sp_executesql @T=N'UPDATE A SET LOG_FACTOR =  0.94 FROM SAQICO_INBOUND A(NOLOCK) WHERE QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND REVISION_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND SERVICE_ID = ''Z0091'' AND A.GREENBOOK <> ''PDC'' '")
							
							S3 = SqlHelper.GetFirst("sp_executesql @T=N'UPDATE A SET LOG_FACTOR =  0.94 FROM SAQICO_INBOUND A(NOLOCK) WHERE QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND REVISION_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND SERVICE_ID = ''Z0092'' AND A.GREENBOOK <> ''PDC'' '")
							
							S3 = SqlHelper.GetFirst("sp_executesql @T=N'UPDATE A SET LOG_FACTOR =  0.94 FROM SAQICO_INBOUND A(NOLOCK) WHERE QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND REVISION_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND SERVICE_ID = ''Z0004'' AND A.GREENBOOK <> ''PDC'' '")
							
							S3 = SqlHelper.GetFirst("sp_executesql @T=N'UPDATE A SET LOG_FACTOR =  0.94 FROM SAQICO_INBOUND A(NOLOCK) WHERE QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND REVISION_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND SERVICE_ID = ''Z0099'' AND A.GREENBOOK <> ''PDC'' '")
							
							S3 = SqlHelper.GetFirst("sp_executesql @T=N'UPDATE A SET LOG_FACTOR =  0.94 FROM SAQICO_INBOUND A(NOLOCK) WHERE QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND REVISION_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND SERVICE_ID = ''Z0035'' AND A.GREENBOOK <> ''PDC'' '")
							
							S3 = SqlHelper.GetFirst("sp_executesql @T=N'UPDATE A SET LOG_FACTOR =  0.94 FROM SAQICO_INBOUND A(NOLOCK) WHERE QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND REVISION_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND SERVICE_ID = ''Z0009'' AND A.GREENBOOK <> ''PDC'' '")

							#PDC Base Price Coefficient
							S3 = SqlHelper.GetFirst("sp_executesql @T=N'UPDATE A SET LOG_FACTOR =  0.92 FROM SAQICO_INBOUND A(NOLOCK) WHERE QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND REVISION_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND SERVICE_ID = ''Z0091'' AND A.GREENBOOK = ''PDC'' '")
							
							S3 = SqlHelper.GetFirst("sp_executesql @T=N'UPDATE A SET LOG_FACTOR =  0.92 FROM SAQICO_INBOUND A(NOLOCK) WHERE QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND REVISION_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND SERVICE_ID = ''Z0092'' AND A.GREENBOOK = ''PDC'' '")
							
							S3 = SqlHelper.GetFirst("sp_executesql @T=N'UPDATE A SET LOG_FACTOR =  0.92 FROM SAQICO_INBOUND A(NOLOCK) WHERE QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND REVISION_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND SERVICE_ID = ''Z0004'' AND A.GREENBOOK = ''PDC'' '")
							
							S3 = SqlHelper.GetFirst("sp_executesql @T=N'UPDATE A SET LOG_FACTOR =  0.92 FROM SAQICO_INBOUND A(NOLOCK) WHERE QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND REVISION_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND SERVICE_ID = ''Z0099'' AND A.GREENBOOK = ''PDC'' '")
							
							S3 = SqlHelper.GetFirst("sp_executesql @T=N'UPDATE A SET LOG_FACTOR =  0.92 FROM SAQICO_INBOUND A(NOLOCK) WHERE QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND REVISION_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND SERVICE_ID = ''Z0035'' AND A.GREENBOOK = ''PDC'' '")
							
							S3 = SqlHelper.GetFirst("sp_executesql @T=N'UPDATE A SET LOG_FACTOR =  0.92 FROM SAQICO_INBOUND A(NOLOCK) WHERE QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND REVISION_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND SERVICE_ID = ''Z0009'' AND A.GREENBOOK = ''PDC'' '")

							#Product Offering Coefficient
							#Z0091
							S3 = SqlHelper.GetFirst("sp_executesql @T=N'UPDATE A SET TOTAL_COEFFICIENT= ISNULL(TOTAL_COEFFICIENT,0) + ISNULL(CONVERT(FLOAT,ENTITLEMENT_VALUE_CODE),0) FROM SAQICO_INBOUND A(NOLOCK) JOIN (SELECT distinct quote_ID,equipment_id,service_id, replace(X.Y.value(''(ENTITLEMENT_VALUE_CODE)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_VALUE_CODE,replace(X.Y.value(''(ENTITLEMENT_NAME)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_NAME FROM (SELECT quote_ID,equipment_id,service_id,CONVERT(XML,''<QUOTE_ENTITLEMENT>''+substring(entitlement_xml,charindex (''<ENTITLEMENT_ID>AGS_Z0091_VAL_POFFCO'',entitlement_xml),charindex (''Product Offering Coefficient</ENTITLEMENT_NAME>'',entitlement_xml)-charindex (''<ENTITLEMENT_ID>AGS_Z0091_VAL_POFFCO'',entitlement_xml)+len(''Product Offering Coefficient</ENTITLEMENT_NAME>''))+''</QUOTE_ENTITLEMENT>'') as entitlement_xml FROM "+str(SAQSCE)+" (nolock)a JOIN "+str(CRMTMP)+" C ON A.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND SERVICE_ID = ''Z0091'') e OUTER APPLY e.ENTITLEMENT_XML.nodes(''QUOTE_ENTITLEMENT'') as X(Y) )B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID = B.EQUIPMENT_ID  WHERE B.ENTITLEMENT_NAME=''Product Offering Coefficient'' AND ISNULL(ENTITLEMENT_VALUE_CODE,'''') <>''''  '")
							
							#Z0092
							S3 = SqlHelper.GetFirst("sp_executesql @T=N'UPDATE A SET TOTAL_COEFFICIENT= ISNULL(TOTAL_COEFFICIENT,0) + ISNULL(CONVERT(FLOAT,ENTITLEMENT_VALUE_CODE),0) FROM SAQICO_INBOUND A(NOLOCK) JOIN (SELECT distinct quote_ID,equipment_id,service_id, replace(X.Y.value(''(ENTITLEMENT_VALUE_CODE)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_VALUE_CODE,replace(X.Y.value(''(ENTITLEMENT_NAME)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_NAME FROM (SELECT quote_ID,equipment_id,service_id,CONVERT(XML,''<QUOTE_ENTITLEMENT>''+substring(entitlement_xml,charindex (''<ENTITLEMENT_ID>AGS_Z0092_VAL_POFFCO'',entitlement_xml),charindex (''Product Offering Coefficient</ENTITLEMENT_NAME>'',entitlement_xml)-charindex (''<ENTITLEMENT_ID>AGS_Z0092_VAL_POFFCO'',entitlement_xml)+len(''Product Offering Coefficient</ENTITLEMENT_NAME>''))+''</QUOTE_ENTITLEMENT>'') as entitlement_xml FROM "+str(SAQSCE)+" (nolock)a JOIN "+str(CRMTMP)+" C ON A.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND SERVICE_ID = ''Z0092'') e OUTER APPLY e.ENTITLEMENT_XML.nodes(''QUOTE_ENTITLEMENT'') as X(Y) )B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID = B.EQUIPMENT_ID  WHERE B.ENTITLEMENT_NAME=''Product Offering Coefficient'' AND ISNULL(ENTITLEMENT_VALUE_CODE,'''') <>''''  '")
							
							#Z0004
							S3 = SqlHelper.GetFirst("sp_executesql @T=N'UPDATE A SET TOTAL_COEFFICIENT= ISNULL(TOTAL_COEFFICIENT,0) + ISNULL(CONVERT(FLOAT,ENTITLEMENT_VALUE_CODE),0) FROM SAQICO_INBOUND A(NOLOCK) JOIN (SELECT distinct quote_ID,equipment_id,service_id, replace(X.Y.value(''(ENTITLEMENT_VALUE_CODE)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_VALUE_CODE,replace(X.Y.value(''(ENTITLEMENT_NAME)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_NAME FROM (SELECT quote_ID,equipment_id,service_id,CONVERT(XML,''<QUOTE_ENTITLEMENT>''+substring(entitlement_xml,charindex (''<ENTITLEMENT_ID>AGS_Z0004_VAL_POFFCO'',entitlement_xml),charindex (''Product Offering Coefficient</ENTITLEMENT_NAME>'',entitlement_xml)-charindex (''<ENTITLEMENT_ID>AGS_Z0004_VAL_POFFCO'',entitlement_xml)+len(''Product Offering Coefficient</ENTITLEMENT_NAME>''))+''</QUOTE_ENTITLEMENT>'') as entitlement_xml FROM "+str(SAQSCE)+" (nolock)a JOIN "+str(CRMTMP)+" C ON A.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND SERVICE_ID = ''Z0004'') e OUTER APPLY e.ENTITLEMENT_XML.nodes(''QUOTE_ENTITLEMENT'') as X(Y) )B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID = B.EQUIPMENT_ID  WHERE B.ENTITLEMENT_NAME=''Product Offering Coefficient'' AND ISNULL(ENTITLEMENT_VALUE_CODE,'''') <>''''  '")
							
							#Z0099
							S3 = SqlHelper.GetFirst("sp_executesql @T=N'UPDATE A SET TOTAL_COEFFICIENT= ISNULL(TOTAL_COEFFICIENT,0) + ISNULL(CONVERT(FLOAT,ENTITLEMENT_VALUE_CODE),0) FROM SAQICO_INBOUND A(NOLOCK) JOIN (SELECT distinct quote_ID,equipment_id,service_id, replace(X.Y.value(''(ENTITLEMENT_VALUE_CODE)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_VALUE_CODE,replace(X.Y.value(''(ENTITLEMENT_NAME)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_NAME FROM (SELECT quote_ID,equipment_id,service_id,CONVERT(XML,''<QUOTE_ENTITLEMENT>''+substring(entitlement_xml,charindex (''<ENTITLEMENT_ID>AGS_Z0099_VAL_POFFCO'',entitlement_xml),charindex (''Product Offering Coefficient</ENTITLEMENT_NAME>'',entitlement_xml)-charindex (''<ENTITLEMENT_ID>AGS_Z0099_VAL_POFFCO'',entitlement_xml)+len(''Product Offering Coefficient</ENTITLEMENT_NAME>''))+''</QUOTE_ENTITLEMENT>'') as entitlement_xml FROM "+str(SAQSCE)+" (nolock)a JOIN "+str(CRMTMP)+" C ON A.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND SERVICE_ID = ''Z0099'') e OUTER APPLY e.ENTITLEMENT_XML.nodes(''QUOTE_ENTITLEMENT'') as X(Y) )B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID = B.EQUIPMENT_ID  WHERE B.ENTITLEMENT_NAME=''Product Offering Coefficient'' AND ISNULL(ENTITLEMENT_VALUE_CODE,'''') <>''''  '")
							
							#Z0035
							S3 = SqlHelper.GetFirst("sp_executesql @T=N'UPDATE A SET TOTAL_COEFFICIENT= ISNULL(TOTAL_COEFFICIENT,0) + ISNULL(CONVERT(FLOAT,ENTITLEMENT_VALUE_CODE),0) FROM SAQICO_INBOUND A(NOLOCK) JOIN (SELECT distinct quote_ID,equipment_id,service_id, replace(X.Y.value(''(ENTITLEMENT_VALUE_CODE)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_VALUE_CODE,replace(X.Y.value(''(ENTITLEMENT_NAME)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_NAME FROM (SELECT quote_ID,equipment_id,service_id,CONVERT(XML,''<QUOTE_ENTITLEMENT>''+substring(entitlement_xml,charindex (''<ENTITLEMENT_ID>AGS_Z0035_VAL_POFFCO'',entitlement_xml),charindex (''Product Offering Coefficient</ENTITLEMENT_NAME>'',entitlement_xml)-charindex (''<ENTITLEMENT_ID>AGS_Z0035_VAL_POFFCO'',entitlement_xml)+len(''Product Offering Coefficient</ENTITLEMENT_NAME>''))+''</QUOTE_ENTITLEMENT>'') as entitlement_xml FROM "+str(SAQSCE)+" (nolock)a JOIN "+str(CRMTMP)+" C ON A.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND SERVICE_ID = ''Z0035'') e OUTER APPLY e.ENTITLEMENT_XML.nodes(''QUOTE_ENTITLEMENT'') as X(Y) )B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID = B.EQUIPMENT_ID  WHERE B.ENTITLEMENT_NAME=''Product Offering Coefficient'' AND ISNULL(ENTITLEMENT_VALUE_CODE,'''') <>''''  '")
							
							#Z0009
							S3 = SqlHelper.GetFirst("sp_executesql @T=N'UPDATE A SET TOTAL_COEFFICIENT= ISNULL(TOTAL_COEFFICIENT,0) + ISNULL(CONVERT(FLOAT,ENTITLEMENT_VALUE_CODE),0) FROM SAQICO_INBOUND A(NOLOCK) JOIN (SELECT distinct quote_ID,equipment_id,service_id, replace(X.Y.value(''(ENTITLEMENT_VALUE_CODE)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_VALUE_CODE,replace(X.Y.value(''(ENTITLEMENT_NAME)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_NAME FROM (SELECT quote_ID,equipment_id,service_id,CONVERT(XML,''<QUOTE_ENTITLEMENT>''+substring(entitlement_xml,charindex (''<ENTITLEMENT_ID>AGS_Z0009_VAL_POFFCO'',entitlement_xml),charindex (''Product Offering Coefficient</ENTITLEMENT_NAME>'',entitlement_xml)-charindex (''<ENTITLEMENT_ID>AGS_Z0009_VAL_POFFCO'',entitlement_xml)+len(''Product Offering Coefficient</ENTITLEMENT_NAME>''))+''</QUOTE_ENTITLEMENT>'') as entitlement_xml FROM "+str(SAQSCE)+" (nolock)a JOIN "+str(CRMTMP)+" C ON A.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND SERVICE_ID = ''Z0009'') e OUTER APPLY e.ENTITLEMENT_XML.nodes(''QUOTE_ENTITLEMENT'') as X(Y) )B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID = B.EQUIPMENT_ID  WHERE B.ENTITLEMENT_NAME=''Product Offering Coefficient'' AND ISNULL(ENTITLEMENT_VALUE_CODE,'''') <>''''  '")

							#Greenbook Coefficient
							#Z0091
							S3 = SqlHelper.GetFirst("sp_executesql @T=N'UPDATE A SET TOTAL_COEFFICIENT= ISNULL(TOTAL_COEFFICIENT,0) + ISNULL(CONVERT(FLOAT,ENTITLEMENT_VALUE_CODE),0) FROM SAQICO_INBOUND A(NOLOCK) JOIN (SELECT distinct quote_ID,equipment_id,service_id, replace(X.Y.value(''(ENTITLEMENT_VALUE_CODE)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_VALUE_CODE,replace(X.Y.value(''(ENTITLEMENT_NAME)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_NAME FROM (SELECT quote_ID,equipment_id,service_id,CONVERT(XML,''<QUOTE_ENTITLEMENT>''+substring(entitlement_xml,charindex (''<ENTITLEMENT_ID>AGS_Z0091_VAL_GRNBCO'',entitlement_xml),charindex (''Greenbook Coefficient</ENTITLEMENT_NAME>'',entitlement_xml)-charindex (''<ENTITLEMENT_ID>AGS_Z0091_VAL_GRNBCO'',entitlement_xml)+len(''Greenbook Coefficient</ENTITLEMENT_NAME>''))+''</QUOTE_ENTITLEMENT>'') as entitlement_xml FROM "+str(SAQSCE)+" (nolock)a JOIN "+str(CRMTMP)+" C ON A.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND SERVICE_ID = ''Z0091'') e OUTER APPLY e.ENTITLEMENT_XML.nodes(''QUOTE_ENTITLEMENT'') as X(Y) )B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID = B.EQUIPMENT_ID  WHERE B.ENTITLEMENT_NAME=''Greenbook Coefficient'' AND ISNULL(ENTITLEMENT_VALUE_CODE,'''') <>''''  '")
							
							#Z0092
							S3 = SqlHelper.GetFirst("sp_executesql @T=N'UPDATE A SET TOTAL_COEFFICIENT= ISNULL(TOTAL_COEFFICIENT,0) + ISNULL(CONVERT(FLOAT,ENTITLEMENT_VALUE_CODE),0) FROM SAQICO_INBOUND A(NOLOCK) JOIN (SELECT distinct quote_ID,equipment_id,service_id, replace(X.Y.value(''(ENTITLEMENT_VALUE_CODE)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_VALUE_CODE,replace(X.Y.value(''(ENTITLEMENT_NAME)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_NAME FROM (SELECT quote_ID,equipment_id,service_id,CONVERT(XML,''<QUOTE_ENTITLEMENT>''+substring(entitlement_xml,charindex (''<ENTITLEMENT_ID>AGS_Z0092_VAL_GRNBCO'',entitlement_xml),charindex (''Greenbook Coefficient</ENTITLEMENT_NAME>'',entitlement_xml)-charindex (''<ENTITLEMENT_ID>AGS_Z0092_VAL_GRNBCO'',entitlement_xml)+len(''Greenbook Coefficient</ENTITLEMENT_NAME>''))+''</QUOTE_ENTITLEMENT>'') as entitlement_xml FROM "+str(SAQSCE)+" (nolock)a JOIN "+str(CRMTMP)+" C ON A.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND SERVICE_ID = ''Z0092'') e OUTER APPLY e.ENTITLEMENT_XML.nodes(''QUOTE_ENTITLEMENT'') as X(Y) )B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID = B.EQUIPMENT_ID  WHERE B.ENTITLEMENT_NAME=''Greenbook Coefficient'' AND ISNULL(ENTITLEMENT_VALUE_CODE,'''') <>''''  '")
							
							#Z0004
							S3 = SqlHelper.GetFirst("sp_executesql @T=N'UPDATE A SET TOTAL_COEFFICIENT= ISNULL(TOTAL_COEFFICIENT,0) + ISNULL(CONVERT(FLOAT,ENTITLEMENT_VALUE_CODE),0) FROM SAQICO_INBOUND A(NOLOCK) JOIN (SELECT distinct quote_ID,equipment_id,service_id, replace(X.Y.value(''(ENTITLEMENT_VALUE_CODE)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_VALUE_CODE,replace(X.Y.value(''(ENTITLEMENT_NAME)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_NAME FROM (SELECT quote_ID,equipment_id,service_id,CONVERT(XML,''<QUOTE_ENTITLEMENT>''+substring(entitlement_xml,charindex (''<ENTITLEMENT_ID>AGS_Z0004_VAL_GRNBCO'',entitlement_xml),charindex (''Greenbook Coefficient</ENTITLEMENT_NAME>'',entitlement_xml)-charindex (''<ENTITLEMENT_ID>AGS_Z0004_VAL_GRNBCO'',entitlement_xml)+len(''Greenbook Coefficient</ENTITLEMENT_NAME>''))+''</QUOTE_ENTITLEMENT>'') as entitlement_xml FROM "+str(SAQSCE)+" (nolock)a JOIN "+str(CRMTMP)+" C ON A.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND SERVICE_ID = ''Z0004'') e OUTER APPLY e.ENTITLEMENT_XML.nodes(''QUOTE_ENTITLEMENT'') as X(Y) )B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID = B.EQUIPMENT_ID  WHERE B.ENTITLEMENT_NAME=''Greenbook Coefficient'' AND ISNULL(ENTITLEMENT_VALUE_CODE,'''') <>''''  '")
							
							#Z0099
							S3 = SqlHelper.GetFirst("sp_executesql @T=N'UPDATE A SET TOTAL_COEFFICIENT= ISNULL(TOTAL_COEFFICIENT,0) + ISNULL(CONVERT(FLOAT,ENTITLEMENT_VALUE_CODE),0) FROM SAQICO_INBOUND A(NOLOCK) JOIN (SELECT distinct quote_ID,equipment_id,service_id, replace(X.Y.value(''(ENTITLEMENT_VALUE_CODE)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_VALUE_CODE,replace(X.Y.value(''(ENTITLEMENT_NAME)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_NAME FROM (SELECT quote_ID,equipment_id,service_id,CONVERT(XML,''<QUOTE_ENTITLEMENT>''+substring(entitlement_xml,charindex (''<ENTITLEMENT_ID>AGS_Z0099_VAL_GRNBCO'',entitlement_xml),charindex (''Greenbook Coefficient</ENTITLEMENT_NAME>'',entitlement_xml)-charindex (''<ENTITLEMENT_ID>AGS_Z0099_VAL_GRNBCO'',entitlement_xml)+len(''Greenbook Coefficient</ENTITLEMENT_NAME>''))+''</QUOTE_ENTITLEMENT>'') as entitlement_xml FROM "+str(SAQSCE)+" (nolock)a JOIN "+str(CRMTMP)+" C ON A.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND SERVICE_ID = ''Z0099'') e OUTER APPLY e.ENTITLEMENT_XML.nodes(''QUOTE_ENTITLEMENT'') as X(Y) )B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID = B.EQUIPMENT_ID  WHERE B.ENTITLEMENT_NAME=''Greenbook Coefficient'' AND ISNULL(ENTITLEMENT_VALUE_CODE,'''') <>''''  '")
							
							#Z0035
							S3 = SqlHelper.GetFirst("sp_executesql @T=N'UPDATE A SET TOTAL_COEFFICIENT= ISNULL(TOTAL_COEFFICIENT,0) + ISNULL(CONVERT(FLOAT,ENTITLEMENT_VALUE_CODE),0) FROM SAQICO_INBOUND A(NOLOCK) JOIN (SELECT distinct quote_ID,equipment_id,service_id, replace(X.Y.value(''(ENTITLEMENT_VALUE_CODE)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_VALUE_CODE,replace(X.Y.value(''(ENTITLEMENT_NAME)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_NAME FROM (SELECT quote_ID,equipment_id,service_id,CONVERT(XML,''<QUOTE_ENTITLEMENT>''+substring(entitlement_xml,charindex (''<ENTITLEMENT_ID>AGS_Z0035_VAL_GRNBCO'',entitlement_xml),charindex (''Greenbook Coefficient</ENTITLEMENT_NAME>'',entitlement_xml)-charindex (''<ENTITLEMENT_ID>AGS_Z0035_VAL_GRNBCO'',entitlement_xml)+len(''Greenbook Coefficient</ENTITLEMENT_NAME>''))+''</QUOTE_ENTITLEMENT>'') as entitlement_xml FROM "+str(SAQSCE)+" (nolock)a JOIN "+str(CRMTMP)+" C ON A.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND SERVICE_ID = ''Z0035'') e OUTER APPLY e.ENTITLEMENT_XML.nodes(''QUOTE_ENTITLEMENT'') as X(Y) )B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID = B.EQUIPMENT_ID  WHERE B.ENTITLEMENT_NAME=''Greenbook Coefficient'' AND ISNULL(ENTITLEMENT_VALUE_CODE,'''') <>''''  '")
							
							#Z0009
							S3 = SqlHelper.GetFirst("sp_executesql @T=N'UPDATE A SET TOTAL_COEFFICIENT= ISNULL(TOTAL_COEFFICIENT,0) + ISNULL(CONVERT(FLOAT,ENTITLEMENT_VALUE_CODE),0) FROM SAQICO_INBOUND A(NOLOCK) JOIN (SELECT distinct quote_ID,equipment_id,service_id, replace(X.Y.value(''(ENTITLEMENT_VALUE_CODE)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_VALUE_CODE,replace(X.Y.value(''(ENTITLEMENT_NAME)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_NAME FROM (SELECT quote_ID,equipment_id,service_id,CONVERT(XML,''<QUOTE_ENTITLEMENT>''+substring(entitlement_xml,charindex (''<ENTITLEMENT_ID>AGS_Z0009_VAL_GRNBCO'',entitlement_xml),charindex (''Greenbook Coefficient</ENTITLEMENT_NAME>'',entitlement_xml)-charindex (''<ENTITLEMENT_ID>AGS_Z0009_VAL_GRNBCO'',entitlement_xml)+len(''Greenbook Coefficient</ENTITLEMENT_NAME>''))+''</QUOTE_ENTITLEMENT>'') as entitlement_xml FROM "+str(SAQSCE)+" (nolock)a JOIN "+str(CRMTMP)+" C ON A.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND SERVICE_ID = ''Z0009'') e OUTER APPLY e.ENTITLEMENT_XML.nodes(''QUOTE_ENTITLEMENT'') as X(Y) )B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID = B.EQUIPMENT_ID  WHERE B.ENTITLEMENT_NAME=''Greenbook Coefficient'' AND ISNULL(ENTITLEMENT_VALUE_CODE,'''') <>''''  '")

							#Uptime Improvement Coefficient
							#Z0091
							S3 = SqlHelper.GetFirst("sp_executesql @T=N'UPDATE A SET TOTAL_COEFFICIENT= ISNULL(TOTAL_COEFFICIENT,0) + ISNULL(CONVERT(FLOAT,ENTITLEMENT_VALUE_CODE),0) FROM SAQICO_INBOUND A(NOLOCK) JOIN (SELECT distinct quote_ID,equipment_id,service_id, replace(X.Y.value(''(ENTITLEMENT_VALUE_CODE)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_VALUE_CODE,replace(X.Y.value(''(ENTITLEMENT_NAME)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_NAME FROM (SELECT quote_ID,equipment_id,service_id,CONVERT(XML,''<QUOTE_ENTITLEMENT>''+substring(entitlement_xml,charindex (''<ENTITLEMENT_ID>AGS_Z0091_VAL_UPIMCO'',entitlement_xml),charindex (''Uptime Improvement Coefficient</ENTITLEMENT_NAME>'',entitlement_xml)-charindex (''<ENTITLEMENT_ID>AGS_Z0091_VAL_UPIMCO'',entitlement_xml)+len(''Uptime Improvement Coefficient</ENTITLEMENT_NAME>''))+''</QUOTE_ENTITLEMENT>'') as entitlement_xml FROM "+str(SAQSCE)+" (nolock)a JOIN "+str(CRMTMP)+" C ON A.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND SERVICE_ID = ''Z0091'') e OUTER APPLY e.ENTITLEMENT_XML.nodes(''QUOTE_ENTITLEMENT'') as X(Y) )B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID = B.EQUIPMENT_ID  WHERE B.ENTITLEMENT_NAME=''Uptime Improvement Coefficient'' AND ISNULL(ENTITLEMENT_VALUE_CODE,'''') <>''''  '")
							
							#Z0092
							S3 = SqlHelper.GetFirst("sp_executesql @T=N'UPDATE A SET TOTAL_COEFFICIENT= ISNULL(TOTAL_COEFFICIENT,0) + ISNULL(CONVERT(FLOAT,ENTITLEMENT_VALUE_CODE),0) FROM SAQICO_INBOUND A(NOLOCK) JOIN (SELECT distinct quote_ID,equipment_id,service_id, replace(X.Y.value(''(ENTITLEMENT_VALUE_CODE)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_VALUE_CODE,replace(X.Y.value(''(ENTITLEMENT_NAME)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_NAME FROM (SELECT quote_ID,equipment_id,service_id,CONVERT(XML,''<QUOTE_ENTITLEMENT>''+substring(entitlement_xml,charindex (''<ENTITLEMENT_ID>AGS_Z0092_VAL_UPIMCO'',entitlement_xml),charindex (''Uptime Improvement Coefficient</ENTITLEMENT_NAME>'',entitlement_xml)-charindex (''<ENTITLEMENT_ID>AGS_Z0092_VAL_UPIMCO'',entitlement_xml)+len(''Uptime Improvement Coefficient</ENTITLEMENT_NAME>''))+''</QUOTE_ENTITLEMENT>'') as entitlement_xml FROM "+str(SAQSCE)+" (nolock)a JOIN "+str(CRMTMP)+" C ON A.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND SERVICE_ID = ''Z0092'') e OUTER APPLY e.ENTITLEMENT_XML.nodes(''QUOTE_ENTITLEMENT'') as X(Y) )B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID = B.EQUIPMENT_ID  WHERE B.ENTITLEMENT_NAME=''Uptime Improvement Coefficient'' AND ISNULL(ENTITLEMENT_VALUE_CODE,'''') <>''''  '")
							
							#Z0004
							S3 = SqlHelper.GetFirst("sp_executesql @T=N'UPDATE A SET TOTAL_COEFFICIENT= ISNULL(TOTAL_COEFFICIENT,0) + ISNULL(CONVERT(FLOAT,ENTITLEMENT_VALUE_CODE),0) FROM SAQICO_INBOUND A(NOLOCK) JOIN (SELECT distinct quote_ID,equipment_id,service_id, replace(X.Y.value(''(ENTITLEMENT_VALUE_CODE)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_VALUE_CODE,replace(X.Y.value(''(ENTITLEMENT_NAME)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_NAME FROM (SELECT quote_ID,equipment_id,service_id,CONVERT(XML,''<QUOTE_ENTITLEMENT>''+substring(entitlement_xml,charindex (''<ENTITLEMENT_ID>AGS_Z0004_VAL_UPIMCO'',entitlement_xml),charindex (''Uptime Improvement Coefficient</ENTITLEMENT_NAME>'',entitlement_xml)-charindex (''<ENTITLEMENT_ID>AGS_Z0004_VAL_UPIMCO'',entitlement_xml)+len(''Uptime Improvement Coefficient</ENTITLEMENT_NAME>''))+''</QUOTE_ENTITLEMENT>'') as entitlement_xml FROM "+str(SAQSCE)+" (nolock)a JOIN "+str(CRMTMP)+" C ON A.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND SERVICE_ID = ''Z0004'') e OUTER APPLY e.ENTITLEMENT_XML.nodes(''QUOTE_ENTITLEMENT'') as X(Y) )B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID = B.EQUIPMENT_ID  WHERE B.ENTITLEMENT_NAME=''Uptime Improvement Coefficient'' AND ISNULL(ENTITLEMENT_VALUE_CODE,'''') <>''''  '")
							
							#Z0099
							S3 = SqlHelper.GetFirst("sp_executesql @T=N'UPDATE A SET TOTAL_COEFFICIENT= ISNULL(TOTAL_COEFFICIENT,0) + ISNULL(CONVERT(FLOAT,ENTITLEMENT_VALUE_CODE),0) FROM SAQICO_INBOUND A(NOLOCK) JOIN (SELECT distinct quote_ID,equipment_id,service_id, replace(X.Y.value(''(ENTITLEMENT_VALUE_CODE)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_VALUE_CODE,replace(X.Y.value(''(ENTITLEMENT_NAME)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_NAME FROM (SELECT quote_ID,equipment_id,service_id,CONVERT(XML,''<QUOTE_ENTITLEMENT>''+substring(entitlement_xml,charindex (''<ENTITLEMENT_ID>AGS_Z0099_VAL_UPIMCO'',entitlement_xml),charindex (''Uptime Improvement Coefficient</ENTITLEMENT_NAME>'',entitlement_xml)-charindex (''<ENTITLEMENT_ID>AGS_Z0099_VAL_UPIMCO'',entitlement_xml)+len(''Uptime Improvement Coefficient</ENTITLEMENT_NAME>''))+''</QUOTE_ENTITLEMENT>'') as entitlement_xml FROM "+str(SAQSCE)+" (nolock)a JOIN "+str(CRMTMP)+" C ON A.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND SERVICE_ID = ''Z0099'') e OUTER APPLY e.ENTITLEMENT_XML.nodes(''QUOTE_ENTITLEMENT'') as X(Y) )B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID = B.EQUIPMENT_ID  WHERE B.ENTITLEMENT_NAME=''Uptime Improvement Coefficient'' AND ISNULL(ENTITLEMENT_VALUE_CODE,'''') <>''''  '")
							
							#Z0035
							S3 = SqlHelper.GetFirst("sp_executesql @T=N'UPDATE A SET TOTAL_COEFFICIENT= ISNULL(TOTAL_COEFFICIENT,0) + ISNULL(CONVERT(FLOAT,ENTITLEMENT_VALUE_CODE),0) FROM SAQICO_INBOUND A(NOLOCK) JOIN (SELECT distinct quote_ID,equipment_id,service_id, replace(X.Y.value(''(ENTITLEMENT_VALUE_CODE)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_VALUE_CODE,replace(X.Y.value(''(ENTITLEMENT_NAME)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_NAME FROM (SELECT quote_ID,equipment_id,service_id,CONVERT(XML,''<QUOTE_ENTITLEMENT>''+substring(entitlement_xml,charindex (''<ENTITLEMENT_ID>AGS_Z0035_VAL_UPIMCO'',entitlement_xml),charindex (''Uptime Improvement Coefficient</ENTITLEMENT_NAME>'',entitlement_xml)-charindex (''<ENTITLEMENT_ID>AGS_Z0035_VAL_UPIMCO'',entitlement_xml)+len(''Uptime Improvement Coefficient</ENTITLEMENT_NAME>''))+''</QUOTE_ENTITLEMENT>'') as entitlement_xml FROM "+str(SAQSCE)+" (nolock)a JOIN "+str(CRMTMP)+" C ON A.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND SERVICE_ID = ''Z0035'') e OUTER APPLY e.ENTITLEMENT_XML.nodes(''QUOTE_ENTITLEMENT'') as X(Y) )B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID = B.EQUIPMENT_ID  WHERE B.ENTITLEMENT_NAME=''Uptime Improvement Coefficient'' AND ISNULL(ENTITLEMENT_VALUE_CODE,'''') <>''''  '")
							
							#Z0009
							S3 = SqlHelper.GetFirst("sp_executesql @T=N'UPDATE A SET TOTAL_COEFFICIENT= ISNULL(TOTAL_COEFFICIENT,0) + ISNULL(CONVERT(FLOAT,ENTITLEMENT_VALUE_CODE),0) FROM SAQICO_INBOUND A(NOLOCK) JOIN (SELECT distinct quote_ID,equipment_id,service_id, replace(X.Y.value(''(ENTITLEMENT_VALUE_CODE)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_VALUE_CODE,replace(X.Y.value(''(ENTITLEMENT_NAME)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_NAME FROM (SELECT quote_ID,equipment_id,service_id,CONVERT(XML,''<QUOTE_ENTITLEMENT>''+substring(entitlement_xml,charindex (''<ENTITLEMENT_ID>AGS_Z0009_VAL_UPIMCO'',entitlement_xml),charindex (''Uptime Improvement Coefficient</ENTITLEMENT_NAME>'',entitlement_xml)-charindex (''<ENTITLEMENT_ID>AGS_Z0009_VAL_UPIMCO'',entitlement_xml)+len(''Uptime Improvement Coefficient</ENTITLEMENT_NAME>''))+''</QUOTE_ENTITLEMENT>'') as entitlement_xml FROM "+str(SAQSCE)+" (nolock)a JOIN "+str(CRMTMP)+" C ON A.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND SERVICE_ID = ''Z0009'') e OUTER APPLY e.ENTITLEMENT_XML.nodes(''QUOTE_ENTITLEMENT'') as X(Y) )B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID = B.EQUIPMENT_ID  WHERE B.ENTITLEMENT_NAME=''Uptime Improvement Coefficient'' AND ISNULL(ENTITLEMENT_VALUE_CODE,'''') <>''''  '")

							#Wafer Node Coefficient
							#Z0091
							S3 = SqlHelper.GetFirst("sp_executesql @T=N'UPDATE A SET TOTAL_COEFFICIENT= ISNULL(TOTAL_COEFFICIENT,0) + ISNULL(CONVERT(FLOAT,ENTITLEMENT_VALUE_CODE),0) FROM SAQICO_INBOUND A(NOLOCK) JOIN (SELECT distinct quote_ID,equipment_id,service_id, replace(X.Y.value(''(ENTITLEMENT_VALUE_CODE)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_VALUE_CODE,replace(X.Y.value(''(ENTITLEMENT_NAME)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_NAME FROM (SELECT quote_ID,equipment_id,service_id,CONVERT(XML,''<QUOTE_ENTITLEMENT>''+substring(entitlement_xml,charindex (''<ENTITLEMENT_ID>AGS_Z0091_VAL_WAFNCO'',entitlement_xml),charindex (''Wafer Node Coefficient</ENTITLEMENT_NAME>'',entitlement_xml)-charindex (''<ENTITLEMENT_ID>AGS_Z0091_VAL_WAFNCO'',entitlement_xml)+len(''Wafer Node Coefficient</ENTITLEMENT_NAME>''))+''</QUOTE_ENTITLEMENT>'') as entitlement_xml FROM "+str(SAQSCE)+" (nolock)a JOIN "+str(CRMTMP)+" C ON A.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND SERVICE_ID = ''Z0091'') e OUTER APPLY e.ENTITLEMENT_XML.nodes(''QUOTE_ENTITLEMENT'') as X(Y) )B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID = B.EQUIPMENT_ID  WHERE B.ENTITLEMENT_NAME=''Wafer Node Coefficient'' AND ISNULL(ENTITLEMENT_VALUE_CODE,'''') <>''''  '")
							
							#Z0092
							S3 = SqlHelper.GetFirst("sp_executesql @T=N'UPDATE A SET TOTAL_COEFFICIENT= ISNULL(TOTAL_COEFFICIENT,0) + ISNULL(CONVERT(FLOAT,ENTITLEMENT_VALUE_CODE),0) FROM SAQICO_INBOUND A(NOLOCK) JOIN (SELECT distinct quote_ID,equipment_id,service_id, replace(X.Y.value(''(ENTITLEMENT_VALUE_CODE)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_VALUE_CODE,replace(X.Y.value(''(ENTITLEMENT_NAME)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_NAME FROM (SELECT quote_ID,equipment_id,service_id,CONVERT(XML,''<QUOTE_ENTITLEMENT>''+substring(entitlement_xml,charindex (''<ENTITLEMENT_ID>AGS_Z0092_VAL_WAFNCO'',entitlement_xml),charindex (''Wafer Node Coefficient</ENTITLEMENT_NAME>'',entitlement_xml)-charindex (''<ENTITLEMENT_ID>AGS_Z0092_VAL_WAFNCO'',entitlement_xml)+len(''Wafer Node Coefficient</ENTITLEMENT_NAME>''))+''</QUOTE_ENTITLEMENT>'') as entitlement_xml FROM "+str(SAQSCE)+" (nolock)a JOIN "+str(CRMTMP)+" C ON A.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND SERVICE_ID = ''Z0092'') e OUTER APPLY e.ENTITLEMENT_XML.nodes(''QUOTE_ENTITLEMENT'') as X(Y) )B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID = B.EQUIPMENT_ID  WHERE B.ENTITLEMENT_NAME=''Wafer Node Coefficient'' AND ISNULL(ENTITLEMENT_VALUE_CODE,'''') <>''''  '")
							
							#Z0004
							S3 = SqlHelper.GetFirst("sp_executesql @T=N'UPDATE A SET TOTAL_COEFFICIENT= ISNULL(TOTAL_COEFFICIENT,0) + ISNULL(CONVERT(FLOAT,ENTITLEMENT_VALUE_CODE),0) FROM SAQICO_INBOUND A(NOLOCK) JOIN (SELECT distinct quote_ID,equipment_id,service_id, replace(X.Y.value(''(ENTITLEMENT_VALUE_CODE)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_VALUE_CODE,replace(X.Y.value(''(ENTITLEMENT_NAME)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_NAME FROM (SELECT quote_ID,equipment_id,service_id,CONVERT(XML,''<QUOTE_ENTITLEMENT>''+substring(entitlement_xml,charindex (''<ENTITLEMENT_ID>AGS_Z0004_VAL_WAFNCO'',entitlement_xml),charindex (''Wafer Node Coefficient</ENTITLEMENT_NAME>'',entitlement_xml)-charindex (''<ENTITLEMENT_ID>AGS_Z0004_VAL_WAFNCO'',entitlement_xml)+len(''Wafer Node Coefficient</ENTITLEMENT_NAME>''))+''</QUOTE_ENTITLEMENT>'') as entitlement_xml FROM "+str(SAQSCE)+" (nolock)a JOIN "+str(CRMTMP)+" C ON A.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND SERVICE_ID = ''Z0004'') e OUTER APPLY e.ENTITLEMENT_XML.nodes(''QUOTE_ENTITLEMENT'') as X(Y) )B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID = B.EQUIPMENT_ID  WHERE B.ENTITLEMENT_NAME=''Wafer Node Coefficient'' AND ISNULL(ENTITLEMENT_VALUE_CODE,'''') <>''''  '")
							
							#Z0099
							S3 = SqlHelper.GetFirst("sp_executesql @T=N'UPDATE A SET TOTAL_COEFFICIENT= ISNULL(TOTAL_COEFFICIENT,0) + ISNULL(CONVERT(FLOAT,ENTITLEMENT_VALUE_CODE),0) FROM SAQICO_INBOUND A(NOLOCK) JOIN (SELECT distinct quote_ID,equipment_id,service_id, replace(X.Y.value(''(ENTITLEMENT_VALUE_CODE)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_VALUE_CODE,replace(X.Y.value(''(ENTITLEMENT_NAME)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_NAME FROM (SELECT quote_ID,equipment_id,service_id,CONVERT(XML,''<QUOTE_ENTITLEMENT>''+substring(entitlement_xml,charindex (''<ENTITLEMENT_ID>AGS_Z0099_VAL_WAFNCO'',entitlement_xml),charindex (''Wafer Node Coefficient</ENTITLEMENT_NAME>'',entitlement_xml)-charindex (''<ENTITLEMENT_ID>AGS_Z0099_VAL_WAFNCO'',entitlement_xml)+len(''Wafer Node Coefficient</ENTITLEMENT_NAME>''))+''</QUOTE_ENTITLEMENT>'') as entitlement_xml FROM "+str(SAQSCE)+" (nolock)a JOIN "+str(CRMTMP)+" C ON A.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND SERVICE_ID = ''Z0099'') e OUTER APPLY e.ENTITLEMENT_XML.nodes(''QUOTE_ENTITLEMENT'') as X(Y) )B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID = B.EQUIPMENT_ID  WHERE B.ENTITLEMENT_NAME=''Wafer Node Coefficient'' AND ISNULL(ENTITLEMENT_VALUE_CODE,'''') <>''''  '")
							
							#Z0035
							S3 = SqlHelper.GetFirst("sp_executesql @T=N'UPDATE A SET TOTAL_COEFFICIENT= ISNULL(TOTAL_COEFFICIENT,0) + ISNULL(CONVERT(FLOAT,ENTITLEMENT_VALUE_CODE),0) FROM SAQICO_INBOUND A(NOLOCK) JOIN (SELECT distinct quote_ID,equipment_id,service_id, replace(X.Y.value(''(ENTITLEMENT_VALUE_CODE)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_VALUE_CODE,replace(X.Y.value(''(ENTITLEMENT_NAME)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_NAME FROM (SELECT quote_ID,equipment_id,service_id,CONVERT(XML,''<QUOTE_ENTITLEMENT>''+substring(entitlement_xml,charindex (''<ENTITLEMENT_ID>AGS_Z0035_VAL_WAFNCO'',entitlement_xml),charindex (''Wafer Node Coefficient</ENTITLEMENT_NAME>'',entitlement_xml)-charindex (''<ENTITLEMENT_ID>AGS_Z0035_VAL_WAFNCO'',entitlement_xml)+len(''Wafer Node Coefficient</ENTITLEMENT_NAME>''))+''</QUOTE_ENTITLEMENT>'') as entitlement_xml FROM "+str(SAQSCE)+" (nolock)a JOIN "+str(CRMTMP)+" C ON A.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND SERVICE_ID = ''Z0035'') e OUTER APPLY e.ENTITLEMENT_XML.nodes(''QUOTE_ENTITLEMENT'') as X(Y) )B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID = B.EQUIPMENT_ID  WHERE B.ENTITLEMENT_NAME=''Wafer Node Coefficient'' AND ISNULL(ENTITLEMENT_VALUE_CODE,'''') <>''''  '")
							
							#Z0009
							S3 = SqlHelper.GetFirst("sp_executesql @T=N'UPDATE A SET TOTAL_COEFFICIENT= ISNULL(TOTAL_COEFFICIENT,0) + ISNULL(CONVERT(FLOAT,ENTITLEMENT_VALUE_CODE),0) FROM SAQICO_INBOUND A(NOLOCK) JOIN (SELECT distinct quote_ID,equipment_id,service_id, replace(X.Y.value(''(ENTITLEMENT_VALUE_CODE)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_VALUE_CODE,replace(X.Y.value(''(ENTITLEMENT_NAME)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_NAME FROM (SELECT quote_ID,equipment_id,service_id,CONVERT(XML,''<QUOTE_ENTITLEMENT>''+substring(entitlement_xml,charindex (''<ENTITLEMENT_ID>AGS_Z0009_VAL_WAFNCO'',entitlement_xml),charindex (''Wafer Node Coefficient</ENTITLEMENT_NAME>'',entitlement_xml)-charindex (''<ENTITLEMENT_ID>AGS_Z0009_VAL_WAFNCO'',entitlement_xml)+len(''Wafer Node Coefficient</ENTITLEMENT_NAME>''))+''</QUOTE_ENTITLEMENT>'') as entitlement_xml FROM "+str(SAQSCE)+" (nolock)a JOIN "+str(CRMTMP)+" C ON A.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND SERVICE_ID = ''Z0009'') e OUTER APPLY e.ENTITLEMENT_XML.nodes(''QUOTE_ENTITLEMENT'') as X(Y) )B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID = B.EQUIPMENT_ID  WHERE B.ENTITLEMENT_NAME=''Wafer Node Coefficient'' AND ISNULL(ENTITLEMENT_VALUE_CODE,'''') <>''''  '")

							#Device Type Coefficient
							#Z0091
							S3 = SqlHelper.GetFirst("sp_executesql @T=N'UPDATE A SET TOTAL_COEFFICIENT= ISNULL(TOTAL_COEFFICIENT,0) + ISNULL(CONVERT(FLOAT,ENTITLEMENT_VALUE_CODE),0) FROM SAQICO_INBOUND A(NOLOCK) JOIN (SELECT distinct quote_ID,equipment_id,service_id, replace(X.Y.value(''(ENTITLEMENT_VALUE_CODE)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_VALUE_CODE,replace(X.Y.value(''(ENTITLEMENT_NAME)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_NAME FROM (SELECT quote_ID,equipment_id,service_id,CONVERT(XML,''<QUOTE_ENTITLEMENT>''+substring(entitlement_xml,charindex (''<ENTITLEMENT_ID>AGS_Z0091_VAL_DEVTCO'',entitlement_xml),charindex (''Device Type Coefficient</ENTITLEMENT_NAME>'',entitlement_xml)-charindex (''<ENTITLEMENT_ID>AGS_Z0091_VAL_DEVTCO'',entitlement_xml)+len(''Device Type Coefficient</ENTITLEMENT_NAME>''))+''</QUOTE_ENTITLEMENT>'') as entitlement_xml FROM "+str(SAQSCE)+" (nolock)a JOIN "+str(CRMTMP)+" C ON A.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND SERVICE_ID = ''Z0091'') e OUTER APPLY e.ENTITLEMENT_XML.nodes(''QUOTE_ENTITLEMENT'') as X(Y) )B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID = B.EQUIPMENT_ID  WHERE B.ENTITLEMENT_NAME=''Device Type Coefficient'' AND ISNULL(ENTITLEMENT_VALUE_CODE,'''') <>''''  '")
							
							#Z0092
							S3 = SqlHelper.GetFirst("sp_executesql @T=N'UPDATE A SET TOTAL_COEFFICIENT= ISNULL(TOTAL_COEFFICIENT,0) + ISNULL(CONVERT(FLOAT,ENTITLEMENT_VALUE_CODE),0) FROM SAQICO_INBOUND A(NOLOCK) JOIN (SELECT distinct quote_ID,equipment_id,service_id, replace(X.Y.value(''(ENTITLEMENT_VALUE_CODE)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_VALUE_CODE,replace(X.Y.value(''(ENTITLEMENT_NAME)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_NAME FROM (SELECT quote_ID,equipment_id,service_id,CONVERT(XML,''<QUOTE_ENTITLEMENT>''+substring(entitlement_xml,charindex (''<ENTITLEMENT_ID>AGS_Z0092_VAL_DEVTCO'',entitlement_xml),charindex (''Device Type Coefficient</ENTITLEMENT_NAME>'',entitlement_xml)-charindex (''<ENTITLEMENT_ID>AGS_Z0092_VAL_DEVTCO'',entitlement_xml)+len(''Device Type Coefficient</ENTITLEMENT_NAME>''))+''</QUOTE_ENTITLEMENT>'') as entitlement_xml FROM "+str(SAQSCE)+" (nolock)a JOIN "+str(CRMTMP)+" C ON A.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND SERVICE_ID = ''Z0092'') e OUTER APPLY e.ENTITLEMENT_XML.nodes(''QUOTE_ENTITLEMENT'') as X(Y) )B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID = B.EQUIPMENT_ID  WHERE B.ENTITLEMENT_NAME=''Device Type Coefficient'' AND ISNULL(ENTITLEMENT_VALUE_CODE,'''') <>''''  '")
							
							#Z0004
							S3 = SqlHelper.GetFirst("sp_executesql @T=N'UPDATE A SET TOTAL_COEFFICIENT= ISNULL(TOTAL_COEFFICIENT,0) + ISNULL(CONVERT(FLOAT,ENTITLEMENT_VALUE_CODE),0) FROM SAQICO_INBOUND A(NOLOCK) JOIN (SELECT distinct quote_ID,equipment_id,service_id, replace(X.Y.value(''(ENTITLEMENT_VALUE_CODE)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_VALUE_CODE,replace(X.Y.value(''(ENTITLEMENT_NAME)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_NAME FROM (SELECT quote_ID,equipment_id,service_id,CONVERT(XML,''<QUOTE_ENTITLEMENT>''+substring(entitlement_xml,charindex (''<ENTITLEMENT_ID>AGS_Z0004_VAL_DEVTCO'',entitlement_xml),charindex (''Device Type Coefficient</ENTITLEMENT_NAME>'',entitlement_xml)-charindex (''<ENTITLEMENT_ID>AGS_Z0004_VAL_DEVTCO'',entitlement_xml)+len(''Device Type Coefficient</ENTITLEMENT_NAME>''))+''</QUOTE_ENTITLEMENT>'') as entitlement_xml FROM "+str(SAQSCE)+" (nolock)a JOIN "+str(CRMTMP)+" C ON A.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND SERVICE_ID = ''Z0004'') e OUTER APPLY e.ENTITLEMENT_XML.nodes(''QUOTE_ENTITLEMENT'') as X(Y) )B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID = B.EQUIPMENT_ID  WHERE B.ENTITLEMENT_NAME=''Device Type Coefficient'' AND ISNULL(ENTITLEMENT_VALUE_CODE,'''') <>''''  '")
							
							#Z0099
							S3 = SqlHelper.GetFirst("sp_executesql @T=N'UPDATE A SET TOTAL_COEFFICIENT= ISNULL(TOTAL_COEFFICIENT,0) + ISNULL(CONVERT(FLOAT,ENTITLEMENT_VALUE_CODE),0) FROM SAQICO_INBOUND A(NOLOCK) JOIN (SELECT distinct quote_ID,equipment_id,service_id, replace(X.Y.value(''(ENTITLEMENT_VALUE_CODE)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_VALUE_CODE,replace(X.Y.value(''(ENTITLEMENT_NAME)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_NAME FROM (SELECT quote_ID,equipment_id,service_id,CONVERT(XML,''<QUOTE_ENTITLEMENT>''+substring(entitlement_xml,charindex (''<ENTITLEMENT_ID>AGS_Z0099_VAL_DEVTCO'',entitlement_xml),charindex (''Device Type Coefficient</ENTITLEMENT_NAME>'',entitlement_xml)-charindex (''<ENTITLEMENT_ID>AGS_Z0099_VAL_DEVTCO'',entitlement_xml)+len(''Device Type Coefficient</ENTITLEMENT_NAME>''))+''</QUOTE_ENTITLEMENT>'') as entitlement_xml FROM "+str(SAQSCE)+" (nolock)a JOIN "+str(CRMTMP)+" C ON A.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND SERVICE_ID = ''Z0099'') e OUTER APPLY e.ENTITLEMENT_XML.nodes(''QUOTE_ENTITLEMENT'') as X(Y) )B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID = B.EQUIPMENT_ID  WHERE B.ENTITLEMENT_NAME=''Device Type Coefficient'' AND ISNULL(ENTITLEMENT_VALUE_CODE,'''') <>''''  '")
							
							#Z0035
							S3 = SqlHelper.GetFirst("sp_executesql @T=N'UPDATE A SET TOTAL_COEFFICIENT= ISNULL(TOTAL_COEFFICIENT,0) + ISNULL(CONVERT(FLOAT,ENTITLEMENT_VALUE_CODE),0) FROM SAQICO_INBOUND A(NOLOCK) JOIN (SELECT distinct quote_ID,equipment_id,service_id, replace(X.Y.value(''(ENTITLEMENT_VALUE_CODE)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_VALUE_CODE,replace(X.Y.value(''(ENTITLEMENT_NAME)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_NAME FROM (SELECT quote_ID,equipment_id,service_id,CONVERT(XML,''<QUOTE_ENTITLEMENT>''+substring(entitlement_xml,charindex (''<ENTITLEMENT_ID>AGS_Z0035_VAL_DEVTCO'',entitlement_xml),charindex (''Device Type Coefficient</ENTITLEMENT_NAME>'',entitlement_xml)-charindex (''<ENTITLEMENT_ID>AGS_Z0035_VAL_DEVTCO'',entitlement_xml)+len(''Device Type Coefficient</ENTITLEMENT_NAME>''))+''</QUOTE_ENTITLEMENT>'') as entitlement_xml FROM "+str(SAQSCE)+" (nolock)a JOIN "+str(CRMTMP)+" C ON A.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND SERVICE_ID = ''Z0035'') e OUTER APPLY e.ENTITLEMENT_XML.nodes(''QUOTE_ENTITLEMENT'') as X(Y) )B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID = B.EQUIPMENT_ID  WHERE B.ENTITLEMENT_NAME=''Device Type Coefficient'' AND ISNULL(ENTITLEMENT_VALUE_CODE,'''') <>''''  '")
							
							#Z0009
							S3 = SqlHelper.GetFirst("sp_executesql @T=N'UPDATE A SET TOTAL_COEFFICIENT= ISNULL(TOTAL_COEFFICIENT,0) + ISNULL(CONVERT(FLOAT,ENTITLEMENT_VALUE_CODE),0) FROM SAQICO_INBOUND A(NOLOCK) JOIN (SELECT distinct quote_ID,equipment_id,service_id, replace(X.Y.value(''(ENTITLEMENT_VALUE_CODE)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_VALUE_CODE,replace(X.Y.value(''(ENTITLEMENT_NAME)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_NAME FROM (SELECT quote_ID,equipment_id,service_id,CONVERT(XML,''<QUOTE_ENTITLEMENT>''+substring(entitlement_xml,charindex (''<ENTITLEMENT_ID>AGS_Z0009_VAL_DEVTCO'',entitlement_xml),charindex (''Device Type Coefficient</ENTITLEMENT_NAME>'',entitlement_xml)-charindex (''<ENTITLEMENT_ID>AGS_Z0009_VAL_DEVTCO'',entitlement_xml)+len(''Device Type Coefficient</ENTITLEMENT_NAME>''))+''</QUOTE_ENTITLEMENT>'') as entitlement_xml FROM "+str(SAQSCE)+" (nolock)a JOIN "+str(CRMTMP)+" C ON A.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND SERVICE_ID = ''Z0009'') e OUTER APPLY e.ENTITLEMENT_XML.nodes(''QUOTE_ENTITLEMENT'') as X(Y) )B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID = B.EQUIPMENT_ID  WHERE B.ENTITLEMENT_NAME=''Device Type Coefficient'' AND ISNULL(ENTITLEMENT_VALUE_CODE,'''') <>''''  '")

							#CSA Tools per Fab Coefficient
							#Z0091
							S3 = SqlHelper.GetFirst("sp_executesql @T=N'UPDATE A SET TOTAL_COEFFICIENT= ISNULL(TOTAL_COEFFICIENT,0) + ISNULL(CONVERT(FLOAT,ENTITLEMENT_VALUE_CODE),0) FROM SAQICO_INBOUND A(NOLOCK) JOIN (SELECT distinct quote_ID,equipment_id,service_id, replace(X.Y.value(''(ENTITLEMENT_VALUE_CODE)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_VALUE_CODE,replace(X.Y.value(''(ENTITLEMENT_NAME)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_NAME FROM (SELECT quote_ID,equipment_id,service_id,CONVERT(XML,''<QUOTE_ENTITLEMENT>''+substring(entitlement_xml,charindex (''<ENTITLEMENT_ID>AGS_Z0091_VAL_TLSFCO'',entitlement_xml),charindex (''#CSA Tools per Fab Coefficient</ENTITLEMENT_NAME>'',entitlement_xml)-charindex (''<ENTITLEMENT_ID>AGS_Z0091_VAL_TLSFCO'',entitlement_xml)+len(''#CSA Tools per Fab Coefficient</ENTITLEMENT_NAME>''))+''</QUOTE_ENTITLEMENT>'') as entitlement_xml FROM "+str(SAQSCE)+" (nolock)a JOIN "+str(CRMTMP)+" C ON A.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND SERVICE_ID = ''Z0091'') e OUTER APPLY e.ENTITLEMENT_XML.nodes(''QUOTE_ENTITLEMENT'') as X(Y) )B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID = B.EQUIPMENT_ID  WHERE B.ENTITLEMENT_NAME=''#CSA Tools per Fab Coefficient'' AND ISNULL(ENTITLEMENT_VALUE_CODE,'''') <>''''  '")
							
							#Z0092
							S3 = SqlHelper.GetFirst("sp_executesql @T=N'UPDATE A SET TOTAL_COEFFICIENT= ISNULL(TOTAL_COEFFICIENT,0) + ISNULL(CONVERT(FLOAT,ENTITLEMENT_VALUE_CODE),0) FROM SAQICO_INBOUND A(NOLOCK) JOIN (SELECT distinct quote_ID,equipment_id,service_id, replace(X.Y.value(''(ENTITLEMENT_VALUE_CODE)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_VALUE_CODE,replace(X.Y.value(''(ENTITLEMENT_NAME)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_NAME FROM (SELECT quote_ID,equipment_id,service_id,CONVERT(XML,''<QUOTE_ENTITLEMENT>''+substring(entitlement_xml,charindex (''<ENTITLEMENT_ID>AGS_Z0092_VAL_TLSFCO'',entitlement_xml),charindex (''#CSA Tools per Fab Coefficient</ENTITLEMENT_NAME>'',entitlement_xml)-charindex (''<ENTITLEMENT_ID>AGS_Z0092_VAL_TLSFCO'',entitlement_xml)+len(''#CSA Tools per Fab Coefficient</ENTITLEMENT_NAME>''))+''</QUOTE_ENTITLEMENT>'') as entitlement_xml FROM "+str(SAQSCE)+" (nolock)a JOIN "+str(CRMTMP)+" C ON A.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND SERVICE_ID = ''Z0092'') e OUTER APPLY e.ENTITLEMENT_XML.nodes(''QUOTE_ENTITLEMENT'') as X(Y) )B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID = B.EQUIPMENT_ID  WHERE B.ENTITLEMENT_NAME=''#CSA Tools per Fab Coefficient'' AND ISNULL(ENTITLEMENT_VALUE_CODE,'''') <>''''  '")
							
							#Z0004
							S3 = SqlHelper.GetFirst("sp_executesql @T=N'UPDATE A SET TOTAL_COEFFICIENT= ISNULL(TOTAL_COEFFICIENT,0) + ISNULL(CONVERT(FLOAT,ENTITLEMENT_VALUE_CODE),0) FROM SAQICO_INBOUND A(NOLOCK) JOIN (SELECT distinct quote_ID,equipment_id,service_id, replace(X.Y.value(''(ENTITLEMENT_VALUE_CODE)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_VALUE_CODE,replace(X.Y.value(''(ENTITLEMENT_NAME)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_NAME FROM (SELECT quote_ID,equipment_id,service_id,CONVERT(XML,''<QUOTE_ENTITLEMENT>''+substring(entitlement_xml,charindex (''<ENTITLEMENT_ID>AGS_Z0004_VAL_TLSFCO'',entitlement_xml),charindex (''# CSA Tools per Fab Coefficien</ENTITLEMENT_NAME>'',entitlement_xml)-charindex (''<ENTITLEMENT_ID>AGS_Z0004_VAL_TLSFCO'',entitlement_xml)+len(''# CSA Tools per Fab Coefficien</ENTITLEMENT_NAME>''))+''</QUOTE_ENTITLEMENT>'') as entitlement_xml FROM "+str(SAQSCE)+" (nolock)a JOIN "+str(CRMTMP)+" C ON A.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND SERVICE_ID = ''Z0004'') e OUTER APPLY e.ENTITLEMENT_XML.nodes(''QUOTE_ENTITLEMENT'') as X(Y) )B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID = B.EQUIPMENT_ID  WHERE B.ENTITLEMENT_NAME=''# CSA Tools per Fab Coefficien'' AND ISNULL(ENTITLEMENT_VALUE_CODE,'''') <>''''  '")
							
							#Z0099
							S3 = SqlHelper.GetFirst("sp_executesql @T=N'UPDATE A SET TOTAL_COEFFICIENT= ISNULL(TOTAL_COEFFICIENT,0) + ISNULL(CONVERT(FLOAT,ENTITLEMENT_VALUE_CODE),0) FROM SAQICO_INBOUND A(NOLOCK) JOIN (SELECT distinct quote_ID,equipment_id,service_id, replace(X.Y.value(''(ENTITLEMENT_VALUE_CODE)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_VALUE_CODE,replace(X.Y.value(''(ENTITLEMENT_NAME)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_NAME FROM (SELECT quote_ID,equipment_id,service_id,CONVERT(XML,''<QUOTE_ENTITLEMENT>''+substring(entitlement_xml,charindex (''<ENTITLEMENT_ID>AGS_Z0099_VAL_TLSFCO'',entitlement_xml),charindex (''#CSA Tools per Fab Coefficient</ENTITLEMENT_NAME>'',entitlement_xml)-charindex (''<ENTITLEMENT_ID>AGS_Z0099_VAL_TLSFCO'',entitlement_xml)+len(''#CSA Tools per Fab Coefficient</ENTITLEMENT_NAME>''))+''</QUOTE_ENTITLEMENT>'') as entitlement_xml FROM "+str(SAQSCE)+" (nolock)a JOIN "+str(CRMTMP)+" C ON A.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND SERVICE_ID = ''Z0099'') e OUTER APPLY e.ENTITLEMENT_XML.nodes(''QUOTE_ENTITLEMENT'') as X(Y) )B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID = B.EQUIPMENT_ID  WHERE B.ENTITLEMENT_NAME=''#CSA Tools per Fab Coefficient'' AND ISNULL(ENTITLEMENT_VALUE_CODE,'''') <>''''  '")
							
							#Z0035
							S3 = SqlHelper.GetFirst("sp_executesql @T=N'UPDATE A SET TOTAL_COEFFICIENT= ISNULL(TOTAL_COEFFICIENT,0) + ISNULL(CONVERT(FLOAT,ENTITLEMENT_VALUE_CODE),0) FROM SAQICO_INBOUND A(NOLOCK) JOIN (SELECT distinct quote_ID,equipment_id,service_id, replace(X.Y.value(''(ENTITLEMENT_VALUE_CODE)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_VALUE_CODE,replace(X.Y.value(''(ENTITLEMENT_NAME)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_NAME FROM (SELECT quote_ID,equipment_id,service_id,CONVERT(XML,''<QUOTE_ENTITLEMENT>''+substring(entitlement_xml,charindex (''<ENTITLEMENT_ID>AGS_Z0035_VAL_TLSFCO'',entitlement_xml),charindex (''# CSA Tools per Fab Coefficien</ENTITLEMENT_NAME>'',entitlement_xml)-charindex (''<ENTITLEMENT_ID>AGS_Z0035_VAL_TLSFCO'',entitlement_xml)+len(''# CSA Tools per Fab Coefficien</ENTITLEMENT_NAME>''))+''</QUOTE_ENTITLEMENT>'') as entitlement_xml FROM "+str(SAQSCE)+" (nolock)a JOIN "+str(CRMTMP)+" C ON A.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND SERVICE_ID = ''Z0035'') e OUTER APPLY e.ENTITLEMENT_XML.nodes(''QUOTE_ENTITLEMENT'') as X(Y) )B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID = B.EQUIPMENT_ID  WHERE B.ENTITLEMENT_NAME=''# CSA Tools per Fab Coefficien'' AND ISNULL(ENTITLEMENT_VALUE_CODE,'''') <>''''  '")
							
							#Z0009
							S3 = SqlHelper.GetFirst("sp_executesql @T=N'UPDATE A SET TOTAL_COEFFICIENT= ISNULL(TOTAL_COEFFICIENT,0) + ISNULL(CONVERT(FLOAT,ENTITLEMENT_VALUE_CODE),0) FROM SAQICO_INBOUND A(NOLOCK) JOIN (SELECT distinct quote_ID,equipment_id,service_id, replace(X.Y.value(''(ENTITLEMENT_VALUE_CODE)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_VALUE_CODE,replace(X.Y.value(''(ENTITLEMENT_NAME)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_NAME FROM (SELECT quote_ID,equipment_id,service_id,CONVERT(XML,''<QUOTE_ENTITLEMENT>''+substring(entitlement_xml,charindex (''<ENTITLEMENT_ID>AGS_Z0009_VAL_TLSFCO'',entitlement_xml),charindex (''#CSA Tools per Fab Coefficient</ENTITLEMENT_NAME>'',entitlement_xml)-charindex (''<ENTITLEMENT_ID>AGS_Z0009_VAL_TLSFCO'',entitlement_xml)+len(''#CSA Tools per Fab Coefficient</ENTITLEMENT_NAME>''))+''</QUOTE_ENTITLEMENT>'') as entitlement_xml FROM "+str(SAQSCE)+" (nolock)a JOIN "+str(CRMTMP)+" C ON A.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND SERVICE_ID = ''Z0009'') e OUTER APPLY e.ENTITLEMENT_XML.nodes(''QUOTE_ENTITLEMENT'') as X(Y) )B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID = B.EQUIPMENT_ID  WHERE B.ENTITLEMENT_NAME=''#CSA Tools per Fab Coefficient'' AND ISNULL(ENTITLEMENT_VALUE_CODE,'''') <>''''  '")
							
							#Entitlement Roll Up
							S3 = SqlHelper.GetFirst("sp_executesql @T=N'UPDATE A SET ENTITLEMENT_XML= B.ENTITLEMENT_XML FROM SAQIEN A(NOLOCK) JOIN "+str(CRMTMP)+" ON A.EQUIPMENT_ID = EQUIPMENT_IDD JOIN "+str(SAQIEN)+" B(NOLOCK) ON A.QUOTE_ID = B.QUOTE_ID AND A.QTEREV_ID = B.QTEREV_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID = B.EQUIPMENT_ID AND A.LINE = B.LINE WHERE A.QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND A.QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"''   '")
					
							CRMTMP21 = SqlHelper.GetFirst("sp_executesql @T=N'DELETE FROM "+str(CRMTMP)+" ' ")	
							
							SAQSCE_DRP = SqlHelper.GetFirst("sp_executesql @T=N'IF EXISTS (SELECT ''X'' FROM SYS.OBJECTS WHERE NAME= ''"+str(SAQSCE)+"'' ) BEGIN DROP TABLE "+str(SAQSCE)+" END  ' ")
							
						else:
							Check_flag12=0
					
					SAQIEN_DRP = SqlHelper.GetFirst("sp_executesql @T=N'IF EXISTS (SELECT ''X'' FROM SYS.OBJECTS WHERE NAME= ''"+str(SAQIEN)+"'' ) BEGIN DROP TABLE "+str(SAQIEN)+" END  ' ")
					
					#Entitlement Roll Up
					S3 = SqlHelper.GetFirst("sp_executesql @T=N'UPDATE A SET ENTITLEMENT_XML= B.ENTITLEMENT_XML FROM SAQSCE A(NOLOCK) JOIN SAQIEN B(NOLOCK) ON A.QUOTE_ID = B.QUOTE_ID AND A.QTEREV_ID = B.QTEREV_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID = B.EQUIPMENT_ID WHERE A.QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND A.QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"''   '")
					
					#SSCM Coefficient
					S3 = SqlHelper.GetFirst("sp_executesql @T=N'UPDATE A SET TOTAL_COEFFICIENT= ISNULL(TOTAL_COEFFICIENT,0) + ISNULL(CONVERT(FLOAT,NPI_COEFFICIENT),0)+ ISNULL(CONVERT(FLOAT,SERVICECOMPLEXITY_COEFFICIENT),0) + ISNULL(CONVERT(FLOAT,CAPITALAVOIDANCE_COEFFICIENT),0) FROM SAQICO_INBOUND A(NOLOCK) WHERE QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND REVISION_ID = ''"+str(Qt_Id.REVISION_ID)+"''   '")
					
					#Total Cost Entitlement Impact
					primaryQueryItems = SqlHelper.GetFirst(
						""
						+ str(Parameter1.QUERY_CRITERIA_1)
						+ "  SAQICO SET TOTAL_COST_WSEEDSTOCK = TOTAL_COST_WSEEDSTOCK + ISNULL(ENTITLEMENT_COST_IMPACT,0) FROM SAQICO A(NOLOCK) JOIN (SELECT DISTINCT QUOTE_ID,SERVICE_ID,EQUIPMENT_ID,REVISION_ID FROM SAQICO_INBOUND(NOLOCK)  WHERE ISNULL(PROCESS_STATUS,'''')=''INPROGRESS'' AND TIMESTAMP = '"+str(timestamp_sessionid)+"' )B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID = B.EQUIPMENT_ID AND QTEREV_ID = REVISION_ID  ' ")
											
					#Model Price
					primaryQueryItems = SqlHelper.GetFirst(
						""
						+ str(Parameter1.QUERY_CRITERIA_1)
						+ "  SAQICO SET MODEL_PRICE_INGL_CURR = EXP(ISNULL(INTERCEPT,0) + (LOG(TOTAL_COST_WOSEEDSTOCK)) * ISNULL(LOG_FACTOR,1) + ISNULL(TOTAL_COEFFICIENT,0) )  FROM SAQICO (NOLOCK)A JOIN (SELECT DISTINCT QUOTE_ID,SERVICE_ID,EQUIPMENT_ID,TOTAL_COEFFICIENT,INTERCEPT,LOG_FACTOR,REVISION_ID FROM SAQICO_INBOUND(NOLOCK)  WHERE ISNULL(PROCESS_STATUS,'''')=''INPROGRESS'' AND TIMESTAMP = '"+str(timestamp_sessionid)+"' )B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID = B.EQUIPMENT_ID AND QTEREV_ID = REVISION_ID WHERE A.GREENBOOK<>''PDC'' AND ISNULL(TOTAL_COST_WOSEEDSTOCK,0)>0 AND A.SERVICE_ID NOT IN (''Z0100'',''Z0101'')  ' ")
					
					#Model Price for Z0100 / Z0101
					primaryQueryItems = SqlHelper.GetFirst(
						""
						+ str(Parameter1.QUERY_CRITERIA_1)
						+ "  SAQICO SET MODEL_PRICE_INGL_CURR = TOTAL_COST_WSEEDSTOCK / (1 - (CNSM_MARGIN_PERCENT/100)) FROM SAQICO (NOLOCK)A JOIN (SELECT DISTINCT QUOTE_ID,SERVICE_ID,EQUIPMENT_ID,REVISION_ID,LINE FROM SAQICO_INBOUND(NOLOCK)  WHERE ISNULL(PROCESS_STATUS,'''')=''INPROGRESS'' AND TIMESTAMP = '"+str(timestamp_sessionid)+"' )B ON A.QUOTE_ID = B.QUOTE_ID AND A.LINE = B.LINE AND A.EQUIPMENT_ID = B.EQUIPMENT_ID AND QTEREV_ID = REVISION_ID JOIN SAQTRV C(NOLOCK) ON A.QUOTE_ID = C.QUOTE_ID AND A.QTEREV_ID = C.QTEREV_ID LEFT JOIN SABGMR D(NOLOCK) ON A.GREENBOOK = D.GREENBOOK AND C.BLUEBOOK = D.BLUEBOOK WHERE ISNULL(TOTAL_COST_WSEEDSTOCK,0)>0 AND A.SERVICE_ID IN (''Z0100'',''Z0101'') ' ")
						
					start13 = 1
					end13 = 500

					Check_flag13 = 1
					while Check_flag13 == 1:

						table13 = SqlHelper.GetFirst(
									"SELECT DISTINCT equipment_id FROM (SELECT DISTINCT equipment_id, ROW_NUMBER()OVER(ORDER BY equipment_id) AS SNO FROM (SELECT DISTINCT equipment_id FROM SAQICO_INBOUND (NOLOCK) WHERE ISNULL(PROCESS_STATUS,'')='INPROGRESS' AND TIMESTAMP = "+str(timestamp_sessionid)+" AND SERVICE_ID NOT IN ('Z0100','Z0101') )A) A WHERE SNO>= "+str(start13)+" AND SNO<="+str(end13)+""
								)
								
						CRMTMP13 = SqlHelper.GetFirst("sp_executesql @T=N'IF NOT EXISTS (SELECT ''X'' FROM SYS.OBJECTS WHERE NAME= ''"+str(CRMTMP)+"'' ) BEGIN CREATE TABLE "+str(CRMTMP)+" (EQUIPMENT_IDD VARCHAR(100)) END  ' ")
						
						SAQIEN13 = SqlHelper.GetFirst("sp_executesql @T=N'IF EXISTS (SELECT ''X'' FROM SYS.OBJECTS WHERE NAME= ''"+str(SAQIEN)+"'' ) BEGIN DROP TABLE "+str(SAQIEN)+"  END  ' ")
						
						table_insert = SqlHelper.GetFirst(
							"sp_executesql @T=N'INSERT "+str(CRMTMP)+" SELECT DISTINCT equipment_id FROM (SELECT DISTINCT equipment_id, ROW_NUMBER()OVER(ORDER BY equipment_id) AS SNO FROM (SELECT DISTINCT equipment_id FROM SAQICO_INBOUND (NOLOCK) WHERE ISNULL(PROCESS_STATUS,'''')=''INPROGRESS'' AND TIMESTAMP = '"+str(timestamp_sessionid)+"' AND SERVICE_ID NOT IN (''Z0100'',''Z0101'') )A ) A WHERE SNO>= "+str(start13)+" AND SNO<="+str(end13)+"  '")
						
						table_insert = SqlHelper.GetFirst(
							"sp_executesql @T=N'SELECT * INTO "+str(SAQIEN)+" FROM SAQSCE(NOLOCK) JOIN "+str(CRMTMP)+"  ON EQUIPMENT_ID = EQUIPMENT_IDD  WHERE QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"''  '")
						
						start13 = start13 + 500
						end13 = end13 + 500

						if str(table13) != "None":
						
						
							#Contract Coverage + Model Price 
							#Z0091
							S3 = SqlHelper.GetFirst("sp_executesql @T=N'UPDATE A SET MODEL_PRICE_INGL_CURR = MODEL_PRICE_INGL_CURR * (1 + ISNULL(CONVERT(FLOAT,ENTITLEMENT_VALUE_CODE),0) ) FROM SAQICO A(NOLOCK) JOIN (SELECT distinct quote_ID,equipment_id,service_id,QTEREV_ID, replace(X.Y.value(''(ENTITLEMENT_VALUE_CODE)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_VALUE_CODE,replace(X.Y.value(''(ENTITLEMENT_DESCRIPTION)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_DESCRIPTION FROM (SELECT quote_ID,equipment_id,service_id,QTEREV_ID,CONVERT(XML,REPLACE(''<QUOTE_ENTITLEMENT>''+substring(entitlement_xml,charindex (''<ENTITLEMENT_ID>AGS_Z0091_VAL_CCRTCO'',entitlement_xml),charindex (''Contract Coverage & Response Time Coefficient</ENTITLEMENT_DESCRIPTION>'',entitlement_xml)-charindex (''<ENTITLEMENT_ID>AGS_Z0091_VAL_CCRTCO'',entitlement_xml)+len(''Contract Coverage & Response Time Coefficient</ENTITLEMENT_DESCRIPTION>''))+''</QUOTE_ENTITLEMENT>'',''Contract Coverage & Response Time Coefficient'',''Contract Cov'')) as entitlement_xml FROM SAQSCE (nolock)a JOIN "+str(CRMTMP)+" C ON A.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND SERVICE_ID = ''Z0091'' AND ENTITLEMENT_XML LIKE ''%Contract Coverage & Response Time Coefficient%'' ) e OUTER APPLY e.ENTITLEMENT_XML.nodes(''QUOTE_ENTITLEMENT'') as X(Y) )B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID = B.EQUIPMENT_ID AND A.QTEREV_ID = B.QTEREV_ID  WHERE B.ENTITLEMENT_DESCRIPTION=''Contract Cov'' AND ISNULL(ENTITLEMENT_VALUE_CODE,'''') <>''''  '")
							
							#Z0092
							S3 = SqlHelper.GetFirst("sp_executesql @T=N'UPDATE A SET MODEL_PRICE_INGL_CURR = MODEL_PRICE_INGL_CURR * (1 + ISNULL(CONVERT(FLOAT,ENTITLEMENT_VALUE_CODE),0) ) FROM SAQICO A(NOLOCK) JOIN (SELECT distinct quote_ID,equipment_id,service_id,QTEREV_ID, replace(X.Y.value(''(ENTITLEMENT_VALUE_CODE)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_VALUE_CODE,replace(X.Y.value(''(ENTITLEMENT_DESCRIPTION)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_DESCRIPTION FROM (SELECT quote_ID,equipment_id,service_id,QTEREV_ID,CONVERT(XML,REPLACE(''<QUOTE_ENTITLEMENT>''+substring(entitlement_xml,charindex (''<ENTITLEMENT_ID>AGS_Z0092_VAL_CCRTCO'',entitlement_xml),charindex (''Contract Coverage & Response Time Coefficient</ENTITLEMENT_DESCRIPTION>'',entitlement_xml)-charindex (''<ENTITLEMENT_ID>AGS_Z0092_VAL_CCRTCO'',entitlement_xml)+len(''Contract Coverage & Response Time Coefficient</ENTITLEMENT_DESCRIPTION>''))+''</QUOTE_ENTITLEMENT>'',''Contract Coverage & Response Time Coefficient'',''Contract Cov'')) as entitlement_xml FROM SAQSCE (nolock)a JOIN "+str(CRMTMP)+" C ON A.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND SERVICE_ID = ''Z0092'' AND ENTITLEMENT_XML LIKE ''%%Contract Coverage & Response Time Coefficient%%'' ) e OUTER APPLY e.ENTITLEMENT_XML.nodes(''QUOTE_ENTITLEMENT'') as X(Y) )B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID = B.EQUIPMENT_ID AND A.QTEREV_ID = B.QTEREV_ID  WHERE B.ENTITLEMENT_DESCRIPTION=''Contract Cov'' AND ISNULL(ENTITLEMENT_VALUE_CODE,'''') <>''''  '")
							
							#Z0004
							S3 = SqlHelper.GetFirst("sp_executesql @T=N'UPDATE A SET MODEL_PRICE_INGL_CURR = MODEL_PRICE_INGL_CURR * (1 + ISNULL(CONVERT(FLOAT,ENTITLEMENT_VALUE_CODE),0) ) FROM SAQICO A(NOLOCK) JOIN (SELECT distinct quote_ID,equipment_id,service_id,QTEREV_ID, replace(X.Y.value(''(ENTITLEMENT_VALUE_CODE)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_VALUE_CODE,replace(X.Y.value(''(ENTITLEMENT_DESCRIPTION)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_DESCRIPTION FROM (SELECT quote_ID,equipment_id,service_id,QTEREV_ID,CONVERT(XML,REPLACE(''<QUOTE_ENTITLEMENT>''+substring(entitlement_xml,charindex (''<ENTITLEMENT_ID>AGS_Z0004_VAL_CCRTCO'',entitlement_xml),charindex (''Contract Coverage & Response Time Coefficient</ENTITLEMENT_DESCRIPTION>'',entitlement_xml)-charindex (''<ENTITLEMENT_ID>AGS_Z0004_VAL_CCRTCO'',entitlement_xml)+len(''Contract Coverage & Response Time Coefficient</ENTITLEMENT_DESCRIPTION>''))+''</QUOTE_ENTITLEMENT>'',''Contract Coverage & Response Time Coefficient'',''Contract Cov'')) as entitlement_xml FROM SAQSCE (nolock)a JOIN "+str(CRMTMP)+" C ON A.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND SERVICE_ID = ''Z0004'' AND ENTITLEMENT_XML LIKE ''%%Contract Coverage & Response Time Coefficient%%'' ) e OUTER APPLY e.ENTITLEMENT_XML.nodes(''QUOTE_ENTITLEMENT'') as X(Y) )B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID = B.EQUIPMENT_ID AND A.QTEREV_ID = B.QTEREV_ID  WHERE B.ENTITLEMENT_DESCRIPTION=''Contract Cov'' AND ISNULL(ENTITLEMENT_VALUE_CODE,'''') <>''''  '")
							
							#Z0099
							S3 = SqlHelper.GetFirst("sp_executesql @T=N'UPDATE A SET MODEL_PRICE_INGL_CURR = MODEL_PRICE_INGL_CURR * (1 + ISNULL(CONVERT(FLOAT,ENTITLEMENT_VALUE_CODE),0) ) FROM SAQICO A(NOLOCK) JOIN (SELECT distinct quote_ID,equipment_id,service_id,QTEREV_ID, replace(X.Y.value(''(ENTITLEMENT_VALUE_CODE)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_VALUE_CODE,replace(X.Y.value(''(ENTITLEMENT_DESCRIPTION)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_DESCRIPTION FROM (SELECT quote_ID,equipment_id,service_id,QTEREV_ID,CONVERT(XML,REPLACE(''<QUOTE_ENTITLEMENT>''+substring(entitlement_xml,charindex (''<ENTITLEMENT_ID>AGS_Z0099_VAL_CCRTCO'',entitlement_xml),charindex (''Contract Coverage & Response Time Coefficient</ENTITLEMENT_DESCRIPTION>'',entitlement_xml)-charindex (''<ENTITLEMENT_ID>AGS_Z0099_VAL_CCRTCO'',entitlement_xml)+len(''Contract Coverage & Response Time Coefficient</ENTITLEMENT_DESCRIPTION>''))+''</QUOTE_ENTITLEMENT>'',''Contract Coverage & Response Time Coefficient'',''Contract Cov'')) as entitlement_xml FROM SAQSCE (nolock)a JOIN "+str(CRMTMP)+" C ON A.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE A.QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND A.QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND SERVICE_ID = ''Z0099'' AND ENTITLEMENT_XML LIKE ''%%Contract Coverage & Response Time Coefficient%%'' ) e OUTER APPLY e.ENTITLEMENT_XML.nodes(''QUOTE_ENTITLEMENT'') as X(Y) )B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID = B.EQUIPMENT_ID AND A.QTEREV_ID = B.QTEREV_ID  WHERE B.ENTITLEMENT_DESCRIPTION=''Contract Cov'' AND ISNULL(ENTITLEMENT_VALUE_CODE,'''') <>''''  '")
							
							#Z0035
							S3 = SqlHelper.GetFirst("sp_executesql @T=N'UPDATE A SET MODEL_PRICE_INGL_CURR = MODEL_PRICE_INGL_CURR * (1 + ISNULL(CONVERT(FLOAT,ENTITLEMENT_VALUE_CODE),0) ) FROM SAQICO A(NOLOCK) JOIN (SELECT distinct quote_ID,equipment_id,service_id,QTEREV_ID, replace(X.Y.value(''(ENTITLEMENT_VALUE_CODE)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_VALUE_CODE,replace(X.Y.value(''(ENTITLEMENT_DESCRIPTION)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_DESCRIPTION FROM (SELECT quote_ID,equipment_id,service_id,QTEREV_ID,CONVERT(XML,REPLACE(''<QUOTE_ENTITLEMENT>''+substring(entitlement_xml,charindex (''<ENTITLEMENT_ID>AGS_Z0035_VAL_CCRTCO'',entitlement_xml),charindex (''Contract Coverage & Response Time Coefficient</ENTITLEMENT_DESCRIPTION>'',entitlement_xml)-charindex (''<ENTITLEMENT_ID>AGS_Z0035_VAL_CCRTCO'',entitlement_xml)+len(''Contract Coverage & Response Time Coefficient</ENTITLEMENT_DESCRIPTION>''))+''</QUOTE_ENTITLEMENT>'',''Contract Coverage & Response Time Coefficient'',''Contract Cov'')) as entitlement_xml FROM SAQSCE (nolock)a JOIN "+str(CRMTMP)+" C ON A.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE A.QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND A.QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND SERVICE_ID = ''Z0035'' AND ENTITLEMENT_XML LIKE ''%%Contract Coverage & Response Time Coefficient%%'' ) e OUTER APPLY e.ENTITLEMENT_XML.nodes(''QUOTE_ENTITLEMENT'') as X(Y) )B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID = B.EQUIPMENT_ID AND A.QTEREV_ID = B.QTEREV_ID  WHERE B.ENTITLEMENT_DESCRIPTION=''Contract Cov'' AND ISNULL(ENTITLEMENT_VALUE_CODE,'''') <>''''  '")
							
							#Z0009
							S3 = SqlHelper.GetFirst("sp_executesql @T=N'UPDATE A SET MODEL_PRICE_INGL_CURR = MODEL_PRICE_INGL_CURR * (1 + ISNULL(CONVERT(FLOAT,ENTITLEMENT_VALUE_CODE),0) ) FROM SAQICO A(NOLOCK) JOIN (SELECT distinct quote_ID,equipment_id,service_id,QTEREV_ID, replace(X.Y.value(''(ENTITLEMENT_VALUE_CODE)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_VALUE_CODE,replace(X.Y.value(''(ENTITLEMENT_DESCRIPTION)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_DESCRIPTION FROM (SELECT quote_ID,equipment_id,service_id,QTEREV_ID,CONVERT(XML,REPLACE(''<QUOTE_ENTITLEMENT>''+substring(entitlement_xml,charindex (''<ENTITLEMENT_ID>AGS_Z0009_VAL_CCRTCO'',entitlement_xml),charindex (''Contract Coverage & Response Time Coefficient</ENTITLEMENT_DESCRIPTION>'',entitlement_xml)-charindex (''<ENTITLEMENT_ID>AGS_Z0009_VAL_CCRTCO'',entitlement_xml)+len(''Contract Coverage & Response Time Coefficient</ENTITLEMENT_DESCRIPTION>''))+''</QUOTE_ENTITLEMENT>'',''Contract Coverage & Response Time Coefficient'',''Contract Cov'')) as entitlement_xml FROM SAQSCE (nolock)a JOIN "+str(CRMTMP)+" C ON A.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE A.QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND A.QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND SERVICE_ID = ''Z0009'' AND ENTITLEMENT_XML LIKE ''%Contract Coverage & Response Time Coefficient%'' ) e OUTER APPLY e.ENTITLEMENT_XML.nodes(''QUOTE_ENTITLEMENT'') as X(Y) )B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID = B.EQUIPMENT_ID AND A.QTEREV_ID = B.QTEREV_ID  WHERE B.ENTITLEMENT_DESCRIPTION=''Contract Cov'' AND ISNULL(ENTITLEMENT_VALUE_CODE,'''') <>''''  '")
						
							#Head Break In
							#Z0091
							S3 = SqlHelper.GetFirst("sp_executesql @T=N'UPDATE A SET TOTAL_COST_WSEEDSTOCK = TOTAL_COST_WSEEDSTOCK + (ISNULL(CONVERT(FLOAT,C.FACTOR_TXTVAR),0) * ISNULL(HEAD_REBUILD_QTY,0) )  FROM SAQICO A(NOLOCK) JOIN (SELECT distinct quote_ID,equipment_id,service_id,QTEREV_ID, replace(X.Y.value(''(ENTITLEMENT_VALUE_CODE)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_VALUE_CODE,replace(X.Y.value(''(ENTITLEMENT_NAME)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_NAME FROM (SELECT A.quote_ID,A.equipment_id,A.service_id,A.QTEREV_ID,CONVERT(XML,''<QUOTE_ENTITLEMENT>''+substring(entitlement_xml,charindex (''<ENTITLEMENT_ID>AGS_Z0091_STT_HDBRIN'',entitlement_xml),charindex (''Head break-in</ENTITLEMENT_NAME>'',entitlement_xml)-charindex (''<ENTITLEMENT_ID>AGS_Z0091_STT_HDBRIN'',entitlement_xml)+len(''Head break-in</ENTITLEMENT_NAME>''))+''</QUOTE_ENTITLEMENT>'') as entitlement_xml FROM "+str(SAQIEN)+"  (nolock)A JOIN "+str(CRMTMP)+" C ON A.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE A.QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND A.QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND A.SERVICE_ID = ''Z0091'' ) e OUTER APPLY e.ENTITLEMENT_XML.nodes(''QUOTE_ENTITLEMENT'') as X(Y) )B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID = B.EQUIPMENT_ID AND A.QTEREV_ID = B.QTEREV_ID JOIN MAEQUP (NOLOCK) ON A.EQUIPMENT_ID  = MAEQUP.EQUIPMENT_ID JOIN PRCFVA C(NOLOCK) ON MAEQUP.SUBSTRATE_SIZE_GROUP = C.FACTOR_VARIABLE_ID WHERE B.ENTITLEMENT_NAME=''Head break-in'' AND ISNULL(B.ENTITLEMENT_VALUE_CODE,'''') = ''002'' AND C.FACTOR_ID  = ''HBWFCT''  '")
							
							S3 = SqlHelper.GetFirst("sp_executesql @T=N'UPDATE A SET MODEL_PRICE_INGL_CURR = MODEL_PRICE_INGL_CURR + (ISNULL(CONVERT(FLOAT,C.FACTOR_TXTVAR),0) * ISNULL(HEAD_REBUILD_QTY,0))   FROM SAQICO A(NOLOCK) JOIN (SELECT distinct quote_ID,equipment_id,service_id,QTEREV_ID, replace(X.Y.value(''(ENTITLEMENT_VALUE_CODE)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_VALUE_CODE,replace(X.Y.value(''(ENTITLEMENT_NAME)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_NAME FROM (SELECT A.quote_ID,A.equipment_id,A.service_id,A.QTEREV_ID,CONVERT(XML,''<QUOTE_ENTITLEMENT>''+substring(entitlement_xml,charindex (''<ENTITLEMENT_ID>AGS_Z0091_STT_HDBRIN'',entitlement_xml),charindex (''Head break-in</ENTITLEMENT_NAME>'',entitlement_xml)-charindex (''<ENTITLEMENT_ID>AGS_Z0091_STT_HDBRIN'',entitlement_xml)+len(''Head break-in</ENTITLEMENT_NAME>''))+''</QUOTE_ENTITLEMENT>'') as entitlement_xml FROM "+str(SAQIEN)+" (nolock)A JOIN "+str(CRMTMP)+" C ON A.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE A.QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND A.QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND A.SERVICE_ID = ''Z0091'' ) e OUTER APPLY e.ENTITLEMENT_XML.nodes(''QUOTE_ENTITLEMENT'') as X(Y) )B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID = B.EQUIPMENT_ID AND A.QTEREV_ID = B.QTEREV_ID JOIN MAEQUP (NOLOCK) ON A.EQUIPMENT_ID  = MAEQUP.EQUIPMENT_ID JOIN PRCFVA C(NOLOCK) ON MAEQUP.SUBSTRATE_SIZE_GROUP = C.FACTOR_VARIABLE_ID WHERE B.ENTITLEMENT_NAME=''Head break-in'' AND ISNULL(B.ENTITLEMENT_VALUE_CODE,'''') = ''002'' AND C.FACTOR_ID  = ''HBWFPR''  '")
							
							#Z0035
							S3 = SqlHelper.GetFirst("sp_executesql @T=N'UPDATE A SET TOTAL_COST_WSEEDSTOCK = TOTAL_COST_WSEEDSTOCK + (ISNULL(CONVERT(FLOAT,C.FACTOR_TXTVAR),0) * ISNULL(HEAD_REBUILD_QTY,0) )  FROM SAQICO A(NOLOCK) JOIN (SELECT distinct quote_ID,equipment_id,service_id,QTEREV_ID, replace(X.Y.value(''(ENTITLEMENT_VALUE_CODE)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_VALUE_CODE,replace(X.Y.value(''(ENTITLEMENT_NAME)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_NAME FROM (SELECT A.quote_ID,A.equipment_id,A.service_id,A.QTEREV_ID,CONVERT(XML,''<QUOTE_ENTITLEMENT>''+substring(entitlement_xml,charindex (''<ENTITLEMENT_ID>AGS_Z0035_STT_HDBRIN'',entitlement_xml),charindex (''Head break-in</ENTITLEMENT_NAME>'',entitlement_xml)-charindex (''<ENTITLEMENT_ID>AGS_Z0035_STT_HDBRIN'',entitlement_xml)+len(''Head break-in</ENTITLEMENT_NAME>''))+''</QUOTE_ENTITLEMENT>'') as entitlement_xml FROM "+str(SAQIEN)+"  (nolock)A JOIN "+str(CRMTMP)+" C ON A.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE A.QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND A.QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND A.SERVICE_ID = ''Z0035'' ) e OUTER APPLY e.ENTITLEMENT_XML.nodes(''QUOTE_ENTITLEMENT'') as X(Y) )B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID = B.EQUIPMENT_ID AND A.QTEREV_ID = B.QTEREV_ID JOIN MAEQUP (NOLOCK) ON A.EQUIPMENT_ID  = MAEQUP.EQUIPMENT_ID JOIN PRCFVA C(NOLOCK) ON MAEQUP.SUBSTRATE_SIZE_GROUP = C.FACTOR_VARIABLE_ID WHERE B.ENTITLEMENT_NAME=''Head break-in'' AND ISNULL(B.ENTITLEMENT_VALUE_CODE,'''') = ''002'' AND C.FACTOR_ID  = ''HBWFCT''  '")
							
							S3 = SqlHelper.GetFirst("sp_executesql @T=N'UPDATE A SET MODEL_PRICE_INGL_CURR = MODEL_PRICE_INGL_CURR + (ISNULL(CONVERT(FLOAT,C.FACTOR_TXTVAR),0) * ISNULL(HEAD_REBUILD_QTY,0))   FROM SAQICO A(NOLOCK) JOIN (SELECT distinct quote_ID,equipment_id,service_id,QTEREV_ID, replace(X.Y.value(''(ENTITLEMENT_VALUE_CODE)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_VALUE_CODE,replace(X.Y.value(''(ENTITLEMENT_NAME)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_NAME FROM (SELECT A.quote_ID,A.equipment_id,A.service_id,A.QTEREV_ID,CONVERT(XML,''<QUOTE_ENTITLEMENT>''+substring(entitlement_xml,charindex (''<ENTITLEMENT_ID>AGS_Z0035_STT_HDBRIN'',entitlement_xml),charindex (''Head break-in</ENTITLEMENT_NAME>'',entitlement_xml)-charindex (''<ENTITLEMENT_ID>AGS_Z0035_STT_HDBRIN'',entitlement_xml)+len(''Head break-in</ENTITLEMENT_NAME>''))+''</QUOTE_ENTITLEMENT>'') as entitlement_xml FROM "+str(SAQIEN)+" (nolock)A JOIN "+str(CRMTMP)+" C ON A.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE A.QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND A.QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND A.SERVICE_ID = ''Z0035'' ) e OUTER APPLY e.ENTITLEMENT_XML.nodes(''QUOTE_ENTITLEMENT'') as X(Y) )B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID = B.EQUIPMENT_ID AND A.QTEREV_ID = B.QTEREV_ID JOIN MAEQUP (NOLOCK) ON A.EQUIPMENT_ID  = MAEQUP.EQUIPMENT_ID JOIN PRCFVA C(NOLOCK) ON MAEQUP.SUBSTRATE_SIZE_GROUP = C.FACTOR_VARIABLE_ID WHERE B.ENTITLEMENT_NAME=''Head break-in'' AND ISNULL(B.ENTITLEMENT_VALUE_CODE,'''') = ''002'' AND C.FACTOR_ID  = ''HBWFPR''  '")
							
							#Z0009
							S3 = SqlHelper.GetFirst("sp_executesql @T=N'UPDATE A SET TOTAL_COST_WSEEDSTOCK = TOTAL_COST_WSEEDSTOCK + (ISNULL(CONVERT(FLOAT,C.FACTOR_TXTVAR),0) * ISNULL(HEAD_REBUILD_QTY,0) )  FROM SAQICO A(NOLOCK) JOIN (SELECT distinct quote_ID,equipment_id,service_id,QTEREV_ID, replace(X.Y.value(''(ENTITLEMENT_VALUE_CODE)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_VALUE_CODE,replace(X.Y.value(''(ENTITLEMENT_NAME)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_NAME FROM (SELECT A.quote_ID,A.equipment_id,A.service_id,A.QTEREV_ID,CONVERT(XML,''<QUOTE_ENTITLEMENT>''+substring(entitlement_xml,charindex (''<ENTITLEMENT_ID>AGS_Z0009_STT_HDBRIN'',entitlement_xml),charindex (''Head break-in</ENTITLEMENT_NAME>'',entitlement_xml)-charindex (''<ENTITLEMENT_ID>AGS_Z0009_STT_HDBRIN'',entitlement_xml)+len(''Head break-in</ENTITLEMENT_NAME>''))+''</QUOTE_ENTITLEMENT>'') as entitlement_xml FROM "+str(SAQIEN)+"  (nolock)A JOIN "+str(CRMTMP)+" C ON A.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE A.QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND A.QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND A.SERVICE_ID = ''Z0009'' ) e OUTER APPLY e.ENTITLEMENT_XML.nodes(''QUOTE_ENTITLEMENT'') as X(Y) )B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID = B.EQUIPMENT_ID AND A.QTEREV_ID = B.QTEREV_ID JOIN MAEQUP (NOLOCK) ON A.EQUIPMENT_ID  = MAEQUP.EQUIPMENT_ID JOIN PRCFVA C(NOLOCK) ON MAEQUP.SUBSTRATE_SIZE_GROUP = C.FACTOR_VARIABLE_ID WHERE B.ENTITLEMENT_NAME=''Head break-in'' AND ISNULL(B.ENTITLEMENT_VALUE_CODE,'''') = ''002'' AND C.FACTOR_ID  = ''HBWFCT''  '")
							
							S3 = SqlHelper.GetFirst("sp_executesql @T=N'UPDATE A SET MODEL_PRICE_INGL_CURR = MODEL_PRICE_INGL_CURR + (ISNULL(CONVERT(FLOAT,C.FACTOR_TXTVAR),0) * ISNULL(HEAD_REBUILD_QTY,0))   FROM SAQICO A(NOLOCK) JOIN (SELECT distinct quote_ID,equipment_id,service_id,QTEREV_ID, replace(X.Y.value(''(ENTITLEMENT_VALUE_CODE)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_VALUE_CODE,replace(X.Y.value(''(ENTITLEMENT_NAME)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_NAME FROM (SELECT A.quote_ID,A.equipment_id,A.service_id,A.QTEREV_ID,CONVERT(XML,''<QUOTE_ENTITLEMENT>''+substring(entitlement_xml,charindex (''<ENTITLEMENT_ID>AGS_Z0009_STT_HDBRIN'',entitlement_xml),charindex (''Head break-in</ENTITLEMENT_NAME>'',entitlement_xml)-charindex (''<ENTITLEMENT_ID>AGS_Z0009_STT_HDBRIN'',entitlement_xml)+len(''Head break-in</ENTITLEMENT_NAME>''))+''</QUOTE_ENTITLEMENT>'') as entitlement_xml FROM "+str(SAQIEN)+" (nolock)A JOIN "+str(CRMTMP)+" C ON A.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE A.QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND A.QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND A.SERVICE_ID = ''Z0009'' ) e OUTER APPLY e.ENTITLEMENT_XML.nodes(''QUOTE_ENTITLEMENT'') as X(Y) )B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID = B.EQUIPMENT_ID AND A.QTEREV_ID = B.QTEREV_ID JOIN MAEQUP (NOLOCK) ON A.EQUIPMENT_ID  = MAEQUP.EQUIPMENT_ID JOIN PRCFVA C(NOLOCK) ON MAEQUP.SUBSTRATE_SIZE_GROUP = C.FACTOR_VARIABLE_ID WHERE B.ENTITLEMENT_NAME=''Head break-in'' AND ISNULL(B.ENTITLEMENT_VALUE_CODE,'''') = ''002'' AND C.FACTOR_ID  = ''HBWFPR''  '")
							
							#Z0091
							#Application Engineering
							S3 = SqlHelper.GetFirst("sp_executesql @T=N'UPDATE A SET MODEL_PRICE_INGL_CURR = MODEL_PRICE_INGL_CURR + ISNULL(CONVERT(FLOAT,C.ENTITLEMENT_PRICE_IMPACT),0) , TOTAL_COST_WSEEDSTOCK = TOTAL_COST_WSEEDSTOCK + ISNULL(CONVERT(FLOAT,C.ENTITLEMENT_COST_IMPACT),0)  FROM SAQICO A(NOLOCK) JOIN (SELECT distinct quote_ID,equipment_id,service_id,QTEREV_ID, replace(X.Y.value(''(ENTITLEMENT_VALUE_CODE)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_VALUE_CODE,replace(X.Y.value(''(ENTITLEMENT_NAME)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_NAME FROM (SELECT A.quote_ID,A.equipment_id,A.service_id,A.QTEREV_ID,CONVERT(XML,''<QUOTE_ENTITLEMENT>''+substring(entitlement_xml,charindex (''<ENTITLEMENT_ID>AGS_Z0091_NET_NUMLAY'',entitlement_xml),charindex (''Number of Layers</ENTITLEMENT_NAME>'',entitlement_xml)-charindex (''<ENTITLEMENT_ID>AGS_Z0091_NET_NUMLAY'',entitlement_xml)+len(''Number of Layers</ENTITLEMENT_NAME>''))+''</QUOTE_ENTITLEMENT>'') as entitlement_xml FROM "+str(SAQIEN)+" (nolock)A JOIN "+str(CRMTMP)+" C ON A.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE A.QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND A.QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND A.SERVICE_ID = ''Z0091'' ) e OUTER APPLY e.ENTITLEMENT_XML.nodes(''QUOTE_ENTITLEMENT'') as X(Y) )B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID = B.EQUIPMENT_ID AND A.QTEREV_ID = B.QTEREV_ID JOIN PREGBV C(NOLOCK) ON B.ENTITLEMENT_NAME = C.ENTITLEMENT_NAME AND B.ENTITLEMENT_VALUE_CODE = C.ENTITLEMENT_VALUE_CODE WHERE B.ENTITLEMENT_NAME=''Number of Layers'' AND ISNULL(B.ENTITLEMENT_VALUE_CODE,'''') <>''''  '")
							
							#Z0035
							#Application Engineering
							S3 = SqlHelper.GetFirst("sp_executesql @T=N'UPDATE A SET MODEL_PRICE_INGL_CURR = MODEL_PRICE_INGL_CURR + ISNULL(CONVERT(FLOAT,C.ENTITLEMENT_PRICE_IMPACT),0) , TOTAL_COST_WSEEDSTOCK = TOTAL_COST_WSEEDSTOCK + ISNULL(CONVERT(FLOAT,C.ENTITLEMENT_COST_IMPACT),0)  FROM SAQICO A(NOLOCK) JOIN (SELECT distinct quote_ID,equipment_id,service_id,QTEREV_ID, replace(X.Y.value(''(ENTITLEMENT_VALUE_CODE)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_VALUE_CODE,replace(X.Y.value(''(ENTITLEMENT_NAME)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_NAME FROM (SELECT A.quote_ID,A.equipment_id,A.service_id,A.QTEREV_ID,CONVERT(XML,''<QUOTE_ENTITLEMENT>''+substring(entitlement_xml,charindex (''<ENTITLEMENT_ID>AGS_Z0035_NET_NUMLAY'',entitlement_xml),charindex (''Number of Layers</ENTITLEMENT_NAME>'',entitlement_xml)-charindex (''<ENTITLEMENT_ID>AGS_Z0035_NET_NUMLAY'',entitlement_xml)+len(''Number of Layers</ENTITLEMENT_NAME>''))+''</QUOTE_ENTITLEMENT>'') as entitlement_xml FROM "+str(SAQIEN)+" (nolock)A JOIN "+str(CRMTMP)+" C ON A.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE A.QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND A.QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND A.SERVICE_ID = ''Z0035'' ) e OUTER APPLY e.ENTITLEMENT_XML.nodes(''QUOTE_ENTITLEMENT'') as X(Y) )B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID = B.EQUIPMENT_ID AND A.QTEREV_ID = B.QTEREV_ID JOIN PREGBV C(NOLOCK) ON B.ENTITLEMENT_NAME = C.ENTITLEMENT_NAME AND B.ENTITLEMENT_VALUE_CODE = C.ENTITLEMENT_VALUE_CODE WHERE B.ENTITLEMENT_NAME=''Number of Layers'' AND ISNULL(B.ENTITLEMENT_VALUE_CODE,'''') <>''''  '")
							
							#Z0091
							#Specialized Coating
							S3 = SqlHelper.GetFirst("sp_executesql @T=N'UPDATE A SET TOTAL_COST_WSEEDSTOCK = TOTAL_COST_WSEEDSTOCK +  ( ISNULL(CONVERT(FLOAT,C.ENTITLEMENT_COST_IMPACT),0) * ISNULL(HEAD_REBUILD_QTY,0) ), MODEL_PRICE_INGL_CURR = MODEL_PRICE_INGL_CURR + (ISNULL(CONVERT(FLOAT,C.ENTITLEMENT_PRICE_IMPACT),0)  * ISNULL(HEAD_REBUILD_QTY,0) )   FROM SAQICO A(NOLOCK) JOIN (SELECT distinct quote_ID,equipment_id,service_id,QTEREV_ID, replace(X.Y.value(''(ENTITLEMENT_VALUE_CODE)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_VALUE_CODE,replace(X.Y.value(''(ENTITLEMENT_NAME)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_NAME FROM (SELECT A.quote_ID,A.equipment_id,A.service_id,A.QTEREV_ID,CONVERT(XML,''<QUOTE_ENTITLEMENT>''+substring(entitlement_xml,charindex (''<ENTITLEMENT_ID>AGS_Z0091_STT_SPCCOT'',entitlement_xml),charindex (''Specialized Coating</ENTITLEMENT_NAME>'',entitlement_xml)-charindex (''<ENTITLEMENT_ID>AGS_Z0091_STT_SPCCOT'',entitlement_xml)+len(''Specialized Coating</ENTITLEMENT_NAME>''))+''</QUOTE_ENTITLEMENT>'') as entitlement_xml FROM "+str(SAQIEN)+" (nolock)A JOIN "+str(CRMTMP)+" C ON A.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE A.QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND A.QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND A.SERVICE_ID = ''Z0091'' ) e OUTER APPLY e.ENTITLEMENT_XML.nodes(''QUOTE_ENTITLEMENT'') as X(Y) )B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID = B.EQUIPMENT_ID AND A.QTEREV_ID = B.QTEREV_ID JOIN PREGBV C(NOLOCK) ON B.ENTITLEMENT_NAME = C.ENTITLEMENT_NAME AND B.ENTITLEMENT_VALUE_CODE = C.ENTITLEMENT_VALUE_CODE WHERE B.ENTITLEMENT_NAME=''Specialized Coating'' AND ISNULL(C.ENTITLEMENT_DISPLAY_VALUE,'''') = ''Included''  '")
							
							#Z0035
							#Specialized Coating
							S3 = SqlHelper.GetFirst("sp_executesql @T=N'UPDATE A SET TOTAL_COST_WSEEDSTOCK = TOTAL_COST_WSEEDSTOCK +  ( ISNULL(CONVERT(FLOAT,C.ENTITLEMENT_COST_IMPACT),0) * ISNULL(HEAD_REBUILD_QTY,0) ), MODEL_PRICE_INGL_CURR = MODEL_PRICE_INGL_CURR + (ISNULL(CONVERT(FLOAT,C.ENTITLEMENT_PRICE_IMPACT),0)  * ISNULL(HEAD_REBUILD_QTY,0) )   FROM SAQICO A(NOLOCK) JOIN (SELECT distinct quote_ID,equipment_id,service_id,QTEREV_ID, replace(X.Y.value(''(ENTITLEMENT_VALUE_CODE)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_VALUE_CODE,replace(X.Y.value(''(ENTITLEMENT_NAME)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_NAME FROM (SELECT A.quote_ID,A.equipment_id,A.service_id,A.QTEREV_ID,CONVERT(XML,''<QUOTE_ENTITLEMENT>''+substring(entitlement_xml,charindex (''<ENTITLEMENT_ID>AGS_Z0035_STT_SPCCOT'',entitlement_xml),charindex (''Specialized Coating</ENTITLEMENT_NAME>'',entitlement_xml)-charindex (''<ENTITLEMENT_ID>AGS_Z0035_STT_SPCCOT'',entitlement_xml)+len(''Specialized Coating</ENTITLEMENT_NAME>''))+''</QUOTE_ENTITLEMENT>'') as entitlement_xml FROM "+str(SAQIEN)+" (nolock)A JOIN "+str(CRMTMP)+" C ON A.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE A.QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND A.QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND A.SERVICE_ID = ''Z0035'' ) e OUTER APPLY e.ENTITLEMENT_XML.nodes(''QUOTE_ENTITLEMENT'') as X(Y) )B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID = B.EQUIPMENT_ID AND A.QTEREV_ID = B.QTEREV_ID JOIN PREGBV C(NOLOCK) ON B.ENTITLEMENT_NAME = C.ENTITLEMENT_NAME AND B.ENTITLEMENT_VALUE_CODE = C.ENTITLEMENT_VALUE_CODE WHERE B.ENTITLEMENT_NAME=''Specialized Coating'' AND ISNULL(C.ENTITLEMENT_DISPLAY_VALUE,'''') = ''Included''  '")
							
							#Z0009
							#Specialized Coating
							S3 = SqlHelper.GetFirst("sp_executesql @T=N'UPDATE A SET TOTAL_COST_WSEEDSTOCK = TOTAL_COST_WSEEDSTOCK +  ( ISNULL(CONVERT(FLOAT,C.ENTITLEMENT_COST_IMPACT),0) * ISNULL(HEAD_REBUILD_QTY,0) ), MODEL_PRICE_INGL_CURR = MODEL_PRICE_INGL_CURR + (ISNULL(CONVERT(FLOAT,C.ENTITLEMENT_PRICE_IMPACT),0)  * ISNULL(HEAD_REBUILD_QTY,0) )   FROM SAQICO A(NOLOCK) JOIN (SELECT distinct quote_ID,equipment_id,service_id,QTEREV_ID, replace(X.Y.value(''(ENTITLEMENT_VALUE_CODE)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_VALUE_CODE,replace(X.Y.value(''(ENTITLEMENT_NAME)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_NAME FROM (SELECT A.quote_ID,A.equipment_id,A.service_id,A.QTEREV_ID,CONVERT(XML,''<QUOTE_ENTITLEMENT>''+substring(entitlement_xml,charindex (''<ENTITLEMENT_ID>AGS_Z0009_STT_SPCCOT'',entitlement_xml),charindex (''Specialized Coating</ENTITLEMENT_NAME>'',entitlement_xml)-charindex (''<ENTITLEMENT_ID>AGS_Z0009_STT_SPCCOT'',entitlement_xml)+len(''Specialized Coating</ENTITLEMENT_NAME>''))+''</QUOTE_ENTITLEMENT>'') as entitlement_xml FROM "+str(SAQIEN)+" (nolock)A JOIN "+str(CRMTMP)+" C ON A.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE A.QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND A.QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND A.SERVICE_ID = ''Z0009'' ) e OUTER APPLY e.ENTITLEMENT_XML.nodes(''QUOTE_ENTITLEMENT'') as X(Y) )B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID = B.EQUIPMENT_ID AND A.QTEREV_ID = B.QTEREV_ID JOIN PREGBV C(NOLOCK) ON B.ENTITLEMENT_NAME = C.ENTITLEMENT_NAME AND B.ENTITLEMENT_VALUE_CODE = C.ENTITLEMENT_VALUE_CODE WHERE B.ENTITLEMENT_NAME=''Specialized Coating'' AND ISNULL(C.ENTITLEMENT_DISPLAY_VALUE,'''') = ''Included''  '")
							
							#Z0091
							#Specialized Cleaning					
							S3 = SqlHelper.GetFirst("sp_executesql @T=N'UPDATE A SET TOTAL_COST_WSEEDSTOCK = TOTAL_COST_WSEEDSTOCK + (ISNULL(CONVERT(FLOAT,C.ENTITLEMENT_COST_IMPACT),0) * ISNULL(HEAD_REBUILD_QTY,0)), MODEL_PRICE_INGL_CURR = MODEL_PRICE_INGL_CURR + (ISNULL(CONVERT(FLOAT,C.ENTITLEMENT_PRICE_IMPACT),0)  * ISNULL(HEAD_REBUILD_QTY,0) )   FROM SAQICO A(NOLOCK) JOIN (SELECT distinct quote_ID,equipment_id,service_id,QTEREV_ID, replace(X.Y.value(''(ENTITLEMENT_VALUE_CODE)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_VALUE_CODE,replace(X.Y.value(''(ENTITLEMENT_NAME)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_NAME FROM (SELECT A.quote_ID,A.equipment_id,A.service_id,A.QTEREV_ID,CONVERT(XML,''<QUOTE_ENTITLEMENT>''+substring(entitlement_xml,charindex (''<ENTITLEMENT_ID>AGS_Z0091_STT_SPCCLN'',entitlement_xml),charindex (''Specialized Cleaning</ENTITLEMENT_NAME>'',entitlement_xml)-charindex (''<ENTITLEMENT_ID>AGS_Z0091_STT_SPCCLN'',entitlement_xml)+len(''Specialized Cleaning</ENTITLEMENT_NAME>''))+''</QUOTE_ENTITLEMENT>'') as entitlement_xml FROM "+str(SAQIEN)+"  (nolock)A JOIN "+str(CRMTMP)+" C ON A.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE A.QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND A.QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND A.SERVICE_ID = ''Z0091'' ) e OUTER APPLY e.ENTITLEMENT_XML.nodes(''QUOTE_ENTITLEMENT'') as X(Y) )B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID = B.EQUIPMENT_ID AND A.QTEREV_ID = B.QTEREV_ID JOIN PREGBV C(NOLOCK) ON B.ENTITLEMENT_NAME = C.ENTITLEMENT_NAME AND B.ENTITLEMENT_VALUE_CODE = C.ENTITLEMENT_VALUE_CODE WHERE B.ENTITLEMENT_NAME=''Specialized Cleaning'' AND ISNULL(C.ENTITLEMENT_DISPLAY_VALUE,'''') = ''Included''  '")
							
							#Z0035
							#Specialized Cleaning					
							S3 = SqlHelper.GetFirst("sp_executesql @T=N'UPDATE A SET TOTAL_COST_WSEEDSTOCK = TOTAL_COST_WSEEDSTOCK + (ISNULL(CONVERT(FLOAT,C.ENTITLEMENT_COST_IMPACT),0) * ISNULL(HEAD_REBUILD_QTY,0)), MODEL_PRICE_INGL_CURR = MODEL_PRICE_INGL_CURR + (ISNULL(CONVERT(FLOAT,C.ENTITLEMENT_PRICE_IMPACT),0)  * ISNULL(HEAD_REBUILD_QTY,0) )   FROM SAQICO A(NOLOCK) JOIN (SELECT distinct quote_ID,equipment_id,service_id,QTEREV_ID, replace(X.Y.value(''(ENTITLEMENT_VALUE_CODE)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_VALUE_CODE,replace(X.Y.value(''(ENTITLEMENT_NAME)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_NAME FROM (SELECT A.quote_ID,A.equipment_id,A.service_id,A.QTEREV_ID,CONVERT(XML,''<QUOTE_ENTITLEMENT>''+substring(entitlement_xml,charindex (''<ENTITLEMENT_ID>AGS_Z0035_STT_SPCCLN'',entitlement_xml),charindex (''Specialized Cleaning</ENTITLEMENT_NAME>'',entitlement_xml)-charindex (''<ENTITLEMENT_ID>AGS_Z0035_STT_SPCCLN'',entitlement_xml)+len(''Specialized Cleaning</ENTITLEMENT_NAME>''))+''</QUOTE_ENTITLEMENT>'') as entitlement_xml FROM "+str(SAQIEN)+"  (nolock)A JOIN "+str(CRMTMP)+" C ON A.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE A.QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND A.QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND A.SERVICE_ID = ''Z0035'' ) e OUTER APPLY e.ENTITLEMENT_XML.nodes(''QUOTE_ENTITLEMENT'') as X(Y) )B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID = B.EQUIPMENT_ID AND A.QTEREV_ID = B.QTEREV_ID JOIN PREGBV C(NOLOCK) ON B.ENTITLEMENT_NAME = C.ENTITLEMENT_NAME AND B.ENTITLEMENT_VALUE_CODE = C.ENTITLEMENT_VALUE_CODE WHERE B.ENTITLEMENT_NAME=''Specialized Cleaning'' AND ISNULL(C.ENTITLEMENT_DISPLAY_VALUE,'''') = ''Included''  '")
							
							#Z0009
							#Specialized Cleaning					
							S3 = SqlHelper.GetFirst("sp_executesql @T=N'UPDATE A SET TOTAL_COST_WSEEDSTOCK = TOTAL_COST_WSEEDSTOCK + (ISNULL(CONVERT(FLOAT,C.ENTITLEMENT_COST_IMPACT),0) * ISNULL(HEAD_REBUILD_QTY,0)), MODEL_PRICE_INGL_CURR = MODEL_PRICE_INGL_CURR + (ISNULL(CONVERT(FLOAT,C.ENTITLEMENT_PRICE_IMPACT),0)  * ISNULL(HEAD_REBUILD_QTY,0) )   FROM SAQICO A(NOLOCK) JOIN (SELECT distinct quote_ID,equipment_id,service_id,QTEREV_ID, replace(X.Y.value(''(ENTITLEMENT_VALUE_CODE)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_VALUE_CODE,replace(X.Y.value(''(ENTITLEMENT_NAME)[1]'', ''VARCHAR(128)''),'';#38'',''&'') as ENTITLEMENT_NAME FROM (SELECT A.quote_ID,A.equipment_id,A.service_id,A.QTEREV_ID,CONVERT(XML,''<QUOTE_ENTITLEMENT>''+substring(entitlement_xml,charindex (''<ENTITLEMENT_ID>AGS_Z0009_STT_SPCCLN'',entitlement_xml),charindex (''Specialized Cleaning</ENTITLEMENT_NAME>'',entitlement_xml)-charindex (''<ENTITLEMENT_ID>AGS_Z0009_STT_SPCCLN'',entitlement_xml)+len(''Specialized Cleaning</ENTITLEMENT_NAME>''))+''</QUOTE_ENTITLEMENT>'') as entitlement_xml FROM "+str(SAQIEN)+"  (nolock)A JOIN "+str(CRMTMP)+" C ON A.EQUIPMENT_ID = C.EQUIPMENT_IDD WHERE A.QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND A.QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND A.SERVICE_ID = ''Z0009'' ) e OUTER APPLY e.ENTITLEMENT_XML.nodes(''QUOTE_ENTITLEMENT'') as X(Y) )B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID = B.EQUIPMENT_ID AND A.QTEREV_ID = B.QTEREV_ID JOIN PREGBV C(NOLOCK) ON B.ENTITLEMENT_NAME = C.ENTITLEMENT_NAME AND B.ENTITLEMENT_VALUE_CODE = C.ENTITLEMENT_VALUE_CODE WHERE B.ENTITLEMENT_NAME=''Specialized Cleaning'' AND ISNULL(C.ENTITLEMENT_DISPLAY_VALUE,'''') = ''Included''  '")
							
							CRMTMP31 = SqlHelper.GetFirst("sp_executesql @T=N'DELETE FROM "+str(CRMTMP)+" ' ")
							
							SAQIEN_DRP = SqlHelper.GetFirst("sp_executesql @T=N'IF EXISTS (SELECT ''X'' FROM SYS.OBJECTS WHERE NAME= ''"+str(SAQIEN)+"'' ) BEGIN DROP TABLE "+str(SAQIEN)+" END  ' ")
						
						else:
							Check_flag13 = 0

					#Price Margin 
					primaryQueryItems = SqlHelper.GetFirst(
						""
						+ str(Parameter1.QUERY_CRITERIA_1)
						+ "  A SET TARGET_PRICE_MARGIN= FACTOR_TXTVAR,TARGET_PRICE_MARGIN_RECORD_ID = CALCULATION_VARIABLE_RECORD_ID FROM SAQICO (NOLOCK)A JOIN PRCFVA B(NOLOCK) ON A.SERVICE_ID = B.FACTOR_VARIABLE_ID WHERE QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND A.QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND FACTOR_ID=''TGMRGN'' AND TARGET_PRICE_MARGIN IS NULL ' ")
					
					primaryQueryItems = SqlHelper.GetFirst(
						""
						+ str(Parameter1.QUERY_CRITERIA_1)
						+ "  A SET SLSDIS_PRICE_MARGIN= FACTOR_TXTVAR,SLSDIS_PRICE_MARGIN_RECORD_ID=CALCULATION_VARIABLE_RECORD_ID FROM SAQICO (NOLOCK)A JOIN PRCFVA B(NOLOCK) ON A.SERVICE_ID = B.FACTOR_VARIABLE_ID WHERE QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND A.QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND FACTOR_ID=''SLMRGN'' AND SLSDIS_PRICE_MARGIN IS NULL ' ")
					
					primaryQueryItems = SqlHelper.GetFirst(
						""
						+ str(Parameter1.QUERY_CRITERIA_1)
						+ "  A SET BD_PRICE_MARGIN= FACTOR_TXTVAR,BD_PRICE_MARGIN_RECORD_ID=CALCULATION_VARIABLE_RECORD_ID FROM SAQICO (NOLOCK)A JOIN PRCFVA B(NOLOCK) ON A.SERVICE_ID = B.FACTOR_VARIABLE_ID WHERE QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND A.QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND FACTOR_ID=''BDMRGN'' AND BD_PRICE_MARGIN IS NULL ' ")
					
					primaryQueryItems = SqlHelper.GetFirst(
						""
						+ str(Parameter1.QUERY_CRITERIA_1)
						+ "  A SET CEILING_PRICE_MARGIN= FACTOR_TXTVAR,CEILING_PRICE_MARGIN_RECORD_ID=CALCULATION_VARIABLE_RECORD_ID FROM SAQICO (NOLOCK)A JOIN PRCFVA B(NOLOCK) ON A.SERVICE_ID = B.FACTOR_VARIABLE_ID WHERE QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND A.QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND FACTOR_ID=''CEMRGN'' AND CEILING_PRICE_MARGIN IS NULL ' ")
					
					primaryQueryItems = SqlHelper.GetFirst(
						""
						+ str(Parameter1.QUERY_CRITERIA_1)
						+ "  A SET SALDIS_PERCENT= FACTOR_TXTVAR FROM SAQICO (NOLOCK)A JOIN PRCFVA B(NOLOCK) ON A.SERVICE_ID = B.FACTOR_VARIABLE_ID WHERE QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND A.QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND FACTOR_ID=''SLDISC'' AND SALDIS_PERCENT IS NULL ' ")
					
					primaryQueryItems = SqlHelper.GetFirst(
						""
						+ str(Parameter1.QUERY_CRITERIA_1)
						+ "  A SET BD_DISCOUNT= FACTOR_TXTVAR,BD_DISCOUNT_RECORD_ID=CALCULATION_VARIABLE_RECORD_ID FROM SAQICO (NOLOCK)A JOIN PRCFVA B(NOLOCK) ON A.SERVICE_ID = B.FACTOR_VARIABLE_ID WHERE QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND A.QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND FACTOR_ID=''BDDISC'' AND BD_DISCOUNT IS NULL ' ")

					#Target Price
					primaryQueryItems = SqlHelper.GetFirst(
						""
						+ str(Parameter1.QUERY_CRITERIA_1)
						+ "  A SET TARGET_PRICE_INGL_CURR = CASE WHEN ISNULL(MODEL_PRICE_INGL_CURR/(1-(CONVERT(FLOAT,SALDIS_PERCENT)/100)),0) > ISNULL(TOTAL_COST_WSEEDSTOCK / (1-(TARGET_PRICE_MARGIN/100)),0) THEN ISNULL(MODEL_PRICE_INGL_CURR/(1-(CONVERT(FLOAT,SALDIS_PERCENT)/100)),0) ELSE ISNULL(TOTAL_COST_WSEEDSTOCK / (1-(TARGET_PRICE_MARGIN/100)),0) END FROM SAQICO (NOLOCK)A JOIN (SELECT DISTINCT QUOTE_ID,REVISION_ID,SERVICE_ID,EQUIPMENT_ID FROM SAQICO_INBOUND(NOLOCK)  WHERE ISNULL(PROCESS_STATUS,'''')=''INPROGRESS'' AND TIMESTAMP = '"+str(timestamp_sessionid)+"')B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID = B.EQUIPMENT_ID AND QTEREV_ID = REVISION_ID ' ")

					#Sale Discounted Price
					primaryQueryItems = SqlHelper.GetFirst(
						""
						+ str(Parameter1.QUERY_CRITERIA_1)
						+ "  A SET SLSDIS_PRICE_INGL_CURR = CASE WHEN ISNULL(MODEL_PRICE_INGL_CURR,0) > ISNULL(TOTAL_COST_WSEEDSTOCK / (1-(CONVERT(FLOAT,SLSDIS_PRICE_MARGIN)/100)),0) THEN ISNULL(MODEL_PRICE_INGL_CURR,0) ELSE ISNULL(TOTAL_COST_WSEEDSTOCK / (1-(CONVERT(FLOAT,SLSDIS_PRICE_MARGIN)/100)),0) END FROM SAQICO (NOLOCK)A JOIN (SELECT DISTINCT QUOTE_ID,REVISION_ID,SERVICE_ID,EQUIPMENT_ID FROM SAQICO_INBOUND(NOLOCK)  WHERE ISNULL(PROCESS_STATUS,'''')=''INPROGRESS'' AND TIMESTAMP = '"+str(timestamp_sessionid)+"')B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID = B.EQUIPMENT_ID AND QTEREV_ID = REVISION_ID ' ")

					#BD Price
					primaryQueryItems = SqlHelper.GetFirst(
						""
						+ str(Parameter1.QUERY_CRITERIA_1)
						+ "  A SET BD_PRICE_INGL_CURR = CASE WHEN ISNULL(MODEL_PRICE_INGL_CURR * (1-(CONVERT(FLOAT,BD_DISCOUNT)/100)) ,0) > ISNULL(TOTAL_COST_WSEEDSTOCK / (1-(CONVERT(FLOAT,BD_PRICE_MARGIN)/100)),0) THEN ISNULL(MODEL_PRICE_INGL_CURR * (1-(CONVERT(FLOAT,BD_DISCOUNT)/100)) ,0) ELSE ISNULL(TOTAL_COST_WSEEDSTOCK / (1-(CONVERT(FLOAT,BD_PRICE_MARGIN)/100)),0) END FROM SAQICO (NOLOCK)A JOIN (SELECT DISTINCT QUOTE_ID,SERVICE_ID,EQUIPMENT_ID,REVISION_ID FROM SAQICO_INBOUND(NOLOCK)  WHERE ISNULL(PROCESS_STATUS,'''')=''INPROGRESS'' AND TIMESTAMP = '"+str(timestamp_sessionid)+"')B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID = B.EQUIPMENT_ID AND QTEREV_ID = REVISION_ID ' ")

					#Ceiling Price
					primaryQueryItems = SqlHelper.GetFirst(
						""
						+ str(Parameter1.QUERY_CRITERIA_1)
						+ "  A SET CEILING_PRICE_INGL_CURR = TARGET_PRICE_INGL_CURR * (1 + (CONVERT(FLOAT,CEILING_PRICE_MARGIN)/100)) FROM SAQICO (NOLOCK)A JOIN (SELECT DISTINCT  QUOTE_ID,SERVICE_ID,EQUIPMENT_ID,REVISION_ID FROM SAQICO_INBOUND(NOLOCK)  WHERE ISNULL(PROCESS_STATUS,'''')=''INPROGRESS'' AND TIMESTAMP = '"+str(timestamp_sessionid)+"')B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID = B.EQUIPMENT_ID AND QTEREV_ID = REVISION_ID ' ")

					#Sales Price
					primaryQueryItems = SqlHelper.GetFirst(
						""
						+ str(Parameter1.QUERY_CRITERIA_1)
						+ "  A SET SALES_PRICE_INGL_CURR = TARGET_PRICE_INGL_CURR - (TARGET_PRICE_INGL_CURR * (ISNULL(DISCOUNT,0)/100)) FROM SAQICO (NOLOCK)A JOIN (SELECT DISTINCT  QUOTE_ID,SERVICE_ID,EQUIPMENT_ID,REVISION_ID FROM SAQICO_INBOUND(NOLOCK)  WHERE ISNULL(PROCESS_STATUS,'''')=''INPROGRESS'' AND TIMESTAMP = '"+str(timestamp_sessionid)+"')B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID = B.EQUIPMENT_ID AND QTEREV_ID = REVISION_ID  ' ")
					
					#Annualized Net Price
					primaryQueryItems = SqlHelper.GetFirst(
						""
						+ str(Parameter1.QUERY_CRITERIA_1)
						+ "  A SET NET_PRICE_INGL_CURR = SALES_PRICE_INGL_CURR - CASE WHEN ISNULL(YEAR_OVER_YEAR,0)=0 THEN 0 ELSE (SALES_PRICE_INGL_CURR * (YEAR_OVER_YEAR/100)) END  FROM SAQICO (NOLOCK)A JOIN (SELECT DISTINCT QUOTE_ID,SERVICE_ID,EQUIPMENT_ID,REVISION_ID FROM SAQICO_INBOUND(NOLOCK)  WHERE ISNULL(PROCESS_STATUS,'''')=''INPROGRESS'' AND TIMESTAMP = '"+str(timestamp_sessionid)+"')B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID = B.EQUIPMENT_ID  AND QTEREV_ID = REVISION_ID ' ")

					#Contractual Net Price / Cost
					primaryQueryItems = SqlHelper.GetFirst(
						""
						+ str(Parameter1.QUERY_CRITERIA_1)
						+ "  A SET CNTPRI_INGL_CURR = ((NET_PRICE_INGL_CURR/365) * contractdays) * ISNULL(CONTRACT_PERIOD_FACTOR,1),CNTCST_INGL_CURR = ((TOTAL_COST_WSEEDSTOCK/365) * contractdays) * ISNULL(CONTRACT_PERIOD_FACTOR,1)  FROM SAQICO (NOLOCK)A JOIN (SELECT DISTINCT QUOTE_ID,SERVICE_ID,EQUIPMENT_ID,REVISION_ID,LINE FROM SAQICO_INBOUND(NOLOCK)  WHERE ISNULL(PROCESS_STATUS,'''')=''INPROGRESS'' AND TIMESTAMP = '"+str(timestamp_sessionid)+"')B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID = B.EQUIPMENT_ID  AND QTEREV_ID = REVISION_ID AND A.LINE = B.LINE JOIN (select line,CONTRACT_PERIOD_FACTOR,SERVICE_ID,QUOTE_ID,datediff(dd,dateadd(dd,-1,CONTRACT_VALID_FROM),CONTRACT_VALID_TO) as contractdays from SAQRIT,PRCTPF WHERE QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND datediff(mm,dateadd(dd,-1,CONTRACT_VALID_FROM),CONTRACT_VALID_TO) BETWEEN PERIOD_FROM AND PERIOD_TO)C ON A.QUOTE_ID = C.QUOTE_ID AND A.LINE = C.LINE AND A.SERVICE_ID = C.SERVICE_ID ' ")
					
					#Z0101 / Z0100 Target /Sales / BD / Ceiling / Final Price
					primaryQueryItems = SqlHelper.GetFirst(
						""
						+ str(Parameter1.QUERY_CRITERIA_1)
						+ "  A SET TARGET_PRICE_INGL_CURR = MODEL_PRICE_INGL_CURR,SALES_PRICE_INGL_CURR = MODEL_PRICE_INGL_CURR,CEILING_PRICE_INGL_CURR = MODEL_PRICE_INGL_CURR,BD_PRICE_INGL_CURR = MODEL_PRICE_INGL_CURR,SLSDIS_PRICE_INGL_CURR = MODEL_PRICE_INGL_CURR,NET_PRICE_INGL_CURR = MODEL_PRICE_INGL_CURR,CNTPRI_INGL_CURR = MODEL_PRICE_INGL_CURR,CNTCST_INGL_CURR = TOTAL_COST_WSEEDSTOCK FROM SAQICO (NOLOCK)A JOIN (SELECT DISTINCT QUOTE_ID,REVISION_ID,SERVICE_ID,EQUIPMENT_ID,LINE FROM SAQICO_INBOUND(NOLOCK)  WHERE ISNULL(PROCESS_STATUS,'''')=''INPROGRESS'' AND TIMESTAMP = '"+str(timestamp_sessionid)+"')B ON A.QUOTE_ID = B.QUOTE_ID AND A.LINE = B.LINE AND A.EQUIPMENT_ID = B.EQUIPMENT_ID AND QTEREV_ID = REVISION_ID WHERE A.SERVICE_ID IN (''Z0100'',''Z0101'') ' ")

					#Item Roll Up
					primaryQueryItems = SqlHelper.GetFirst(
					""
					+ str(Parameter1.QUERY_CRITERIA_1)
					+ "  SAQITM SET TAX_AMOUNT_INGL_CURR = ROUND((SUB_SAQITM.SALES_PRICE_INGL_CURR * (ISNULL(SAQITM.TAX_PERCENTAGE,0)/100)),CONVERT(INT,"+str(roundcurr.DECIMAL_PLACES)+"),CONVERT(INT,"+str(roundcurr.ROUNDING_METHOD)+")) ,NET_PRICE_INGL_CURR = SUB_SAQITM.CNTPRI_INGL_CURR,UNIT_PRICE_INGL_CURR = SUB_SAQITM.SALES_PRICE_INGL_CURR,ESTVAL_INGL_CURR = SUB_SAQITM.ESTVAL_INGL_CURR FROM SAQRIT SAQITM(NOLOCK) JOIN(SELECT SUM(SAQICO.ESTVAL_INGL_CURR) AS ESTVAL_INGL_CURR,SUM(SAQICO.NET_PRICE_INGL_CURR) AS NET_PRICE_INGL_CURR,SUM(ISNULL(CNTPRI_INGL_CURR,0)) AS CNTPRI_INGL_CURR,SUM(SALES_PRICE_INGL_CURR) AS SALES_PRICE_INGL_CURR,SAQICO.QTEREV_ID,LINE,SAQICO.QUOTE_ID,SAQICO.SERVICE_ID FROM SAQICO (NOLOCK) WHERE QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' GROUP BY SAQICO.QUOTE_ID,SAQICO.SERVICE_ID,SAQICO.QTEREV_ID,SAQICO.LINE) SUB_SAQITM  ON SAQITM.QUOTE_ID = SUB_SAQITM.QUOTE_ID AND SAQITM.SERVICE_ID = SUB_SAQITM.SERVICE_ID  AND SAQITM.SERVICE_ID <> ''Z0116'' AND SUB_SAQITM.QTEREV_ID = SAQITM.QTEREV_ID  AND SAQITM.LINE = SUB_SAQITM.LINE ' ")

					#Item Roll Up Year 1
					primaryQueryItems = SqlHelper.GetFirst(
					""
					+ str(Parameter1.QUERY_CRITERIA_1)
					+ "  SAQITM SET YEAR_1_INGL_CURR = SUB_SAQITM.CNTPRI_INGL_CURR  FROM SAQRIT SAQITM(NOLOCK) JOIN(SELECT SUM(SAQICO.CNTPRI_INGL_CURR) AS CNTPRI_INGL_CURR,SAQICO.QTEREV_ID,LINE,SAQICO.QUOTE_ID,SAQICO.SERVICE_ID FROM SAQICO (NOLOCK) WHERE QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND YEAR=''YEAR 1'' GROUP BY SAQICO.QUOTE_ID,SAQICO.SERVICE_ID,SAQICO.QTEREV_ID,SAQICO.LINE) SUB_SAQITM  ON SAQITM.QUOTE_ID = SUB_SAQITM.QUOTE_ID AND SAQITM.SERVICE_ID = SUB_SAQITM.SERVICE_ID AND SUB_SAQITM.QTEREV_ID = SAQITM.QTEREV_ID  AND SAQITM.LINE = SUB_SAQITM.LINE ' ")

					#Item Roll Up Year 2
					primaryQueryItems = SqlHelper.GetFirst(
					""
					+ str(Parameter1.QUERY_CRITERIA_1)
					+ "  SAQITM SET YEAR_2_INGL_CURR = SUB_SAQITM.CNTPRI_INGL_CURR  FROM SAQRIT SAQITM(NOLOCK) JOIN(SELECT SUM(SAQICO.CNTPRI_INGL_CURR) AS CNTPRI_INGL_CURR,SAQICO.QTEREV_ID,LINE,SAQICO.QUOTE_ID,SAQICO.SERVICE_ID FROM SAQICO (NOLOCK) WHERE QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND YEAR=''YEAR 2'' GROUP BY SAQICO.QUOTE_ID,SAQICO.SERVICE_ID,SAQICO.QTEREV_ID,SAQICO.LINE) SUB_SAQITM  ON SAQITM.QUOTE_ID = SUB_SAQITM.QUOTE_ID AND SAQITM.SERVICE_ID = SUB_SAQITM.SERVICE_ID AND SUB_SAQITM.QTEREV_ID = SAQITM.QTEREV_ID  AND SAQITM.LINE = SUB_SAQITM.LINE ' ")

					#Item Roll Up Year 3
					primaryQueryItems = SqlHelper.GetFirst(
					""
					+ str(Parameter1.QUERY_CRITERIA_1)
					+ "  SAQITM SET YEAR_3_INGL_CURR = SUB_SAQITM.CNTPRI_INGL_CURR  FROM SAQRIT SAQITM(NOLOCK) JOIN(SELECT SUM(SAQICO.CNTPRI_INGL_CURR) AS CNTPRI_INGL_CURR,SAQICO.QTEREV_ID,LINE,SAQICO.QUOTE_ID,SAQICO.SERVICE_ID FROM SAQICO (NOLOCK) WHERE QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND YEAR=''YEAR 3'' GROUP BY SAQICO.QUOTE_ID,SAQICO.SERVICE_ID,SAQICO.QTEREV_ID,SAQICO.LINE) SUB_SAQITM  ON SAQITM.QUOTE_ID = SUB_SAQITM.QUOTE_ID AND SAQITM.SERVICE_ID = SUB_SAQITM.SERVICE_ID AND SUB_SAQITM.QTEREV_ID = SAQITM.QTEREV_ID  AND SAQITM.LINE = SUB_SAQITM.LINE ' ")

					#Item Roll Up Year 4
					primaryQueryItems = SqlHelper.GetFirst(
					""
					+ str(Parameter1.QUERY_CRITERIA_1)
					+ "  SAQITM SET YEAR_4_INGL_CURR = SUB_SAQITM.CNTPRI_INGL_CURR  FROM SAQRIT SAQITM(NOLOCK) JOIN(SELECT SUM(SAQICO.CNTPRI_INGL_CURR) AS CNTPRI_INGL_CURR,SAQICO.QTEREV_ID,LINE,SAQICO.QUOTE_ID,SAQICO.SERVICE_ID FROM SAQICO (NOLOCK) WHERE QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND YEAR=''YEAR 4'' GROUP BY SAQICO.QUOTE_ID,SAQICO.SERVICE_ID,SAQICO.QTEREV_ID,SAQICO.LINE) SUB_SAQITM  ON SAQITM.QUOTE_ID = SUB_SAQITM.QUOTE_ID AND SAQITM.SERVICE_ID = SUB_SAQITM.SERVICE_ID AND SUB_SAQITM.QTEREV_ID = SAQITM.QTEREV_ID  AND SAQITM.LINE = SUB_SAQITM.LINE ' ")

					#Item Roll Up Year 5
					primaryQueryItems = SqlHelper.GetFirst(
					""
					+ str(Parameter1.QUERY_CRITERIA_1)
					+ "  SAQITM SET YEAR_5_INGL_CURR = SUB_SAQITM.CNTPRI_INGL_CURR  FROM SAQRIT SAQITM(NOLOCK) JOIN(SELECT SUM(SAQICO.CNTPRI_INGL_CURR) AS CNTPRI_INGL_CURR,SAQICO.QTEREV_ID,LINE,SAQICO.QUOTE_ID,SAQICO.SERVICE_ID FROM SAQICO (NOLOCK) WHERE QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND YEAR=''YEAR 5'' GROUP BY SAQICO.QUOTE_ID,SAQICO.SERVICE_ID,SAQICO.QTEREV_ID,SAQICO.LINE) SUB_SAQITM  ON SAQITM.QUOTE_ID = SUB_SAQITM.QUOTE_ID AND SAQITM.SERVICE_ID = SUB_SAQITM.SERVICE_ID AND SUB_SAQITM.QTEREV_ID = SAQITM.QTEREV_ID  AND SAQITM.LINE = SUB_SAQITM.LINE ' ")

					#Item Tax Amount
					primaryQueryItems = SqlHelper.GetFirst(
					""
					+ str(Parameter1.QUERY_CRITERIA_1)
					+ "  SAQITM SET TAX_AMOUNT_INGL_CURR =  ( (ISNULL(NET_PRICE_INGL_CURR,0) ) * (TAX_PERCENTAGE/100)) FROM SAQRIT SAQITM(NOLOCK) JOIN(SELECT DISTINCT QUOTE_ID,SERVICE_ID,EQUIPMENT_ID,REVISION_ID FROM SAQICO_INBOUND(NOLOCK)  WHERE ISNULL(PROCESS_STATUS,'''')=''INPROGRESS'' AND TIMESTAMP = '"+str(timestamp_sessionid)+"') SUB_SAQITM  ON SAQITM.QUOTE_ID = SUB_SAQITM.QUOTE_ID AND SAQITM.SERVICE_ID = SUB_SAQITM.SERVICE_ID AND SUB_SAQITM.REVISION_ID = SAQITM.QTEREV_ID ' ")

					#Item Net Value
					primaryQueryItems = SqlHelper.GetFirst(
					""
					+ str(Parameter1.QUERY_CRITERIA_1)
					+ "  SAQITM SET NET_VALUE_INGL_CURR =  ISNULL(NET_PRICE_INGL_CURR,0) + ISNULL(TAX_AMOUNT_INGL_CURR,0)  FROM SAQRIT SAQITM(NOLOCK) JOIN(SELECT DISTINCT QUOTE_ID,SERVICE_ID,EQUIPMENT_ID,REVISION_ID FROM SAQICO_INBOUND(NOLOCK)  WHERE ISNULL(PROCESS_STATUS,'''')=''INPROGRESS'' AND TIMESTAMP = '"+str(timestamp_sessionid)+"') SUB_SAQITM  ON SAQITM.QUOTE_ID = SUB_SAQITM.QUOTE_ID AND SAQITM.SERVICE_ID = SUB_SAQITM.SERVICE_ID AND SUB_SAQITM.REVISION_ID = SAQITM.QTEREV_ID ' ")

					#Item Exchange Rate
					primaryQueryItems = SqlHelper.GetFirst(
						""
						+ str(Parameter1.QUERY_CRITERIA_1)
						+ "  A SET NET_PRICE = ROUND( (NET_PRICE_INGL_CURR * ISNULL(EXCHANGE_RATE,1)) ,CONVERT(INT,"+str(roundcurr.DECIMAL_PLACES)+"),CONVERT(INT,"+str(roundcurr.ROUNDING_METHOD)+")), NET_VALUE = ROUND( (NET_VALUE_INGL_CURR * ISNULL(EXCHANGE_RATE,1)) ,CONVERT(INT,"+str(roundcurr.DECIMAL_PLACES)+"),CONVERT(INT,"+str(roundcurr.ROUNDING_METHOD)+")), UNIT_PRICE = ROUND( (UNIT_PRICE_INGL_CURR * ISNULL(EXCHANGE_RATE,1)) ,CONVERT(INT,"+str(roundcurr.DECIMAL_PLACES)+"),CONVERT(INT,"+str(roundcurr.ROUNDING_METHOD)+")), YEAR_1 = ROUND( (YEAR_1_INGL_CURR * ISNULL(EXCHANGE_RATE,1)) ,CONVERT(INT,"+str(roundcurr.DECIMAL_PLACES)+"),CONVERT(INT,"+str(roundcurr.ROUNDING_METHOD)+")),YEAR_2 = ROUND( (YEAR_2_INGL_CURR * ISNULL(EXCHANGE_RATE,1)) ,CONVERT(INT,"+str(roundcurr.DECIMAL_PLACES)+"),CONVERT(INT,"+str(roundcurr.ROUNDING_METHOD)+")),YEAR_3 = ROUND( (YEAR_3_INGL_CURR) ,CONVERT(INT,"+str(roundcurr.DECIMAL_PLACES)+"),CONVERT(INT,"+str(roundcurr.ROUNDING_METHOD)+")), YEAR_4 = ROUND( (YEAR_4_INGL_CURR) ,CONVERT(INT,"+str(roundcurr.DECIMAL_PLACES)+"),CONVERT(INT,"+str(roundcurr.ROUNDING_METHOD)+")), YEAR_5 = ROUND( (YEAR_5_INGL_CURR) ,CONVERT(INT,"+str(roundcurr.DECIMAL_PLACES)+"),CONVERT(INT,"+str(roundcurr.ROUNDING_METHOD)+")), TAX_AMOUNT = ROUND( (TAX_AMOUNT_INGL_CURR) ,CONVERT(INT,"+str(roundcurr.DECIMAL_PLACES)+"),CONVERT(INT,"+str(roundcurr.ROUNDING_METHOD)+"))  FROM SAQRIT (NOLOCK)A JOIN (SELECT DISTINCT QUOTE_ID,SERVICE_ID,EQUIPMENT_ID,REVISION_ID FROM SAQICO_INBOUND(NOLOCK)  WHERE ISNULL(PROCESS_STATUS,'''')=''INPROGRESS'' AND TIMESTAMP = '"+str(timestamp_sessionid)+"')B ON A.QUOTE_ID = B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.OBJECT_ID = B.EQUIPMENT_ID AND QTEREV_ID = REVISION_ID ' ")

					primaryQueryItems = SqlHelper.GetFirst(
						""
					+ str(Parameter1.QUERY_CRITERIA_1)
					+ "  SAQICO SET STATUS=''PARTIALLY PRICED'' FROM SAQICO (NOLOCK) JOIN (SELECT DISTINCT QUOTE_ID,SERVICE_ID,EQUIPMENT_ID,REVISION_ID FROM SAQICO_INBOUND(NOLOCK)  WHERE ISNULL(PROCESS_STATUS,'''')=''INPROGRESS'' AND TIMESTAMP = '"+str(timestamp_sessionid)+"' AND ISNULL(COST_MODULE_AVAILABLE,'''')=''UNAVAILABLE'' AND ISNULL(COST_CALCULATION_STATUS,'''') <> ''Chamber map not required'' )SAQICO_INBOUND ON SAQICO.QUOTE_ID = SAQICO_INBOUND.QUOTE_ID AND SAQICO.SERVICE_ID = SAQICO_INBOUND.SERVICE_ID AND SAQICO.EQUIPMENT_ID = SAQICO_INBOUND.EQUIPMENT_ID AND SAQICO.QTEREV_ID = SAQICO_INBOUND.REVISION_ID  '")

					primaryQueryItems = SqlHelper.GetFirst(
						""
					+ str(Parameter1.QUERY_CRITERIA_1)
					+ "  SAQICO SET STATUS=''ERROR'' FROM SAQICO (NOLOCK) JOIN (SELECT DISTINCT QUOTE_ID,SERVICE_ID,EQUIPMENT_ID,REVISION_ID FROM SAQICO_INBOUND(NOLOCK)  WHERE ISNULL(PROCESS_STATUS,'''')=''INPROGRESS'' AND TIMESTAMP = '"+str(timestamp_sessionid)+"' AND ISNULL(COST_MODULE_AVAILABLE,'''')=''UNAVAILABLE'' AND ISNULL(COST_CALCULATION_STATUS,'''') = ''Tool Not Available'' )SAQICO_INBOUND ON SAQICO.QUOTE_ID = SAQICO_INBOUND.QUOTE_ID AND SAQICO.SERVICE_ID = SAQICO_INBOUND.SERVICE_ID AND SAQICO.EQUIPMENT_ID = SAQICO_INBOUND.EQUIPMENT_ID AND SAQICO.QTEREV_ID = SAQICO_INBOUND.REVISION_ID  '")

					primaryQueryItems = SqlHelper.GetFirst(
						""
					+ str(Parameter1.QUERY_CRITERIA_1)
					+ "  SAQITM SET STATUS=''PARTIALLY PRICED'' FROM SAQRIT SAQITM (NOLOCK) WHERE QUOTE_REVISION_CONTRACT_ITEM_ID IN (SELECT DISTINCT QTEITM_RECORD_ID FROM SAQICO_INBOUND(NOLOCK)A JOIN SAQICO B(NOLOCK) ON A.QUOTE_ID= B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID = B.EQUIPMENT_ID  WHERE ISNULL(PROCESS_STATUS,'''')=''INPROGRESS'' AND TIMESTAMP = '"+str(timestamp_sessionid)+"' AND ISNULL(COST_MODULE_AVAILABLE,'''')=''UNAVAILABLE'' AND B.STATUS=''PARTIALLY PRICED'') AND SERVICE_ID IN (SELECT DISTINCT SERVICE_ID FROM PRSPRV(NOLOCK) WHERE ISNULL(SSCM_COST,''FALSE'')=''TRUE'' )  '")

					primaryQueryItems = SqlHelper.GetFirst(
						""
					+ str(Parameter1.QUERY_CRITERIA_1)
					+ "  SAQITM SET STATUS=''ACQUIRED'' FROM SAQRIT SAQITM (NOLOCK) WHERE QUOTE_REVISION_CONTRACT_ITEM_ID IN (SELECT DISTINCT QTEITM_RECORD_ID FROM SAQICO_INBOUND(NOLOCK)A JOIN SAQICO B(NOLOCK) ON A.QUOTE_ID= B.QUOTE_ID AND A.SERVICE_ID = B.SERVICE_ID AND A.EQUIPMENT_ID = B.EQUIPMENT_ID  WHERE ISNULL(PROCESS_STATUS,'''')=''INPROGRESS'' AND TIMESTAMP = '"+str(timestamp_sessionid)+"' AND B.STATUS=''ACQUIRED'') AND SERVICE_ID IN (SELECT DISTINCT SERVICE_ID FROM PRSPRV(NOLOCK) WHERE ISNULL(SSCM_COST,''FALSE'')=''TRUE'' )  '")

					primaryQueryItems = SqlHelper.GetFirst(
						""
					+ str(Parameter1.QUERY_CRITERIA_1)
					+ "  SAQITM SET STATUS=''ERROR'' FROM SAQRIT SAQITM (NOLOCK) WHERE QUOTE_REVISION_CONTRACT_ITEM_ID IN (SELECT DISTINCT QTEITM_RECORD_ID FROM SAQICO(NOLOCK)  WHERE QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND STATUS IN (''ERROR'',''ASSEMBLY IS MISSING'')) AND SERVICE_ID IN (SELECT DISTINCT SERVICE_ID FROM PRSPRV(NOLOCK) WHERE ISNULL(SSCM_COST,''FALSE'')=''TRUE'' )  '")

					primaryQueryItems = SqlHelper.GetFirst(
						""
					+ str(Parameter1.QUERY_CRITERIA_1)
					+ "  SAQTRV SET REVISION_STATUS=''ON HOLD - COSTING'' FROM SAQTRV A(NOLOCK) JOIN (SELECT DISTINCT QUOTE_ID,QTEREV_ID FROM SAQICO B(NOLOCK)  WHERE  STATUS  IN (''PARTIALLY PRICED'',''ERROR'',''ASSEMBLY IS MISSING'') AND QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'')B ON A.QUOTE_ID = B.QUOTE_ID AND A.QTEREV_ID = B.QTEREV_ID '")

					primaryQueryItems = SqlHelper.GetFirst(
						""
					+ str(Parameter1.QUERY_CRITERIA_1)
					+ "  SAQTRV SET REVISION_STATUS=''APPROVAL PENDING'' FROM SAQTRV A(NOLOCK) WHERE QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND NOT EXISTS (SELECT ''X'' FROM SAQICO B(NOLOCK)  WHERE  STATUS IN(''PARTIALLY PRICED'',''ERROR'',''ASSEMBLY IS MISSING'') AND QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'') '")

					quote_revision_object = SqlHelper.GetFirst("SELECT QUOTE_RECORD_ID, QTEREV_RECORD_ID FROM SAQTRV WHERE QUOTE_ID = '"+str(Qt_Id.QUOTE_ID)+"' AND QTEREV_ID = '"+str(Qt_Id.REVISION_ID)+"' ")

					##Calling the iflow script to update the details in c4c..(cpq to c4c write back...)
					CQCPQC4CWB.writeback_to_c4c("quote_header",quote_revision_object.QUOTE_RECORD_ID,quote_revision_object.QTEREV_RECORD_ID)
					CQCPQC4CWB.writeback_to_c4c("opportunity_header",quote_revision_object.QUOTE_RECORD_ID,quote_revision_object.QTEREV_RECORD_ID)
					
					primaryQueryItems = SqlHelper.GetFirst(
						""
					+ str(Parameter1.QUERY_CRITERIA_1)
					+ "  SAQICO SET STATUS=''ACQUIRED'' FROM SAQICO (NOLOCK) JOIN SAQICA(NOLOCK) ON SAQICO.QUOTE_ID = SAQICA.QUOTE_ID AND SAQICO.SERVICE_ID = SAQICA.SERVICE_ID AND SAQICO.QTEREV_ID = SAQICA.QTEREV_ID AND SAQICO.EQUIPMENT_ID = SAQICA.EQUIPMENT_ID JOIN SAQICO_INBOUND C(NOLOCK)ON SAQICO.QUOTE_ID = C.QUOTE_ID AND SAQICO.QTEREV_ID = C.REVISION_ID  AND SAQICO.SERVICE_ID = C.SERVICE_ID AND SAQICO.EQUIPMENT_ID = C.EQUIPMENT_ID WHERE TIMESTAMP = '"+str(timestamp_sessionid)+"' AND STATUS NOT IN (''PARTIALLY PRICED'',''ERROR'',''ASSEMBLY IS MISSING'') '")

					primaryQueryItems = SqlHelper.GetFirst(
						""
					+ str(Parameter1.QUERY_CRITERIA_1)
					+ "  SAQITM SET STATUS=''PRICED'' FROM SAQRIT SAQITM (NOLOCK) WHERE QUOTE_REVISION_CONTRACT_ITEM_ID NOT IN (SELECT QTEITM_RECORD_ID FROM SAQICO B(NOLOCK) WHERE QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND STATUS IN (''PARTIALLY PRICED'',''ERROR'',''ASSEMBLY IS MISSING'')) AND STATUS NOT IN (''ON HOLD - COSTING'',''ON HOLD - PRICING'',''ACQUIRING'',''PARTIALLY PRICED'',''ERROR'',''ASSEMBLY IS MISSING'') '")
					
					primaryQueryItems = SqlHelper.GetFirst(
						""
					+ str(Parameter1.QUERY_CRITERIA_1)
					+ "  SAQICO SET STATUS=''ACQUIRED'' FROM SAQICO (NOLOCK) JOIN SAQICA(NOLOCK) ON SAQICO.QUOTE_ID = SAQICA.QUOTE_ID AND SAQICO.SERVICE_ID = SAQICA.SERVICE_ID AND SAQICO.QTEREV_ID = SAQICA.QTEREV_ID AND SAQICO.EQUIPMENT_ID = SAQICA.EQUIPMENT_ID JOIN SAQICO_INBOUND C(NOLOCK)ON SAQICO.QUOTE_ID = C.QUOTE_ID AND SAQICO.QTEREV_ID = C.REVISION_ID  AND SAQICO.SERVICE_ID = C.SERVICE_ID AND SAQICO.EQUIPMENT_ID = C.EQUIPMENT_ID WHERE TIMESTAMP = '"+str(timestamp_sessionid)+"' AND STATUS NOT IN (''PARTIALLY PRICED'',''ERROR'',''ASSEMBLY IS MISSING'') '")
					
					primaryQueryItems = SqlHelper.GetFirst(
						""
					+ str(Parameter1.QUERY_CRITERIA_1)
					+ "  SAQITM SET STATUS=''PRICED'' FROM SAQRIT SAQITM (NOLOCK) WHERE QUOTE_REVISION_CONTRACT_ITEM_ID NOT IN (SELECT QTEITM_RECORD_ID FROM SAQICO B(NOLOCK) WHERE QUOTE_ID = ''"+str(Qt_Id.QUOTE_ID)+"'' AND QTEREV_ID = ''"+str(Qt_Id.REVISION_ID)+"'' AND STATUS IN (''PARTIALLY PRICED'',''ERROR'',''ASSEMBLY IS MISSING'')) AND STATUS NOT IN (''ON HOLD - COSTING'',''ON HOLD - PRICING'',''ACQUIRING'',''PARTIALLY PRICED'',''ERROR'',''ASSEMBLY IS MISSING'') '")

					#Status Completed in SYINPL by CPQ Table Entry ID
					StatusUpdateQuery = SqlHelper.GetFirst(""+ str(Parameter1.QUERY_CRITERIA_1)+ "  SYINPL SET STATUS = ''COMPLETED'' FROM SYINPL (NOLOCK) A WHERE CpqTableEntryId = ''"+str(json_data.CpqTableEntryId)+"'' AND SESSION_ID =''"+str(SYINPL_SESSION.A)+"'' ' ")

					StatusUpdateQuery = SqlHelper.GetFirst(""+ str(Parameter2.QUERY_CRITERIA_1)+ " FROM SAQICO_INBOUND  WHERE ISNULL(SESSION_ID,'''')=''"+str(sessiondetail.A)+ "'' ' ")

					SAQIEN_DRP = SqlHelper.GetFirst("sp_executesql @T=N'IF EXISTS (SELECT ''X'' FROM SYS.OBJECTS WHERE NAME= ''"+str(SAQIEN)+"'' ) BEGIN DROP TABLE "+str(SAQIEN)+" END  ' ")
					
					CRMTMP_DRP = SqlHelper.GetFirst("sp_executesql @T=N'IF EXISTS (SELECT ''X'' FROM SYS.OBJECTS WHERE NAME= ''"+str(CRMTMP)+"'' ) BEGIN DROP TABLE "+str(CRMTMP)+" END  ' ")
					
					Log.Info("QTPOSTQTPR pricing async call End --->"+str(Qt_Id.QUOTE_ID))
					# Mail system				
					Header = "<!DOCTYPE html><html><head><style>table {font-family: Calibri, sans-serif; border-collapse: collapse; width: 75%}td, th {  border: 1px solid #dddddd;  text-align: left; padding: 8px;}.im {color: #222;}tr:nth-child(even) {background-color: #dddddd;} #grey{background: rgb(245,245,245);} #bd{color : 'black';} </style></head><body id = 'bd'>"

					Table_start = "<p>Hi Team,<br><br>Pricing has been completed in CPQ, for the equipment's in below Quote ID.</p><table class='table table-bordered'><tr><th id = 'grey'>Quote ID</th><th id = 'grey'>Tools sent (CPQ-SSCM)</th><th id = 'grey'>Tools received (SSCM-CPQ)</th><th id = 'grey'>Price Calculation Status</th></tr><tr><td >"+str(Emailinfo.QUOTE_ID)+"</td><td>"+str(Emailinfo.SSCM)+"</td ><td>"+str(Emailinfo1.CPQ)+"</td><td>Completed</td></tr>"

					Table_info = ""
					Table_End = "</table><p><strong>Note : </strong>Please do not reply to this email.</p></body></html>"

					Error_Info = Header + Table_start + Table_info + Table_End

					LOGIN_CRE = SqlHelper.GetFirst("SELECT USER_NAME as Username,Password FROM SYCONF where Domain ='SUPPORT_MAIL'")

					# Create new SmtpClient object
					mailClient = SmtpClient()

					# Set the host and port (eg. smtp.gmail.com)
					mailClient.Host = "smtp.gmail.com"
					mailClient.Port = 587
					mailClient.EnableSsl = "true"

					# Setup NetworkCredential
					mailCred = NetworkCredential()
					mailCred.UserName = str(LOGIN_CRE.Username)
					mailCred.Password = str(LOGIN_CRE.Password)
					mailClient.Credentials = mailCred

					#Current user email(Toemail)
					#UserId = User.Id
					#Log.Info("123 UserId.UserId --->"+str(UserId))
					UserEmail = SqlHelper.GetFirst("SELECT isnull(email,'"+str(LOGIN_CRE.Username)+"') as email FROM saempl (nolock) where employee_id  = '"+str(ToEml.OWNER_ID)+"'")
					#Log.Info("123 UserEmail.email --->"+str(UserEmail.email))

					# Create two mail adresses, one for send from and the another for recipient
					if UserEmail is None:
						toEmail = MailAddress("suresh.muniyandi@bostonharborconsulting.com")
					else:
						toEmail = MailAddress(UserEmail.email)
					fromEmail = MailAddress(str(LOGIN_CRE.Username))

					# Create new MailMessage object
					msg = MailMessage(fromEmail, toEmail)

					# Set message subject and body
					msg.Subject = "Pricing Completed - AMAT CPQ(X-Tenant)"
					msg.IsBodyHtml = True
					msg.Body = Error_Info

					# Bcc Emails	
					copyEmail4 = MailAddress("baji.baba@bostonharborconsulting.com")
					msg.Bcc.Add(copyEmail4)

					copyEmail6 = MailAddress("suresh.muniyandi@bostonharborconsulting.com")
					msg.Bcc.Add(copyEmail6)

					# Send the message
					mailClient.Send(msg)


					Greenbkquery=SqlHelper.GetList("SELECT DISTINCT SAQICO.GREENBOOK,ISNULL(SABUUN.DISTRIBUTION_EMAIL,'') AS DISTRIBUTION_EMAIL  FROM SAQICO(NOLOCK) JOIN SABUUN (NOLOCK) ON SAQICO.GREENBOOK = SABUUN.BUSINESSUNIT_ID WHERE SAQICO.STATUS IN ('ERROR','PARTIALLY PRICED','ASSEMBLY IS MISSING') AND SAQICO.QUOTE_ID = '"+str(Qt_Id.QUOTE_ID)+"' AND SAQICO.QTEREV_ID = '"+str(Qt_Id.REVISION_ID)+"' ")

					for Gbk in Greenbkquery:


						Grnbkdataquery=SqlHelper.GetList("SELECT SAQICO.GREENBOOK,SAQICO.QUOTE_ID,SAQICO.SERVICE_ID,SAQICO.EQUIPMENT_ID,SAQICA.ASSEMBLY_ID,SAQICA.COST_MODULE_AVAILABLE,ISNULL(SAQICA.COST_MODULE_STATUS,'ASSEMBLY IS MISSING') AS COST_MODULE_STATUS FROM SAQICO (NOLOCK) JOIN SAQICA (NOLOCK) ON SAQICO.QUOTE_ID = SAQICA.QUOTE_ID AND SAQICO.QTEREV_ID = SAQICA.QTEREV_ID AND SAQICO.SERVICE_ID = SAQICA.SERVICE_ID AND SAQICO.EQUIPMENT_ID = SAQICA.EQUIPMENT_ID WHERE SAQICO.STATUS IN ('ERROR','PARTIALLY PRICED' ) AND SAQICO.GREENBOOK= '"+str(Gbk.GREENBOOK)+"' AND SAQICO.QUOTE_ID = '"+str(Qt_Id.QUOTE_ID)+"' AND SAQICO.QTEREV_ID = '"+str(Qt_Id.REVISION_ID)+"' AND  SAQICA.COST_MODULE_AVAILABLE= 'UNAVAILABLE' AND SAQICA.COST_MODULE_STATUS <>'Chamber map not required' UNION ALL SELECT SAQICO.GREENBOOK,SAQICO.QUOTE_ID,SAQICO.SERVICE_ID,SAQICO.EQUIPMENT_ID,'' AS ASSEMBLY_ID,'' AS COST_MODULE_AVAILABLE,'ASSEMBLY IS MISSING' AS COST_MODULE_STATUS FROM SAQICO (NOLOCK)  WHERE SAQICO.STATUS IN ('ASSEMBLY IS MISSING' ) AND SAQICO.GREENBOOK= '"+str(Gbk.GREENBOOK)+"' AND SAQICO.QUOTE_ID = '"+str(Qt_Id.QUOTE_ID)+"' AND SAQICO.QTEREV_ID = '"+str(Qt_Id.REVISION_ID)+"' ")

						tbl_info = ''
						for gbkinfo in Grnbkdataquery:
							tbl_info = tbl_info+"<tr><td>"+str(gbkinfo.SERVICE_ID)+"</td><td>"+str(gbkinfo.GREENBOOK)+"</td ><td>"+str(gbkinfo.EQUIPMENT_ID)+"</td><td>"+str(gbkinfo.ASSEMBLY_ID)+"</td><td>"+str(gbkinfo.COST_MODULE_AVAILABLE)+"</td><td>"+str(gbkinfo.COST_MODULE_STATUS)+"</td></tr>"
						if len(tbl_info) > 0:
							Header = "<!DOCTYPE html><html><head><style>table {font-family: Calibri, sans-serif; border-collapse: collapse; width: 75%}td, th {  border: 1px solid #dddddd;  text-align: left; padding: 8px;}.im {color: #222;}tr:nth-child(even) {background-color: #dddddd;} #grey{background: rgb(245,245,245);} #bd{color : 'black';} </style></head><body id = 'bd'>"

							Table_start = "<p>Hi Team,<br><br>This Quote "+str(Qt_Id.QUOTE_ID)+"  is placed on ON HOLD COSTING status for the below cost information pending from SSCM system or Assembly missing in CPQ from IBASE.</p><table class='table table-bordered'><tr><th id = 'grey'>Service ID</th><th id = 'grey'>Green Book</th><th id = 'grey'>Equipment ID</th><th id = 'grey'>Assembly ID</th><th id = 'grey'>Cost Module Available</th><th id = 'grey'>Cost Module Status</th></tr>"+str(tbl_info)

							Table_info = ""
							Table_End = "</table><p><strong>Note : </strong>Please do not reply to this email.</p></body></html>"

							Error_Info = Header + Table_start + Table_info + Table_End

							LOGIN_CRE = SqlHelper.GetFirst("SELECT USER_NAME as Username,Password FROM SYCONF where Domain ='SUPPORT_MAIL'")

							# Create new SmtpClient object
							mailClient = SmtpClient()

							# Set the host and port (eg. smtp.gmail.com)
							mailClient.Host = "smtp.gmail.com"
							mailClient.Port = 587
							mailClient.EnableSsl = "true"

							# Setup NetworkCredential
							mailCred = NetworkCredential()
							mailCred.UserName = str(LOGIN_CRE.Username)
							mailCred.Password = str(LOGIN_CRE.Password)
							mailClient.Credentials = mailCred

							UserEmail = []
							if len(Gbk.DISTRIBUTION_EMAIL) > 0:
								UserEmail = str(Gbk.DISTRIBUTION_EMAIL).split(';')

							if len(UserEmail) == 0:
									toEmail = MailAddress("suresh.muniyandi@bostonharborconsulting.com")
							else:								
								toEmail = MailAddress(UserEmail[0])
							
							fromEmail = MailAddress(str(LOGIN_CRE.Username))	

							# Create new MailMessage object
							msg = MailMessage(fromEmail, toEmail)							

							# Set message subject and body
							sub = "On Hold - Costing Quote("+str(Gbk.GREENBOOK)+")- AMAT CPQ (X-Tenant)"
							msg.Subject = sub
							msg.IsBodyHtml = True
							msg.Body = Error_Info

							#Comon CC mails
							copyEmail = MailAddress("suresh.muniyandi@bostonharborconsulting.com")
							msg.CC.Add(copyEmail)					

							copyEmail5 = MailAddress("baji.baba@bostonharborconsulting.com")
							msg.CC.Add(copyEmail5) 

							# Bcc Emails	
							if len(UserEmail) > 0:
								for emalinfo in  UserEmail:
									copyEmail = MailAddress(emalinfo)
									msg.Bcc.Add(copyEmail)

							# Send the message QT_REC_ID
							mailClient.Send(msg)
					#opening quote for update quote items
					try:
						quote_Edit = QuoteHelper.Edit(Qt_Id.QUOTE_ID)
					except:
						Log.Info("quote error")
					CallingCQIFWUDQTM = ScriptExecutor.ExecuteGlobal("CQIFWUDQTM",{"QT_REC_ID":Qt_Id.QUOTE_ID})	
					# Billing matrix async call
					LOGIN_CREDENTIALS = SqlHelper.GetFirst("SELECT USER_NAME as Username,Password,Domain FROM SYCONF where Domain='AMAT_TST'")

					if LOGIN_CREDENTIALS is not None:
						Login_Username = str(LOGIN_CREDENTIALS.Username)
						Login_Password = str(LOGIN_CREDENTIALS.Password)
						authorization = Login_Username+":"+Login_Password
						binaryAuthorization = UTF8.GetBytes(authorization)
						authorization = Convert.ToBase64String(binaryAuthorization)
						authorization = "Basic " + authorization


						webclient = System.Net.WebClient()
						webclient.Headers[System.Net.HttpRequestHeader.ContentType] = "application/json"
						webclient.Headers[System.Net.HttpRequestHeader.Authorization] = authorization;
						
						result = '''<?xml version="1.0" encoding="UTF-8"?><soapenv:Envelope	xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">	<soapenv:Body><CPQ_Columns>	<QUOTE_ID>{Qt_Id}</QUOTE_ID><REVISION_ID>{Rev_Id}</REVISION_ID></CPQ_Columns></soapenv:Body></soapenv:Envelope>'''.format( Qt_Id= quote_revision_object.QUOTE_RECORD_ID,Rev_Id = quote_revision_object.QTEREV_RECORD_ID)
						
						LOGIN_CRE = SqlHelper.GetFirst("SELECT URL FROM SYCONF where EXTERNAL_TABLE_NAME ='BILLING_MATRIX_ASYNC'")
						Async = webclient.UploadString(str(LOGIN_CRE.URL), str(result))

						level = "QT_QTQICO LEVEL"
						try:
							CQVLDRIFLW.iflow_valuedriver_rolldown(str(Emailinfo.QUOTE_RECORD_ID),level)
						except:
							Log.Info('Quote error')
					
					
					Unprocsseddataquery = SqlHelper.GetFirst("SELECT count(*) as cnt from SYINPL(NOLOCK) WHERE INTEGRATION_NAME = 'SSCM_TO_CPQ_PRICING_DATA' AND ISNULL(STATUS,'') = '' ")	

					if Unprocsseddataquery.cnt > 0 :
						#Async call for SSCM TO CPQ Unprocessed data 
						LOGIN_CREDENTIALS = SqlHelper.GetFirst("SELECT USER_NAME as Username,Password,Domain FROM SYCONF where Domain='AMAT_TST'")
						if LOGIN_CREDENTIALS is not None:
							Login_Username = str(LOGIN_CREDENTIALS.Username)
							Login_Password = str(LOGIN_CREDENTIALS.Password)
							authorization = Login_Username+":"+Login_Password
							binaryAuthorization = UTF8.GetBytes(authorization)
							authorization = Convert.ToBase64String(binaryAuthorization)
							authorization = "Basic " + authorization


							webclient = System.Net.WebClient()
							webclient.Headers[System.Net.HttpRequestHeader.ContentType] = "application/json"
							webclient.Headers[System.Net.HttpRequestHeader.Authorization] = authorization;
							
							result = '<?xml version="1.0" encoding="UTF-8"?><soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"><soapenv:Body ></soapenv:Body></soapenv:Envelope>'
							
							LOGIN_CRE = SqlHelper.GetFirst("SELECT URL FROM SYCONF where EXTERNAL_TABLE_NAME ='CPQ_TO_SSCM_PRICING_ASYNC'")
							Async = webclient.UploadString(str(LOGIN_CRE.URL), str(result))
					else: 
						ApiResponse = ApiResponseFactory.JsonResponse({"Response": [{"Status": "200", "Message": "Data Successfully Uploaded"}]})
				else:
					if Saqico_Flag == 0:
						Header = "<!DOCTYPE html><html><head><style>table {font-family: Calibri, sans-serif; border-collapse: collapse; width: 75%}td, th {  border: 1px solid #dddddd;  text-align: left; padding: 8px;}.im {color: #222;}tr:nth-child(even) {background-color: #dddddd;} #bd{color : 'black';} </style></head><body id = 'bd'>"

						Table_start = "<p>Hi Team,<br><br>SSCM Pricing script having follwing SAQICO data error for following Quote Id ---  "+str(Qt_Id.QUOTE_ID)+".<br><br></p><br>"
						
						Table_End = "</table><p><strong>Note : </strong>Please do not reply to this email.</p></body></html>"
						Table_info = ""     

						Error_Info = Header + Table_start + Table_info + Table_End

						LOGIN_CRE = SqlHelper.GetFirst("SELECT USER_NAME as Username,Password FROM SYCONF where Domain ='SUPPORT_MAIL'")

						# Create new SmtpClient object
						mailClient = SmtpClient()

						# Set the host and port (eg. smtp.gmail.com)
						mailClient.Host = "smtp.gmail.com"
						mailClient.Port = 587
						mailClient.EnableSsl = "true"

						# Setup NetworkCredential
						mailCred = NetworkCredential()
						mailCred.UserName = str(LOGIN_CRE.Username)
						mailCred.Password = str(LOGIN_CRE.Password)
						mailClient.Credentials = mailCred

						# Create two mail adresses, one for send from and the another for recipient
						toEmail = MailAddress("suresh.muniyandi@bostonharborconsulting.com")
						fromEmail = MailAddress(str(LOGIN_CRE.Username))

						# Create new MailMessage object
						msg = MailMessage(fromEmail, toEmail)

						# Set message subject and body
						msg.Subject = "SSCM to CPQ - SAQICO Error Notification(X-Tenant)"
						msg.IsBodyHtml = True
						msg.Body = Error_Info

						# CC Emails 	
						copyEmail4 = MailAddress("baji.baba@bostonharborconsulting.com")
						msg.CC.Add(copyEmail4)
						
						copyEmail5 = MailAddress("suresh.muniyandi@bostonharborconsulting.com")
						msg.CC.Add(copyEmail5) 					

						# Send the message
						mailClient.Send(msg)
					if Check_flag == 1:
						#Status Empty in SYINPL
						StatusUpdateQuery = SqlHelper.GetFirst(""+ str(Parameter1.QUERY_CRITERIA_1)+ "  A SET STATUS = ''Hold'' FROM SYINPL (NOLOCK) A WHERE SESSION_ID=''"+str(SYINPL_SESSION.A)+"''   AND  STATUS = ''INPROGRESS'' '")
	else:
		ApiResponse = ApiResponseFactory.JsonResponse({"Response": [{"Status": "200", "Message": "Session is running.Status is Inprogress"}]})
		

except:
	#Status Empty in SYINPL
	StatusUpdateQuery = SqlHelper.GetFirst(""+ str(Parameter1.QUERY_CRITERIA_1)+ "  A SET STATUS = '''' FROM SYINPL (NOLOCK) A WHERE SESSION_ID=''"+str(SYINPL_SESSION.A)+"''  ' ")
				
	Header = "<!DOCTYPE html><html><head><style>table {font-family: Calibri, sans-serif; border-collapse: collapse; width: 75%}td, th {  border: 1px solid #dddddd;  text-align: left; padding: 8px;}.im {color: #222;}tr:nth-child(even) {background-color: #dddddd;} #bd{color : 'black';} </style></head><body id = 'bd'>"

	Table_start = "<p>Hi Team,<br><br>SSCM Pricing script having follwing Error in Line number "+str(sys.exc_info()[-1].tb_lineno)+".<br><br>"+str(sys.exc_info()[1])+"</p><br>"
	
	Table_End = "</table><p><strong>Note : </strong>Please do not reply to this email.</p></body></html>"
	Table_info = ""     

	Error_Info = Header + Table_start + Table_info + Table_End

	LOGIN_CRE = SqlHelper.GetFirst("SELECT USER_NAME as Username,Password FROM SYCONF where Domain ='SUPPORT_MAIL'")

	# Create new SmtpClient object
	mailClient = SmtpClient()

	# Set the host and port (eg. smtp.gmail.com)
	mailClient.Host = "smtp.gmail.com"
	mailClient.Port = 587
	mailClient.EnableSsl = "true"

	# Setup NetworkCredential
	mailCred = NetworkCredential()
	mailCred.UserName = str(LOGIN_CRE.Username)
	mailCred.Password = str(LOGIN_CRE.Password)
	mailClient.Credentials = mailCred

	# Create two mail adresses, one for send from and the another for recipient
	toEmail = MailAddress("suresh.muniyandi@bostonharborconsulting.com")
	fromEmail = MailAddress(str(LOGIN_CRE.Username))

	# Create new MailMessage object
	msg = MailMessage(fromEmail, toEmail)

	# Set message subject and body
	msg.Subject = "SSCM to CPQ - Pricing Error Notification(X-Tenant)"
	msg.IsBodyHtml = True
	msg.Body = Error_Info

	# CC Emails 	
	copyEmail4 = MailAddress("baji.baba@bostonharborconsulting.com")
	msg.CC.Add(copyEmail4)

	copyEmail5 = MailAddress("suresh.muniyandi@bostonharborconsulting.com")
	msg.CC.Add(copyEmail5)
	
	# Send the message
	mailClient.Send(msg) 
	
	Log.Info("QTPOSTQTPR ERROR---->:" + str(sys.exc_info()[1]))
	Log.Info("QTPOSTQTPR ERROR LINE NO---->:" + str(sys.exc_info()[-1].tb_lineno))
	ApiResponse = ApiResponseFactory.JsonResponse({"Response": [{"Status": "400", "Message": str(sys.exc_info()[1])}]})