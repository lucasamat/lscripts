# =========================================================================================================================================
#   __script_name : CQSTSVADTN.PY
#   __script_description : THIS SCRIPT IS USED TO CHANGE THE REVISION STATUS/WORKFLOW STATUS, TRIGGER INSERT QUOTE ITEMS AND SSCM PRICING SCRIPTS
#   __primary_author__ : DHURGA
#   __create_date :13-10-2021
# ==========================================================================================================================================
import re
import Webcom.Configurator.Scripting.Test.TestProduct
from SYDATABASE import SQL
import CQPARTIFLW
import CQCPQC4CWB
import time
import System.Net
from System import Convert
from System.Text.Encoding import UTF8
Sql = SQL()
TestProduct = Webcom.Configurator.Scripting.Test.TestProduct() or "Sales"
import CQREVSTSCH
try:
    contract_quote_record_id = Quote.QuoteId
except:
    contract_quote_record_id = ''
try:
    contract_quote_rec_id = Quote.GetGlobal("contract_quote_record_id")
except:
    contract_quote_rec_id = ''
try:
    quote_revision_record_id = Quote.GetGlobal("quote_revision_record_id")	
except:
    quote_revision_record_id =  ""
try:
    current_prod = Product.Name	
except:
    current_prod = "Sales"
try:
    TabName = TestProduct.CurrentTab
except:
    TabName = "Quotes"

try:
    quote_revision_rec_id = Quote.GetGlobal("quote_revision_record_id")
except:
    Trace.Write("Quote Not Loaded")
user_id = str(User.Id)
user_name = str(User.UserName) 



get_flag_Status = Sql.GetFirst("SELECT REVISION_STATUS,MODVRS_DIRTY_FLAG FROM SAQTRV (NOLOCK) WHERE QUOTE_RECORD_ID = '{}' AND QTEREV_RECORD_ID = '{}'".format(contract_quote_rec_id,quote_revision_record_id))

