#script to populate quote tables and document creations
#author:Dhurga Gopalakrishnan

import Webcom.Configurator.Scripting.Test.TestProduct

from SYDATABASE import SQL
import datetime
Sql = SQL()
import SYCNGEGUID as CPQID
import time
import CQREVSTSCH
import re
UserId = str(User.Id)
UserName = str(User.UserName)
INCLUDESPARE =add_style =  ""
get_billing_types = get_ttl_amt = '' 
contract_quote_record_id = Quote.GetGlobal("contract_quote_record_id")
quote_revision_record_id = Quote.GetGlobal("quote_revision_record_id")
gettoolquote=Sql.GetFirst("select QUOTE_TYPE,QUOTE_ID from SAQTMT where MASTER_TABLE_QUOTE_RECORD_ID='"+str(contract_quote_record_id)+"'")


#Document XML

#Hadoop Fix, A055S000P01-10549- start, A055S000P01-20862 - M 
update_rev_expire_date  = "UPDATE SAQTRV SET REV_EXPIRE_DATE = CONVERT(date,DATEADD(DAY, 90, GETDATE())) where QUOTE_RECORD_ID ='{quote_record_id}' AND QTEREV_RECORD_ID = '{rev_rec_id}' " .format(quote_record_id=contract_quote_record_id,rev_rec_id = quote_revision_record_id)
#Hadoop Fix, A055S000P01-20862 - End - M
Sql.RunQuery(update_rev_expire_date)
c4c_quote_id = gettoolquote.QUOTE_ID
cartobj = Sql.GetFirst("select CART_ID, USERID from CART where ExternalId = '{}'".format(c4c_quote_id))



def _insert_item_level_delivery_schedule():
    insert_item_level_delivery_schedule = "INSERT QT__SAQIPD (QUOTE_REV_ITEM_PART_DELIVERY_RECORD_ID,DELIVERY_SCHED_CAT,DELIVERY_SCHED_DATE,LINE,PART_DESCRIPTION,PART_NUMBER,PART_RECORD_ID,SERVICE_DESCRIPTION,SERVICE_ID,SERVICE_RECORD_ID,QUANTITY,QUOTE_ID,QTEITMPRT_RECORD_ID,QTEITM_RECORD_ID,QUOTE_RECORD_ID,QTEREV_ID,QTEREVSPT_RECORD_ID,QTEREV_RECORD_ID) select QUOTE_REV_ITEM_PART_DELIVERY_RECORD_ID,DELIVERY_SCHED_CAT,DELIVERY_SCHED_DATE,LINE,PART_DESCRIPTION,PART_NUMBER,PART_RECORD_ID,SERVICE_DESCRIPTION,SERVICE_ID,SERVICE_RECORD_ID,QUANTITY,QUOTE_ID,QTEITMPRT_RECORD_ID,QTEITM_RECORD_ID,QUOTE_RECORD_ID,QTEREV_ID,QTEREVSPT_RECORD_ID,QTEREV_RECORD_ID FROM SAQIPD where QUOTE_RECORD_ID = '{QuoteRecordId}' and QTEREV_RECORD_ID= '{rev_rec_id}'".format(QuoteRecordId=contract_quote_record_id,rev_rec_id=quote_revision_record_id)
    #Log.Info('insert_item_level_delivery_schedule==='+str(insert_item_level_delivery_schedule))
    Sql.RunQuery(insert_item_level_delivery_schedule)

#insert item level parts
def _insert_item_level_parts():
    get_forecst_details_obj_insert = Quote.QuoteTables["SAQIFP"]
    get_forecst_details_obj_insert.Rows.Clear()
    get_forecst_details_obj = SqlHelper.GetList("select QUOTE_ITEM_FORECAST_PART_RECORD_ID,CUSTOMER_PART_NUMBER,PRICING_STATUS,CUSTOMER_PART_NUMBER_RECORD_ID,ANNUAL_QUANTITY,BASEUOM_ID,BASEUOM_RECORD_ID,LINE,DELIVERY_MODE,SCHEDULE_MODE,EXTENDED_PRICE,UNIT_PRICE_INGL_CURR,SERVICE_ID,SERVICE_DESCRIPTION,PART_DESCRIPTION,PART_NUMBER,PART_RECORD_ID,SERVICE_RECORD_ID,QUOTE_ID,UNIT_PRICE,DOC_CURRENCY,EXTPRI_INGL_CURR,PRICINGPROCEDURE_ID,TAX,TAX_PERCENTAGE,QTEREV_RECORD_ID,QUOTE_RECORD_ID,QTEREV_ID,{UserId} as ownerId,{CartId} as cartId FROM SAQIFP where QUOTE_RECORD_ID = '{QuoteRecordId}' and QTEREV_RECORD_ID= '{rev_rec_id}'".format(QuoteRecordId=contract_quote_record_id,rev_rec_id=quote_revision_record_id,UserId= cartobj.USERID,CartId = cartobj.CART_ID))
    if get_forecst_details_obj:
        for val in get_forecst_details_obj:
            newRow = get_forecst_details_obj_insert.AddNewRow()
            if val.QUOTE_ITEM_FORECAST_PART_RECORD_ID:
                newRow['QUOTE_ITEM_FORECAST_PART_RECORD_ID'] = val.QUOTE_ITEM_FORECAST_PART_RECORD_ID
            else:
                newRow['QUOTE_ITEM_FORECAST_PART_RECORD_ID'] = ''
            
            #newRow['ITEM_LINE_ID'] =  val.LINE
            #newRow['QTEITM_RECORD_ID'] =  val.QTEITM_RECORD_ID
            #newRow['SERIAL_NUMBER'] =  val.SERIAL_NUMBER
            if val.CUSTOMER_PART_NUMBER:
                newRow['CUSTOMER_PART_NUMBER'] = val.CUSTOMER_PART_NUMBER
            else:
                val.CUSTOMER_PART_NUMBER =''
            if val.LINE:
                newRow['LINE'] = val.LINE
            else:
                val.LINE =''
                
                
                
            if val.DELIVERY_MODE:
                newRow['DELIVERY_MODE'] = val.DELIVERY_MODE
            else:
                val.DELIVERY_MODE =''
            if val.SCHEDULE_MODE:
                newRow['SCHEDULE_MODE'] = val.SCHEDULE_MODE
            else:
                val.SCHEDULE_MODE =''
            if val.EXTPRI_INGL_CURR:
                newRow['EXTENDED_PRICE'] = val.EXTPRI_INGL_CURR
            else:
                val.EXTPRI_INGL_CURR ='' 
            if val.SERVICE_ID:
                newRow['SERVICE_ID'] = val.SERVICE_ID
            else:
                val.SERVICE_ID ='' 
            if val.SERVICE_DESCRIPTION:
                newRow['SERVICE_DESCRIPTION'] = val.SERVICE_DESCRIPTION
            else:
                val.SERVICE_DESCRIPTION ='' 
            if val.PART_NUMBER:
                newRow['PART_NUMBER'] = val.PART_NUMBER
            else:
                val.PART_NUMBER ='' 
            if val.UNIT_PRICE_INGL_CURR:
                newRow['UNIT_PRICE'] = val.UNIT_PRICE_INGL_CURR
            else:
                val.UNIT_PRICE_INGL_CURR =''
            if val.TAX_PERCENTAGE:
                newRow['TAX_PERCENTAGE'] = val.TAX_PERCENTAGE
            else:
                val.TAX_PERCENTAGE =''
            if val.TAX:
                newRow['TAX'] = val.TAX
            else:
                val.TAX='' 
            
            newRow['QUOTE_RECORD_ID'] = val.QUOTE_RECORD_ID
            newRow['QUOTE_ID'] = val.QUOTE_ID
            
            newRow['QTEREV_RECORD_ID'] = val.QTEREV_RECORD_ID
        get_forecst_details_obj_insert.Save()
    #delete_item_parts = Sql.RunQuery("DELETE  from QT__SAQIFP where QUOTE_RECORD_ID = '{QuoteRecordId}' and QTEREV_RECORD_ID= '{rev_rec_id}' and cartId = {CartId} and ownerId = {UserId}".format(QuoteRecordId=contract_quote_record_id,rev_rec_id=quote_revision_record_id,UserId= cartobj.USERID,CartId = cartobj.CART_ID))
    #insert_item_parts = "INSERT QT__SAQIFP (QUOTE_ITEM_FORECAST_PART_RECORD_ID,CUSTOMER_PART_NUMBER,PRICING_STATUS,CUSTOMER_PART_NUMBER_RECORD_ID,ANNUAL_QUANTITY,BASEUOM_ID,BASEUOM_RECORD_ID,LINE,DELIVERY_MODE,SCHEDULE_MODE,EXTENDED_PRICE,SERVICE_ID,SERVICE_DESCRIPTION,PART_DESCRIPTION,PART_NUMBER,PART_RECORD_ID,SERVICE_RECORD_ID,QUOTE_ID,UNIT_PRICE,DOC_CURRENCY,PRICINGPROCEDURE_ID,TAX,TAX_PERCENTAGE,QTEREV_RECORD_ID,QUOTE_RECORD_ID,QTEREV_ID,ownerId,cartId) select QUOTE_ITEM_FORECAST_PART_RECORD_ID,CUSTOMER_PART_NUMBER,PRICING_STATUS,CUSTOMER_PART_NUMBER_RECORD_ID,ANNUAL_QUANTITY,BASEUOM_ID,BASEUOM_RECORD_ID,LINE,DELIVERY_MODE,SCHEDULE_MODE,EXTENDED_PRICE,SERVICE_ID,SERVICE_DESCRIPTION,PART_DESCRIPTION,PART_NUMBER,PART_RECORD_ID,SERVICE_RECORD_ID,QUOTE_ID,UNIT_PRICE,DOC_CURRENCY,PRICINGPROCEDURE_ID,TAX,TAX_PERCENTAGE,QTEREV_RECORD_ID,QUOTE_RECORD_ID,QTEREV_ID,{UserId} as ownerId,{CartId} as cartId FROM SAQIFP where QUOTE_RECORD_ID = '{QuoteRecordId}' and QTEREV_RECORD_ID= '{rev_rec_id}'".format(QuoteRecordId=contract_quote_record_id,rev_rec_id=quote_revision_record_id,UserId= cartobj.USERID,CartId = cartobj.CART_ID)
    #Sql.RunQuery(insert_item_parts)