def Dynamic_Status_Bar(quote_item_insert,Text):
    status =''
    error_msg = ""
    oppurtunity_writeback = ""
    revision_status = ""
    revision_flag = ""
    exchng_rateflag = False  #INC08614363 - A
    quote_revision_record_id = Quote.GetGlobal("quote_revision_record_id")
    get_quality_required = Sql.GetFirst("SELECT COUNT(CPQTABLEENTRYADDEDBY) as CNT FROM SAQFBL where QUOTE_RECORD_ID = '{}' AND QTEREV_RECORD_ID = '{}' AND (ISNULL(QUALITY_REQUIRED,'') = '' or QUALITY_REQUIRED ='Select')".format(Quote.GetGlobal("contract_quote_record_id"),Quote.GetGlobal("quote_revision_record_id")))
    # removing underscore in the ibase status column will enable retain in configure stage. Temporarily changed for disabling
    get_ibase_missing = Sql.GetFirst("SELECT COUNT(CpqTableEntryId) as CNT FROM SAQSCO WHERE QUOTE_RECORD_ID = '{}' AND QTEREV_RECORD_ID = '{}' AND IBASE_ATTSTS = 'INCOMPLETE'  ".format(Quote.GetGlobal("contract_quote_record_id"),quote_revision_record_id))
    #INC08614363 - A
    #A055S000P01-20612 start A
    get_ibase_no_assembly = Sql.GetFirst("SELECT COUNT(CpqTableEntryId) as CNT FROM SAQSCO WHERE QUOTE_RECORD_ID = '{}' AND QTEREV_RECORD_ID = '{}' AND IBASE_ATTSTS ='NO ASSEMBLY'".format(Quote.GetGlobal("contract_quote_record_id"),quote_revision_record_id))
    req_event_missing = Sql.GetFirst("SELECT COUNT(CpqTableEntryId) as CNT FROM SAQSCO (NOLOCK) WHERE QUOTE_RECORD_ID = '{}' AND QTEREV_RECORD_ID = '{}' AND IBASE_ATTSTS = 'REQUIRED EVENT IS MISSING'  ".format(Quote.GetGlobal("contract_quote_record_id"),quote_revision_record_id))
    Trace.Write("req_event_missing="+str(req_event_missing))
    #A055S000P01-20612 end A
    get_exchangerate=Sql.GetFirst("SELECT EXCHANGE_RATE FROM SAQTRV WHERE QUOTE_RECORD_ID = '"+str(Quote.GetGlobal("contract_quote_record_id"))+"' AND QTEREV_RECORD_ID = '"+str(quote_revision_record_id)+"' ")
    #A055S000P01-20612 start A
    if get_quality_required.CNT != 0 or get_ibase_missing.CNT!=0 or req_event_missing.CNT!=0 or get_ibase_no_assembly.CNT!=0  or not get_exchangerate.EXCHANGE_RATE:
        #A055S000P01-20612 end A
        #INC08614363 - A
        update_workflow_status_conf = "UPDATE SAQTRV SET REVISION_STATUS = 'CFG-CONFIGURING',WORKFLOW_STATUS = 'CONFIGURE' WHERE QUOTE_RECORD_ID = '{QuoteRecordId}' and QTEREV_RECORD_ID = '{RevisionRecordId}' ".format(QuoteRecordId=Quote.GetGlobal("contract_quote_record_id"),RevisionRecordId = quote_revision_record_id)	
        Sql.RunQuery(update_workflow_status_conf)
        status = "CFG_CONFIGURING_STATUS"
    #INC08614363 - A
    #A055S000P01-20612 start A
    if str(Text) == 'COMPLETE STAGE' and (str(TabName) == "Quotes" or str(TabName) == "Quote") and current_prod == "Sales" and  get_quality_required.CNT == 0 and get_ibase_missing.CNT==0 and req_event_missing.CNT==0 and get_ibase_no_assembly.CNT==0 and get_exchangerate.EXCHANGE_RATE:
        #A055S000P01-20612 end A
        #INC08614363 - A
        #Salesorg[SAQTRV]
        getsalesorg_info = Sql.GetFirst("SELECT SALESORG_ID,REVISION_STATUS from SAQTRV where QUOTE_RECORD_ID = '{}' AND QTEREV_RECORD_ID = '{}'".format(Quote.GetGlobal("contract_quote_record_id"),quote_revision_record_id))

        #Product offerring[SAQTSV] 
        get_service_info = Sql.GetFirst("SELECT COUNT(DISTINCT SERVICE_ID) as COUNT from SAQTSV where QUOTE_RECORD_ID = '{}' AND QTEREV_RECORD_ID = '{}'".format(Quote.GetGlobal("contract_quote_record_id"),quote_revision_record_id))

        #Fab Location[SAQFBL]
        get_fab_info = Sql.GetFirst("SELECT COUNT(DISTINCT FABLOCATION_ID) as COUNT from SAQFBL where QUOTE_RECORD_ID = '{}' AND QTEREV_RECORD_ID = '{}'".format(Quote.GetGlobal("contract_quote_record_id"),quote_revision_record_id))
    
        #Involved Parties[SAQTIP] 
        get_involved_parties_info = Sql.GetFirst("SELECT COUNT(DISTINCT PARTY_ID) as COUNT from SAQTIP where QUOTE_RECORD_ID = '{}' AND QTEREV_RECORD_ID = '{}'".format(Quote.GetGlobal("contract_quote_record_id"),quote_revision_record_id))

        #Sales Team[SAQDLT]
        get_sales_team_info = Sql.GetFirst("SELECT COUNT(DISTINCT C4C_PARTNERFUNCTION_ID) as COUNT from SAQDLT where QUOTE_RECORD_ID = '{}' AND QTEREV_RECORD_ID = '{}' AND (C4C_PARTNERFUNCTION_ID = 'BD' OR C4C_PARTNERFUNCTION_ID = 'CONTRACT MANAGER' OR C4C_PARTNERFUNCTION_ID = 'PRICING PERSON' )".format(Quote.GetGlobal("contract_quote_record_id"),quote_revision_record_id))
        
        #VC offerring[SAQTSE]
        get_complete_list = []
        get_vc_offerring_info = Sql.GetList(" SELECT  CONFIGURATION_STATUS,SERVICE_ID  FROM SAQSGE WHERE QUOTE_RECORD_ID = '{}' AND QTEREV_RECORD_ID = '{}' and CONFIGURATION_STATUS = 'COMPLETE' ".format(Quote.GetGlobal("contract_quote_record_id"),quote_revision_record_id))
        if get_vc_offerring_info:
            for val in get_vc_offerring_info:
                if  val.CONFIGURATION_STATUS:
                    status = val.CONFIGURATION_STATUS
                    if status == "COMPLETE" and status != "":				
                        get_complete_list.append('T')
                    else:
                        get_complete_list.append('F')
                else:
                    get_complete_list.append('F')
        else:
            get_complete_list.append('F')
        #get_equip_details = Sql.GetFirst("SELECT COUNT(DISTINCT SERVICE_ID) as SERVICE_ID from SAQSCO where QUOTE_RECORD_ID = '{}' AND QTEREV_RECORD_ID = '{}'".format(Quote.GetGlobal("contract_quote_record_id"),quote_revision_record_id))
        #For Tool Based Quotes[SAQTSV]		
        get_tool_service_info = Sql.GetList("SELECT DISTINCT SERVICE_ID as SERVICE_ID from SAQTSV(NOLOCK) where QUOTE_RECORD_ID = '{}' AND QTEREV_RECORD_ID = '{}'".format(Quote.GetGlobal("contract_quote_record_id"),quote_revision_record_id))
        #get_quality_required start validations#A055S000P01-18587

        #get_quality_required  vlidations-end3A055S000P01-18587
        tool_check = []
        Z0110_check = []
            #return status,error_msg
        for tserv in get_tool_service_info:
        
            if str(tserv.SERVICE_ID) in ('Z0004', 'Z0004W', 'Z0009-TOOL', 'Z0010-TOOL', 'Z0035', 'Z0035W', 'Z0090', 'Z0091', 'Z0091W', 'Z0092', 'Z0092W', 'Z0099'):
            
                #Tools service[SAQSCO]
                get_tools_info = Sql.GetFirst("SELECT COUNT(DISTINCT SERVICE_ID) as COUNT from SAQSCO(NOLOCK) where QUOTE_RECORD_ID = '{}' AND QTEREV_RECORD_ID = '{}' AND SERVICE_ID = '{}' ".format(Quote.GetGlobal("contract_quote_record_id"),quote_revision_record_id,tserv.SERVICE_ID))
                if get_tools_info:
                    if get_tools_info.COUNT > 0:				
                        tool_check.append('T')				
                    else:
                        tool_check.append('F')
                else:
                    tool_check.append('F')
                
            elif str(tserv.SERVICE_ID).upper() == 'Z0110':
                tool_check.append('T')
                
                get_consigned_parts = Sql.GetFirst("select ENTITLEMENT_XML from SAQITE where QUOTE_RECORD_ID = '{qtid}' AND QTEREV_RECORD_ID = '{qt_rev_id}' and SERVICE_ID = '{get_service}'".format(qtid =contract_quote_rec_id,qt_rev_id=quote_revision_rec_id,get_service = str(tserv.SERVICE_ID).strip()))
                if get_consigned_parts:
                    updateentXML = get_consigned_parts.ENTITLEMENT_XML
                    pattern_tag = re.compile(r'(<QUOTE_ITEM_ENTITLEMENT>[\w\W]*?</QUOTE_ITEM_ENTITLEMENT>)')
                    pattern_id = re.compile(r'<ENTITLEMENT_ID>AGS_[^>]*?_TSC_ONSTCP</ENTITLEMENT_ID>')
                    pattern_name = re.compile(r'<ENTITLEMENT_DISPLAY_VALUE>([^>]*?)</ENTITLEMENT_DISPLAY_VALUE>')
                    #consinged_part = 'True'
                    for m in re.finditer(pattern_tag, updateentXML):
                        sub_string = m.group(1)
                        get_ent_id = re.findall(pattern_id,sub_string)
                        get_ent_val= re.findall(pattern_name,sub_string)
                        if get_ent_id:							
                            get_ent_val = str(get_ent_val[0])
                            
                            if str(get_ent_val) == '$1M/site':
                                #sum of the price for all parts[SAQIFP]
                                get_tools_info = Sql.GetFirst("SELECT SUM(DISTINCT UNIT_PRICE) as SUM from SAQIFP(NOLOCK) where QUOTE_RECORD_ID = '{}' AND QTEREV_RECORD_ID = '{}' AND SERVICE_ID = '{}' ".format(Quote.GetGlobal("contract_quote_record_id"),quote_revision_record_id),str(tserv.SERVICE_ID))
                                if get_tools_info.SUM > '10000000':
                                    Z0110_check.append('T')
                                else:
                                    Z0110_check.append('F')
            else:
                tool_check.append('T')
        #All Addon Products which require parts to be added
        get_addon_service_info = Sql.GetList("SELECT DISTINCT SERVICE_ID as SERVICE_ID from SAQSAO(NOLOCK) where QUOTE_RECORD_ID = '{}' AND QTEREV_RECORD_ID = '{}'".format(Quote.GetGlobal("contract_quote_record_id"),quote_revision_record_id))
        
        fpm_flag=0
        get_fpm_service_info = Sql.GetFirst("SELECT COUNT(DISTINCT SERVICE_ID) as CNT from SAQTSV(NOLOCK) where QUOTE_RECORD_ID = '{}' AND QTEREV_RECORD_ID = '{}' AND SERVICE_ID IN('Z0108','Z0110')".format(Quote.GetGlobal("contract_quote_record_id"),quote_revision_record_id))
        if get_fpm_service_info:
            if get_fpm_service_info.CNT > 0:
                fpm_flag=1
                
        #addon check    
        Addon_check = []		
        for dt in get_addon_service_info:		
            if str(dt.SERVICE_ID) in ['Z0100', 'Z0101', 'Z0123', 'Z0108', 'Z0110']:
                get_parts_info = Sql.GetFirst("SELECT COUNT(DISTINCT PART_NUMBER) as COUNT from SAQSPT(NOLOCK) where SAQTSV.QUOTE_RECORD_ID = '{}' AND SAQTSV.QTEREV_RECORD_ID = '{}' AND SERVICE_ID = '{}'".format(Quote.GetGlobal("contract_quote_record_id"),quote_revision_record_id),str(dt.SERVICE_ID))
                
                
                if get_parts_info.COUNT > 0:
                    Addon_check.append('T')	
                else:
                    Addon_check.append('F')
            else:
                Addon_check.append('T')		
        # INC08607538 - Start - M
        get_workflow_statusquery = Sql.GetFirst("SELECT WORKFLOW_STATUS, REVISION_STATUS FROM SAQTRV where WORKFLOW_STATUS = 'CONFIGURE' AND QUOTE_RECORD_ID = '{QuoteRecordId}' and QTEREV_RECORD_ID = '{RevisionRecordId}' ".format(QuoteRecordId=Quote.GetGlobal("contract_quote_record_id"),RevisionRecordId = quote_revision_record_id))
        if get_workflow_statusquery:
            if get_workflow_statusquery.WORKFLOW_STATUS == 'CONFIGURE' and get_workflow_statusquery.REVISION_STATUS == 'CFG-CONFIGURING':          
                Log.Info("getsalesorg_info---> "+str(getsalesorg_info).upper()+" ---> "+str(get_service_info.COUNT)+" ---> "+str(get_fab_info.COUNT)+" ---> "+str(get_involved_parties_info.COUNT)+" ---> "+str(get_sales_team_info.COUNT)+" ---> "+str(get_sales_team_info.COUNT)+" ---> "+str(get_complete_list)+" ---> "+str(tool_check)+" ---> "+str(Z0110_check)+" ---> "+str(Addon_check)+" ---> "+str(req_event_missing))
                # INC08830942 - Starts - M     
                if str(getsalesorg_info).upper() != "NONE" and get_service_info.COUNT > 0 and get_fab_info.COUNT > 0  and get_involved_parties_info.COUNT > 0  and get_sales_team_info.COUNT > 0  and 'F' not in get_complete_list and 'F' not in tool_check and 'F' not in Z0110_check and 'F' not in Addon_check and req_event_missing.CNT==0:
                # INC08830942 - Ends - M 
                    update_workflow_status = "UPDATE SAQTRV SET REVISION_STATUS = 'CFG-ACQUIRING',WORKFLOW_STATUS = 'CONFIGURE' WHERE QUOTE_RECORD_ID = '{QuoteRecordId}' and QTEREV_RECORD_ID = '{RevisionRecordId}' ".format(QuoteRecordId=Quote.GetGlobal("contract_quote_record_id"),RevisionRecordId = quote_revision_record_id)	
                    Sql.RunQuery(update_workflow_status)
                
        # INC08607538 - End - M
        #AO55S000P01-17018 Starts
        #get pricing status from saqico-A055S000P01-17164 start
        price_preview_status = []
        annualized_items_status = []
        item_covered_obj = Sql.GetList("SELECT DISTINCT STATUS FROM SAQICO (NOLOCK) WHERE QUOTE_RECORD_ID = '{}' AND QTEREV_RECORD_ID = '{}'".format(Quote.GetGlobal("contract_quote_record_id"),quote_revision_record_id))
        if item_covered_obj:
            for status in item_covered_obj:
                annualized_items_status.append(status.STATUS)
                if status.STATUS:
                    price_status = status.STATUS
                    if str(price_status).upper() == "ACQUIRED":
                        price_preview_status.append('T')
                    else:
                        price_preview_status.append('F')
                else:
                    price_preview_status.append('F')
        else:
            Trace.Write("NO Quote Items")
            price_preview_status.append('F')
        annualized_items_status = list(set(annualized_items_status))
        #A055S000P01-17164 start
        get_workflow_status = Sql.GetFirst(" SELECT WORKFLOW_STATUS,REVISION_STATUS FROM SAQTRV WHERE QUOTE_RECORD_ID = '{}' AND QTEREV_RECORD_ID = '{}' ".format(Quote.GetGlobal("contract_quote_record_id"),quote_revision_record_id))
        if get_workflow_status.WORKFLOW_STATUS not in ("APPROVALS","LEGAL SOW","QUOTE-DOCUMNETS","CLEAN BOOKING CHECKLIST","BOOKED")  and  get_quality_required.CNT == 0:
            if str(getsalesorg_info).upper() != "NONE" and get_service_info.COUNT > 0 and   'F' not in get_complete_list and 'F' not in tool_check and 'F' not in price_preview_status and Text == "COMPLETE STAGE" :
                if 'PRR-ON HOLD PRICING' not in annualized_items_status and 'OFFLINE PRICING' in annualized_items_status:				
                    update_workflow_status = "UPDATE SAQTRV SET WORKFLOW_STATUS = 'PRICING REVIEW',REVISION_STATUS='PRR-ON HOLD PRICING' WHERE QUOTE_RECORD_ID = '{QuoteRecordId}' and QTEREV_RECORD_ID = '{RevisionRecordId}' ".format(QuoteRecordId=Quote.GetGlobal("contract_quote_record_id"),RevisionRecordId = Quote.GetGlobal("quote_revision_record_id"))
                    Sql.RunQuery(update_workflow_status)
                else:
                    Trace.Write('183---->')
                    update_workflow_status = "UPDATE SAQTRV SET WORKFLOW_STATUS = 'PRICING',REVISION_STATUS='PRI-PRICING' WHERE QUOTE_RECORD_ID = '{QuoteRecordId}' and QTEREV_RECORD_ID = '{RevisionRecordId}' ".format(QuoteRecordId=Quote.GetGlobal("contract_quote_record_id"),RevisionRecordId = Quote.GetGlobal("quote_revision_record_id"))
                    #Sql.RunQuery(update_workflow_status)
                    ScriptExecutor.ExecuteGlobal('CQSDELPGPN',{'QUOTE_ID':Quote.GetGlobal("contract_quote_record_id"),'QTEREV_ID':Quote.GetGlobal("quote_revision_record_id"),'ACTION':'EMAIL'})
            if str(getsalesorg_info).upper() != "NONE" and get_service_info.COUNT > 0 and   'F'  in get_complete_list and 'F' not in tool_check and 'F' not in price_preview_status and Text == "COMPLETE STAGE":
                if 'PRR-ON HOLD PRICING' not in annualized_items_status and 'OFFLINE PRICING' in annualized_items_status:	
                    update_workflow_status = "UPDATE SAQTRV SET WORKFLOW_STATUS = 'PRICING REVIEW',REVISION_STATUS='PRR-ON HOLD PRICING' WHERE QUOTE_RECORD_ID = '{QuoteRecordId}' and QTEREV_RECORD_ID = '{RevisionRecordId}' ".format(QuoteRecordId=Quote.GetGlobal("contract_quote_record_id"),RevisionRecordId = Quote.GetGlobal("quote_revision_record_id"))
                    Sql.RunQuery(update_workflow_status)
                else:
                    Trace.Write('193---->')
                    if 'PRR-ON HOLD PRICING'  in annualized_items_status:
                        update_workflow_onhold_pricing_status = "UPDATE SAQTRV SET WORKFLOW_STATUS = 'PRICING REVIEW',REVISION_STATUS='PRR- ON HOLD PRICING' WHERE QUOTE_RECORD_ID = '{QuoteRecordId}' and QTEREV_RECORD_ID = '{RevisionRecordId}' ".format(QuoteRecordId=Quote.GetGlobal("contract_quote_record_id"),RevisionRecordId = Quote.GetGlobal("quote_revision_record_id"))
                        Sql.RunQuery(update_workflow_onhold_pricing_status)
            if str(getsalesorg_info).upper() != "NONE" and get_service_info.COUNT > 0 and   'F'  in get_complete_list and 'F' not in tool_check and 'F'  in price_preview_status and Text == "COMPLETE STAGE":
                update_workflow_onhold_status = "UPDATE SAQTRV SET WORKFLOW_STATUS = 'CONFIGURE',REVISION_STATUS='CFG-ON HOLD-COSTING' WHERE QUOTE_RECORD_ID = '{QuoteRecordId}' and QTEREV_RECORD_ID = '{RevisionRecordId}' ".format(QuoteRecordId=Quote.GetGlobal("contract_quote_record_id"),RevisionRecordId = Quote.GetGlobal("quote_revision_record_id"))
                #Sql.RunQuery(update_workflow_onhold_status)
        #A055S000P01-17164 end		
        #get pricing status from saqico-A055S000P01-17164 end
        #get_workflow_status = Sql.GetFirst(" SELECT WORKFLOW_STATUS,REVISION_STATUS FROM SAQTRV WHERE QUOTE_RECORD_ID = '{}' AND QTEREV_RECORD_ID = '{}' ".format(Quote.GetGlobal("contract_quote_record_id"),quote_revision_record_id))
        if get_workflow_status.REVISION_STATUS == "APR-APPROVAL PENDING" and Text == "COMPLETE STAGE" and get_quality_required.CNT == 0:
            update_workflow_status = "UPDATE SAQTRV SET WORKFLOW_STATUS = 'APPROVALS' WHERE QUOTE_RECORD_ID = '{QuoteRecordId}' and QTEREV_RECORD_ID = '{RevisionRecordId}' ".format(QuoteRecordId=Quote.GetGlobal("contract_quote_record_id"),RevisionRecordId = quote_revision_record_id)
            Sql.RunQuery(update_workflow_status)
        #AO55S000P01-17018 Ends
    #workflow status bar update status -- A055S000P01-17166
    get_workflow_status = Sql.GetFirst("SELECT WORKFLOW_STATUS,REVISION_STATUS,CLM_AGREEMENT_NUM FROM SAQTRV WHERE QUOTE_RECORD_ID = '{}' AND QTEREV_RECORD_ID = '{}' ".format(Quote.GetGlobal("contract_quote_record_id"),quote_revision_record_id))
    try:
        revision_status = str(get_workflow_status.REVISION_STATUS)
    except:
        revision_status = ""
    if get_workflow_status:
        if get_workflow_status.REVISION_STATUS == "OPD-CUSTOMER ACCEPTED":
            #A055S000P01-17165 started
            Trace.Write('205---')
            #update_legal_status = "UPDATE SAQTRV SET WORKFLOW_STATUS = 'LEGAL SOW',REVISION_STATUS ='LGL-PREPARING LEGAL SOW' WHERE QUOTE_RECORD_ID = '{QuoteRecordId}' and QTEREV_RECORD_ID = '{RevisionRecordId}' ".format(QuoteRecordId=Quote.GetGlobal("contract_quote_record_id"),RevisionRecordId = quote_revision_record_id)
            #Sql.RunQuery(update_legal_status)
            #A055S000P01-17165 end
            status = "GENERATE SOW"
        elif get_workflow_status.WORKFLOW_STATUS == "CONFIGURE":
            status = "CONFIGURE"
        elif get_workflow_status.WORKFLOW_STATUS == "PRICING REVIEW":
            status = "PRICING REVIEW"
        elif get_workflow_status.WORKFLOW_STATUS == "PRICING":
            status = "PRICING"
        elif get_workflow_status.WORKFLOW_STATUS == "APPROVALS" and get_workflow_status.REVISION_STATUS not in  ("APR-APPROVED"):
            status = "APPROVALS"
        elif get_workflow_status.WORKFLOW_STATUS == "APPROVALS" and get_workflow_status.REVISION_STATUS =="APR-APPROVED":
            status = "APR-APPROVALS"
        elif get_workflow_status.WORKFLOW_STATUS == "LEGAL SOW" and get_workflow_status.REVISION_STATUS not in  ("LGL-PREPARING LEGAL SOW","LGL-LEGAL SOW ACCEPTED"):
            status = "LEGAL SOW"
    
        elif get_workflow_status.WORKFLOW_STATUS == "QUOTE DOCUMENTS" and get_workflow_status.REVISION_STATUS != "OPD-CUSTOMER ACCEPTED":
            status = "QUOTE DOCUMENTS"
        elif get_workflow_status.WORKFLOW_STATUS == "QUOTE DOCUMENTS" and get_workflow_status.REVISION_STATUS == "OPD-CUSTOMER ACCEPTED":
            status = "GENERATE SOW"
        elif get_workflow_status.WORKFLOW_STATUS == "LEGAL SOW" and get_workflow_status.REVISION_STATUS == "LGL-PREPARING LEGAL SOW":
            status = "COMPLETESOW"
        elif get_workflow_status.WORKFLOW_STATUS == "LEGAL SOW" and get_workflow_status.REVISION_STATUS == "LGL-LEGAL SOW ACCEPTED":
            status = "LEGAL SOW ACCEPT"
        elif get_workflow_status.WORKFLOW_STATUS == "CLEAN BOOKING CHECKLIST" and get_workflow_status.REVISION_STATUS == "CBC-CBC COMPLETED":
            status = "CBC-COMPLETED"
        elif get_workflow_status.WORKFLOW_STATUS == "CLEAN BOOKING CHECKLIST" and get_workflow_status.REVISION_STATUS not in  ("CBC-CBC COMPLETED"):
            status = "CLEAN BOOKING CHECKLIST"
        elif get_workflow_status.REVISION_STATUS == "BOK-CONTRACT BOOKED" and get_workflow_status.WORKFLOW_STATUS =="BOOKED":
            status = "BOOKEDCONTRACT"
        elif get_workflow_status.WORKFLOW_STATUS == "BOOKED" and get_workflow_status.REVISION_STATUS not in ("BOOKED"):
            status = "BOOKED"
        else:
            status = "CONFIGURE"
        Trace.Write('Text-->'+str(Text)+'--WF-->'+str(get_workflow_status.WORKFLOW_STATUS)+'--RS-->'+str(get_workflow_status.REVISION_STATUS))
        if get_workflow_status.WORKFLOW_STATUS == "PRICING" and get_workflow_status.REVISION_STATUS =="PRI-PRICING" and str(Text) == 'COMPLETE STAGE' and fpm_flag==0:
            oppurtunity_writeback = "YES"
            #1491 start
            
            acquired_items_status = []
            items_status = Sql.GetList("SELECT DISTINCT STATUS FROM SAQRIT (NOLOCK) WHERE QUOTE_RECORD_ID = '{}' AND QTEREV_RECORD_ID = '{}'".format(Quote.GetGlobal("contract_quote_record_id"),quote_revision_record_id))
            if items_status:
                for status in items_status:
                    acquired_items_status.append(status.STATUS)
            acquired_items_status = list(set(acquired_items_status))
            if 'ACQUIRING' not in acquired_items_status:
                # INC08832348 - Start - M
                mismatched_billings_obj = Sql.GetList("SELECT MAX(SAQIBP.LINE) as LINE FROM SAQIBP JOIN SAQRIT ON SAQRIT.QUOTE_RECORD_ID = SAQIBP.QUOTE_RECORD_ID AND SAQRIT.QTEREV_RECORD_ID = SAQIBP.QTEREV_RECORD_ID AND SAQRIT.SERVICE_ID = SAQIBP.SERVICE_ID AND SAQRIT.LINE = SAQIBP.LINE WHERE SAQIBP.QUOTE_RECORD_ID = '{QuoteRecordId}' AND SAQIBP.QTEREV_RECORD_ID = '{QuoteRevisionRecordId}' GROUP BY SAQIBP.QUOTE_RECORD_ID, SAQIBP.QTEREV_RECORD_ID, SAQIBP.SERVICE_ID, SAQIBP.LINE, SAQIBP.BILLING_YEAR HAVING SUM(CASE WHEN SAQIBP.BILLING_TYPE IN ('MILESTONE','FIXED') THEN SAQIBP.BILLING_VALUE_INGL_CURR ELSE SAQIBP.ESTVAL_INGL_CURR END) <> MAX(ANNBILAMT_INGL_CURR)".format(QuoteRecordId=Quote.GetGlobal("contract_quote_record_id"), QuoteRevisionRecordId=quote_revision_record_id))

                if not mismatched_billings_obj:                
                    update_approval_pending_status = "UPDATE SAQTRV SET WORKFLOW_STATUS = 'APPROVALS',REVISION_STATUS = 'APR-APPROVAL PENDING' where QUOTE_RECORD_ID='{contract_quote_rec_id}' AND QTEREV_RECORD_ID = '{quote_revision_rec_id}'".format(contract_quote_rec_id=Quote.GetGlobal("contract_quote_record_id"),quote_revision_rec_id=quote_revision_record_id)
                    Sql.RunQuery(update_approval_pending_status)
                    oppurtunity_writeback ="YES"
                # # INC08818816 - Start - M    
                # bill_plan_years = Sql.GetList("SELECT DISTINCT BILLING_YEAR,SERVICE_ID,BILLING_TYPE from SAQIBP WHERE QUOTE_RECORD_ID = '"+str(Quote.GetGlobal("contract_quote_record_id"))+"' AND QTEREV_RECORD_ID = '"+str(quote_revision_record_id)+"' ")
                # # INC08818816 - Stop - M
                # billing_message= []
                # if bill_plan_years:
                #     for val in bill_plan_years:
                #         bill_year= val.BILLING_YEAR
                #         service_id= val.SERVICE_ID
                #         # INC08818816 - Start - M
                #         if bill_year != 'YEAR 1' and val.BILLING_TYPE == 'MILESTONE':
                #             break
                #         if val.BILLING_TYPE == 'MILESTONE':
                #             bill_years_gl_curr = 'SUM(NET_VALUE_INGL_CURR)'
                #         else:
                #             bill_years_gl_curr= "SUM("+bill_year.replace(' ','_')+"_INGL_CURR)"
                #         item_bill_type = Sql.GetFirst("SELECT BILLING_TYPE,"+bill_years_gl_curr+" as year_gc from SAQRIT where QUOTE_RECORD_ID= '"+str(Quote.GetGlobal("contract_quote_record_id"))+"' and QTEREV_RECORD_ID ='"+str(quote_revision_record_id)+"' and SERVICE_ID='"+str(service_id)+"' group by BILLING_TYPE")
                #         # INC08818816 - Stop - M
                #         if item_bill_type:
                #             item_billing_type = item_bill_type.BILLING_TYPE
                #             if str(item_billing_type).upper() in ('FIXED','MILESTONE'):
                #                 get_bill_val ='SUM(BILLING_VALUE_INGL_CURR)'
                #                 get_dt_amt = 'BILLING_VALUE_INGL_CURR'
                            
                #             else:
                #                 get_bill_val = 'SUM(ESTVAL_INGL_CURR)'
                #                 get_dt_amt = 'ESTVAL_INGL_CURR'
                #             get_year_amt = item_bill_type.year_gc
                            
                #             get_total_bill_amt = Sql.GetFirst("SELECT  "+get_bill_val+" as total_monthly_billval from SAQIBP where QUOTE_RECORD_ID= '"+str(Quote.GetGlobal("contract_quote_record_id"))+"' and BILLING_YEAR= '"+str(bill_year)+"' and SERVICE_ID= '"+str(service_id)+"'  and QTEREV_RECORD_ID ='"+str(quote_revision_record_id)+"' ")
                #             if get_year_amt == get_total_bill_amt.total_monthly_billval:
                #                 billing_message.append('F')
                #             else:
                #                 billing_message.append('T')
                #             oppurtunity_writeback ="YES"
                #             if 'T' not in billing_message:
                #                 update_approval_pending_status = "UPDATE SAQTRV SET WORKFLOW_STATUS = 'APPROVALS',REVISION_STATUS = 'APR-APPROVAL PENDING' where QUOTE_RECORD_ID='{contract_quote_rec_id}' AND QTEREV_RECORD_ID = '{quote_revision_rec_id}'".format(contract_quote_rec_id=Quote.GetGlobal("contract_quote_record_id"),quote_revision_rec_id=quote_revision_record_id)
                #                 Sql.RunQuery(update_approval_pending_status)
                #update_approval_pending_status = "UPDATE SAQTRV SET WORKFLOW_STATUS = 'APPROVALS',REVISION_STATUS = 'APR-APPROVAL PENDING' where QUOTE_RECORD_ID='{contract_quote_rec_id}' AND QTEREV_RECORD_ID = '{quote_revision_rec_id}'".format(contract_quote_rec_id=Quote.GetGlobal("contract_quote_record_id"),quote_revision_rec_id=quote_revision_record_id)
                #Sql.RunQuery(update_approval_pending_status)
                # INC08832348 - End - M
            #1491 end
        if get_workflow_status.WORKFLOW_STATUS == "APPROVALS" and get_workflow_status.REVISION_STATUS =="APR-APPROVED" and str(Text) == 'COMPLETE STAGE':
            oppurtunity_writeback = "YES"
            update_output_doc_status = "UPDATE SAQTRV SET WORKFLOW_STATUS = 'QUOTE DOCUMENTS',REVISION_STATUS = 'OPD-PREPARING QUOTE DOCUMENTS' where QUOTE_RECORD_ID='{contract_quote_rec_id}' AND QTEREV_RECORD_ID = '{quote_revision_rec_id}'".format(contract_quote_rec_id=Quote.GetGlobal("contract_quote_record_id"),quote_revision_rec_id=quote_revision_record_id)
            Sql.RunQuery(update_output_doc_status)
            status = "QUOTE DOCUMENTS"
        
        if get_workflow_status.WORKFLOW_STATUS == "PRICING" and get_workflow_status.REVISION_STATUS =="PRI-PRICING" and str(Text) == 'COMPLETE STAGE' and fpm_flag==1:
            Log.Info("FPM Update")
            oppurtunity_writeback = "YES"
            update_approval_pending_status = "UPDATE SAQTRV SET WORKFLOW_STATUS = 'APPROVALS',REVISION_STATUS = 'APR-APPROVAL PENDING' where QUOTE_RECORD_ID='{contract_quote_rec_id}' AND QTEREV_RECORD_ID = '{quote_revision_rec_id}'".format(contract_quote_rec_id=Quote.GetGlobal("contract_quote_record_id"),quote_revision_rec_id=quote_revision_record_id)
            Sql.RunQuery(update_approval_pending_status)
            #Q-INC08658760-M
            status = "APPROVALS"
            #Q-INC08658760-M
            
        #CQCPQC4CWB.writeback_to_c4c("quote_header",Quote.GetGlobal("contract_quote_record_id"),Quote.GetGlobal("quote_revision_record_id"))
        #CQCPQC4CWB.writeback_to_c4c("opportunity_header",Quote.GetGlobal("contract_quote_record_id"),Quote.GetGlobal("quote_revision_record_id"))
        #legel sow on complete stage stage-green
        if get_workflow_status.REVISION_STATUS == "OPD-CUSTOMER ACCEPTED" and Text == "COMPLETE STAGE" and get_quality_required.CNT == 0:
            oppurtunity_writeback = "YES"
            update_legalsow_status = "UPDATE SAQTRV SET WORKFLOW_STATUS = 'LEGAL SOW',REVISION_STATUS = 'LGL-LEGAL SOW ACCEPTED' where QUOTE_RECORD_ID='{contract_quote_rec_id}' AND QTEREV_RECORD_ID = '{quote_revision_rec_id}'".format(contract_quote_rec_id=Quote.GetGlobal("contract_quote_record_id"),quote_revision_rec_id=quote_revision_record_id)
            Sql.RunQuery(update_legalsow_status)
            update_rev_cbc_status = "UPDATE SAQTRV SET WORKFLOW_STATUS = 'CLEAN BOOKING CHECKLIST',REVISION_STATUS = 'CBC-PREPARING CBC' where QUOTE_RECORD_ID='{contract_quote_rec_id}' AND QTEREV_RECORD_ID = '{quote_revision_rec_id}'".format(contract_quote_rec_id=Quote.GetGlobal("contract_quote_record_id"),quote_revision_rec_id=quote_revision_record_id)
            Sql.RunQuery(update_rev_cbc_status)
            status = "LEGAL SOW ACCEPT"
        #legel sow on complete stage stage-green end
        
        #Log.Info('279--contract_quote_rec_id--'+str(contract_quote_rec_id))
        if oppurtunity_writeback == "YES":
            try:
                CQCPQC4CWB.writeback_to_c4c("quote_header",Quote.GetGlobal("contract_quote_record_id"),Quote.GetGlobal("quote_revision_record_id"))
                CQCPQC4CWB.writeback_to_c4c("opportunity_header",Quote.GetGlobal("contract_quote_record_id"),Quote.GetGlobal("quote_revision_record_id"))
            except:
                Log.Info("writeback-except")
                pass 
        if str(get_workflow_status.REVISION_STATUS) == "LGL-PREPARING LEGAL SOW" and str(get_workflow_status.CLM_AGREEMENT_NUM) == "":
            error_msg = "You will not be able to complete the stage until the Legal SoW in CLM is executed"
    #A055S000P01-20699 A
    if (get_ibase_missing.CNT!=0 or get_ibase_no_assembly.CNT!=0 or req_event_missing.CNT!=0):
        error_msg = "<div><img src=\'/mt/APPLIEDMATERIALS_PRD/Additionalfiles/warning1.svg\' class=\'wid20_px\'><p>MISSING ASSEMBLIE(S), EVENTS AND<span class ='p-5'>/</span>OR ATTRIBUTES <span class ='p-5'>/</span> FROM IBASE <span class ='p-5'>|</span></p><p> One or more tools on the quote are missing Assemblie(s) or Attributes from the iBase. Please remove the impacted tools from the Fab Location node and work with FSO to correct the iBase for missing attributes/assemblies. In the case of missing events, kindly work with SBU to correct the event/assembly mapping in SSCM. Once corrected, you may re-add the tools and proceed.</p></div>"
    #A055S000P01-20699 A
    servicelevel_entitilement_obj = Sql.GetFirst("""SELECT COUNT(CONFIGURATION_STATUS) AS CNT FROM SAQTSE(NOLOCK) WHERE QUOTE_RECORD_ID = '{QuoteRecordId}' AND QTEREV_RECORD_ID = '{QuoteRevisionRecordId}' AND ISNULL(CONFIGURATION_STATUS,'') <> 'COMPLETE'""".format(QuoteRecordId=Quote.GetGlobal("contract_quote_record_id"),QuoteRevisionRecordId=quote_revision_record_id))
    
    #INC08614363 - A
    #A055S000P01-20612 start 
    if quote_item_insert == 'yes' and Text == "COMPLETE STAGE" and status not in ("CFG_CONFIGURING_STATUS","PRICING","GENERATE SOW","COMPLETESOW","APPROVALS","LEGAL SOW","QUOTE DOCUMENTS","BOOKED","CLEAN BOOKING CHECKLIST","LEGAL SOW ACCEPT") and get_quality_required.CNT == 0 and req_event_missing.CNT==0 and get_ibase_missing.CNT==0 and get_ibase_no_assembly.CNT==0 and servicelevel_entitilement_obj.CNT == 0 and get_exchangerate.EXCHANGE_RATE:
        #A055S000P01-20612 end
        #INC08614363 - A

        Log.Info('quote_item_insert--'+str(quote_item_insert)+" - "+str(Quote.GetGlobal("contract_quote_record_id")))
        service_id_query = Sql.GetList("SELECT SAQTSV.*,MAMTRL.MATERIALCONFIG_TYPE FROM SAQTSV INNER JOIN MAMTRL ON SAP_PART_NUMBER = SERVICE_ID WHERE QUOTE_RECORD_ID = '{}' AND QTEREV_RECORD_ID = '{}'  ".format(contract_quote_rec_id,quote_revision_record_id))
        if service_id_query:
            for service_id in service_id_query:
                get_ent_config_status = Sql.GetFirst(""" SELECT COUNT(CONFIGURATION_STATUS) AS COUNT FROM SAQTSE (NOLOCK) WHERE QUOTE_RECORD_ID = '{}' AND QTEREV_RECORD_ID = '{}' AND SERVICE_ID = '{}' AND CONFIGURATION_STATUS='COMPLETE' """.format(contract_quote_rec_id,quote_revision_record_id,service_id.SERVICE_ID))
                if get_ent_config_status.COUNT > 0 or service_id.MATERIALCONFIG_TYPE =='SIMPLE MATERIAL' or (service_id.SERVICE_ID in ('Z0114','Z0117')):
                    data = ScriptExecutor.ExecuteGlobal("CQINSQTITM",{"ContractQuoteRecordId":contract_quote_rec_id, "ContractQuoteRevisionRecordId":quote_revision_record_id, "ServiceId":service_id.SERVICE_ID, "ActionType":'INSERT_LINE_ITEMS'})
            #SAQRIT - Status - Offline Pricing
            Sql.RunQuery("UPDATE SAQRIT SET STATUS = SAQICO.STATUS FROM SAQRIT (NOLOCK) JOIN SAQICO (NOLOCK) ON SAQICO.QUOTE_RECORD_ID = SAQRIT.QUOTE_RECORD_ID AND SAQICO.QTEREV_RECORD_ID = SAQRIT.QTEREV_RECORD_ID AND SAQICO.SERVICE_ID = SAQRIT.SERVICE_ID AND SAQICO.QTEITM_RECORD_ID = SAQRIT.QUOTE_REVISION_CONTRACT_ITEM_ID WHERE SAQRIT.QUOTE_RECORD_ID = '{QuoteRecordId}' AND SAQRIT.QTEREV_RECORD_ID = '{QuoteRevisionRecordId}'".format(QuoteRecordId=contract_quote_rec_id,QuoteRevisionRecordId=quote_revision_record_id))

            Sql.RunQuery("UPDATE SAQRIT SET STATUS = 'OFFLINE PRICING' FROM SAQRIT (NOLOCK) JOIN SAQICO (NOLOCK) ON SAQICO.QUOTE_RECORD_ID = SAQRIT.QUOTE_RECORD_ID AND SAQICO.QTEREV_RECORD_ID = SAQRIT.QTEREV_RECORD_ID AND SAQICO.SERVICE_ID = SAQRIT.SERVICE_ID AND SAQICO.QTEITM_RECORD_ID = SAQRIT.QUOTE_REVISION_CONTRACT_ITEM_ID WHERE SAQRIT.QUOTE_RECORD_ID = '{QuoteRecordId}' AND SAQRIT.QTEREV_RECORD_ID = '{QuoteRevisionRecordId}' AND ISNULL(SAQICO.STATUS,'') = 'OFFLINE PRICING'".format(QuoteRecordId=contract_quote_rec_id,QuoteRevisionRecordId=quote_revision_record_id))
            
            items_status = []
            items_obj = Sql.GetList("SELECT ISNULL(STATUS,'') as STATUS FROM SAQRIT (NOLOCK) WHERE QUOTE_RECORD_ID = '{QuoteRecordId}' and QTEREV_RECORD_ID = '{QuoteRevisionRecordId}'".format(QuoteRecordId=contract_quote_rec_id,QuoteRevisionRecordId=quote_revision_record_id))
            if items_obj:
                items_status = [item_obj.STATUS for item_obj in items_obj]
            Log.Info(str(contract_quote_rec_id)+"=============="+str(items_status))
            if 'CFG-ON HOLD - COSTING' in items_status:
                Sql.RunQuery("UPDATE SAQTRV SET WORKFLOW_STATUS = 'CONFIGURE',REVISION_STATUS='CFG-ON HOLD - COSTING' WHERE QUOTE_RECORD_ID = '{QuoteRecordId}' and QTEREV_RECORD_ID = '{QuoteRevisionRecordId}' ".format(QuoteRecordId=contract_quote_rec_id,QuoteRevisionRecordId=quote_revision_record_id))
            elif 'PRR-ON HOLD PRICING' in items_status or 'OFFLINE PRICING' in items_status:
                Sql.RunQuery("UPDATE SAQTRV SET WORKFLOW_STATUS = 'PRICING REVIEW',REVISION_STATUS='PRR-ON HOLD PRICING' WHERE QUOTE_RECORD_ID = '{QuoteRecordId}' and QTEREV_RECORD_ID = '{QuoteRevisionRecordId}' ".format(QuoteRecordId=contract_quote_rec_id,QuoteRevisionRecordId=quote_revision_record_id))			
            
        try:
            ##Calling the iflow for quote header writeback to cpq to c4c code starts..
            CQCPQC4CWB.writeback_to_c4c("quote_header",Quote.GetGlobal("contract_quote_record_id"),Quote.GetGlobal("quote_revision_record_id"))
            CQCPQC4CWB.writeback_to_c4c("opportunity_header",Quote.GetGlobal("contract_quote_record_id"),Quote.GetGlobal("quote_revision_record_id"))
            ##Calling the iflow for quote header writeback to cpq to c4c code ends...
        except:
            pass
        #restricted for multiple calls scenario based on status
        if status not in ("GENERATE SOW","COMPLETESOW","APPROVALS","LEGAL SOW","QUOTE DOCUMENTS","BOOKED","CLEAN BOOKING CHECKLIST","LEGAL SOW ACCEPT"):

            quote_line_item_obj = Sql.GetFirst("""SELECT LINE  FROM SAQICO (NOLOCK) 
                                                    JOIN PRSPRV (NOLOCK) ON PRSPRV.SERVICE_ID = SAQICO.SERVICE_ID
                                                    WHERE QUOTE_RECORD_ID = '{QuoteRecordId}' AND QTEREV_RECORD_ID = '{QuoteRevisionRecordId}' 
                                                    AND ISNULL(STATUS,'') = '' AND ISNULL(PRSPRV.SSCM_COST,0) = 1""".format(QuoteRecordId=contract_quote_rec_id,QuoteRevisionRecordId=quote_revision_record_id
                                                    ))
            #added condition to restrict email trigger thrice
        
            if quote_line_item_obj :
                quote_revision_obj = Sql.GetFirst("SELECT QTEREV_ID,QUOTE_ID from SAQTMT where MASTER_TABLE_QUOTE_RECORD_ID = '{QuoteRecordId}' ".format(QuoteRecordId=contract_quote_rec_id))
                if quote_revision_obj:
                    Log.Info("===> QTPOSTACRM called from CQSTSVADTN--> "+str(quote_revision_obj.QUOTE_ID))
                    revision_flag = "True"
                    ScriptExecutor.ExecuteGlobal('QTPOSTACRM',{'QUOTE_ID':quote_revision_obj.QUOTE_ID,'REVISION_ID':quote_revision_obj.QTEREV_ID, 'Fun_type':'cpq_to_sscm'})
                    # SqlHelper.GetFirst("sp_executesql @T=N'update A SET A.STATUS = (CASE WHEN A.STATUS =''ERROR'' THEN ''ERROR'' WHEN A.STATUS =''PARTIALLY PRICED'' THEN ''ERROR'' END) from SAQRIT A inner join ( select SERVICE_ID,LINE,SAQICO.QUOTE_ID from SAQICO WHERE SAQICO.QUOTE_ID = ''"+str(quote_revision_obj.QUOTE_ID)+"'' group by SERVICE_ID,LINE,SAQICO.QUOTE_ID Having count(*) > 1 ) as od on od.LINE = A.LINE AND od.SERVICE_ID = A.SERVICE_ID '")
                    # SqlHelper.GetFirst("sp_executesql @T=N'update A SET A.STATUS = (CASE WHEN A.STATUS =''ACQUIRING'' THEN ''ACQUIRING'' WHEN A.STATUS =''ERROR'' THEN ''ERROR'' END) from SAQRIT A inner join ( select SERVICE_ID,LINE,SAQICO.QUOTE_ID from SAQICO WHERE SAQICO.QUOTE_ID = ''"+str(quote_revision_obj.QUOTE_ID)+"'' group by SERVICE_ID,LINE,SAQICO.QUOTE_ID Having count(*) > 1 ) as od on od.LINE = A.LINE AND od.SERVICE_ID = A.SERVICE_ID '")
                    # SqlHelper.GetFirst("sp_executesql @T=N'update A SET A.STATUS = (CASE WHEN A.STATUS =''ACQUIRING'' THEN ''PARTIALLY PRICING'' WHEN A.STATUS =''PARTIALLY PRICING'' THEN ''PARTIALLY PRICING'' END) from SAQRIT A inner join ( select SERVICE_ID,LINE,SAQICO.QUOTE_ID from SAQICO WHERE SAQICO.QUOTE_ID = ''"+str(quote_revision_obj.QUOTE_ID)+"'' group by SERVICE_ID,LINE,SAQICO.QUOTE_ID Having count(*) > 1 ) as od on od.LINE = A.LINE AND od.SERVICE_ID = A.SERVICE_ID '")
        # Pricing Calculation - End
        
            ##calling the iflow for pricing start..
            try:
                contract_quote_obj = Sql.GetFirst("SELECT QUOTE_ID FROM SAQTMT (NOLOCK) WHERE MASTER_TABLE_QUOTE_RECORD_ID = '{QuoteRecordId}'".format(QuoteRecordId=Quote.GetGlobal("contract_quote_record_id")))
                if contract_quote_obj:
                    contract_quote_id = contract_quote_obj.QUOTE_ID
                count=Sql.GetFirst("SELECT COUNT(*) AS CNT FROM SAQSPT WHERE QUOTE_ID= '"+str(contract_quote_id)+"' and CUSTOMER_ANNUAL_QUANTITY IS NOT NULL ")      
                if count.CNT==0:
                    CQPARTIFLW.iflow_pricing_call(str(User.UserName),str(contract_quote_id),str(quote_revision_record_id),'')
                        
            except:
                Log.Info("PART PRICING IFLOW ERROR!")
    else:
        if servicelevel_entitilement_obj.CNT != 0:
            update_workflow_status = "UPDATE SAQTRV SET REVISION_STATUS = 'CFG-CONFIGURING',WORKFLOW_STATUS = 'CONFIGURE' WHERE QUOTE_RECORD_ID = '{QuoteRecordId}' and QTEREV_RECORD_ID = '{RevisionRecordId}' ".format(QuoteRecordId=Quote.GetGlobal("contract_quote_record_id"),RevisionRecordId = quote_revision_record_id)	
            Sql.RunQuery(update_workflow_status)
    #   ##calling the iflow for pricing end
    Trace.Write('status--297---------'+str(status))
    CQREVSTSCH.Revisionstatusdatecapture(Quote.GetGlobal("contract_quote_record_id"),Quote.GetGlobal("quote_revision_record_id"),)
    #INC08636305 - M
    cost_model_msg = ''
    if get_flag_Status:
        Trace.Write('aaa')
        if get_flag_Status.MODVRS_DIRTY_FLAG == 1:
            Trace.Write('aba')
            cost_model_msg = ('<div id="dirty-flag-warning"><div class="col-md-12 alert-warning"><label> <img src="/mt/APPLIEDMATERIALS_TST/Additionalfiles/warning1.svg" alt="Warning"> 99999 | NEW COST MODEL VERSIONS AVAILABLE | There are new cost model versions available from SSCM. In order to update the costs and prices, please revision the quote.</label></div></div>')
    #INC08614363 - A
    
    if not get_exchangerate.EXCHANGE_RATE:
        exchng_rateflag = True
    return status,error_msg,revision_status,revision_flag,exchng_rateflag,cost_model_msg
    #INC08614363 - A
    #INC08636305 - M
    