#quote table insert for billing matrix
def insert_quote_billing_plan():
    Trace.Write('inside billing mtraix---')
    quote_get_bill_details = Quote.QuoteTables["BM_YEAR_1"]
    quote_get_bill_details.Rows.Clear()
    quote_bills_header = Quote.QuoteTables["Billing_Matrix_Header"]
    quote_bills_header.Rows.Clear()
   
    services_obj = Sql.GetList("SELECT DISTINCT SERVICE_ID FROM SAQTSV (NOLOCK) WHERE QUOTE_RECORD_ID = '{}' AND QTEREV_RECORD_ID = '{}' ".format(contract_quote_record_id,quote_revision_record_id))
    item_billing_plans_obj_year = Sql.GetList("SELECT DISTINCT BILLING_YEAR FROM SAQIBP (NOLOCK) WHERE QUOTE_RECORD_ID = '{}' AND QTEREV_RECORD_ID = '{}' GROUP BY EQUIPMENT_ID,BILLING_YEAR,SERVICE_ID".format(contract_quote_record_id,quote_revision_record_id))
    if item_billing_plans_obj_year is not None and services_obj:
        #quotient, remainder = divmod(item_billing_plan_obj.cnt, 12)
        #years = quotient + (1 if remainder > 0 else 0)
        #if not years:
            #years = 1
        for item_billing_plan_obj_year in item_billing_plans_obj_year:
            if item_billing_plan_obj_year.BILLING_YEAR:
                no_of_year = item_billing_plan_obj_year.BILLING_YEAR.split(" ")[1]
                Trace.Write("no_of_year--"+str(no_of_year))
                item_billing_plans_obj = Sql.GetList("""SELECT FORMAT(BILLING_DATE, 'MM-dd-yyyy') as BILLING_DATE FROM (SELECT ROW_NUMBER() OVER(ORDER BY BILLING_DATE)
                                                            AS ROW, * FROM (SELECT DISTINCT BILLING_DATE
                                                            FROM SAQIBP (NOLOCK) WHERE QUOTE_RECORD_ID = '{}' 
                                                            AND QTEREV_RECORD_ID = '{}' AND BILLING_YEAR = '{}' GROUP BY EQUIPMENT_ID, BILLING_DATE,SERVICE_ID) IQ) OQ """.format(
                                                            contract_quote_record_id,quote_revision_record_id,item_billing_plan_obj_year.BILLING_YEAR))
                if item_billing_plans_obj:
                    billing_date_column = [item_billing_plan_obj.BILLING_DATE for item_billing_plan_obj in item_billing_plans_obj]
                    date_columns = " ,".join(['MONTH_{}'.format(index) for index in range(1, len(billing_date_column)+1)])
                    header_select_date_columns = ",".join(["'{}' AS MONTH_{}".format(date_column, index) for index, date_column in enumerate(billing_date_column, 1)])
                    select_date_columns = ",".join(['[{}] AS MONTH_{}'.format(date_column, index) for index, date_column in enumerate(billing_date_column, 1)])
                    sum_select_date_columns = ",".join(['SUM([{}]) AS MONTH_{}'.format(date_column, index) for index, date_column in enumerate(billing_date_column, 1)])
                    
                    
                    get_bill_details_obj = SqlHelper.GetList("""SELECT TOP 1
                                        QUOTE_ID,										
                                        QUOTE_RECORD_ID,QTEREV_RECORD_ID,
                                        {SelectDateColoumn},
                                        {Year} as YEAR,
                                        {UserId} as ownerId,{CartId} as cartId
                                    FROM SAQIBP (NOLOCK)
                                    WHERE QUOTE_RECORD_ID='{QuoteRecordId}' AND QTEREV_RECORD_ID = '{RevisionRecordId}'""".format(
                                        QuoteRecordId=contract_quote_record_id,RevisionRecordId=quote_revision_record_id,DateColumn=date_columns,Year=no_of_year,SelectDateColoumn=header_select_date_columns, UserId= cartobj.USERID,CartId = cartobj.CART_ID
                                        ))
                    #for val in a:
                    
                    if get_bill_details_obj:
                        for val in get_bill_details_obj:
                            newRow = quote_bills_header.AddNewRow()
                            newRow['MONTH_1'] = val.MONTH_1
                            try:
                                newRow['MONTH_2'] = val.MONTH_2 if val.MONTH_2 else 0
                            except:
                                newRow['MONTH_2'] = 0
                            newRow['YEAR'] = val.YEAR
                            try:
                                newRow['MONTH_3'] = val.MONTH_3 if val.MONTH_3 else 0
                            except:
                                newRow['MONTH_3'] = 0
                            try:
                                newRow['MONTH_4'] = val.MONTH_4 if val.MONTH_4 else 0
                            except:
                                newRow['MONTH_4'] = 0
                            try:
                                newRow['MONTH_5'] = val.MONTH_5 if val.MONTH_5 else 0
                            except:
                                newRow['MONTH_5'] = 0
                            try:
                                newRow['MONTH_6'] = val.MONTH_6 if val.MONTH_6 else 0
                            except:
                                newRow['MONTH_6'] = 0
                            try:
                                newRow['MONTH_7'] = val.MONTH_7 if val.MONTH_7 else 0
                            except:
                                newRow['MONTH_7'] = 0
                                
                                
                            try:
                                newRow['MONTH_8'] = val.MONTH_8 if val.MONTH_8 else 0
                            except:
                                newRow['MONTH_8'] = 0
                            try:
                                newRow['MONTH_9'] = val.MONTH_9 if val.MONTH_9 else 0
                            except:
                                newRow['MONTH_9'] = 0
                            try:
                                newRow['MONTH_10'] = val.MONTH_10 if val.MONTH_10 else 0
                            except:
                                newRow['MONTH_10'] = 0
                            try:
                                newRow['MONTH_11'] = val.MONTH_11 if val.MONTH_11 else 0
                            except:
                                newRow['MONTH_11'] = 0
                            try:
                                newRow['MONTH_12'] = val.MONTH_12 if val.MONTH_12 else 0
                            except:
                                newRow['MONTH_12'] = 0
                            try:
                                newRow['MONTH_13'] = val.MONTH_13 if val.MONTH_13 else 0
                            except:
                                newRow['MONTH_13'] = 0
                            newRow['QUOTE_RECORD_ID'] = val.QUOTE_RECORD_ID
                            newRow['QUOTE_ID'] = val.QUOTE_ID
                            
                            newRow['QTEREV_RECORD_ID'] = val.QTEREV_RECORD_ID
                            


                        quote_bills_header.Save()
    
                    '''Sql.RunQuery("""INSERT QT__Billing_Matrix_Header (
                                        QUOTE_ID,QUOTE_RECORD_ID,QTEREV_RECORD_ID,{DateColumn},YEAR,ownerId,cartId
                                    )
                                    SELECT TOP 1
                                        QUOTE_ID,										
                                        QUOTE_RECORD_ID,QTEREV_RECORD_ID,
                                        {SelectDateColoumn},
                                        {Year} as YEAR,
                                        {UserId} as ownerId,{CartId} as cartId
                                    FROM SAQIBP (NOLOCK)
                                    WHERE QUOTE_RECORD_ID='{QuoteRecordId}' AND QTEREV_RECORD_ID = '{RevisionRecordId}'""".format(
                                        QuoteRecordId=contract_quote_record_id,RevisionRecordId=quote_revision_record_id,DateColumn=date_columns,Year=no_of_year,SelectDateColoumn=header_select_date_columns, UserId= cartobj.USERID,CartId = cartobj.CART_ID
                                        ))'''
                    pivot_columns = ",".join(['[{}]'.format(billing_date) for billing_date in billing_date_column])
                    
                    for service_obj in services_obj:
                        no_of_years = 'Year '+no_of_year
                        Qustr = "WHERE QUOTE_RECORD_ID='{}' AND QTEREV_RECORD_ID = '{}' AND SERVICE_ID = '{}' AND BILLING_YEAR='{}' AND BILLING_DATE BETWEEN '{}' AND '{}'".format(contract_quote_record_id,quote_revision_record_id,
                                                                                        service_obj.SERVICE_ID,no_of_years, billing_date_column[0], billing_date_column[-1])				
                        Trace.Write('Qustr---'+str(Qustr))
                        #INC08834314 - Start - M
                        get_billing_type = Sql.GetFirst("SELECT BILLING_TYPE from SAQRIT(NOLOCK) where SERVICE_ID = '{}' and QUOTE_RECORD_ID = '{}' AND QTEREV_RECORD_ID = '{}' AND SERVICE_ID NOT IN ('Z0101','A6200','Z0108','Z0110')".format(service_obj.SERVICE_ID,contract_quote_record_id,quote_revision_record_id))
                        #INC08834314 - End - M
                        Trace.Write('SERVICE_ID---'+str(service_obj.SERVICE_ID))
                        if get_billing_type:
                            get_billing_types = get_billing_type.BILLING_TYPE
                            if str(get_billing_types).upper() =='FIXED':
                                get_ttl_amt = 'BILLING_VALUE'
                            elif str(get_billing_types).upper() =='VARIABLE':
                                get_ttl_amt = 'ESTVAL_INDT_CURR'
                            else:
                                get_ttl_amt = 'BILLING_VALUE'
                            get_bill_details_obj_data = Sql.GetList("""SELECT DISTINCT TOP 1000 * FROM ( SELECT * FROM (
                                                                                    SELECT ROW_NUMBER() OVER(ORDER BY EQUIPMENT_ID)
                                                                                    AS ROW, LINE,SERVICE_ID,SERVICE_DESCRIPTION,EQUIPMENT_ID,SERIAL_NUMBER,GREENBOOK,{BillingYear} as BILLING_YEAR,ANNUAL_BILLING_AMOUNT,QUOTE_RECORD_ID,GREENBOOK_RECORD_ID,QTEREV_RECORD_ID,EQUIPMENT_RECORD_ID,SERVICE_RECORD_ID,[WARRANTY_END_DATE], {SelectDateColoumn}
                                                                                            FROM (
                                                                                                    SELECT
                                                                                                            LINE,SERVICE_ID,SERVICE_DESCRIPTION,EQUIPMENT_ID,SERIAL_NUMBER,GREENBOOK,{get_ttl_amt},ANNUAL_BILLING_AMOUNT,QUOTE_RECORD_ID,GREENBOOK_RECORD_ID,QTEREV_RECORD_ID,EQUIPMENT_RECORD_ID,SERVICE_RECORD_ID,CONVERT(VARCHAR(10),WARRANTY_END_DATE,101) AS [WARRANTY_END_DATE],CONVERT(VARCHAR(10),FORMAT(BILLING_DATE,'MM-dd-yyyy'),101) AS [BILLING_DATE]                                          
                                                                                                    FROM SAQIBP
                                                                                                    {WhereString}
                                                                                            ) AS IQ
                                                                                            PIVOT
                                                                                            (
                                                                                                    SUM({get_ttl_amt})
                                                                                                    FOR BILLING_DATE IN ({PivotColumns})
                                                                                            )AS PVT

                                                                                    ) OQ WHERE ROW BETWEEN 1 AND 10000 ) AS FQ ORDER BY EQUIPMENT_ID""".format(BillingYear=no_of_year,PivotColumns=pivot_columns,WhereString=Qustr,SelectDateColoumn=select_date_columns,get_ttl_amt=get_ttl_amt))
                        
                            if get_bill_details_obj_data:
                                
                                
                                for val in get_bill_details_obj_data:
                                    newRow = quote_get_bill_details.AddNewRow()
                                    newRow['ANNUAL_BILLING_AMOUNT'] =  val.ANNUAL_BILLING_AMOUNT if val.ANNUAL_BILLING_AMOUNT else 0.00
                                    newRow['BILLING_TYPE'] = get_billing_types
                                    newRow['EQUIPMENT_ID'] =  val.EQUIPMENT_ID
                                    newRow['GREENBOOK'] = val.GREENBOOK
                                    newRow['YEAR'] =  val.BILLING_YEAR
                                    newRow['BILLING_INTERVAL'] =  ''
                                    newRow['SERVICE_ID'] = val.SERVICE_ID
                                    newRow['SERVICE_DESCRIPTION'] = val.SERVICE_DESCRIPTION
                                    newRow['SERIAL_NUMBER'] =  ''
                                    try:
                                        newRow['MONTH_1'] = val.MONTH_1 if val.MONTH_1  else 0
                                    except:
                                        
                                        newRow['MONTH_1'] = 0
                                    try:
                                        newRow['MONTH_2'] = val.MONTH_2 if val.MONTH_2 else 0
                                    except:
                                        
                                        newRow['MONTH_2'] = 0
                                    try:
                                        newRow['MONTH_3'] = val.MONTH_3 if val.MONTH_3  else 0
                                    except:
                                        
                                        newRow['MONTH_3'] = 0
                                    try:
                                        newRow['MONTH_4'] = val.MONTH_4 if val.MONTH_4 else 0
                                    except:
                                        
                                        newRow['MONTH_4'] = 0
                                    try:
                                        newRow['MONTH_3'] = val.MONTH_3 if val.MONTH_3 else 0
                                    except:
                                        
                                        newRow['MONTH_3'] = 0
                                    try:
                                        newRow['MONTH_4'] = val.MONTH_4 if val.MONTH_4 else 0
                                    except:
                                        newRow['MONTH_4'] = 0
                                    try:
                                        newRow['MONTH_5'] = val.MONTH_5 if val.MONTH_5 else 0
                                    except:
                                        newRow['MONTH_5'] = 0
                                    try:
                                        newRow['MONTH_6'] = val.MONTH_6 if val.MONTH_6 else 0
                                    except:
                                        newRow['MONTH_6'] = 0
                                    try:
                                        newRow['MONTH_7'] = val.MONTH_7 if val.MONTH_7  else 0
                                    except:
                                        newRow['MONTH_7'] = 0
                                    try:
                                        newRow['MONTH_8'] = val.MONTH_8 if val.MONTH_8  else 0
                                    except:
                                        newRow['MONTH_8'] = 0
                                    try:
                                        newRow['MONTH_9'] = val.MONTH_9 if val.MONTH_9  else 0
                                    except:
                                        newRow['MONTH_9'] = 0
                                    try:
                                        newRow['MONTH_10'] = val.MONTH_10 if val.MONTH_10  else 0
                                    except:
                                        newRow['MONTH_10'] = 0
                                    try:
                                        newRow['MONTH_11'] = val.MONTH_11 if val.MONTH_11  else 0
                                    except:
                                        newRow['MONTH_11'] = 0
                                    try:
                                        newRow['MONTH_12'] = val.MONTH_12 if val.MONTH_12  else 0
                                    except:
                                        newRow['MONTH_12'] = 0
                                    try:
                                        newRow['MONTH_13'] = val.MONTH_13 if val.MONTH_13  else 0
                                    except:
                                        newRow['MONTH_13'] = 0
                                    newRow['QUOTE_RECORD_ID'] = contract_quote_record_id
                                    newRow['QUOTE_ID'] = c4c_quote_id
                                    
                                    newRow['QTEREV_RECORD_ID'] = quote_revision_record_id
                                    
                                Trace.Write('353-BILLING_YEAR-'+str(newRow))
                                
                                quote_get_bill_details.Save()
                        
                        # Total based on service - end
    #set global start
    SUM_YEAR1 = Sql.GetFirst("SELECT convert(varchar,FORMAT(cast(SUM(MONTH_1) as numeric(10,2)),'###,###,##0.00','en-US'))  AS MONTH_1, convert(varchar,FORMAT(cast(SUM(MONTH_2) as numeric(10,2)),'###,###,##0.00','en-US'))  AS MONTH_2, convert(varchar,FORMAT(cast(SUM(MONTH_3) as numeric(10,2)),'###,###,##0.00','en-US'))  AS MONTH_3, convert(varchar,FORMAT(cast(SUM(MONTH_4) as numeric(10,2)),'###,###,##0.00','en-US'))  AS MONTH_4, convert(varchar,FORMAT(cast(SUM(MONTH_5) as numeric(10,2)),'###,###,##0.00','en-US'))  AS MONTH_5, convert(varchar,FORMAT(cast(SUM(MONTH_6) as numeric(10,2)),'###,###,##0.00','en-US'))  AS MONTH_6, convert(varchar,FORMAT(cast(SUM(MONTH_7) as numeric(10,2)),'###,###,##0.00','en-US'))  AS MONTH_7, convert(varchar,FORMAT(cast(SUM(MONTH_8) as numeric(10,2)),'###,###,##0.00','en-US'))  AS MONTH_8, convert(varchar,FORMAT(cast(SUM(MONTH_9) as numeric(10,2)),'###,###,##0.00','en-US'))  AS MONTH_9, convert(varchar,FORMAT(cast(SUM(MONTH_10) as numeric(10,2)),'###,###,##0.00','en-US'))  AS MONTH_10, convert(varchar,FORMAT(cast(SUM(MONTH_11) as numeric(10,2)),'###,###,##0.00','en-US'))  AS MONTH_11, convert(varchar,FORMAT(cast(SUM(MONTH_12) as numeric(10,2)),'###,###,##0.00','en-US'))  AS MONTH_12,convert(varchar,FORMAT(cast(SUM(MONTH_13) as numeric(10,2)),'###,###,##0.00','en-US'))  AS MONTH_13 FROM QT__BM_YEAR_1(NOLOCK) WHERE QUOTE_RECORD_ID = '"+str(contract_quote_record_id)+"' AND YEAR = '1' AND QTEREV_RECORD_ID = '"+str(quote_revision_record_id) + "'")
    SUM_YEAR2 = Sql.GetFirst("SELECT convert(varchar,FORMAT(cast(SUM(MONTH_1) as numeric(10,2)),'###,###,##0.00','en-US'))  AS MONTH_1, convert(varchar,FORMAT(cast(SUM(MONTH_2) as numeric(10,2)),'###,###,##0.00','en-US'))  AS MONTH_2, convert(varchar,FORMAT(cast(SUM(MONTH_3) as numeric(10,2)),'###,###,##0.00','en-US'))  AS MONTH_3, convert(varchar,FORMAT(cast(SUM(MONTH_4) as numeric(10,2)),'###,###,##0.00','en-US'))  AS MONTH_4, convert(varchar,FORMAT(cast(SUM(MONTH_5) as numeric(10,2)),'###,###,##0.00','en-US'))  AS MONTH_5, convert(varchar,FORMAT(cast(SUM(MONTH_6) as numeric(10,2)),'###,###,##0.00','en-US'))  AS MONTH_6, convert(varchar,FORMAT(cast(SUM(MONTH_7) as numeric(10,2)),'###,###,##0.00','en-US'))  AS MONTH_7, convert(varchar,FORMAT(cast(SUM(MONTH_8) as numeric(10,2)),'###,###,##0.00','en-US'))  AS MONTH_8, convert(varchar,FORMAT(cast(SUM(MONTH_9) as numeric(10,2)),'###,###,##0.00','en-US'))  AS MONTH_9, convert(varchar,FORMAT(cast(SUM(MONTH_10) as numeric(10,2)),'###,###,##0.00','en-US'))  AS MONTH_10, convert(varchar,FORMAT(cast(SUM(MONTH_11) as numeric(10,2)),'###,###,##0.00','en-US'))  AS MONTH_11, convert(varchar,FORMAT(cast(SUM(MONTH_12) as numeric(10,2)),'###,###,##0.00','en-US'))  AS MONTH_12,convert(varchar,FORMAT(cast(SUM(MONTH_13) as numeric(10,2)),'###,###,##0.00','en-US'))  AS MONTH_13 FROM QT__BM_YEAR_1(NOLOCK) WHERE QUOTE_RECORD_ID = '"+str(contract_quote_record_id)+"' AND YEAR = '2'  AND QTEREV_RECORD_ID = '"+str(quote_revision_record_id) + "'")
    SUM_YEAR3 = Sql.GetFirst("SELECT convert(varchar,FORMAT(cast(SUM(MONTH_1) as numeric(10,2)),'###,###,##0.00','en-US'))  AS MONTH_1, convert(varchar,FORMAT(cast(SUM(MONTH_2) as numeric(10,2)),'###,###,##0.00','en-US'))  AS MONTH_2, convert(varchar,FORMAT(cast(SUM(MONTH_3) as numeric(10,2)),'###,###,##0.00','en-US'))  AS MONTH_3, convert(varchar,FORMAT(cast(SUM(MONTH_4) as numeric(10,2)),'###,###,##0.00','en-US'))  AS MONTH_4, convert(varchar,FORMAT(cast(SUM(MONTH_5) as numeric(10,2)),'###,###,##0.00','en-US'))  AS MONTH_5, convert(varchar,FORMAT(cast(SUM(MONTH_6) as numeric(10,2)),'###,###,##0.00','en-US'))  AS MONTH_6, convert(varchar,FORMAT(cast(SUM(MONTH_7) as numeric(10,2)),'###,###,##0.00','en-US'))  AS MONTH_7, convert(varchar,FORMAT(cast(SUM(MONTH_8) as numeric(10,2)),'###,###,##0.00','en-US'))  AS MONTH_8, convert(varchar,FORMAT(cast(SUM(MONTH_9) as numeric(10,2)),'###,###,##0.00','en-US'))  AS MONTH_9, convert(varchar,FORMAT(cast(SUM(MONTH_10) as numeric(10,2)),'###,###,##0.00','en-US'))  AS MONTH_10, convert(varchar,FORMAT(cast(SUM(MONTH_11) as numeric(10,2)),'###,###,##0.00','en-US'))  AS MONTH_11, convert(varchar,FORMAT(cast(SUM(MONTH_12) as numeric(10,2)),'###,###,##0.00','en-US'))  AS MONTH_12,convert(varchar,FORMAT(cast(SUM(MONTH_13) as numeric(10,2)),'###,###,##0.00','en-US'))  AS MONTH_13 FROM QT__BM_YEAR_1(NOLOCK) WHERE QUOTE_RECORD_ID = '"+str(contract_quote_record_id)+"' AND YEAR = '3'  AND QTEREV_RECORD_ID = '"+str(quote_revision_record_id) + "'")
    SUM_YEAR4 = Sql.GetFirst("SELECT convert(varchar,FORMAT(cast(SUM(MONTH_1) as numeric(10,2)),'###,###,##0.00','en-US'))  AS MONTH_1, convert(varchar,FORMAT(cast(SUM(MONTH_2) as numeric(10,2)),'###,###,##0.00','en-US'))  AS MONTH_2, convert(varchar,FORMAT(cast(SUM(MONTH_3) as numeric(10,2)),'###,###,##0.00','en-US'))  AS MONTH_3, convert(varchar,FORMAT(cast(SUM(MONTH_4) as numeric(10,2)),'###,###,##0.00','en-US'))  AS MONTH_4, convert(varchar,FORMAT(cast(SUM(MONTH_5) as numeric(10,2)),'###,###,##0.00','en-US'))  AS MONTH_5, convert(varchar,FORMAT(cast(SUM(MONTH_6) as numeric(10,2)),'###,###,##0.00','en-US'))  AS MONTH_6, convert(varchar,FORMAT(cast(SUM(MONTH_7) as numeric(10,2)),'###,###,##0.00','en-US'))  AS MONTH_7, convert(varchar,FORMAT(cast(SUM(MONTH_8) as numeric(10,2)),'###,###,##0.00','en-US'))  AS MONTH_8, convert(varchar,FORMAT(cast(SUM(MONTH_9) as numeric(10,2)),'###,###,##0.00','en-US'))  AS MONTH_9, convert(varchar,FORMAT(cast(SUM(MONTH_10) as numeric(10,2)),'###,###,##0.00','en-US'))  AS MONTH_10, convert(varchar,FORMAT(cast(SUM(MONTH_11) as numeric(10,2)),'###,###,##0.00','en-US'))  AS MONTH_11, convert(varchar,FORMAT(cast(SUM(MONTH_12) as numeric(10,2)),'###,###,##0.00','en-US'))  AS MONTH_12,convert(varchar,FORMAT(cast(SUM(MONTH_13) as numeric(10,2)),'###,###,##0.00','en-US'))  AS MONTH_13 FROM QT__BM_YEAR_1(NOLOCK) WHERE QUOTE_RECORD_ID = '"+str(contract_quote_record_id)+"' AND YEAR = '4'  AND QTEREV_RECORD_ID = '"+str(quote_revision_record_id) + "'")
    SUM_YEAR5 = Sql.GetFirst("SELECT convert(varchar,FORMAT(cast(SUM(MONTH_1) as numeric(10,2)),'###,###,##0.00','en-US'))  AS MONTH_1, convert(varchar,FORMAT(cast(SUM(MONTH_2) as numeric(10,2)),'###,###,##0.00','en-US'))  AS MONTH_2, convert(varchar,FORMAT(cast(SUM(MONTH_3) as numeric(10,2)),'###,###,##0.00','en-US'))  AS MONTH_3, convert(varchar,FORMAT(cast(SUM(MONTH_4) as numeric(10,2)),'###,###,##0.00','en-US'))  AS MONTH_4, convert(varchar,FORMAT(cast(SUM(MONTH_5) as numeric(10,2)),'###,###,##0.00','en-US'))  AS MONTH_5, convert(varchar,FORMAT(cast(SUM(MONTH_6) as numeric(10,2)),'###,###,##0.00','en-US'))  AS MONTH_6, convert(varchar,FORMAT(cast(SUM(MONTH_7) as numeric(10,2)),'###,###,##0.00','en-US'))  AS MONTH_7, convert(varchar,FORMAT(cast(SUM(MONTH_8) as numeric(10,2)),'###,###,##0.00','en-US'))  AS MONTH_8, convert(varchar,FORMAT(cast(SUM(MONTH_9) as numeric(10,2)),'###,###,##0.00','en-US'))  AS MONTH_9, convert(varchar,FORMAT(cast(SUM(MONTH_10) as numeric(10,2)),'###,###,##0.00','en-US'))  AS MONTH_10, convert(varchar,FORMAT(cast(SUM(MONTH_11) as numeric(10,2)),'###,###,##0.00','en-US'))  AS MONTH_11, convert(varchar,FORMAT(cast(SUM(MONTH_12) as numeric(10,2)),'###,###,##0.00','en-US'))  AS MONTH_12,convert(varchar,FORMAT(cast(SUM(MONTH_13) as numeric(10,2)),'###,###,##0.00','en-US'))  AS MONTH_13 FROM QT__BM_YEAR_1(NOLOCK) WHERE QUOTE_RECORD_ID = '"+str(contract_quote_record_id)+"' AND YEAR = '5' AND  QTEREV_RECORD_ID = '"+str(quote_revision_record_id) + "'")
    if SUM_YEAR1:
        M1_Y1 = SUM_YEAR1.MONTH_1
        Quote.SetGlobal('M1_Y1', str(M1_Y1))
        M2_Y1 = SUM_YEAR1.MONTH_2
        Quote.SetGlobal('M2_Y1', str(M2_Y1))
        M3_Y1 = SUM_YEAR1.MONTH_3
        Quote.SetGlobal('M3_Y1', str(M3_Y1))
        M4_Y1 = SUM_YEAR1.MONTH_4
        Quote.SetGlobal('M4_Y1', str(M4_Y1))
        M5_Y1 = SUM_YEAR1.MONTH_5
        Quote.SetGlobal('M5_Y1', str(M5_Y1))
        M6_Y1 = SUM_YEAR1.MONTH_6
        Quote.SetGlobal('M6_Y1', str(M6_Y1))
        M7_Y1 = SUM_YEAR1.MONTH_7
        Quote.SetGlobal('M7_Y1', str(M7_Y1))
        M8_Y1 = SUM_YEAR1.MONTH_8
        Quote.SetGlobal('M8_Y1', str(M8_Y1))
        M9_Y1 = SUM_YEAR1.MONTH_9
        Quote.SetGlobal('M9_Y1', str(M9_Y1))
        M10_Y1 = SUM_YEAR1.MONTH_10
        Quote.SetGlobal('M10_Y1', str(M10_Y1))
        M11_Y1 = SUM_YEAR1.MONTH_11
        Quote.SetGlobal('M11_Y1', str(M11_Y1))
        M12_Y1 = SUM_YEAR1.MONTH_12
        Quote.SetGlobal('M12_Y1', str(M12_Y1))
        M13_Y1 = SUM_YEAR1.MONTH_13
        Quote.SetGlobal('M13_Y1', str(M13_Y1))
        Quote.SetGlobal('BM_YEAR_1', 'BM_YEAR_1')
        Quote.GetCustomField('BM_YEAR_1').Content = 'BM_YEAR_1'
    if SUM_YEAR2:
        M1_Y2 =''
        if str(SUM_YEAR2.MONTH_1) != "":
            M1_Y2 = SUM_YEAR2.MONTH_1
            Quote.SetGlobal('M1_Y2', str(M1_Y2))
            #Quote.GetCustomField('BM_YEAR_2').Content = 'BM_YEAR_2' INC08622848 M
        else:
            Quote.SetGlobal('M1_Y2', '')
        M2_Y2 = SUM_YEAR2.MONTH_2
        Quote.SetGlobal('M2_Y2', str(M2_Y2))
        if M2_Y2:
            Quote.GetCustomField('BM_YEAR_2').Content = 'BM_YEAR_2'
            Quote.SetGlobal('BM_YEAR_2', 'BM_YEAR_2')
        else:
            Quote.GetCustomField('BM_YEAR_2').Content = ''
            Quote.SetGlobal('BM_YEAR_2', '')
        #Quote.SetGlobal('M2_Y2', str(M2_Y2)) INC08622848 M
        M3_Y2 = SUM_YEAR2.MONTH_3
        Quote.SetGlobal('M3_Y2', str(M3_Y2))
        M4_Y2 = SUM_YEAR2.MONTH_4
        Quote.SetGlobal('M4_Y2', str(M4_Y2))
        M5_Y2 = SUM_YEAR2.MONTH_5
        Quote.SetGlobal('M5_Y2', str(M5_Y2))
        M6_Y2 = SUM_YEAR2.MONTH_6
        Quote.SetGlobal('M6_Y2', str(M6_Y2))
        M7_Y2 = SUM_YEAR2.MONTH_7
        Quote.SetGlobal('M7_Y2', str(M7_Y2))
        M8_Y2 = SUM_YEAR2.MONTH_8
        Quote.SetGlobal('M8_Y2', str(M8_Y2))
        M9_Y2 = SUM_YEAR2.MONTH_9
        Quote.SetGlobal('M9_Y2', str(M9_Y2))
        M10_Y2 = SUM_YEAR2.MONTH_10
        Quote.SetGlobal('M10_Y2', str(M10_Y2))
        M11_Y2 = SUM_YEAR2.MONTH_11
        Quote.SetGlobal('M11_Y2', str(M11_Y2))
        M12_Y2 = SUM_YEAR2.MONTH_12
        Quote.SetGlobal('M12_Y2', str(M12_Y2))
        M13_Y2 = SUM_YEAR2.MONTH_13
        Quote.SetGlobal('M13_Y2', str(M13_Y2))
        #Quote.SetGlobal('BM_YEAR_2', 'BM_YEAR_2')
        #Quote.GetCustomField('BM_YEAR_2').Content = 'BM_YEAR_2'
    if SUM_YEAR3:
        #Quote.GetCustomField('BM_YEAR_3').Content = 'BM_YEAR_3'
        #Quote.SetGlobal('BM_YEAR_3', 'BM_YEAR_3')
        #M1_Y3 = SUM_YEAR3.MONTH_1
        M1_Y3 =''
        if str(SUM_YEAR3.MONTH_1) != "":
            M1_Y3 = SUM_YEAR3.MONTH_1
            Quote.SetGlobal('M1_Y3', str(M1_Y3))
            Quote.GetCustomField('BM_YEAR_3').Content = 'BM_YEAR_3'
        else:
            Quote.SetGlobal('M1_Y3', '')
        Quote.SetGlobal('M1_Y3', str(M1_Y3))
        M2_Y3 = SUM_YEAR3.MONTH_2
        Quote.SetGlobal('M2_Y3', str(M2_Y3))
        M3_Y3 = SUM_YEAR3.MONTH_3
        Quote.SetGlobal('M3_Y3', str(M3_Y3))
        M4_Y3 = SUM_YEAR3.MONTH_4
        Quote.SetGlobal('M4_Y3', str(M4_Y3))
        M5_Y3 = SUM_YEAR3.MONTH_5
        Quote.SetGlobal('M5_Y3', str(M5_Y3))
        M6_Y3 = SUM_YEAR3.MONTH_6
        Quote.SetGlobal('M6_Y3', str(M6_Y3))
        M7_Y3 = SUM_YEAR3.MONTH_7
        Quote.SetGlobal('M7_Y3', str(M7_Y3))
        M8_Y3 = SUM_YEAR3.MONTH_8
        Quote.SetGlobal('M8_Y3', str(M8_Y3))
        M9_Y3 = SUM_YEAR3.MONTH_9
        Quote.SetGlobal('M9_Y3', str(M9_Y3))
        M10_Y3 = SUM_YEAR3.MONTH_10
        Quote.SetGlobal('M10_Y3', str(M10_Y3))
        M11_Y3 = SUM_YEAR3.MONTH_11
        Quote.SetGlobal('M11_Y3', str(M10_Y3))
        M12_Y3 = SUM_YEAR3.MONTH_12
        Quote.SetGlobal('M12_Y3', str(M12_Y3))
        M13_Y3 = SUM_YEAR3.MONTH_13
        Quote.SetGlobal('M13_Y3', str(M13_Y3))
    if SUM_YEAR4:
        M1_Y4 =''
        if str(SUM_YEAR4.MONTH_1) != "":
            M1_Y4 = SUM_YEAR4.MONTH_1
            Quote.SetGlobal('M1_Y4', str(M1_Y4))
            Quote.GetCustomField('BM_YEAR_4').Content = 'BM_YEAR_4'
        else:
            Quote.SetGlobal('M1_Y4', '')
        M2_Y4 = SUM_YEAR4.MONTH_2
        Quote.SetGlobal('M2_Y4', str(M2_Y4))
        M3_Y4 = SUM_YEAR4.MONTH_3
        Quote.SetGlobal('M3_Y4', str(M3_Y4))
        M4_Y4 = SUM_YEAR4.MONTH_4
        Quote.SetGlobal('M4_Y4', str(M4_Y4))
        M5_Y4 = SUM_YEAR4.MONTH_5
        Quote.SetGlobal('M5_Y4', str(M5_Y4))
        M6_Y4 = SUM_YEAR4.MONTH_6
        Quote.SetGlobal('M6_Y4', str(M6_Y4))
        M7_Y4 = SUM_YEAR4.MONTH_7
        Quote.SetGlobal('M7_Y4', str(M7_Y4))
        M8_Y4 = SUM_YEAR4.MONTH_8
        Quote.SetGlobal('M8_Y4', str(M8_Y4))
        M9_Y4 = SUM_YEAR4.MONTH_9
        Quote.SetGlobal('M9_Y4', str(M9_Y4))
        M10_Y4 = SUM_YEAR4.MONTH_10
        Quote.SetGlobal('M10_Y4', str(M10_Y4))
        M11_Y4 = SUM_YEAR4.MONTH_11
        Quote.SetGlobal('M11_Y4', str(M11_Y4))
        M12_Y4 = SUM_YEAR4.MONTH_12
        Quote.SetGlobal('M12_Y4', str(M12_Y4))
        M13_Y4 = SUM_YEAR4.MONTH_13
        Quote.SetGlobal('M13_Y4', str(M13_Y4))
    if SUM_YEAR5:
        M1_Y5 =''
        if str(SUM_YEAR5.MONTH_1) != "":
            M1_Y5 = SUM_YEAR5.MONTH_1
            Quote.SetGlobal('M1_Y5', str(M1_Y5))
            Quote.GetCustomField('BM_YEAR_5').Content = 'BM_YEAR_5'
        else:
            Quote.SetGlobal('M1_Y5', '')
        #M1_Y5 = SUM_YEAR5.MONTH_1
        #Quote.SetGlobal('M1_Y5', str(M1_Y5))
        M2_Y5 = SUM_YEAR5.MONTH_2
        Quote.SetGlobal('M2_Y5', str(M2_Y5))
        M3_Y5 = SUM_YEAR5.MONTH_3
        Quote.SetGlobal('M3_Y5', str(M3_Y5))
        M4_Y5 = SUM_YEAR5.MONTH_4
        Quote.SetGlobal('M4_Y5', str(M4_Y5))
        M5_Y5 = SUM_YEAR5.MONTH_5
        Quote.SetGlobal('M5_Y5', str(M5_Y5))
        M6_Y5 = SUM_YEAR5.MONTH_6
        Quote.SetGlobal('M6_Y5', str(M6_Y5))
        M7_Y5 = SUM_YEAR5.MONTH_7
        Quote.SetGlobal('M7_Y5', str(M7_Y5))
        M8_Y5 = SUM_YEAR5.MONTH_8
        Quote.SetGlobal('M8_Y5', str(M8_Y5))
        M9_Y5 = SUM_YEAR5.MONTH_9
        Quote.SetGlobal('M9_Y5', str(M9_Y5))
        M10_Y5 = SUM_YEAR5.MONTH_10
        Quote.SetGlobal('M10_Y5', str(M10_Y5))
        M11_Y5 = SUM_YEAR5.MONTH_11
        Quote.SetGlobal('M11_Y5', str(M11_Y5))
        M12_Y5 = SUM_YEAR5.MONTH_12
        Quote.SetGlobal('M12_Y5', str(M12_Y5))
        M13_Y5 = SUM_YEAR5.MONTH_13
        Quote.SetGlobal('M13_Y5', str(M13_Y5))
    if Quote.GetGlobal('M13_Y1') != '0.00':
        GetYear1EndDate = Sql.GetFirst("""SELECT
        ID,
        (SELECT MAX(convert(date, LastUpdateDate))
            FROM (VALUES (MONTH_1),(MONTH_2),(MONTH_3),(MONTH_4),(MONTH_5),(MONTH_6),(MONTH_7),(MONTH_8),(MONTH_9),(MONTH_10),(MONTH_11),(MONTH_12),(MONTH_13)) AS UpdateDate(LastUpdateDate))
        AS LastUpdateDate
        FROM QT__Billing_Matrix_Header
        where QUOTE_RECORD_ID = '"""+str(contract_quote_record_id)+"""' AND YEAR = '1' AND QTEREV_RECORD_ID = '"""+str(quote_revision_record_id)+"""'""")
    else:

        GetYear1EndDate = Sql.GetFirst("""SELECT
        ID,
        (SELECT MAX(convert(date, LastUpdateDate))
            FROM (VALUES (MONTH_1),(MONTH_2),(MONTH_3),(MONTH_4),(MONTH_5),(MONTH_6),(MONTH_7),(MONTH_8),(MONTH_9),(MONTH_10),(MONTH_11),(MONTH_12)) AS UpdateDate(LastUpdateDate))
        AS LastUpdateDate
        FROM QT__Billing_Matrix_Header
        where QUOTE_RECORD_ID = '"""+str(contract_quote_record_id)+"""' AND YEAR = '1' AND QTEREV_RECORD_ID = '"""+str(quote_revision_record_id)+"""'""")

    #DATES_YEAR_1 = SqlHelper.GetFirst("SELECT MONTH_1, MONTH_1, MONTH_2, MONTH_3, MONTH_4, MONTH_5, MONTH_6, MONTH_7, MONTH_8, MONTH_9, MONTH_10, MONTH_10, MONTH_11, MONTH_12 FROM #QT__Billing_Matrix_Header(NOLOCK) WHERE QUOTE_RECORD_ID = '"""+str(recid)+"""' AND YEAR = '4'")

    if Quote.GetGlobal('M13_Y2') != '0.00':
        GetYear2EndDate = Sql.GetFirst("""SELECT
        ID,
        (SELECT MAX(convert(date, LastUpdateDate))
            FROM (VALUES (MONTH_1),(MONTH_2),(MONTH_3),(MONTH_4),(MONTH_5),(MONTH_6),(MONTH_7),(MONTH_8),(MONTH_9),(MONTH_10),(MONTH_11),(MONTH_12),((MONTH_13))) AS UpdateDate(LastUpdateDate))
        AS LastUpdateDate
        FROM QT__Billing_Matrix_Header
        where QUOTE_RECORD_ID = '"""+str(contract_quote_record_id)+"""' AND YEAR = '2' AND QTEREV_RECORD_ID = '"""+str(quote_revision_record_id)+"""'""")
    else:
        GetYear2EndDate = Sql.GetFirst("""SELECT
        ID,
        (SELECT MAX(convert(date, LastUpdateDate))
            FROM (VALUES (MONTH_1),(MONTH_2),(MONTH_3),(MONTH_4),(MONTH_5),(MONTH_6),(MONTH_7),(MONTH_8),(MONTH_9),(MONTH_10),(MONTH_11),(MONTH_12)) AS UpdateDate(LastUpdateDate))
        AS LastUpdateDate
        FROM QT__Billing_Matrix_Header
        where QUOTE_RECORD_ID = '"""+str(contract_quote_record_id)+"""' AND YEAR = '2' AND QTEREV_RECORD_ID = '"""+str(quote_revision_record_id)+"""'""")
    if Quote.GetGlobal('M13_Y3') != '0.00':
        GetYear3EndDate = Sql.GetFirst("""SELECT
        ID,
        (SELECT MAX(convert(date, LastUpdateDate))
            FROM (VALUES (MONTH_1),(MONTH_2),(MONTH_3),(MONTH_4),(MONTH_5),(MONTH_6),(MONTH_7),(MONTH_8),(MONTH_9),(MONTH_10),(MONTH_11),(MONTH_12),(MONTH_13)) AS UpdateDate(LastUpdateDate))
        AS LastUpdateDate
        FROM QT__Billing_Matrix_Header
        where QUOTE_RECORD_ID = '"""+str(contract_quote_record_id)+"""' AND YEAR = '3' AND QTEREV_RECORD_ID = '"""+str(quote_revision_record_id)+"""'""")
    else:
        GetYear3EndDate = Sql.GetFirst("""SELECT
        ID,
        (SELECT MAX(convert(date, LastUpdateDate))
            FROM (VALUES (MONTH_1),(MONTH_2),(MONTH_3),(MONTH_4),(MONTH_5),(MONTH_6),(MONTH_7),(MONTH_8),(MONTH_9),(MONTH_10),(MONTH_11),(MONTH_12)) AS UpdateDate(LastUpdateDate))
        AS LastUpdateDate
        FROM QT__Billing_Matrix_Header
        where QUOTE_RECORD_ID = '"""+str(contract_quote_record_id)+"""' AND YEAR = '3' AND QTEREV_RECORD_ID = '"""+str(quote_revision_record_id)+"""'""")
    if Quote.GetGlobal('M13_Y4') != '0.00':
        GetYear4EndDate = Sql.GetFirst("""SELECT
        ID,
        (SELECT MAX(convert(date, LastUpdateDate))
            FROM (VALUES (MONTH_1),(MONTH_2),(MONTH_3),(MONTH_4),(MONTH_5),(MONTH_6),(MONTH_7),(MONTH_8),(MONTH_9),(MONTH_10),(MONTH_11),(MONTH_12),(MONTH_13)) AS UpdateDate(LastUpdateDate))
        AS LastUpdateDate
        FROM QT__Billing_Matrix_Header
        where QUOTE_RECORD_ID = '"""+str(contract_quote_record_id)+"""' AND YEAR = '4' AND QTEREV_RECORD_ID = '"""+str(quote_revision_record_id)+"""'""")
    else:
        GetYear4EndDate = Sql.GetFirst("""SELECT
        ID,
        (SELECT MAX(convert(date, LastUpdateDate))
            FROM (VALUES (MONTH_1),(MONTH_2),(MONTH_3),(MONTH_4),(MONTH_5),(MONTH_6),(MONTH_7),(MONTH_8),(MONTH_9),(MONTH_10),(MONTH_11),(MONTH_12)) AS UpdateDate(LastUpdateDate))
        AS LastUpdateDate
        FROM QT__Billing_Matrix_Header
        where QUOTE_RECORD_ID = '"""+str(contract_quote_record_id)+"""' AND YEAR = '4' AND QTEREV_RECORD_ID = '"""+str(quote_revision_record_id)+"""'""")
    if Quote.GetGlobal('M13_Y5') != '0.00':
        GetYear5EndDate = Sql.GetFirst("""SELECT
        ID,
        (SELECT MAX(convert(date, LastUpdateDate))
            FROM (VALUES (MONTH_1),(MONTH_2),(MONTH_3),(MONTH_4),(MONTH_5),(MONTH_6),(MONTH_7),(MONTH_8),(MONTH_9),(MONTH_10),(MONTH_11),(MONTH_12),(MONTH_13)) AS UpdateDate(LastUpdateDate))
        AS LastUpdateDate
        FROM QT__Billing_Matrix_Header
        where QUOTE_RECORD_ID = '"""+str(contract_quote_record_id)+"""' AND YEAR = '5' AND QTEREV_RECORD_ID = '"""+str(quote_revision_record_id)+"""'""")
    else:
        GetYear5EndDate = Sql.GetFirst("""SELECT
        ID,
        (SELECT MAX(convert(date, LastUpdateDate))
            FROM (VALUES (MONTH_1),(MONTH_2),(MONTH_3),(MONTH_4),(MONTH_5),(MONTH_6),(MONTH_7),(MONTH_8),(MONTH_9),(MONTH_10),(MONTH_11),(MONTH_12)) AS UpdateDate(LastUpdateDate))
        AS LastUpdateDate
        FROM QT__Billing_Matrix_Header
        where QUOTE_RECORD_ID = '"""+str(contract_quote_record_id)+"""' AND YEAR = '5' AND QTEREV_RECORD_ID = '"""+str(quote_revision_record_id)+"""'""")

    try:
        Y1ED = GetYear1EndDate.LastUpdateDate
        d1 = '{}-{}-{}'.format(Y1ED.Month, Y1ED.Day, Y1ED.Year)
        Quote.SetGlobal('Year1EndDate', str(d1))
        Trace.Write('570----Year1EndDate--'+str(d1))		
    except:
        Trace.Write('570------')
        pass
    try:
        Y2ED = GetYear2EndDate.LastUpdateDate
        d2 = '{}-{}-{}'.format(Y2ED.Month, Y2ED.Day, Y2ED.Year)
        Quote.SetGlobal('Year2EndDate', str(d2))		
    except:
        pass
    try:
        Y3ED = GetYear3EndDate.LastUpdateDate
        d3 = '{}-{}-{}'.format(Y3ED.Month, Y3ED.Day, Y3ED.Year)
        Quote.SetGlobal('Year3EndDate', str(d3))		
    except:
        pass
    try:
        Y4ED = GetYear4EndDate.LastUpdateDate
        d4 = '{}-{}-{}'.format(Y4ED.Month, Y4ED.Day, Y4ED.Year)
        Quote.SetGlobal('Year4EndDate', str(d4))		
    except:
        pass
    try:
        Y5ED = GetYear5EndDate.LastUpdateDate
        d5 = '{}-{}-{}'.format(Y5ED.Month, Y5ED.Day, Y5ED.Year)
        Quote.SetGlobal('Year5EndDate', str(d5))		
    except:
        pass
    return True
#A055S000P01-10549-end
def _insert_subtotal_by_offerring_quote_table():
    
    
    try:
        delete_offerings = "DELETE FROM QT__QT_SAQRIS where cartId = {CartId} AND QUOTE_RECORD_ID ='{c4c_quote_id}' and  QTEREV_RECORD_ID= '{rev_rec_id}'".format(CartId = cartobj.CART_ID,UserId= cartobj.USERID,c4c_quote_id = contract_quote_record_id,rev_rec_id = quote_revision_record_id)
        Sql.RunQuery(delete_offerings)
        delete_items = "DELETE FROM QT__QT_SAQRIT where cartId = {CartId} AND QUOTE_RECORD_ID ='{c4c_quote_id}' and  QTEREV_RECORD_ID= '{rev_rec_id}'".format(CartId = cartobj.CART_ID,c4c_quote_id = contract_quote_record_id,rev_rec_id = quote_revision_record_id)
        Sql.RunQuery(delete_offerings)
        Sql.RunQuery(delete_items)
    except:
        Trace.Write("NO REC FOUND ")


    Quoteofferings = Quote.QuoteTables["QT_SAQRIS"]

    getoffer_details_obj = Sql.GetList("select SAQRIS.COMMITTED_VALUE,SAQRIS.CONTRACT_VALID_FROM,SAQRIS.CONTRACT_VALID_TO,SAQRIS.DIVISION_ID,SAQRIS.DIVISION_RECORD_ID,SAQRIS.DOC_CURRENCY,SAQRIS.DOCCURR_RECORD_ID,SAQRIS.ESTIMATED_VALUE,SAQRIS.GLOBAL_CURRENCY,SAQRIS.GLOBAL_CURRENCY_RECORD_ID,SAQRIS.LINE,SAQRIS.NET_PRICE,SAQRIS.NET_PRICE_INGL_CURR,SAQRIS.NET_VALUE,SAQRIS.NET_VALUE_INGL_CURR,SAQRIS.PLANT_ID,SAQRIS.PLANT_RECORD_ID,SAQRIS.SERVICE_DESCRIPTION,SAQRIS.SERVICE_ID,SAQRIS.SERVICE_RECORD_ID,SAQRIS.QUANTITY,SAQRIS.QUOTE_ID,SAQRIS.QUOTE_RECORD_ID,SAQRIS.QTEREV_ID,SAQRIS.QTEREV_RECORD_ID,SAQRIS.TAX_PERCENTAGE,SAQRIS.TAX_AMOUNT,SAQRIS.TAX_AMOUNT_INGL_CURR,SAQRIS.UNIT_PRICE,SAQRIS.UNIT_PRICE_INGL_CURR,{UserId} as ownerId,{CartId} as cartId from SAQRIS (NOLOCK)  where SAQRIS.QUOTE_RECORD_ID ='{c4c_quote_id}' and  SAQRIS.QTEREV_RECORD_ID= '{rev_rec_id}'".format(CartId = cartobj.CART_ID,UserId= cartobj.USERID,c4c_quote_id = contract_quote_record_id,rev_rec_id = quote_revision_record_id))

    quote_subtotalofferings = Quote.QuoteTables["QT_SAQRIS"]
    quote_subtotalofferings.Rows.Clear()
    if getoffer_details_obj:
        for val in getoffer_details_obj:
            newRow = Quoteofferings.AddNewRow()
            if val.COMMITTED_VALUE:
                newRow['COMMITTED_VALUE'] = val.COMMITTED_VALUE
            else:
                newRow['COMMITTED_VALUE'] =0
            newRow['CONTRACT_VALID_FROM'] = val.CONTRACT_VALID_FROM
            newRow['CONTRACT_VALID_TO'] = val.CONTRACT_VALID_TO
            newRow['DIVISION_ID'] = val.DIVISION_ID
            newRow['DIVISION_RECORD_ID'] = val.DIVISION_RECORD_ID
            newRow['DOC_CURRENCY'] =  val.DOC_CURRENCY
            newRow['DOCCURR_RECORD_ID'] = val.DOCCURR_RECORD_ID
            if val.ESTIMATED_VALUE:
                newRow['ESTIMATED_VALUE'] = val.ESTIMATED_VALUE
            else:
                newRow['ESTIMATED_VALUE'] = 0

            if val.TAX_AMOUNT_INGL_CURR:
                newRow['TAX_AMOUNT_INGL_CURR'] = str(val.TAX_AMOUNT_INGL_CURR)
            else:
                newRow['TAX_AMOUNT_INGL_CURR'] = 0
            newRow['GLOBAL_CURRENCY'] = val.GLOBAL_CURRENCY
            newRow['GLOBAL_CURRENCY_RECORD_ID'] = val.GLOBAL_CURRENCY_RECORD_ID
            newRow['LINE'] = val.LINE
            if val.NET_VALUE:
                newRow['NET_PRICE'] = val.NET_VALUE
            else:
                newRow['NET_PRICE'] = 0
            if val.NET_VALUE:
                newRow['NET_PRICE_INGL_CURR'] = val.NET_VALUE
            else:
                newRow['NET_PRICE_INGL_CURR'] = 0
            newRow['SERVICE_ID'] = val.SERVICE_ID
            # if val.NET_VALUE:
            #     newRow['NET_VALUE'] = val.NET_VALUE
            # else:
            #     newRow['NET_VALUE'] = 0
            newRow['SERVICE_RECORD_ID'] = val.SERVICE_RECORD_ID
            newRow['SERVICE_DESCRIPTION'] = val.SERVICE_DESCRIPTION
            newRow['QUANTITY'] = val.QUANTITY
            newRow['QUOTE_RECORD_ID'] = val.QUOTE_RECORD_ID
            newRow['QUOTE_ID'] = val.QUOTE_ID
            newRow['QTEREV_ID'] = val.QTEREV_ID
            newRow['QTEREV_RECORD_ID'] = val.QTEREV_RECORD_ID
            if val.TAX_PERCENTAGE:
                newRow['TAX_PERCENTAGE'] = val.TAX_PERCENTAGE
            else:
                newRow['TAX_PERCENTAGE'] = 0
            if val.TAX_AMOUNT:
                newRow['TAX_AMOUNT'] = val.TAX_AMOUNT
            else:
                newRow['TAX_AMOUNT'] = 0
            if val.UNIT_PRICE:
                newRow['UNIT_PRICE'] = val.UNIT_PRICE
            else:
                newRow['UNIT_PRICE'] = 0
            if val.UNIT_PRICE_INGL_CURR:
                newRow['UNIT_PRICE_INGL_CURR'] = val.UNIT_PRICE_INGL_CURR
            else:
                newRow['UNIT_PRICE_INGL_CURR'] = 0


        Quoteofferings.Save()
    #insrt_subtotal_offering = ("""INSERT QT__QT_SAQRIS (COMMITTED_VALUE,CONTRACT_VALID_FROM,CONTRACT_VALID_TO,DIVISION_ID,DIVISION_RECORD_ID,DOC_CURRENCY,DOCCURR_RECORD_ID,ESTIMATED_VALUE,GLOBAL_CURRENCY,GLOBAL_CURRENCY_RECORD_ID,LINE,NET_PRICE,NET_PRICE_INGL_CURR,NET_VALUE,NET_VALUE_INGL_CURR,PLANT_ID,PLANT_RECORD_ID,SERVICE_DESCRIPTION,SERVICE_ID,SERVICE_RECORD_ID,QUANTITY,QUOTE_ID,QUOTE_RECORD_ID,QTEREV_ID,QTEREV_RECORD_ID,TAX_PERCENTAGE,TAX_AMOUNT,TAX_AMOUNT_INGL_CURR,UNIT_PRICE,UNIT_PRICE_INGL_CURR,ownerId, cartId) select SAQRIS.COMMITTED_VALUE,SAQRIS.CONTRACT_VALID_FROM,SAQRIS.CONTRACT_VALID_TO,SAQRIS.DIVISION_ID,SAQRIS.DIVISION_RECORD_ID,SAQRIS.DOC_CURRENCY,SAQRIS.DOCCURR_RECORD_ID,SAQRIS.ESTIMATED_VALUE,SAQRIS.GLOBAL_CURRENCY,SAQRIS.GLOBAL_CURRENCY_RECORD_ID,SAQRIS.LINE,SAQRIS.NET_PRICE,SAQRIS.NET_PRICE_INGL_CURR,SAQRIS.NET_VALUE,SAQRIS.NET_VALUE_INGL_CURR,SAQRIS.PLANT_ID,SAQRIS.PLANT_RECORD_ID,SAQRIS.SERVICE_DESCRIPTION,SAQRIS.SERVICE_ID,SAQRIS.SERVICE_RECORD_ID,SAQRIS.QUANTITY,SAQRIS.QUOTE_ID,SAQRIS.QUOTE_RECORD_ID,SAQRIS.QTEREV_ID,SAQRIS.QTEREV_RECORD_ID,SAQRIS.TAX_PERCENTAGE,SAQRIS.TAX_AMOUNT,SAQRIS.TAX_AMOUNT_INGL_CURR,SAQRIS.UNIT_PRICE,SAQRIS.UNIT_PRICE_INGL_CURR,{UserId} as ownerId,{CartId} as cartId from SAQRIS (NOLOCK)  where SAQRIS.QUOTE_RECORD_ID ='{c4c_quote_id}' and  SAQRIS.QTEREV_RECORD_ID= '{rev_rec_id}'""".format(CartId = cartobj.CART_ID,UserId= cartobj.USERID,c4c_quote_id = contract_quote_record_id,rev_rec_id = quote_revision_record_id))
    #Sql.RunQuery(insrt_subtotal_offering)

    get_items_details_obj_insert = Quote.QuoteTables["QT_SAQRIT"]
    get_items_details_obj_insert.Rows.Clear()
    get_items_details_obj = Sql.GetList("""select SAQRIT.LINE,SAQRIT.FABLOCATION_ID,SAQRIT.ASSEMBLY_ID,SAQRIT.GOT_CODE,SAQRIT.KIT_NAME,SAQRIT.OBJECT_ID,SAQRIT.EQUIPMENT_ID,SAQRIT.CONTRACT_VALID_FROM,SAQRIT.MODULE_ID,SAQRIT.MODULE_NAME,SAQRIT.CONTRACT_VALID_TO,SAQRIT.KIT_ID,SAQRIT.POSS_NSO_PART_ID,SAQRIT.MNTEVT_LEVEL,SAQRIT.GREENBOOK,SAQRIT.OFFERING_DESCRIPTION,SAQRIT.SERVICE_DESCRIPTION,SAQRIT.SERVICE_RECORD_ID,SAQRIT.PEREVTCST_INGL_CURR,SAQRIT.SERVICE_ID,SAQRIT.QUOTE_ID,SAQRIT.QUOTE_RECORD_ID,SAQRIT.QTEREV_ID,SAQRIT.QTEREV_RECORD_ID,SAQRIT.PM_ID,SAQRIT.TAX_AMOUNT_INGL_CURR,SAQRIT.PEREVTPRC_INGL_CURR,SAQRIT.ESTVAL_INGL_CURR,SAQRIT.NET_VALUE_INGL_CURR,SAQRIT.NET_VALUE,SAQRIT.ESTIMATED_VALUE,{UserId} as ownerId,{CartId} as cartId from SAQRIT (NOLOCK)  where SAQRIT.QUOTE_RECORD_ID ='{c4c_quote_id}' and  SAQRIT.QTEREV_RECORD_ID= '{rev_rec_id}'""".format(CartId = cartobj.CART_ID,UserId= cartobj.USERID,c4c_quote_id = contract_quote_record_id,rev_rec_id = quote_revision_record_id))
    if get_items_details_obj:
        for val in get_items_details_obj:
            newRow = get_items_details_obj_insert.AddNewRow()
            if val.LINE:
                newRow['LINE'] = val.LINE
            else:
                newRow['LINE'] = ''
            
            newRow['ASSEMBLY_ID'] = val.ASSEMBLY_ID if val.ASSEMBLY_ID else ""
            newRow['GOT_CODE'] = val.GOT_CODE if val.GOT_CODE else ""
            newRow['KIT_NAME'] = val.KIT_NAME if val.KIT_NAME else ""
            newRow['KIT_ID'] = val.KIT_ID if val.KIT_ID else ""
            newRow['MODULE_ID'] = val.MODULE_ID if val.MODULE_ID else ""
            newRow['MODULE_NAME'] = val.MODULE_NAME if val.MODULE_NAME else ""
            newRow['CONTRACT_VALID_FROM'] = val.CONTRACT_VALID_FROM if val.CONTRACT_VALID_FROM else ""
            newRow['CONTRACT_VALID_TO'] = val.CONTRACT_VALID_TO if val.CONTRACT_VALID_TO else ""
            newRow['POSS_NSO_PART_ID'] = val.POSS_NSO_PART_ID if val.POSS_NSO_PART_ID else ""
            newRow['MNTEVT_LEVEL'] = val.MNTEVT_LEVEL if val.MNTEVT_LEVEL else ""
            #newRow['PEREVTCST_INGL_CURR'] = val.PEREVTCST_INGL_CURR if val.PEREVTCST_INGL_CURR else ""
            #newRow['PEREVTPRC_INGL_CURR'] = val.PEREVTPRC_INGL_CURR if val.PEREVTPRC_INGL_CURR else ""
            newRow['EQUIPMENT_ID'] = val.EQUIPMENT_ID if val.EQUIPMENT_ID else ""
            newRow['PM_ID'] = val.PM_ID if val.PM_ID else ""
            if val.FABLOCATION_ID:
                newRow['FABLOCATION_ID'] = val.FABLOCATION_ID
            else:
                val.FABLOCATION_ID =''
            if val.OBJECT_ID:
                newRow['OBJECT_ID'] = val.OBJECT_ID
            else:
                val.OBJECT_ID =''    
                
            if val.TAX_AMOUNT_INGL_CURR:
                newRow['TAX_AMOUNT_INGL_CURR'] = val.TAX_AMOUNT_INGL_CURR
            else:
                val.TAX_AMOUNT_INGL_CURR =''
            if val.GREENBOOK:
                newRow['GREENBOOK'] = val.GREENBOOK
            else:
                val.GREENBOOK =''
            if val.OFFERING_DESCRIPTION:
                newRow['SERVICE_DESCRIPTION'] = val.OFFERING_DESCRIPTION
            else:
                newRow['SERVICE_DESCRIPTION'] =val.SERVICE_DESCRIPTION
            
            if val.SERVICE_ID:
                newRow['SERVICE_ID'] = val.SERVICE_ID
            else:
                val.SERVICE_ID ='' 
            if val.SERVICE_RECORD_ID:
                newRow['SERVICE_RECORD_ID'] = val.SERVICE_RECORD_ID
            else:
                val.SERVICE_RECORD_ID ='' 
            if val.ESTIMATED_VALUE:
                newRow['ESTVAL_INGL_CURR'] = val.ESTIMATED_VALUE
            else:
                val.ESTIMATED_VALUE ='' 
            if val.NET_VALUE:
                newRow['NET_PRICE_INGL_CURR'] = val.NET_VALUE
            else:
                val.NET_PRICE_INGL_CURR =''
        
            
            newRow['QUOTE_RECORD_ID'] = val.QUOTE_RECORD_ID
            newRow['QUOTE_ID'] = val.QUOTE_ID
            newRow['QUOTE_ID'] = val.QUOTE_ID
            
            
        get_items_details_obj_insert.Save()
    #insrt_item_details = ("""INSERT QT__QT_SAQRIT (LINE,FABLOCATION_ID,OBJECT_ID,EQUIPMENT_ID,GREENBOOK,SERVICE_DESCRIPTION,SERVICE_RECORD_ID,SERVICE_ID,QUOTE_ID,QUOTE_RECORD_ID,QTEREV_ID,QTEREV_RECORD_ID,ESTVAL_INGL_CURR,NET_PRICE_INGL_CURR,ownerId, cartId) select SAQRIT.LINE,SAQRIT.FABLOCATION_ID,SAQRIT.OBJECT_ID,SAQRIT.OBJECT_ID as EQUIPMENT_ID,SAQRIT.GREENBOOK,SAQRIT.SERVICE_DESCRIPTION,SAQRIT.SERVICE_RECORD_ID,SAQRIT.SERVICE_ID,SAQRIT.QUOTE_ID,SAQRIT.QUOTE_RECORD_ID,SAQRIT.QTEREV_ID,SAQRIT.QTEREV_RECORD_ID,SAQRIT.ESTVAL_INGL_CURR,SAQRIT.NET_VALUE_INGL_CURR,{UserId} as ownerId,{CartId} as cartId from SAQRIT (NOLOCK)  where SAQRIT.QUOTE_RECORD_ID ='{c4c_quote_id}' and  SAQRIT.QTEREV_RECORD_ID= '{rev_rec_id}'""".format(CartId = cartobj.CART_ID,UserId= cartobj.USERID,c4c_quote_id = contract_quote_record_id,rev_rec_id = quote_revision_record_id))
    #Sql.RunQuery(insrt_item_details)
    get_sold_to_details = Sql.GetFirst("SELECT PARTY_NAME,ADDRESS,EMAIL,PHONE from SAQTIP where QUOTE_RECORD_ID = '{contract_quote_record_id}' and QTEREV_RECORD_ID ='{quote_revision_record_id}'  and CPQ_PARTNER_FUNCTION='SOLD TO'".format(contract_quote_record_id=contract_quote_record_id,quote_revision_record_id=quote_revision_record_id))
    if get_sold_to_details:
        if str(get_sold_to_details.PARTY_NAME):
            Quote.GetCustomField('QD_SOLD_PARTY_NAME').Content = str(get_sold_to_details.PARTY_NAME).title()
        if str(get_sold_to_details.ADDRESS):
            Quote.GetCustomField('QD_SOLD_ADDRESS').Content = str(get_sold_to_details.ADDRESS)
        if str(get_sold_to_details.EMAIL):
            Quote.GetCustomField('QD_SOLD_PARTY_NAME').Content = str(get_sold_to_details.EMAIL).title()
        if str(get_sold_to_details.PHONE):
            Quote.GetCustomField('QD_SOLD_PHONE').Content = str(get_sold_to_details.PHONE)
    get_ship_to_details = Sql.GetFirst("SELECT PARTY_NAME,ADDRESS,EMAIL,PHONE from SAQTIP where QUOTE_RECORD_ID = '{contract_quote_record_id}' and QTEREV_RECORD_ID ='{quote_revision_record_id}'  and CPQ_PARTNER_FUNCTION='SHIP TO'".format(contract_quote_record_id=contract_quote_record_id,quote_revision_record_id=quote_revision_record_id))
    if get_ship_to_details:
        if str(get_ship_to_details.PARTY_NAME):
            Quote.GetCustomField('QD_SHIP_PARTY_NAME').Content = str(get_ship_to_details.PARTY_NAME).title()
        if str(get_ship_to_details.ADDRESS):
            Quote.GetCustomField('QD_SHIP_ADDRESS').Content = str(get_ship_to_details.ADDRESS)
        if str(get_ship_to_details.EMAIL):
            Quote.GetCustomField('QD_SHIP_PARTY_NAME').Content = str(get_ship_to_details.EMAIL).title()
        if str(get_ship_to_details.PHONE):
            Quote.GetCustomField('QD_SHIP_PHONE').Content = str(get_ship_to_details.PHONE)
    get_bill_to_details = Sql.GetFirst("SELECT PARTY_NAME,ADDRESS,EMAIL,PHONE from SAQTIP where QUOTE_RECORD_ID = '{contract_quote_record_id}' and QTEREV_RECORD_ID ='{quote_revision_record_id}'  and CPQ_PARTNER_FUNCTION='BILL TO'".format(contract_quote_record_id=contract_quote_record_id,quote_revision_record_id=quote_revision_record_id))
    if get_bill_to_details:
        if str(get_bill_to_details.PARTY_NAME):
            Quote.GetCustomField('QD_BILL_PARTY_NAME').Content = str(get_bill_to_details.PARTY_NAME).title()
        if str(get_bill_to_details.ADDRESS):
            Quote.GetCustomField('QD_BILL_ADDRESS').Content = str(get_bill_to_details.ADDRESS)
        if str(get_bill_to_details.EMAIL):
            Quote.GetCustomField('QD_BILL_PARTY_NAME').Content = str(get_bill_to_details.EMAIL).title()
        if str(get_bill_to_details.PHONE):
            Quote.GetCustomField('QD_BILL_PHONE').Content = str(get_bill_to_details.PHONE)
    get_pay_to_details = Sql.GetFirst("SELECT PARTY_NAME,ADDRESS,EMAIL,PHONE from SAQTIP where QUOTE_RECORD_ID = '{contract_quote_record_id}' and QTEREV_RECORD_ID ='{quote_revision_record_id}'  and CPQ_PARTNER_FUNCTION='PAYER'".format(contract_quote_record_id=contract_quote_record_id,quote_revision_record_id=quote_revision_record_id))
    if get_pay_to_details:
        if str(get_pay_to_details.PARTY_NAME):
            Quote.GetCustomField('QD_PAY_PARTY_NAME').Content = str(get_pay_to_details.PARTY_NAME).title()
        if str(get_pay_to_details.ADDRESS):
            Quote.GetCustomField('QD_PAY_ADDRESS').Content = str(get_pay_to_details.ADDRESS)
        if str(get_pay_to_details.EMAIL):
            Quote.GetCustomField('QD_PAY_PARTY_NAME').Content = str(get_pay_to_details.EMAIL).title()
        if str(get_pay_to_details.PHONE):
            Quote.GetCustomField('QD_PAY_PHONE').Content = str(get_pay_to_details.PHONE)

    get_revision_details = Sql.GetFirst("SELECT REVISION_DESCRIPTION,REV_EXPIRE_DATE,SALESORG_ID,EXCHANGE_RATE,CONTRACT_VALID_FROM,CONTRACT_VALID_TO,CUSTOMER_NOTES,PAYMENTTERM_NAME,QT_PAYMENTTERM_NAME,GLOBAL_CURRENCY from SAQTRV where QUOTE_RECORD_ID = '{QuoteRecordId}' and QTEREV_RECORD_ID = '{RevisionRecordId}' ".format(QuoteRecordId=contract_quote_record_id,RevisionRecordId = quote_revision_record_id))
    Quote.GetCustomField('Currency').Content = str(get_revision_details.GLOBAL_CURRENCY)
    if get_revision_details:
        Quote.SetGlobal('REV_DESC', str(get_revision_details.REVISION_DESCRIPTION)) 
        Quote.SetGlobal('REV_EXPIRE', str(get_revision_details.REV_EXPIRE_DATE).split()[0])
        if str(get_revision_details.SALESORG_ID) == "2000":
            Quote.SetGlobal('EXC_RATE', 'NA')
        else:
            Quote.SetGlobal('EXC_RATE', str(get_revision_details.EXCHANGE_RATE))
        Quote.SetGlobal('QT_CVF', str(get_revision_details.CONTRACT_VALID_FROM).split()[0])
        Quote.SetGlobal('QT_CVT', str(get_revision_details.CONTRACT_VALID_TO).split()[0])
        if str(get_revision_details.CUSTOMER_NOTES):
            Quote.SetGlobal('QT_CN', str(get_revision_details.CUSTOMER_NOTES))
            Quote.GetCustomField('customer_notes').Content = str(get_revision_details.CUSTOMER_NOTES)
        #Q-INC09009958-M starts.
        if str(get_revision_details.QT_PAYMENTTERM_NAME):
            Quote.SetGlobal('QT_PAYMENT_TERM', str(get_revision_details.QT_PAYMENTTERM_NAME))
        #Q-INC09009958-M ends.
    #set  total net price, total net value start
    total_net_price = total_net_value = total_tax_amt = 0.00
    
    
    quote_subtotalofferings = Quote.QuoteTables["QT_SAQRIS"]

    '''for i in quote_subtotalofferings.Rows:
        Trace.Write('QT_SAQRIS---'+str(i['NET_PRICE']))
        #exts_price += float(i['EXTENDED_PRICE'])
        total_net_price += float(i['NET_PRICE'])
        total_net_value += float(i['NET_VALUE'])
        total_tax_amt += float(i['TAX_AMOUNT'])
        Trace.Write('QT_SAQRIS---total_net_price----'+str(total_net_price))
        Trace.Write('QT_SAQRIS---total_net_value----'+str(total_net_value))
        Quote.SetGlobal('NP', str(total_net_price))
        Quote.SetGlobal('NEV', str(total_net_value))
        Quote.SetGlobal('TX', str(total_tax_amt))'''
    #QC 213,452 start
    get_quotetotal = Sql.GetFirst("SELECT SALESORG_ID,BANK_NAME,INCOTERM_NAME,NET_VALUE_INGL_CURR as netprice,DOC_CURRENCY,ESTVAL_INGL_CURR as est_val,TAX_AMOUNT_INGL_CURR as taxtotal,TOTAL_AMOUNT_INGL_CURR as totamt from SAQTRV where QUOTE_RECORD_ID = '{contract_quote_record_id}' and QTEREV_RECORD_ID ='{quote_revision_record_id}' ".format(contract_quote_record_id=contract_quote_record_id,quote_revision_record_id=quote_revision_record_id))
    
    get_total_doc_val = Sql.GetFirst("SELECT SUM(ESTIMATED_VALUE) as est_vals,SUM(NET_VALUE) as net_val,SUM(TOTAL_AMOUNT) as tot_quote,SUM(TAX_AMOUNT) as tax_amt, SUM(TOTAL_AMOUNT_INGL_CURR) as tot_amt_ingl_curr, SUM(TAX_AMOUNT_INGL_CURR) as tax_amt_ingl_curr from SAQRIT where QUOTE_RECORD_ID = '{contract_quote_record_id}' and QTEREV_RECORD_ID ='{quote_revision_record_id}' ".format(contract_quote_record_id=contract_quote_record_id,quote_revision_record_id=quote_revision_record_id))
    
    Quote.GetCustomField('QT_DOC_CURRENCY').Content = str(get_quotetotal.DOC_CURRENCY)
    get_address_details = Sql.GetFirst("SELECT ADDRESS1,ADDRESS2,CITY,COMPANY_CODE,DESCRIPTION,COUNTRY,FAX,PHONE,POSTALCODE,STATE,REGION,COMPANY_NAME from SASORG where SALESORG_ID = '"+str(get_quotetotal.SALESORG_ID)+"'")
    if get_address_details:
        if get_address_details.ADDRESS1:
            Quote.GetCustomField('QT_ADDRESS_ONE').Content = str(get_address_details.ADDRESS1).title()
        else:
            Quote.GetCustomField('QT_ADDRESS_ONE').Content = ''
        if get_address_details.ADDRESS2:
            Quote.GetCustomField('QT_ADDRESS_TWO').Content =  str(get_address_details.ADDRESS2).title()
        else:
            Quote.GetCustomField('QT_ADDRESS_TWO').Content = ''
        if get_address_details.CITY:
            Quote.GetCustomField('QT_SA_CITY').Content =  str(get_address_details.CITY).title()
        else:
            Quote.GetCustomField('QT_SA_CITY').Content = ''
        if get_address_details.COMPANY_CODE:
            Quote.GetCustomField('QT_SA_COMCODE').Content =  str(get_address_details.COMPANY_CODE).title()
        else:
            Quote.GetCustomField('QT_SA_COMCODE').Content = ''
        if get_address_details.COUNTRY:
            Quote.GetCustomField('QT_SA_CTY').Content = str(get_address_details.COUNTRY).title()
        else:
            Quote.GetCustomField('QT_SA_CTY').Content = ''
        if get_address_details.FAX:
            Quote.GetCustomField('QT_SA_FAX').Content = str(get_address_details.FAX).title()
        else:
            Quote.GetCustomField('QT_SA_FAX').Content = ''
        if get_address_details.PHONE:
            Quote.GetCustomField('QT_SA_PHONE').Content =  str(get_address_details.PHONE)
        else:
            Quote.GetCustomField('QT_SA_PHONE').Content = ''
        if get_address_details.POSTALCODE:
            Quote.GetCustomField('QT_SA_POSTCODE').Content =  str(get_address_details.POSTALCODE)
        else:
            Quote.GetCustomField('QT_SA_POSTCODE').Content = ''
        if get_address_details.STATE:
            Quote.GetCustomField('QT_SA_STATE').Content =  str(get_address_details.STATE)
        else:
            Quote.GetCustomField('QT_SA_STATE').Content = ''
        if get_address_details.REGION:
            Quote.GetCustomField('QT_SA_REGION').Content =  str(get_address_details.REGION).title()
        else:
            Quote.GetCustomField('QT_SA_REGION').Content =''
        if get_address_details.DESCRIPTION:
            Quote.GetCustomField('QT_SA_COMPANY_NAME').Content =  str(get_address_details.DESCRIPTION).title()
        else:
            Quote.GetCustomField('QT_SA_COMPANY_NAME').Content = ''
    if get_quotetotal:
        if get_quotetotal.BANK_NAME:
            Quote.GetCustomField('QT_SA_BANK_NAME').Content = str(get_quotetotal.BANK_NAME).title()
            #Quote.SetGlobal('QT_SA_BANK_NAME', str(get_quotetotal.BANK_NAME))
        else:
            Quote.GetCustomField('QT_SA_BANK_NAME').Content= ''
        if get_quotetotal.INCOTERM_NAME:
            Quote.GetCustomField('QT_SA_INC_NAME').Content = str(get_quotetotal.INCOTERM_NAME)
            #Quote.SetGlobal('QT_SA_INC_NAME', str(get_quotetotal.INCOTERM_NAME))
        else:
            Quote.GetCustomField('QT_SA_INC_NAME').Content= ''
            #Quote.SetGlobal('QT_SA_INC_NAME', '')
        #INC08887223 - M - Start

        #INC08944133 Start - M
        if str(get_total_doc_val.net_val):
            Quote.GetCustomField('doc_net_price').Content = "{0:,.2f}".format(float(get_total_doc_val.net_val))
        else:
            Quote.GetCustomField('doc_net_price').Content = ''

        if str(get_total_doc_val.est_vals):    
            Quote.GetCustomField('tot_est').Content = "{0:,.2f}".format(float(get_total_doc_val.est_vals))
        else:
            Quote.GetCustomField('tot_est').Content = ''
        #INC08944133 End - M

        #INC08641716 m
        if str(get_total_doc_val.tax_amt):
            Quote.GetCustomField('taxtotal').Content = "{0:,.2f}".format(float(get_total_doc_val.tax_amt))
        else:
            Quote.GetCustomField('taxtotal').Content = "{0:,.2f}".format(float(get_total_doc_val.tax_amt_ingl_curr))
        #INC08641716 m
            
        if str(get_total_doc_val.tot_quote):
            Quote.GetCustomField('TL_NET_VALUE').Content = "{0:,.2f}".format(float(get_total_doc_val.tot_quote))
        else:
            Quote.GetCustomField('TL_NET_VALUE').Content = "{0:,.2f}".format(float(get_total_doc_val.tot_amt_ingl_curr))
        #INC08887223 - M - End
            
    get_customer_details = Sql.GetFirst("SELECT CONTACT_NAME,EMAIL from SAQICT where QUOTE_RECORD_ID = '{contract_quote_record_id}' and QTEREV_RECORD_ID ='{quote_revision_record_id}' ".format(contract_quote_record_id=contract_quote_record_id,quote_revision_record_id=quote_revision_record_id))
    if get_customer_details:
        if get_customer_details.CONTACT_NAME:
            Quote.GetCustomField('QT_CT_NAME').Content = get_customer_details.CONTACT_NAME.title()
            #Quote.SetGlobal('QT_CT_NAME', str(get_customer_details.CONTACT_NAME))
        else:
            Quote.GetCustomField('QT_CT_NAME').Content = ''
        if get_customer_details.EMAIL:
            Quote.GetCustomField('QT_CT_EMAIL').Content = str(get_customer_details.EMAIL).title()
        else:
            Quote.GetCustomField('QT_CT_EMAIL').Content = ''
    else:
        Quote.SetGlobal('QT_CT_NAME', '')
        Quote.SetGlobal('QT_CT_EMAIL', '')
    #QC 213 end
    return True