#A055S000P01-17166 start
def complete_sow_update(quote_id_val,quote_rev_id_val,STATUS_SOW):	
    update_rev_status = "UPDATE SAQTRV SET WORKFLOW_STATUS = 'LEGAL SOW',REVISION_STATUS = 'LGL-LEGAL SOW ACCEPTED' where QUOTE_RECORD_ID='{contract_quote_rec_id}' AND QTEREV_RECORD_ID = '{quote_revision_rec_id}'".format(contract_quote_rec_id=contract_quote_rec_id,quote_revision_rec_id=quote_revision_record_id)
    Sql.RunQuery(update_rev_status)	
    CQCPQC4CWB.writeback_to_c4c("quote_header",Quote.GetGlobal("contract_quote_record_id"),Quote.GetGlobal("quote_revision_record_id"))
    
    CQCPQC4CWB.writeback_to_c4c("opportunity_header",Quote.GetGlobal("contract_quote_record_id"),Quote.GetGlobal("quote_revision_record_id"))
    CQREVSTSCH.Revisionstatusdatecapture(Quote.GetGlobal("contract_quote_record_id"),Quote.GetGlobal("quote_revision_record_id"),)
    return True

def create_sow_update(quote_id_val,quote_rev_id_val,STATUS_SOW):	
    update_rev_status = "UPDATE SAQTRV SET WORKFLOW_STATUS = 'LEGAL SOW',REVISION_STATUS = 'LGL-PREPARING LEGAL SOW' where QUOTE_RECORD_ID='{contract_quote_rec_id}' AND QTEREV_RECORD_ID = '{quote_revision_rec_id}'".format(contract_quote_rec_id=contract_quote_rec_id,quote_revision_rec_id=quote_revision_record_id)
    Sql.RunQuery(update_rev_status)	
    #CQCPQC4CWB.writeback_to_c4c("quote_header",Quote.GetGlobal("contract_quote_record_id"),Quote.GetGlobal("quote_revision_record_id"))
    
    #CQCPQC4CWB.writeback_to_c4c("opportunity_header",Quote.GetGlobal("contract_quote_record_id"),Quote.GetGlobal("quote_revision_record_id"))
    CQREVSTSCH.Revisionstatusdatecapture(Quote.GetGlobal("contract_quote_record_id"),Quote.GetGlobal("quote_revision_record_id"),)
    return True
#A055S000P01-17166 end
try:
    quote_item_insert = Param.quote_item_insert
except:
    quote_item_insert = ''

try:
    Text = Param.Text
except:
    Text = ""

try:
    quote_id_val = Param.QUOTE_ID
except:
    quote_id_val = ""

try:
    quote_rev_id_val = Param.REVISION_ID
except:
    quote_rev_id_val = ""
try:
    STATUS_SOW = Param.STATUS
except:
    STATUS_SOW = ""

if STATUS_SOW == "SOW_ACCEPT":
    try:
        ApiResponse = ApiResponseFactory.JsonResponse(complete_sow_update(quote_id_val,quote_rev_id_val,STATUS_SOW))
    except:
        ApiResponse = ApiResponseFactory.JsonResponse(False)
elif STATUS_SOW == "CREATE_SOW":
    ApiResponse = ApiResponseFactory.JsonResponse(create_sow_update(quote_id_val,quote_rev_id_val,STATUS_SOW))
else:
    Trace.Write("quote_item_insert_J "+str(quote_item_insert))
    ApiResponse = ApiResponseFactory.JsonResponse(Dynamic_Status_Bar(quote_item_insert,Text))