#Document XML end


#generate documnet start

get_quote_details = Sql.GetFirst("SELECT QUOTE_ID,QTEREV_ID,QUOTE_NAME,C4C_QUOTE_ID, QUOTE_TYPE FROM SAQTMT(NOLOCK) WHERE MASTER_TABLE_QUOTE_RECORD_ID =  '"+str(contract_quote_record_id)+"' AND QTEREV_RECORD_ID = '"+str(quote_revision_record_id) + "'")
Quote.SetGlobal("qt_rev_id",str(get_quote_details.QTEREV_ID))
def insert_bill_doc(parts_list,billing_matrix):
    insert_quote_billing_plan()
    _insert_subtotal_by_offerring_quote_table()
    
    Trace.Write('500----')
    
    #Quote = QuoteHelper.Edit(c4c_quote_id)
    #time.sleep( 5 )
    Quote.RefreshActions()
    #A055S000P01-8729 start
    get_quote_info_details = Sql.GetFirst("select * from SAQTMT where QUOTE_ID = '"+str(Quote.CompositeNumber)+"'")
    Quote.SetGlobal("contract_quote_record_id",get_quote_info_details.MASTER_TABLE_QUOTE_RECORD_ID)
    Quote.SetGlobal("quote_revision_record_id",str(get_quote_info_details.QTEREV_RECORD_ID))
    get_quote_details = Sql.GetFirst("SELECT QUOTE_ID,QTEREV_ID,QUOTE_NAME,C4C_QUOTE_ID, QUOTE_TYPE FROM SAQTMT(NOLOCK) WHERE MASTER_TABLE_QUOTE_RECORD_ID =  '"+str(get_quote_info_details.MASTER_TABLE_QUOTE_RECORD_ID)+"' AND QTEREV_RECORD_ID = '"+str(get_quote_info_details.QTEREV_RECORD_ID) + "'")
    #A055S000P01-17165 start
    update_workflow_status = "UPDATE SAQTRV SET REVISION_STATUS = 'OPD-PREPARING QUOTE DOCUMENTS',WORKFLOW_STATUS = 'QUOTE DOCUMENTS' WHERE QUOTE_RECORD_ID = '{QuoteRecordId}' and QTEREV_RECORD_ID = '{RevisionRecordId}' ".format(QuoteRecordId=contract_quote_record_id,RevisionRecordId = quote_revision_record_id)			
                
    Sql.RunQuery(update_workflow_status)
    #A055S000P01-20944 - Start - A
    CQREVSTSCH.Revisionstatusdatecapture(contract_quote_record_id,quote_revision_record_id)
    #A055S000P01-20944 - End - A
    #INC08887223 - M - Start
    #Hadoop Fix - M - Start
    quote_name = re.sub("[\n\.><&_-~,?'^]","",get_quote_details.QUOTE_NAME)
    Sql.RunQuery("update SAQTMT set QUOTE_NAME = '{quote_name}' WHERE MASTER_TABLE_QUOTE_RECORD_ID = '{QuoteRecordId}' and QTEREV_RECORD_ID = '{RevisionRecordId}' ".format(quote_name=quote_name,QuoteRecordId=contract_quote_record_id,RevisionRecordId = quote_revision_record_id))
    #A055S000P01-17165 end
   
    saqdoc_output_insert="""INSERT SAQDOC (
                            QUOTE_DOCUMENT_RECORD_ID,
                            DOCUMENT_ID,
                            DOCUMENT_NAME,
                            DOCUMENT_PATH,
                            QUOTE_ID,
                            QUOTE_NAME,
                            QUOTE_RECORD_ID,
                            LANGUAGE_ID,
                            LANGUAGE_NAME,
                            LANGUAGE_RECORD_ID,
                            CPQTABLEENTRYADDEDBY,
                            CPQTABLEENTRYDATEADDED,
                            CpqTableEntryModifiedBy,
                            CpqTableEntryDateModified,
                            STATUS,
                            QTEREV_ID,
                            QTEREV_RECORD_ID,
                            BILLING_INCLUDED,
                            ITEM_INCLUDED,
                            PRTLST_INCLUDED
                            )SELECT
                            CONVERT(VARCHAR(4000),NEWID()) as QUOTE_DOCUMENT_RECORD_ID,
                            '{doc_id}' AS DOCUMENT_ID,
                            '{doc_name}' AS DOCUMENT_NAME,
                            '' AS DOCUMENT_PATH,
                            '{quoteid}' AS QUOTE_ID,
                            '{quotename}' AS QUOTE_NAME,
                            '{quoterecid}' AS QUOTE_RECORD_ID,
                            'EN' AS LANGUAGE_ID,
                            'English' AS LANGUAGE_NAME,
                            MALANG.LANGUAGE_RECORD_ID AS LANGUAGE_RECORD_ID,
                            '{UserName}' as CPQTABLEENTRYADDEDBY,
                            '{dateadded}' as CPQTABLEENTRYDATEADDED,
                            '{UserId}' as CpqTableEntryModifiedBy,
                            '{date}' as CpqTableEntryDateModified,
                            'PENDING' as STATUS,
                            '{qt_revid}' as QTEREV_ID,
                            '{qt_rev_rec_id}' as QTEREV_RECORD_ID,
                            1,
                            1,
                            1
                            FROM MALANG (NOLOCK) WHERE MALANG.LANGUAGE_NAME = 'English'""".format(doc_id='Pending',doc_name='',quoteid=get_quote_details.QUOTE_ID,quotename=quote_name,quoterecid=contract_quote_record_id,qt_revid= get_quote_details.QTEREV_ID,qt_rev_rec_id = quote_revision_record_id,UserName=UserName,dateadded=datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S %p"),UserId=UserId,date=datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S %p"))
            #Log.Info(qtqdoc)
    Sql.RunQuery(saqdoc_output_insert)
    #Hadoop Fix - M - End
    #INC08887223 - M - END
    gen_doc = Quote.GenerateDocument('AMAT Total Quote', GenDocFormat.PDF)
    fileName = Quote.GetLatestGeneratedDocumentFileName()
    GDB = Quote.GetLatestGeneratedDocumentInBytes()
    List = Quote.GetGeneratedDocumentList('AMAT Total Quote')
    for doc in List:
        doc_id = doc.Id
        doc_name = doc.FileName
        if fileName==doc_name:
            quote_id = get_quote_details.QUOTE_ID
            #added_by = audit_fields.USERNAME
            #modified_by = audit_fields.CpqTableEntryModifiedBy
            #modified_date = audit_fields.CpqTableEntryDateModified
            guid = str(Guid.NewGuid()).upper()
            qt_rec_id = contract_quote_record_id
            date_added = doc.DateCreated
            update_query = """UPDATE SAQDOC SET DOCUMENT_ID = '{docid}', DOCUMENT_NAME = '{docname}', STATUS = 'ACQUIRED' WHERE DOCUMENT_ID = 'Pending' AND SAQDOC.LANGUAGE_ID = 'EN' AND STATUS = 'PENDING' AND QUOTE_RECORD_ID = '{recid}' AND QTEREV_RECORD_ID = '{quote_revision_record_id}'""".format(recid=contract_quote_record_id,docid=doc_id,docname=doc_name,quote_revision_record_id=quote_revision_record_id)
            Sql.RunQuery(update_query)
    return True
def insert_spare_doc(parts_list):
    if Quote.GetCustomField('INCLUDE_ITEMS').Content == 'YES':
        #Trace.Write('285----')
        _insert_subtotal_by_offerring_quote_table()
        #insert_quote_billing_plan()
    elif Quote.GetCustomField('INCLUDE_ITEMS').Content == 'YES':
        _insert_subtotal_by_offerring_quote_table()
    elif Quote.GetCustomField('Billing_Matrix').Content == 'YES':
        #Trace.Write('285----')
        insert_quote_billing_plan()
    if str(parts_list) == 'True':
        #Trace.Write('93------')
        Log.Info('SAQDOC---documents-')
        #A055S000P01-17165 start
        update_workflow_status = "UPDATE SAQTRV SET REVISION_STATUS = 'OPD-PREPARING QUOTE DOCUMENTS',WORKFLOW_STATUS = 'QUOTE DOCUMENTS' WHERE QUOTE_RECORD_ID = '{QuoteRecordId}' and QTEREV_RECORD_ID = '{RevisionRecordId}' ".format(QuoteRecordId=contract_quote_record_id,RevisionRecordId = quote_revision_record_id)			
                    
        Sql.RunQuery(update_workflow_status)
        #A055S000P01-20944 - Start - A
        CQREVSTSCH.Revisionstatusdatecapture(contract_quote_record_id,quote_revision_record_id)
        #A055S000P01-20944 - End - A
        #Hadoop Fix - M - Start
        quote_name = re.sub("[\n\.><&_-~,?'^]","",get_quote_details.QUOTE_NAME)
        Sql.RunQuery("update SAQTMT set QUOTE_NAME = '{quote_name}' WHERE MASTER_TABLE_QUOTE_RECORD_ID = '{QuoteRecordId}' and QTEREV_RECORD_ID = '{RevisionRecordId}' ".format(quote_name=quote_name,QuoteRecordId=contract_quote_record_id,RevisionRecordId = quote_revision_record_id))
        #A055S000P01-17165 end
        saqdoc_output_insert="""INSERT SAQDOC (
                            QUOTE_DOCUMENT_RECORD_ID,
                            DOCUMENT_ID,
                            DOCUMENT_NAME,
                            DOCUMENT_PATH,
                            QUOTE_ID,
                            QUOTE_NAME,
                            QUOTE_RECORD_ID,
                            LANGUAGE_ID,
                            LANGUAGE_NAME,
                            LANGUAGE_RECORD_ID,
                            CPQTABLEENTRYADDEDBY,
                            CPQTABLEENTRYDATEADDED,
                            CpqTableEntryModifiedBy,
                            CpqTableEntryDateModified,
                            STATUS,
                            QTEREV_ID,
                            QTEREV_RECORD_ID,
                            ITEM_INCLUDED,
                            PRTLST_INCLUDED
                            )SELECT
                            CONVERT(VARCHAR(4000),NEWID()) as QUOTE_DOCUMENT_RECORD_ID,
                            '{doc_id}' AS DOCUMENT_ID,
                            '{doc_name}' AS DOCUMENT_NAME,
                            '' AS DOCUMENT_PATH,
                            '{quoteid}' AS QUOTE_ID,
                            '{quotename}' AS QUOTE_NAME,
                            '{quoterecid}' AS QUOTE_RECORD_ID,
                            'EN' AS LANGUAGE_ID,
                            'English' AS LANGUAGE_NAME,
                            MALANG.LANGUAGE_RECORD_ID AS LANGUAGE_RECORD_ID,
                            '{UserName}' as CPQTABLEENTRYADDEDBY,
                            '{dateadded}' as CPQTABLEENTRYDATEADDED,
                            '{UserId}' as CpqTableEntryModifiedBy,
                            '{date}' as CpqTableEntryDateModified,
                            'PENDING' as STATUS,
                            '{qt_revid}' as QTEREV_ID,
                            '{qt_rev_rec_id}' as QTEREV_RECORD_ID,
                            1,1
                            FROM MALANG (NOLOCK) WHERE MALANG.LANGUAGE_NAME = 'English'""".format(doc_id='Pending',doc_name='',quoteid=get_quote_details.QUOTE_ID,quotename=quote_name,quoterecid=contract_quote_record_id,qt_revid= get_quote_details.QTEREV_ID,qt_rev_rec_id = quote_revision_record_id,UserName=UserName,dateadded=datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S %p"),UserId=UserId,date=datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S %p"))
            #Log.Info(qtqdoc)
        Sql.RunQuery(saqdoc_output_insert)
        #Hadoop Fix - M - END
        
        gen_doc = Quote.GenerateDocument('AMAT_SUBTOTAL_OFFERING', GenDocFormat.PDF)
        fileName = Quote.GetLatestGeneratedDocumentFileName()
        GDB = Quote.GetLatestGeneratedDocumentInBytes()
        List = Quote.GetGeneratedDocumentList('AMAT_SUBTOTAL_OFFERING')
        for doc in List:
            doc_id = doc.Id
            doc_name = doc.FileName
            if fileName==doc_name:
                quote_id = gettoolquote.QUOTE_ID
                #added_by = audit_fields.USERNAME
                #modified_by = audit_fields.CpqTableEntryModifiedBy
                #modified_date = audit_fields.CpqTableEntryDateModified
                guid = str(Guid.NewGuid()).upper()
                qt_rec_id = contract_quote_record_id
                date_added = doc.DateCreated
                update_query = """UPDATE SAQDOC SET DOCUMENT_ID = '{docid}', DOCUMENT_NAME = '{docname}', STATUS = 'ACQUIRED' WHERE DOCUMENT_ID = 'Pending' AND SAQDOC.LANGUAGE_ID = 'EN' AND STATUS = 'PENDING' AND QUOTE_RECORD_ID = '{recid}' AND QTEREV_RECORD_ID = '{quote_revision_record_id}'""".format(recid=contract_quote_record_id,docid=doc_id,docname=doc_name,quote_revision_record_id=quote_revision_record_id)
                Sql.RunQuery(update_query)
    return True


def language_select():
    Trace.Write("Inside language select")
    sec_str =  get_fpm_service = ''
    get_quote_status = Sql.GetFirst("SELECT REVISION_STATUS,DOC_CURRENCY FROM SAQTRV WHERE QUOTE_RECORD_ID = '{}' AND QTEREV_RECORD_ID = '{}'".format(contract_quote_record_id,quote_revision_record_id))
    get_service_details = Sql.GetFirst("SELECT SERVICE_ID FROM SAQTSV(NOLOCK) WHERE QUOTE_RECORD_ID =  '"+str(contract_quote_record_id)+"' AND QTEREV_RECORD_ID = '"+str(quote_revision_record_id) + "'")
    if get_service_details:
        get_fpm_service_val = get_service_details.SERVICE_ID
        if get_fpm_service_val == "Z0108":
            get_fpm_service = "Z0108"
        elif get_fpm_service_val == "Z0110":
            get_fpm_service = "Z0110"
        else:
            get_fpm_service = ''
    else:
        get_fpm_service = ''
    if get_quote_status:
        if str(get_quote_status.REVISION_STATUS).upper() in ("APR-APPROVED","OPD-PREPARING QUOTE DOCUMENTS"):
            Trace.Write("If")
            sec_str += ('<div id="container">')
            sec_str += (
                    '<div class="dyn_main_head master_manufac glyphicon pointer   glyphicon-chevron-down" onclick="dyn_main_sec_collapse_arrow(this)" data-target=".sec_" data-toggle="collapse"><label class="onlytext"><label class="onlytext"><div>GENERAL SETTINGS</div></label></div>')

        
            sec_str += ('<div id="sec_LANG" class= sec_LANG>')
            #dropdown
            sec_str += (
            '<div style="height: 30px; border-left: 0px; border-right: 0px; border-bottom: 1px solid rgb(204, 204, 204); padding-bottom: 10px;" data-bind="attr: {"id":"drop_cont"+stdAttrCode(),"class": isWholeRow() ? "g4 except_sec dropDownHeight iconhvr" : "g1 except_sec dropDownHeight iconhvr" }" id="drop_cont11744" class="g4 except_sec dropDownHeight iconhvr">')
            sec_str += (
            '<div class="col-md-5">	<abbr data-bind="attr:{"title":label}" title="doc_lang"><label class="col-md-11" data-bind="html: label" style="padding: 5px 5px;margin: 0;" title="doc_lang">Document Language</label></abbr><a href="#" class="col-md-1" style="text-align:right;padding: 7px 5px;color:green">	<i class="fa fa-info-circle autoClosePopover" data-bind="popover: { templateId: "HintTemplate", container: "body", placement: "top", autoClose: true, html: true}" data-original-title="doc_lang" title=""></i></a></div><!--ko if: $data.template() === "DropDownTemplate" && $data.name().toString().indexOf("") === -1 && $data.name().toString().indexOf("") === -1 && $data.name().toString().indexOf("") === -1--><div class="col-md-3 pad-0"><select class="form-control light_yellow" id="Lang"><option value="Select">Select</option><option value="English">English</option><option value="Chinese">Chinese</option></select></div><!-- /ko --><!-- ko if: $data.name().toString().indexOf("") !== -1 || $data.name().toString().indexOf("") !== -1 || $data.name().toString().indexOf("") !== -1--><!-- /ko --><div class="col-md-3 " style="display:none;"> <span class="" data-bind="attr:{"id": $data.name()}" id=""></span></div><div class="col-md-1" style="float: right;"><div class="col-md-12 editiconright"><a href="#" onclick="editclick_row(this)" class="editclick">	<i class="fa fa-pencil" aria-hidden="true"></i></a></div></div><div class="col-md-3 pad-0 mrg-bt-5"></div></div>')


            #dropdown
            sec_str += (
            '<div style="height: 30px; border-left: 0px; border-right: 0px; border-bottom: 1px solid rgb(204, 204, 204); padding-bottom: 10px;" data-bind="attr: {"id":"drop_cont"+stdAttrCode(),"class": isWholeRow() ? "g4 except_sec dropDownHeight iconhvr" : "g1 except_sec dropDownHeight iconhvr" }" id="drop_cont11744" class="g4 except_sec dropDownHeight iconhvr">')
            sec_str += (
            '<div class="col-md-5">	<abbr data-bind="attr:{"title":label}" title="doc_Cur"><label class="col-md-11" data-bind="html: label" style="padding: 5px 5px;margin: 0;" title="doc_lang">Document  Currency</label></abbr><a href="#" class="col-md-1" style="text-align:right;padding: 7px 5px;color:green">	<i class="fa fa-info-circle autoClosePopover" data-bind="popover: { templateId: "HintTemplate", container: "body", placement: "top", autoClose: true, html: true}" data-original-title="doc_lang" title=""></i></a></div><!--ko if: $data.template() === "DropDownTemplate" && $data.name().toString().indexOf("") === -1 && $data.name().toString().indexOf("") === -1 && $data.name().toString().indexOf("") === -1--><div class="col-md-3 pad-0"><select class="form-control light_yellow" id="Lang" ><option value="Select">Select</option><option value="'+str(get_quote_status.DOC_CURRENCY)+'">'+str(get_quote_status.DOC_CURRENCY)+'</option></select></div><!-- /ko --><!-- ko if: $data.name().toString().indexOf("") !== -1 || $data.name().toString().indexOf("") !== -1 || $data.name().toString().indexOf("") !== -1--><!-- /ko --><div class="col-md-3 " style="display:none;"> <span class="" data-bind="attr:{"id": $data.name()}" id=""></span></div><div class="col-md-1" style="float: right;"><div class="col-md-12 editiconright"><a href="#" onclick="editclick_row(this)" class="editclick">	<i class="fa fa-pencil" aria-hidden="true"></i></a></div></div><div class="col-md-3 pad-0 mrg-bt-5"></div></div>')
        
            #Checkbox 1
            sec_str += (
            '<div style="height: 30px; border-left: 0px; border-right: 0px; border-bottom: 1px solid rgb(204, 204, 204); padding-bottom: 10px;" data-bind="attr: {"id":"drop_cont"+stdAttrCode(),"class": isWholeRow() ? "g4 except_sec dropDownHeight iconhvr" : "g1 except_sec dropDownHeight iconhvr" }" id="drop_cont11744" class="g4 except_sec dropDownHeight iconhvr">')
            sec_str += ('<div class="col-md-5">	<abbr data-bind="attr:{"title":label}" title="doc_lang"><label class="col-md-11" data-bind="html: label" style="padding: 5px 5px;margin: 0;" title="doc_lang">Include Expected Date of Fx Rate</label></abbr><a href="#" class="col-md-1" style="text-align:right;padding: 7px 5px;color:green">	<i class="fa fa-info-circle autoClosePopover" data-bind="popover: { templateId: "HintTemplate", container: "body", placement: "top", autoClose: true, html: true}" data-original-title="doc_lang" title=""></i></a></div><div class="col-md-3 pad-0 padt_7"><input id="include_expected_date" class="custom custom_gen_doc" type="checkbox" ><span class="lbl"></span></div><!-- /ko --><div class="col-md-3 " style="display:none;"> <span class="" data-bind="attr:{"id": $data.name()}" id=""></span></div><div class="col-md-1" style="float: right;"><div class="col-md-12 editiconright"><a href="#" onclick="editclick_row(this)" class="editclick">	<i class="fa fa-pencil" aria-hidden="true"></i></a></div></div><div class="col-md-3 pad-0 mrg-bt-5"></div></div><!-- /ko --><!-- ko if: $data.name().toString().indexOf("") !== -1 || $data.name().toString().indexOf("") !== -1 || $data.name().toString().indexOf("") !== -1--><!-- /ko -->')
        
        
            #Checkbox 2
            sec_str += (
            '<div style="height: 30px; border-left: 0px; border-right: 0px; border-bottom: 1px solid rgb(204, 204, 204); padding-bottom: 10px;" data-bind="attr: {"id":"drop_cont"+stdAttrCode(),"class": isWholeRow() ? "g4 except_sec dropDownHeight iconhvr" : "g1 except_sec dropDownHeight iconhvr" }" id="drop_cont11744" class="g4 except_sec dropDownHeight iconhvr">')
            sec_str += ('<div class="col-md-5">	<abbr data-bind="attr:{"title":label}" title="doc_lang"><label class="col-md-11" data-bind="html: label" style="padding: 5px 5px;margin: 0;" title="doc_lang">Include Items</label></abbr><a href="#" class="col-md-1" style="text-align:right;padding: 7px 5px;color:green">	<i class="fa fa-info-circle autoClosePopover" data-bind="popover: { templateId: "HintTemplate", container: "body", placement: "top", autoClose: true, html: true}" data-original-title="doc_lang" title=""></i></a></div><div class="col-md-3 pad-0 padt_7"><input id="include_items" class="custom custom_gen_doc" type="checkbox" ><span class="lbl"></span></div><!-- /ko --><div class="col-md-3 " style="display:none;"> <span class="" data-bind="attr:{"id": $data.name()}" id=""></span></div><div class="col-md-1" style="float: right;"><div class="col-md-12 editiconright"><a href="#" onclick="editclick_row(this)" class="editclick">	<i class="fa fa-pencil" aria-hidden="true"></i></a></div></div><div class="col-md-3 pad-0 mrg-bt-5"></div></div><!-- /ko --><!-- ko if: $data.name().toString().indexOf("") !== -1 || $data.name().toString().indexOf("") !== -1 || $data.name().toString().indexOf("") !== -1--><!-- /ko -->')
        
        
        
            #Checkbox 3
            sec_str += (
            '<div style="height: 30px; border-left: 0px; border-right: 0px; border-bottom: 1px solid rgb(204, 204, 204); padding-bottom: 10px;" data-bind="attr: {"id":"drop_cont"+stdAttrCode(),"class": isWholeRow() ? "g4 except_sec dropDownHeight iconhvr" : "g1 except_sec dropDownHeight iconhvr" }" id="drop_cont11744" class="g4 except_sec dropDownHeight iconhvr">')
            sec_str += ('<div class="col-md-5">	<abbr data-bind="attr:{"title":label}" title="doc_lang"><label class="col-md-11" data-bind="html: label" style="padding: 5px 5px;margin: 0;" title="doc_lang">Include Signature Line</label></abbr><a href="#" class="col-md-1" style="text-align:right;padding: 7px 5px;color:green">	<i class="fa fa-info-circle autoClosePopover" data-bind="popover: { templateId: "HintTemplate", container: "body", placement: "top", autoClose: true, html: true}" data-original-title="doc_lang" title=""></i></a></div><div class="col-md-3 pad-0 padt_7"><input id="include_signature" class="custom custom_gen_doc" type="checkbox" ><span class="lbl"></span></div><!-- /ko --><div class="col-md-3 " style="display:none;"> <span class="" data-bind="attr:{"id": $data.name()}" id=""></span></div><div class="col-md-1" style="float: right;"><div class="col-md-12 editiconright"><a href="#" onclick="editclick_row(this)" class="editclick">	<i class="fa fa-pencil" aria-hidden="true"></i></a></div></div><div class="col-md-3 pad-0 mrg-bt-5"></div></div><!-- /ko --><!-- ko if: $data.name().toString().indexOf("") !== -1 || $data.name().toString().indexOf("") !== -1 || $data.name().toString().indexOf("") !== -1--><!-- /ko -->')
        
            #Appendixes
            sec_str += ('<div id="container">')
            sec_str += (
                    '<div class="dyn_main_head master_manufac glyphicon pointer   glyphicon-chevron-down" onclick="dyn_main_sec_collapse_arrow(this)" data-target=".sec_" data-toggle="collapse"><label class="onlytext"><label class="onlytext"><div>APPENDIXES</div></label></div>')

            sec_str += ('<div id="sec_LANG" class= sec_LANG>')
            #Checkbox 4
            sec_str += (
            '<div style="height: 30px; border-left: 0px; border-right: 0px; border-bottom: 1px solid rgb(204, 204, 204); padding-bottom: 10px;" data-bind="attr: {"id":"drop_cont"+stdAttrCode(),"class": isWholeRow() ? "g4 except_sec dropDownHeight iconhvr" : "g1 except_sec dropDownHeight iconhvr" }" id="drop_cont11744" class="g4 except_sec dropDownHeight iconhvr">')
            sec_str += ('<div class="col-md-5">	<abbr data-bind="attr:{"title":label}" title="doc_lang"><label class="col-md-11" data-bind="html: label" style="padding: 5px 5px;margin: 0;" title="doc_lang">Include Parts List</label></abbr><a href="#" class="col-md-1" style="text-align:right;padding: 7px 5px;color:green">	<i class="fa fa-info-circle autoClosePopover" data-bind="popover: { templateId: "HintTemplate", container: "body", placement: "top", autoClose: true, html: true}" data-original-title="doc_lang" title=""></i></a></div><div class="col-md-3 pad-0 padt_7"><input id="include_parts_list" class="custom custom_gen_doc" type="checkbox" ><span class="lbl"></span></div><!-- /ko --><div class="col-md-3 " style="display:none;"> <span class="" data-bind="attr:{"id": $data.name()}" id=""></span></div><div class="col-md-1" style="float: right;"><div class="col-md-12 editiconright"><a href="#" onclick="editclick_row(this)" class="editclick">	<i class="fa fa-pencil" aria-hidden="true"></i></a></div></div><div class="col-md-3 pad-0 mrg-bt-5"></div></div><!-- /ko --><!-- ko if: $data.name().toString().indexOf("") !== -1 || $data.name().toString().indexOf("") !== -1 || $data.name().toString().indexOf("") !== -1--><!-- /ko -->')
            #checkbox 5
            sec_str += (
            '<div style="height: 30px; border-left: 0px; border-right: 0px; border-bottom: 1px solid rgb(204, 204, 204); padding-bottom: 10px;" data-bind="attr: {"id":"drop_cont"+stdAttrCode(),"class": isWholeRow() ? "g4 except_sec dropDownHeight iconhvr" : "g1 except_sec dropDownHeight iconhvr" }" id="drop_cont11744" class="g4 except_sec dropDownHeight iconhvr">')
            if get_fpm_service == "Z0108":
                sec_str += ('<div class="col-md-5">	<abbr data-bind="attr:{"title":label}" title="doc_lang"><label class="col-md-11" data-bind="html: label" style="padding: 5px 5px;margin: 0;" title="doc_lang">Include Part Delivery schedule(FPM only)</label></abbr><a href="#" class="col-md-1" style="text-align:right;padding: 7px 5px;color:green">	<i class="fa fa-info-circle autoClosePopover" data-bind="popover: { templateId: "HintTemplate", container: "body", placement: "top", autoClose: true, html: true}" data-original-title="doc_lang" title=""></i></a></div><div class="col-md-3 pad-0 padt_7"><input id="include_part_delivery" class="custom custom_gen_doc" type="checkbox" ><span class="lbl"></span></div><!-- /ko --><div class="col-md-3 " style="display:none;"> <span class="" data-bind="attr:{"id": $data.name()}" id=""></span></div><div class="col-md-1" style="float: right;"><div class="col-md-12 editiconright"><a href="#" onclick="editclick_row(this)" class="editclick">	<i class="fa fa-pencil" aria-hidden="true"></i></a></div></div><div class="col-md-3 pad-0 mrg-bt-5"></div></div><!-- /ko --><!-- ko if: $data.name().toString().indexOf("") !== -1 || $data.name().toString().indexOf("") !== -1 || $data.name().toString().indexOf("") !== -1--><!-- /ko -->')
            else:
                sec_str += ('<div class="col-md-5">	<abbr data-bind="attr:{"title":label}" title="doc_lang"><label class="col-md-11" data-bind="html: label" style="padding: 5px 5px;margin: 0;" title="doc_lang">Include Part Delivery schedule(FPM only)</label></abbr><a href="#" class="col-md-1" style="text-align:right;padding: 7px 5px;color:green">	<i class="fa fa-info-circle autoClosePopover" data-bind="popover: { templateId: "HintTemplate", container: "body", placement: "top", autoClose: true, html: true}" data-original-title="doc_lang" title=""></i></a></div><div class="col-md-3 pad-0 padt_7"><input id="include_part_delivery" class="custom custom_gen_doc" type="checkbox" disabled><span class="lbl"></span></div><!-- /ko --><div class="col-md-3 " style="display:none;"> <span class="" data-bind="attr:{"id": $data.name()}" id=""></span></div><div class="col-md-1" style="float: right;"><div class="col-md-12 editiconright"><a href="#" onclick="editclick_row(this)" class="editclick">	<i class="fa fa-pencil" aria-hidden="true"></i></a></div></div><div class="col-md-3 pad-0 mrg-bt-5"></div></div><!-- /ko --><!-- ko if: $data.name().toString().indexOf("") !== -1 || $data.name().toString().indexOf("") !== -1 || $data.name().toString().indexOf("") !== -1--><!-- /ko -->')
            #checkbox 5
            '''sec_str += (
            '<div style="height: 30px; border-left: 0px; border-right: 0px; border-bottom: 1px solid rgb(204, 204, 204); padding-bottom: 10px;" data-bind="attr: {"id":"drop_cont"+stdAttrCode(),"class": isWholeRow() ? "g4 except_sec dropDownHeight iconhvr" : "g1 except_sec dropDownHeight iconhvr" }" id="drop_cont11744" class="g4 except_sec dropDownHeight iconhvr">')
            sec_str += ('<div class="col-md-5">	<abbr data-bind="attr:{"title":label}" title="doc_lang"><label class="col-md-11" data-bind="html: label" style="padding: 5px 5px;margin: 0;" title="doc_lang">Include Detailed Billing Matrix by Offering</label></abbr><a href="#" class="col-md-1" style="text-align:right;padding: 7px 5px;color:green">	<i class="fa fa-info-circle autoClosePopover" data-bind="popover: { templateId: "HintTemplate", container: "body", placement: "top", autoClose: true, html: true}" data-original-title="doc_lang" title=""></i></a></div><div class="col-md-3 pad-0 padt_7"><input id="billmat" class="custom custom_gen_doc" type="checkbox" ><span class="lbl"></span></div><!-- /ko --><div class="col-md-3 " style="display:none;"> <span class="" data-bind="attr:{"id": $data.name()}" id=""></span></div><div class="col-md-1" style="float: right;"><div class="col-md-12 editiconright"><a href="#" onclick="editclick_row(this)" class="editclick">	<i class="fa fa-pencil" aria-hidden="true"></i></a></div></div><div class="col-md-3 pad-0 mrg-bt-5"></div></div><!-- /ko --><!-- ko if: $data.name().toString().indexOf("") !== -1 || $data.name().toString().indexOf("") !== -1 || $data.name().toString().indexOf("") !== -1--><!-- /ko -->')'''

            #dropdown
            sec_str += (
            '<div style="height: 30px; border-left: 0px; border-right: 0px; border-bottom: 1px solid rgb(204, 204, 204); padding-bottom: 10px;" data-bind="attr: {"id":"drop_cont"+stdAttrCode(),"class": isWholeRow() ? "g4 except_sec dropDownHeight iconhvr" : "g1 except_sec dropDownHeight iconhvr" }" id="drop_cont11744" class="g4 except_sec dropDownHeight iconhvr">')
            if get_fpm_service:
                sec_str += ('<div class="col-md-5">	<abbr data-bind="attr:{"title":label}" title="doc_lang"><label class="col-md-11" data-bind="html: label" style="padding: 5px 5px;margin: 0;" title="doc_lang">Include Detailed Billing Matrix by Offering</label></abbr><a href="#" class="col-md-1" style="text-align:right;padding: 7px 5px;color:green">	<i class="fa fa-info-circle autoClosePopover" data-bind="popover: { templateId: "HintTemplate", container: "body", placement: "top", autoClose: true, html: true}" data-original-title="doc_lang" title=""></i></a></div><div class="col-md-3 pad-0 padt_7"><input id="billmat" class="custom custom_gen_doc" type="checkbox" disabled><span class="lbl"></span></div><!-- /ko --><div class="col-md-3 " style="display:none;"> <span class="" data-bind="attr:{"id": $data.name()}" id=""></span></div><div class="col-md-1" style="float: right;"><div class="col-md-12 editiconright"><a href="#" onclick="editclick_row(this)" class="editclick">	<i class="fa fa-pencil" aria-hidden="true"></i></a></div></div><div class="col-md-3 pad-0 mrg-bt-5"></div></div><!-- /ko --><!-- ko if: $data.name().toString().indexOf("") !== -1 || $data.name().toString().indexOf("") !== -1 || $data.name().toString().indexOf("") !== -1--><!-- /ko -->')
            else:
                sec_str += ('<div class="col-md-5">	<abbr data-bind="attr:{"title":label}" title="doc_lang"><label class="col-md-11" data-bind="html: label" style="padding: 5px 5px;margin: 0;" title="doc_lang">Include Detailed Billing Matrix by Offering</label></abbr><a href="#" class="col-md-1" style="text-align:right;padding: 7px 5px;color:green">	<i class="fa fa-info-circle autoClosePopover" data-bind="popover: { templateId: "HintTemplate", container: "body", placement: "top", autoClose: true, html: true}" data-original-title="doc_lang" title=""></i></a></div><div class="col-md-3 pad-0 padt_7"><input id="billmat" class="custom custom_gen_doc" type="checkbox" ><span class="lbl"></span></div><!-- /ko --><div class="col-md-3 " style="display:none;"> <span class="" data-bind="attr:{"id": $data.name()}" id=""></span></div><div class="col-md-1" style="float: right;"><div class="col-md-12 editiconright"><a href="#" onclick="editclick_row(this)" class="editclick">	<i class="fa fa-pencil" aria-hidden="true"></i></a></div></div><div class="col-md-3 pad-0 mrg-bt-5"></div></div><!-- /ko --><!-- ko if: $data.name().toString().indexOf("") !== -1 || $data.name().toString().indexOf("") !== -1 || $data.name().toString().indexOf("") !== -1--><!-- /ko -->')

            sec_str += (
            '<div style="height: 30px; border-left: 0px; border-right: 0px; border-bottom: 1px solid rgb(204, 204, 204); padding-bottom: 10px;" data-bind="attr: {"id":"drop_cont"+stdAttrCode(),"class": isWholeRow() ? "g4 except_sec dropDownHeight iconhvr" : "g1 except_sec dropDownHeight iconhvr" }" id="drop_cont11744" class="g4 except_sec dropDownHeight iconhvr">')
            sec_str += (
            '<div class="col-md-5">	<abbr data-bind="attr:{"title":label}" title="doc_lang"><label class="col-md-11" data-bind="html: label" style="padding: 5px 5px;margin: 0;" title="doc_lang">Include Critical parameter</label></abbr><a href="#" class="col-md-1" style="text-align:right;padding: 7px 5px;color:green">	<i class="fa fa-info-circle autoClosePopover" data-bind="popover: { templateId: "HintTemplate", container: "body", placement: "top", autoClose: true, html: true}" data-original-title="doc_lang" title=""></i></a></div><!--ko if: $data.template() === "DropDownTemplate" && $data.name().toString().indexOf("") === -1 && $data.name().toString().indexOf("") === -1 && $data.name().toString().indexOf("") === -1--><div class="col-md-3 pad-0"><select id="doc" class="form-control light_yellow" id="Lang" disabled><option value="Select">Select</option><option value="Critical Parameters by Greenbook">Critical Parameters by Greenbook</option><option value="Critical Parameters by Fab and Greenbook">Critical Parameters by Fab and Greenbook</option></select></div><!-- /ko --><!-- ko if: $data.name().toString().indexOf("") !== -1 || $data.name().toString().indexOf("") !== -1 || $data.name().toString().indexOf("") !== -1--><!-- /ko --><div class="col-md-3 " style="display:none;"> <span class="" data-bind="attr:{"id": $data.name()}" id=""></span></div><div class="col-md-1" style="float: right;"><div class="col-md-12 editiconright"><a href="#" onclick="editclick_row(this)" class="editclick">	<i class="fa fa-pencil" aria-hidden="true"></i></a></div></div><div class="col-md-3 pad-0 mrg-bt-5"></div></div>')
            #sec_str += (
            #	'<div class="g4  except_sec removeHorLine iconhvr sec_edit_sty"><button id="SEC_DIS_CLOSE" style="display: none;"></button><button id="Lang_cancel" class="btnconfig btnMainBanner #sec_edit_sty_btn" onclick="lang_cancel()" name="SECT_CANCEL">CANCEL</button><button id="Lang_Select" class="btnconfig btnMainBanner sec_edit_sty_btn_inh" onclick="lang_save()" #name="SECT_SAVE">SAVE</button></div>')

            sec_str += (
            "</div>")

            sec_str += '<table class="wth100mrg8"><tbody>'
        else:
            Trace.Write("Else")
            sec_str += ('<div id="container">')
            sec_str += (
                    '<div class="dyn_main_head master_manufac glyphicon pointer   glyphicon-chevron-down" onclick="dyn_main_sec_collapse_arrow(this)" data-target=".sec_" data-toggle="collapse"><label class="onlytext"><label class="onlytext"><div>GENERAL SETTINGS</div></label></div>')

        
            sec_str += ('<div id="sec_LANG" class= sec_LANG>')
            #dropdown
            sec_str += (
            '<div style="height: 30px; border-left: 0px; border-right: 0px; border-bottom: 1px solid rgb(204, 204, 204); padding-bottom: 10px;" data-bind="attr: {"id":"drop_cont"+stdAttrCode(),"class": isWholeRow() ? "g4 except_sec dropDownHeight iconhvr" : "g1 except_sec dropDownHeight iconhvr" }" id="drop_cont11744" class="g4 except_sec dropDownHeight iconhvr">')
            sec_str += (
            '<div class="col-md-5">	<abbr data-bind="attr:{"title":label}" title="doc_lang"><label class="col-md-11" data-bind="html: label" style="padding: 5px 5px;margin: 0;" title="doc_lang">Document Language</label></abbr><a href="#" class="col-md-1" style="text-align:right;padding: 7px 5px;color:green">	<i class="fa fa-info-circle autoClosePopover" data-bind="popover: { templateId: "HintTemplate", container: "body", placement: "top", autoClose: true, html: true}" data-original-title="doc_lang" title=""></i></a></div><!--ko if: $data.template() === "DropDownTemplate" && $data.name().toString().indexOf("") === -1 && $data.name().toString().indexOf("") === -1 && $data.name().toString().indexOf("") === -1--><div class="col-md-3 pad-0"><select class="form-control" id="Lang" disabled><option value="Select">Select</option><option value="English">English</option><option value="Chinese">Chinese</option></select></div><!-- /ko --><!-- ko if: $data.name().toString().indexOf("") !== -1 || $data.name().toString().indexOf("") !== -1 || $data.name().toString().indexOf("") !== -1--><!-- /ko --><div class="col-md-3 " style="display:none;"> <span class="" data-bind="attr:{"id": $data.name()}" id=""></span></div><div class="col-md-1" style="float: right;"><div class="col-md-12 editiconright"><a href="#" onclick="editclick_row(this)" class="editclick">	<i class="fa fa-lock" aria-hidden="true"></i></a></div></div><div class="col-md-3 pad-0 mrg-bt-5"></div></div>')


            #dropdown
            sec_str += (
            '<div style="height: 30px; border-left: 0px; border-right: 0px; border-bottom: 1px solid rgb(204, 204, 204); padding-bottom: 10px;" data-bind="attr: {"id":"drop_cont"+stdAttrCode(),"class": isWholeRow() ? "g4 except_sec dropDownHeight iconhvr" : "g1 except_sec dropDownHeight iconhvr" }" id="drop_cont11744" class="g4 except_sec dropDownHeight iconhvr">')
            sec_str += (
            '<div class="col-md-5">	<abbr data-bind="attr:{"title":label}" title="doc_Cur"><label class="col-md-11" data-bind="html: label" style="padding: 5px 5px;margin: 0;" title="doc_lang">Document  Currency</label></abbr><a href="#" class="col-md-1" style="text-align:right;padding: 7px 5px;color:green">	<i class="fa fa-info-circle autoClosePopover" data-bind="popover: { templateId: "HintTemplate", container: "body", placement: "top", autoClose: true, html: true}" data-original-title="doc_lang" title=""></i></a></div><!--ko if: $data.template() === "DropDownTemplate" && $data.name().toString().indexOf("") === -1 && $data.name().toString().indexOf("") === -1 && $data.name().toString().indexOf("") === -1--><div class="col-md-3 pad-0"><select class="form-control" id="Lang" disabled><option value="Select">Select</option><option value="Japan">YEN</option><option value="Dollar">USD</option><option value="Chinese">YUAN</option></select></div><!-- /ko --><!-- ko if: $data.name().toString().indexOf("") !== -1 || $data.name().toString().indexOf("") !== -1 || $data.name().toString().indexOf("") !== -1--><!-- /ko --><div class="col-md-3 " style="display:none;"> <span class="" data-bind="attr:{"id": $data.name()}" id=""></span></div><div class="col-md-1" style="float: right;"><div class="col-md-12 editiconright"><a href="#" onclick="editclick_row(this)" class="editclick">	<i class="fa fa-lock" aria-hidden="true"></i></a></div></div><div class="col-md-3 pad-0 mrg-bt-5"></div></div>')
        
            #Checkbox 1
            sec_str += (
            '<div style="height: 30px; border-left: 0px; border-right: 0px; border-bottom: 1px solid rgb(204, 204, 204); padding-bottom: 10px;" data-bind="attr: {"id":"drop_cont"+stdAttrCode(),"class": isWholeRow() ? "g4 except_sec dropDownHeight iconhvr" : "g1 except_sec dropDownHeight iconhvr" }" id="drop_cont11744" class="g4 except_sec dropDownHeight iconhvr">')
            sec_str += ('<div class="col-md-5">	<abbr data-bind="attr:{"title":label}" title="doc_lang"><label class="col-md-11" data-bind="html: label" style="padding: 5px 5px;margin: 0;" title="doc_lang">Include Expected Date of Fx Rate</label></abbr><a href="#" class="col-md-1" style="text-align:right;padding: 7px 5px;color:green">	<i class="fa fa-info-circle autoClosePopover" data-bind="popover: { templateId: "HintTemplate", container: "body", placement: "top", autoClose: true, html: true}" data-original-title="doc_lang" title=""></i></a></div><div class="col-md-3 pad-0 padt_7"><input id="fxrate" class="custom custom_gen_doc" type="checkbox" disabled><span class="lbl"></span></div><!-- /ko --><div class="col-md-3 " style="display:none;"> <span class="" data-bind="attr:{"id": $data.name()}" id=""></span></div><div class="col-md-1" style="float: right;"><div class="col-md-12 editiconright"><a href="#" onclick="editclick_row(this)" class="editclick">	<i class="fa fa-lock" aria-hidden="true"></i></a></div></div><div class="col-md-3 pad-0 mrg-bt-5"></div></div><!-- /ko --><!-- ko if: $data.name().toString().indexOf("") !== -1 || $data.name().toString().indexOf("") !== -1 || $data.name().toString().indexOf("") !== -1--><!-- /ko -->')
        
        
            #Checkbox 2
            sec_str += (
            '<div style="height: 30px; border-left: 0px; border-right: 0px; border-bottom: 1px solid rgb(204, 204, 204); padding-bottom: 10px;" data-bind="attr: {"id":"drop_cont"+stdAttrCode(),"class": isWholeRow() ? "g4 except_sec dropDownHeight iconhvr" : "g1 except_sec dropDownHeight iconhvr" }" id="drop_cont11744" class="g4 except_sec dropDownHeight iconhvr">')
            sec_str += ('<div class="col-md-5">	<abbr data-bind="attr:{"title":label}" title="doc_lang"><label class="col-md-11" data-bind="html: label" style="padding: 5px 5px;margin: 0;" title="doc_lang">Include Items</label></abbr><a href="#" class="col-md-1" style="text-align:right;padding: 7px 5px;color:green">	<i class="fa fa-info-circle autoClosePopover" data-bind="popover: { templateId: "HintTemplate", container: "body", placement: "top", autoClose: true, html: true}" data-original-title="doc_lang" title=""></i></a></div><div class="col-md-3 pad-0 padt_7"><input id="bm" class="custom custom_gen_doc" type="checkbox" disabled><span class="lbl"></span></div><!-- /ko --><div class="col-md-3 " style="display:none;"> <span class="" data-bind="attr:{"id": $data.name()}" id=""></span></div><div class="col-md-1" style="float: right;"><div class="col-md-12 editiconright"><a href="#" onclick="editclick_row(this)" class="editclick">	<i class="fa fa-lock" aria-hidden="true"></i></a></div></div><div class="col-md-3 pad-0 mrg-bt-5"></div></div><!-- /ko --><!-- ko if: $data.name().toString().indexOf("") !== -1 || $data.name().toString().indexOf("") !== -1 || $data.name().toString().indexOf("") !== -1--><!-- /ko -->')
        
        
        
            #Checkbox 3
            sec_str += (
            '<div style="height: 30px; border-left: 0px; border-right: 0px; border-bottom: 1px solid rgb(204, 204, 204); padding-bottom: 10px;" data-bind="attr: {"id":"drop_cont"+stdAttrCode(),"class": isWholeRow() ? "g4 except_sec dropDownHeight iconhvr" : "g1 except_sec dropDownHeight iconhvr" }" id="drop_cont11744" class="g4 except_sec dropDownHeight iconhvr">')
            sec_str += ('<div class="col-md-5">	<abbr data-bind="attr:{"title":label}" title="doc_lang"><label class="col-md-11" data-bind="html: label" style="padding: 5px 5px;margin: 0;" title="doc_lang">Include Signature Line</label></abbr><a href="#" class="col-md-1" style="text-align:right;padding: 7px 5px;color:green">	<i class="fa fa-info-circle autoClosePopover" data-bind="popover: { templateId: "HintTemplate", container: "body", placement: "top", autoClose: true, html: true}" data-original-title="doc_lang" title=""></i></a></div><div class="col-md-3 pad-0 padt_7"><input id="include_sign" class="custom custom_gen_doc" type="checkbox" disabled><span class="lbl"></span></div><!-- /ko --><div class="col-md-3 " style="display:none;"> <span class="" data-bind="attr:{"id": $data.name()}" id=""></span></div><div class="col-md-1" style="float: right;"><div class="col-md-12 editiconright"><a href="#" onclick="editclick_row(this)" class="editclick">	<i class="fa fa-lock" aria-hidden="true"></i></a></div></div><div class="col-md-3 pad-0 mrg-bt-5"></div></div><!-- /ko --><!-- ko if: $data.name().toString().indexOf("") !== -1 || $data.name().toString().indexOf("") !== -1 || $data.name().toString().indexOf("") !== -1--><!-- /ko -->')
        
            #Appendixes
            sec_str += ('<div id="container">')
            sec_str += (
                    '<div class="dyn_main_head master_manufac glyphicon pointer   glyphicon-chevron-down" onclick="dyn_main_sec_collapse_arrow(this)" data-target=".sec_" data-toggle="collapse"><label class="onlytext"><label class="onlytext"><div>APPENDIXES</div></label></div>')

            sec_str += ('<div id="sec_LANG" class= sec_LANG>')
            #Checkbox 4
            sec_str += (
            '<div style="height: 30px; border-left: 0px; border-right: 0px; border-bottom: 1px solid rgb(204, 204, 204); padding-bottom: 10px;" data-bind="attr: {"id":"drop_cont"+stdAttrCode(),"class": isWholeRow() ? "g4 except_sec dropDownHeight iconhvr" : "g1 except_sec dropDownHeight iconhvr" }" id="drop_cont11744" class="g4 except_sec dropDownHeight iconhvr">')
            sec_str += ('<div class="col-md-5">	<abbr data-bind="attr:{"title":label}" title="doc_lang"><label class="col-md-11" data-bind="html: label" style="padding: 5px 5px;margin: 0;" title="doc_lang">Include Parts List</label></abbr><a href="#" class="col-md-1" style="text-align:right;padding: 7px 5px;color:green">	<i class="fa fa-info-circle autoClosePopover" data-bind="popover: { templateId: "HintTemplate", container: "body", placement: "top", autoClose: true, html: true}" data-original-title="doc_lang" title=""></i></a></div><div class="col-md-3 pad-0 padt_7"><input id="include_parts_list" class="custom custom_gen_doc" type="checkbox" disabled><span class="lbl"></span></div><!-- /ko --><div class="col-md-3 " style="display:none;"> <span class="" data-bind="attr:{"id": $data.name()}" id=""></span></div><div class="col-md-1" style="float: right;"><div class="col-md-12 editiconright"><a href="#" onclick="editclick_row(this)" class="editclick">	<i class="fa fa-lock" aria-hidden="true"></i></a></div></div><div class="col-md-3 pad-0 mrg-bt-5"></div></div><!-- /ko --><!-- ko if: $data.name().toString().indexOf("") !== -1 || $data.name().toString().indexOf("") !== -1 || $data.name().toString().indexOf("") !== -1--><!-- /ko -->')
            #checkbox 5
            sec_str += (
            '<div style="height: 30px; border-left: 0px; border-right: 0px; border-bottom: 1px solid rgb(204, 204, 204); padding-bottom: 10px;" data-bind="attr: {"id":"drop_cont"+stdAttrCode(),"class": isWholeRow() ? "g4 except_sec dropDownHeight iconhvr" : "g1 except_sec dropDownHeight iconhvr" }" id="drop_cont11744" class="g4 except_sec dropDownHeight iconhvr">')
            sec_str += ('<div class="col-md-5">	<abbr data-bind="attr:{"title":label}" title="doc_lang"><label class="col-md-11" data-bind="html: label" style="padding: 5px 5px;margin: 0;" title="doc_lang">Include Part Delivery schedule(FPM only)</label></abbr><a href="#" class="col-md-1" style="text-align:right;padding: 7px 5px;color:green">	<i class="fa fa-info-circle autoClosePopover" data-bind="popover: { templateId: "HintTemplate", container: "body", placement: "top", autoClose: true, html: true}" data-original-title="doc_lang" title=""></i></a></div><div class="col-md-3 pad-0 padt_7"><input id="part_delivery_schedule" class="custom custom_gen_doc" type="checkbox" disabled><span class="lbl"></span></div><!-- /ko --><div class="col-md-3 " style="display:none;"> <span class="" data-bind="attr:{"id": $data.name()}" id=""></span></div><div class="col-md-1" style="float: right;"><div class="col-md-12 editiconright"><a href="#" onclick="editclick_row(this)" class="editclick">	<i class="fa fa-lock" aria-hidden="true"></i></a></div></div><div class="col-md-3 pad-0 mrg-bt-5"></div></div><!-- /ko --><!-- ko if: $data.name().toString().indexOf("") !== -1 || $data.name().toString().indexOf("") !== -1 || $data.name().toString().indexOf("") !== -1--><!-- /ko -->')	
            #checkbox 5
            sec_str += (
            '<div style="height: 30px; border-left: 0px; border-right: 0px; border-bottom: 1px solid rgb(204, 204, 204); padding-bottom: 10px;" data-bind="attr: {"id":"drop_cont"+stdAttrCode(),"class": isWholeRow() ? "g4 except_sec dropDownHeight iconhvr" : "g1 except_sec dropDownHeight iconhvr" }" id="drop_cont11744" class="g4 except_sec dropDownHeight iconhvr">')
            sec_str += ('<div class="col-md-5">	<abbr data-bind="attr:{"title":label}" title="doc_lang"><label class="col-md-11" data-bind="html: label" style="padding: 5px 5px;margin: 0;" title="doc_lang">Include Detailed Billing Matrix by Offering</label></abbr><a href="#" class="col-md-1" style="text-align:right;padding: 7px 5px;color:green">	<i class="fa fa-info-circle autoClosePopover" data-bind="popover: { templateId: "HintTemplate", container: "body", placement: "top", autoClose: true, html: true}" data-original-title="doc_lang" title=""></i></a></div><div class="col-md-3 pad-0 padt_7"><input id="billmat" class="custom custom_gen_doc" type="checkbox" disabled><span class="lbl"></span></div><!-- /ko --><div class="col-md-3 " style="display:none;"> <span class="" data-bind="attr:{"id": $data.name()}" id=""></span></div><div class="col-md-1" style="float: right;"><div class="col-md-12 editiconright"><a href="#" onclick="editclick_row(this)" class="editclick">	<i class="fa fa-lock" aria-hidden="true"></i></a></div></div><div class="col-md-3 pad-0 mrg-bt-5"></div></div><!-- /ko --><!-- ko if: $data.name().toString().indexOf("") !== -1 || $data.name().toString().indexOf("") !== -1 || $data.name().toString().indexOf("") !== -1--><!-- /ko -->')

            #dropdown
            sec_str += (
            '<div style="height: 30px; border-left: 0px; border-right: 0px; border-bottom: 1px solid rgb(204, 204, 204); padding-bottom: 10px;" data-bind="attr: {"id":"drop_cont"+stdAttrCode(),"class": isWholeRow() ? "g4 except_sec dropDownHeight iconhvr" : "g1 except_sec dropDownHeight iconhvr" }" id="drop_cont11744" class="g4 except_sec dropDownHeight iconhvr">')
            sec_str += (
            '<div class="col-md-5">	<abbr data-bind="attr:{"title":label}" title="doc_lang"><label class="col-md-11" data-bind="html: label" style="padding: 5px 5px;margin: 0;" title="doc_lang">Include Critical parameter</label></abbr><a href="#" class="col-md-1" style="text-align:right;padding: 7px 5px;color:green">	<i class="fa fa-info-circle autoClosePopover" data-bind="popover: { templateId: "HintTemplate", container: "body", placement: "top", autoClose: true, html: true}" data-original-title="doc_lang" title=""></i></a></div><!--ko if: $data.template() === "DropDownTemplate" && $data.name().toString().indexOf("") === -1 && $data.name().toString().indexOf("") === -1 && $data.name().toString().indexOf("") === -1--><div class="col-md-3 pad-0"><select id="doc" class="form-control" id="Lang" disabled><option value="Select">Select</option><option value="Critical Parameters by Greenbook">Critical Parameters by Greenbook</option><option value="Critical Parameters by Fab and Greenbook">Critical Parameters by Fab and Greenbook</option></select></div><!-- /ko --><!-- ko if: $data.name().toString().indexOf("") !== -1 || $data.name().toString().indexOf("") !== -1 || $data.name().toString().indexOf("") !== -1--><!-- /ko --><div class="col-md-3 " style="display:none;"> <span class="" data-bind="attr:{"id": $data.name()}" id=""></span></div><div class="col-md-1" style="float: right;"><div class="col-md-12 editiconright"><a href="#" onclick="editclick_row(this)" class="editclick">	<i class="fa fa-lock" aria-hidden="true"></i></a></div></div><div class="col-md-3 pad-0 mrg-bt-5"></div></div>')


            #sec_str += (
            #	'<div class="g4  except_sec removeHorLine iconhvr sec_edit_sty"><button id="SEC_DIS_CLOSE" style="display: none;"></button><button id="Lang_cancel" class="btnconfig btnMainBanner sec_edit_sty_btn" onclick="lang_cancel()" name="SECT_CANCEL">CANCEL</button><button id="Lang_Select" class="btnconfig btnMainBanner sec_edit_sty_btn_inh" onclick="lang_save()" name="SECT_SAVE">SAVE</button></div>'
            #)

            sec_str += (
            "</div>")

            sec_str += '<table class="wth100mrg8"><tbody>'
    return sec_str
def _insert_parts_delivery():
    Trace.Write('scussces--')
    get_parts_item_delivery_insert = Quote.QuoteTables["QT_SAQSPT"]
    get_parts_item_delivery_insert.Rows.Clear()

    get_parts_delivery_details_obj = Sql.GetList("select SERVICE_ID,CUSTOMER_PART_NUMBER,PART_NUMBER,QUOTE_ID,DELIVERY_1,DELIVERY_2,DELIVERY_3,DELIVERY_4,DELIVERY_5,DELIVERY_6,DELIVERY_7,DELIVERY_8,DELIVERY_9,DELIVERY_10,DELIVERY_11,DELIVERY_12,DELIVERY_13,DELIVERY_14,DELIVERY_15,DELIVERY_16,DELIVERY_17,DELIVERY_18,DELIVERY_19,DELIVERY_20,DELIVERY_21,DELIVERY_22,DELIVERY_23,DELIVERY_24,DELIVERY_25,DELIVERY_26,DELIVERY_27,DELIVERY_28,DELIVERY_29,DELIVERY_30,DELIVERY_31,DELIVERY_32,DELIVERY_33,DELIVERY_34,DELIVERY_35,DELIVERY_36,DELIVERY_37,DELIVERY_38,DELIVERY_39,DELIVERY_40,DELIVERY_41,DELIVERY_42,DELIVERY_43,DELIVERY_44,DELIVERY_45,DELIVERY_46,DELIVERY_47,DELIVERY_48,DELIVERY_49,DELIVERY_50,DELIVERY_51,DELIVERY_52,QTEREV_RECORD_ID,QUOTE_RECORD_ID,QTEREV_ID,{UserId} as ownerId,{CartId} as cartId FROM SAQSPT where QUOTE_RECORD_ID = '{QuoteRecordId}' and QTEREV_RECORD_ID= '{rev_rec_id}'".format(QuoteRecordId=contract_quote_record_id,rev_rec_id=quote_revision_record_id,UserId= cartobj.USERID,CartId = cartobj.CART_ID))
    if get_parts_delivery_details_obj:
        for val in get_parts_delivery_details_obj:
            newRow = get_parts_item_delivery_insert.AddNewRow()
            if val.SERVICE_ID == "Z0108":
                Quote.GetCustomField('QT_OD_DELIVERY_SERVICE').Content = 'YES'
            else:
                Quote.GetCustomField('QT_OD_DELIVERY_SERVICE').Content = "NO_GENERATE_DELIVERY"
            newRow['CUSTOMER_PART_NUMBER'] = val.CUSTOMER_PART_NUMBER if val.CUSTOMER_PART_NUMBER else ""
            newRow['QUOTE_RECORD_ID'] = val.QUOTE_RECORD_ID if val.QUOTE_RECORD_ID else ""
            newRow['PART_NUMBER'] = val.PART_NUMBER if val.PART_NUMBER else ""
            newRow['DELIVERY_1'] = val.DELIVERY_1 if val.DELIVERY_1 else 0
            newRow['DELIVERY_2'] = val.DELIVERY_2 if val.DELIVERY_2 else 0
            newRow['DELIVERY_3'] = val.DELIVERY_3 if val.DELIVERY_3 else 0
            newRow['DELIVERY_4'] = val.DELIVERY_4 if val.DELIVERY_4 else 0
            newRow['DELIVERY_5'] = val.DELIVERY_5 if val.DELIVERY_5 else 0
            newRow['DELIVERY_6'] = val.DELIVERY_6 if val.DELIVERY_6 else 0
            newRow['DELIVERY_7'] = val.DELIVERY_7 if val.DELIVERY_7 else 0
            newRow['DELIVERY_8'] = val.DELIVERY_8 if val.DELIVERY_8 else 0
            newRow['DELIVERY_9'] = val.DELIVERY_9 if val.DELIVERY_9 else 0
            newRow['DELIVERY_10'] = val.DELIVERY_10 if val.DELIVERY_10 else 0
            newRow['DELIVERY_11'] = val.DELIVERY_11 if val.DELIVERY_11 else 0
            newRow['DELIVERY_12'] = val.DELIVERY_12 if val.DELIVERY_12 else 0
            newRow['DELIVERY_13'] = val.DELIVERY_13 if val.DELIVERY_13 else 0
            newRow['DELIVERY_14'] = val.DELIVERY_14 if val.DELIVERY_14 else 0
            newRow['DELIVERY_15'] = val.DELIVERY_15 if val.DELIVERY_15 else 0
            newRow['DELIVERY_16'] = val.DELIVERY_16 if val.DELIVERY_16 else 0
            newRow['DELIVERY_17'] = val.DELIVERY_17 if val.DELIVERY_17 else 0
            newRow['DELIVERY_18'] = val.DELIVERY_18 if val.DELIVERY_18 else 0
            newRow['DELIVERY_19'] = val.DELIVERY_19 if val.DELIVERY_19 else 0
            newRow['DELIVERY_20'] = val.DELIVERY_20 if val.DELIVERY_20 else 0
            newRow['DELIVERY_21'] = val.DELIVERY_21 if val.DELIVERY_21 else 0
            newRow['DELIVERY_22'] = val.DELIVERY_22 if val.DELIVERY_22 else 0
            newRow['DELIVERY_23'] = val.DELIVERY_23 if val.DELIVERY_23 else 0
            newRow['DELIVERY_24'] = val.DELIVERY_24 if val.DELIVERY_24 else 0
            newRow['DELIVERY_25'] = val.DELIVERY_25 if val.DELIVERY_25 else 0
            newRow['DELIVERY_26'] = val.DELIVERY_26 if val.DELIVERY_26 else 0
            newRow['DELIVERY_27'] = val.DELIVERY_27 if val.DELIVERY_27 else 0
            newRow['DELIVERY_28'] = val.DELIVERY_28 if val.DELIVERY_28 else 0
            newRow['DELIVERY_29'] = val.DELIVERY_29 if val.DELIVERY_29 else 0
            newRow['DELIVERY_30'] = val.DELIVERY_30 if val.DELIVERY_30 else 0
            newRow['DELIVERY_31'] = val.DELIVERY_31 if val.DELIVERY_31 else 0
            newRow['DELIVERY_32'] = val.DELIVERY_32 if val.DELIVERY_32 else 0
            newRow['DELIVERY_33'] = val.DELIVERY_33 if val.DELIVERY_33 else 0
            newRow['DELIVERY_34'] = val.DELIVERY_34 if val.DELIVERY_34 else 0
            newRow['DELIVERY_35'] = val.DELIVERY_35 if val.DELIVERY_35 else 0
            newRow['DELIVERY_36'] = val.DELIVERY_36 if val.DELIVERY_36 else 0
            newRow['DELIVERY_37'] = val.DELIVERY_37 if val.DELIVERY_37 else 0
            newRow['DELIVERY_38'] = val.DELIVERY_38 if val.DELIVERY_38 else 0
            newRow['DELIVERY_39'] = val.DELIVERY_39 if val.DELIVERY_39 else 0
            newRow['DELIVERY_40'] = val.DELIVERY_40 if val.DELIVERY_40 else 0
            newRow['DELIVERY_41'] = val.DELIVERY_41 if val.DELIVERY_41 else 0
            newRow['DELIVERY_42'] = val.DELIVERY_42 if val.DELIVERY_42 else 0
            newRow['DELIVERY_43'] = val.DELIVERY_43 if val.DELIVERY_43 else 0
            newRow['DELIVERY_44'] = val.DELIVERY_44 if val.DELIVERY_44 else 0
            newRow['DELIVERY_45'] = val.DELIVERY_45 if val.DELIVERY_45 else 0
            newRow['DELIVERY_46'] = val.DELIVERY_46 if val.DELIVERY_46 else 0
            newRow['DELIVERY_47'] = val.DELIVERY_47 if val.DELIVERY_47 else 0
            newRow['DELIVERY_48'] = val.DELIVERY_48 if val.DELIVERY_48 else 0
            newRow['DELIVERY_49'] = val.DELIVERY_49 if val.DELIVERY_49 else 0
            newRow['DELIVERY_50'] = val.DELIVERY_50 if val.DELIVERY_50 else 0
            newRow['DELIVERY_51'] = val.DELIVERY_51 if val.DELIVERY_51 else 0
            newRow['DELIVERY_52'] = val.DELIVERY_52 if val.DELIVERY_52 else 0
            newRow['QTEREV_ID'] = val.QTEREV_ID
            newRow['QTEREV_RECORD_ID'] = val.QTEREV_RECORD_ID
        get_parts_item_delivery_insert.Save()
    return True

def fpm_quote_doc():
    Trace.Write('FPM QUOTE CREATION __DOC')
    _insert_subtotal_by_offerring_quote_table()
    _insert_item_level_parts()
    _insert_parts_delivery()
    if Quote.GetCustomField('QT_OD_DELIVERY_SERVICE').Content == "YES":
        fpm_delivery = 1 
    else:
        fpm_delivery = 0
    saqdoc_output_insert="""INSERT SAQDOC (
                            QUOTE_DOCUMENT_RECORD_ID,
                            DOCUMENT_ID,
                            DOCUMENT_NAME,
                            DOCUMENT_PATH,
                            QUOTE_ID,
                            QUOTE_NAME,
                            QUOTE_RECORD_ID,
                            LANGUAGE_ID,
                            LANGUAGE_NAME,
                            LANGUAGE_RECORD_ID,
                            CPQTABLEENTRYADDEDBY,
                            CPQTABLEENTRYDATEADDED,
                            CpqTableEntryModifiedBy,
                            CpqTableEntryDateModified,
                            STATUS,
                            QTEREV_ID,
                            QTEREV_RECORD_ID,
                            PRTLST_INCLUDED,
                            ITEM_INCLUDED,
                            DVYSCH_INCLUDED
                            )SELECT
                            CONVERT(VARCHAR(4000),NEWID()) as QUOTE_DOCUMENT_RECORD_ID,
                            '{doc_id}' AS DOCUMENT_ID,
                            '{doc_name}' AS DOCUMENT_NAME,
                            '' AS DOCUMENT_PATH,
                            '{quoteid}' AS QUOTE_ID,
                            '{quotename}' AS QUOTE_NAME,
                            '{quoterecid}' AS QUOTE_RECORD_ID,
                            'EN' AS LANGUAGE_ID,
                            'English' AS LANGUAGE_NAME,
                            MALANG.LANGUAGE_RECORD_ID AS LANGUAGE_RECORD_ID,
                            '{UserName}' as CPQTABLEENTRYADDEDBY,
                            '{dateadded}' as CPQTABLEENTRYDATEADDED,
                            '{UserId}' as CpqTableEntryModifiedBy,
                            '{date}' as CpqTableEntryDateModified,
                            'PENDING' as STATUS,
                            '{qt_revid}' as QTEREV_ID,
                            '{qt_rev_rec_id}' as QTEREV_RECORD_ID,
                            1,
                            1,
                            {fpm_delivery}
                            FROM MALANG (NOLOCK) WHERE MALANG.LANGUAGE_NAME = 'English'""".format(doc_id='Pending',doc_name='',quoteid=get_quote_details.QUOTE_ID,quotename=get_quote_details.QUOTE_NAME,quoterecid=contract_quote_record_id,qt_revid= get_quote_details.QTEREV_ID,qt_rev_rec_id = quote_revision_record_id,fpm_delivery=fpm_delivery,UserName=UserName,dateadded=datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S %p"),UserId=UserId,date=datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S %p"))
            #Log.Info(qtqdoc)
    Sql.RunQuery(saqdoc_output_insert)
    if Quote.GetCustomField('QT_OD_DELIVERY_SERVICE').Content == "YES":
        gen_doc = Quote.GenerateDocument('AMAT_FPM_QUOTE', GenDocFormat.PDF)
        fileName = Quote.GetLatestGeneratedDocumentFileName()
        GDB = Quote.GetLatestGeneratedDocumentInBytes()
        List = Quote.GetGeneratedDocumentList('AMAT_FPM_QUOTE')
    else:
        gen_doc = Quote.GenerateDocument('Amat FPM Z0110', GenDocFormat.PDF)
        fileName = Quote.GetLatestGeneratedDocumentFileName()
        GDB = Quote.GetLatestGeneratedDocumentInBytes()
        List = Quote.GetGeneratedDocumentList('Amat FPM Z0110')
    for doc in List:
        doc_id = doc.Id
        doc_name = doc.FileName
        if fileName==doc_name:
            quote_id = gettoolquote.QUOTE_ID
            #added_by = audit_fields.USERNAME
            #modified_by = audit_fields.CpqTableEntryModifiedBy
            #modified_date = audit_fields.CpqTableEntryDateModified
            guid = str(Guid.NewGuid()).upper()
            qt_rec_id = contract_quote_record_id
            date_added = doc.DateCreated
            update_query = """UPDATE SAQDOC SET DOCUMENT_ID = '{docid}', DOCUMENT_NAME = '{docname}', STATUS = 'ACQUIRED' WHERE DOCUMENT_ID = 'Pending' AND SAQDOC.LANGUAGE_ID = 'EN' AND STATUS = 'PENDING' AND QUOTE_RECORD_ID = '{recid}' AND QTEREV_RECORD_ID = '{quote_revision_record_id}'""".format(recid=contract_quote_record_id,docid=doc_id,docname=doc_name,quote_revision_record_id=quote_revision_record_id)
            Sql.RunQuery(update_query)
    
        #Quote.GetCustomField('tot_est').Content = str(get_quotetotal.est_val)
    return True
try:
    action_type = Param.LOAD
except:
    action_type = ''



try:
    parts_list = Param.parts_list
except:
    parts_list = ''
try:
    billing_matrix = Param.billing_matrix
except:
    billing_matrix = ''
try:
    delivery_schedule = Param.delivery_schedule
except:
    delivery_schedule = ''
try:
    parts_list_include = Param.parts_list_include
except:
    parts_list_include = ''
try:
    include_part_delivery = Param.include_part_delivery
except:
    include_part_delivery = ''
    
Trace.Write("parts_list---"+str(parts_list)+"--billing_matrix---inside--"+str(billing_matrix)+'----'+str(parts_list_include)+'--include_part_delivery---'+str(include_part_delivery))

if str(parts_list) == 'True' and str(billing_matrix) == 'True':
    Quote.GetCustomField('INCLUDE_ITEMS').Content = 'YES'
    #Trace.Write('531------')
    Quote.GetCustomField('Billing_Matrix').Content = 'YES'
    ApiResponse = ApiResponseFactory.JsonResponse(insert_bill_doc(parts_list,billing_matrix))
elif str(billing_matrix) == 'True':
    #Trace.Write('531------')
    Quote.GetCustomField('Billing_Matrix').Content = 'YES'
    Quote.GetCustomField('INCLUDE_ITEMS').Content = 'YES'
    ApiResponse = ApiResponseFactory.JsonResponse(insert_spare_doc(parts_list))
elif str(parts_list_include) == 'True' and str(parts_list) == 'True':
    Quote.GetCustomField('INCLUDE_ITEMS').Content = 'YES'
    Quote.GetCustomField('ITEM_DELIVERY_SCHEDULE').Content = 'YES'
    Quote.GetCustomField('PARTS_DELIVERY_SCHEDULE').Content = 'YES'
    ApiResponse = ApiResponseFactory.JsonResponse(fpm_quote_doc())
elif str(include_part_delivery) == 'True':
    Quote.GetCustomField('INCLUDE_ITEMS').Content = 'YES'
    Quote.GetCustomField('PARTS_DELIVERY_SCHEDULE').Content = 'YES'
    
    ApiResponse = ApiResponseFactory.JsonResponse(fpm_quote_doc())
elif str(parts_list_include) == 'True' and str(parts_list) == 'True' and include_part_delivery == 'True':
    Quote.GetCustomField('INCLUDE_ITEMS').Content = 'YES'
    Quote.GetCustomField('ITEM_DELIVERY_SCHEDULE').Content = 'YES'
    Quote.GetCustomField('PARTS_DELIVERY_SCHEDULE').Content = 'YES'
    ApiResponse = ApiResponseFactory.JsonResponse(fpm_quote_doc())
if action_type == "DOCUMENT":
    ApiResponse = ApiResponseFactory.JsonResponse(language_select())