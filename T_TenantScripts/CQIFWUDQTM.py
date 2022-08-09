#========================================================================================================#================================
#   __script_name : CQIFWUDQTM.PY(SIT)
#   __script_description : THIS SCRIPT USED TO UPDATE QUOTE ITEMS AND QUOTE LINE ITEMS 
#   __primary_author__ : WASIM
#   __create_date :24-08-2021
#   Â© BOSTON HARBOR TECHNOLOGY LLC - ALL RIGHTS RESERVED
# ==========================================================================================================================================

import datetime
#from CPQScripts.GlobalScripts.APPS.CONTRACTQUOTES.SCRIPTS.CQSTATUSBR import Param
import Webcom.Configurator.Scripting.Test.TestProduct
import sys
import re
import System.Net
#import SYCNGEGUID as CPQID
from SYDATABASE import SQL
from System import Convert
import re
import datetime
Sql = SQL()
ScriptExecutor = ScriptExecutor
from System.Text.Encoding import UTF8

def quote_items_pricing(Qt_id, service_ids=[]):
    where_condition = ""	
    pricing_offering = ('Z0046','Z0100','Z0116','Z0117','Z0123')#312
    get_rev_rec_id = Sql.GetFirst("SELECT QTEREV_RECORD_ID,QUOTE_CURRENCY,MASTER_TABLE_QUOTE_RECORD_ID FROM SAQTMT where QUOTE_ID = '{}'".format(Qt_id))
    contract_quote_record_id = get_rev_rec_id.MASTER_TABLE_QUOTE_RECORD_ID
    contract_quote_revision_record_id = get_rev_rec_id.QTEREV_RECORD_ID
    get_exch_rate = Sql.GetFirst("SELECT * FROM SAQTRV where QUOTE_ID = '{}' AND QUOTE_REVISION_RECORD_ID = '{}'".format(Qt_id,contract_quote_revision_record_id))
    
    get_exch_rate = get_exch_rate.EXCHANGE_RATE
    ##updating saqico for cpq pricing product
    if manual_pricing  != 'True':
        #312 commented starts
        # Sql.RunQuery("""UPDATE SAQICO  
        #             SET 
        #             TAXVDC = (TNTVDC * TAXVTP)/100,
        #             TAXVGC = (TNTVGC * TAXVTP)/100
        #             FROM SAQICO (NOLOCK) 
        #             WHERE SAQICO.QUOTE_RECORD_ID = '{QuoteRecordId}' AND SAQICO.QTEREV_RECORD_ID = '{QuoteRevisionRecordId}' AND SAQICO.SERVICE_ID in {pricing_offering}""".format(QuoteRecordId= contract_quote_record_id ,QuoteRevisionRecordId =contract_quote_revision_record_id,pricing_offering=pricing_offering))

        # Sql.RunQuery("""UPDATE SAQICO 
        #             SET TAMTDC = CASE WHEN BILTYP = 'Variable' THEN TENVDC ELSE TNTVDC+ISNULL(TAXVDC,0) END,
        #             TAMTGC = CASE WHEN BILTYP = 'Variable' THEN TENVGC ELSE TNTVGC+ISNULL(TAXVGC,0) END,
        #             STATUS = 'ACQUIRED'
        #             FROM SAQICO (NOLOCK) 
        #             WHERE SAQICO.QUOTE_RECORD_ID = '{QuoteRecordId}' AND SAQICO.QTEREV_RECORD_ID = '{QuoteRevisionRecordId}' AND SAQICO.SERVICE_ID in {pricing_offering}""".format(QuoteRecordId= contract_quote_record_id ,QuoteRevisionRecordId =contract_quote_revision_record_id,pricing_offering=pricing_offering))
        #312 ends
        # Price Bench Marking - Start
        Sql.RunQuery("""UPDATE SAQICO
                SET
                SAQICO.BCHPGC = PRPRBM.ANNUALIZED_BOOKING_PRICE,
                SAQICO.BCHDPT = ((SAQICO.TNTVGC - ISNULL(PRPRBM.ANNUALIZED_BOOKING_PRICE,0))/SAQICO.TNTVGC) * 100
                FROM SAQICO	(NOLOCK)
                JOIN (
                    SELECT SAQICO.CpqTableEntryId, MAX(PRPRBM.CONTRACT_END_DATE) AS CONTRACT_END_DATE, PRPRBM.SERVICE_PRODUCT_NAME,
                            PRPRBM.SERIAL_NUMBER, PRPRBM.EQUIPMENT_NUMBER
                    FROM SAQICO (NOLOCK)
                    JOIN PRPRBM (NOLOCK) ON PRPRBM.EQUIPMENT_NUMBER = RIGHT('000000000000000000' + CONVERT(VARCHAR(18), SAQICO.EQUIPMENT_ID), 18) AND PRPRBM.SERVICE_PRODUCT_NAME = SAQICO.SERVICE_ID AND PRPRBM.SERIAL_NUMBER = RIGHT('000000000000000000' + CONVERT(VARCHAR(18), SAQICO.SERNUM), 18)
                    WHERE SAQICO.QUOTE_RECORD_ID = '{QuoteRecordId}' AND SAQICO.QTEREV_RECORD_ID = '{QuoteRevisionRecordId}'
                    GROUP BY PRPRBM.SERVICE_PRODUCT_NAME, PRPRBM.EQUIPMENT_NUMBER, PRPRBM.SERIAL_NUMBER, SAQICO.CpqTableEntryId
                )AS IQ ON SAQICO.CpqTableEntryId = IQ.CpqTableEntryId
                JOIN PRPRBM (NOLOCK) ON PRPRBM.EQUIPMENT_NUMBER = IQ.EQUIPMENT_NUMBER AND PRPRBM.SERVICE_PRODUCT_NAME = IQ.SERVICE_PRODUCT_NAME AND PRPRBM.SERIAL_NUMBER = IQ.SERIAL_NUMBER AND PRPRBM.CONTRACT_END_DATE = IQ.CONTRACT_END_DATE
                WHERE SAQICO.QUOTE_RECORD_ID = '{QuoteRecordId}' AND SAQICO.QTEREV_RECORD_ID = '{QuoteRevisionRecordId}'					
                """.format(QuoteRecordId=contract_quote_record_id,QuoteRevisionRecordId=contract_quote_revision_record_id))
        
        # Sql.RunQuery("""UPDATE SAQICO
        #         SET
        #         SAQICO.BCHPGC = PRPRBM.ANNUALIZED_BOOKING_PRICE,
        #         SAQICO.BCHDPT = ((SAQICO.TNTVGC - ISNULL(PRPRBM.ANNUALIZED_BOOKING_PRICE,0))/SAQICO.TNTVGC) * 100
        #         FROM SAQICO	(NOLOCK)
        #         JOIN (
        #             SELECT SAQICO.CpqTableEntryId, MAX(PRPRBM.CONTRACT_END_DATE) AS CONTRACT_END_DATE, PRPRBM.SERVICE_PRODUCT_NAME,
        #                     PRPRBM.TOOLCONFG
        #             FROM SAQICO (NOLOCK)
        #             JOIN PRPRBM (NOLOCK) ON PRPRBM.TOOLCONFG = SAQICO.TOLCFG AND PRPRBM.SERVICE_PRODUCT_NAME = SAQICO.SERVICE_ID
        #             WHERE SAQICO.QUOTE_RECORD_ID = '{QuoteRecordId}' AND SAQICO.QTEREV_RECORD_ID = '{QuoteRevisionRecordId}'
        #             GROUP BY PRPRBM.SERVICE_PRODUCT_NAME, PRPRBM.TOOLCONFG, SAQICO.CpqTableEntryId
        #         )AS IQ ON SAQICO.CpqTableEntryId = IQ.CpqTableEntryId
        #         JOIN PRPRBM (NOLOCK) ON PRPRBM.TOOLCONFG = IQ.TOOLCONFG AND PRPRBM.SERVICE_PRODUCT_NAME = IQ.SERVICE_PRODUCT_NAME AND PRPRBM.CONTRACT_END_DATE = IQ.CONTRACT_END_DATE		
        #         WHERE SAQICO.QUOTE_RECORD_ID = '{QuoteRecordId}' AND SAQICO.QTEREV_RECORD_ID = '{QuoteRevisionRecordId}' AND ISNULL(SAQICO.BCHPGC,'')	= ''					
        #         """.format(QuoteRecordId=contract_quote_record_id,QuoteRevisionRecordId=contract_quote_revision_record_id))
        
        Sql.RunQuery("""UPDATE SAQICO
            SET
            SAQICO.BMPPDA = CASE WHEN ISNULL(BCHDPT,0) > ISNULL(BCHDAP,0) THEN 1 ELSE 0 END
            FROM SAQICO	(NOLOCK)			
            WHERE SAQICO.QUOTE_RECORD_ID = '{QuoteRecordId}' AND SAQICO.QTEREV_RECORD_ID = '{QuoteRevisionRecordId}'			
            """.format(QuoteRecordId=contract_quote_record_id,QuoteRevisionRecordId=contract_quote_revision_record_id))

        Log.Info("""+++==== UPDATE SAQICO
                SET
                SAQICO.BCHPGC = PRPRBM.ANNUALIZED_BOOKING_PRICE,
                SAQICO.BCHDPT = ((SAQICO.TNTVGC - ISNULL(PRPRBM.ANNUALIZED_BOOKING_PRICE,0))/SAQICO.TNTVGC) * 100
                FROM SAQICO	(NOLOCK)
                JOIN (
                    SELECT SAQICO.CpqTableEntryId, MAX(PRPRBM.CONTRACT_START_DATE) AS CONTRACT_START_DATE, PRPRBM.SERVICE_PRODUCT_NAME,
                            PRPRBM.TOOLCONFG
                    FROM SAQICO (NOLOCK)
                    JOIN PRPRBM (NOLOCK) ON PRPRBM.TOOLCONFG = SAQICO.TOLCFG AND PRPRBM.SERVICE_PRODUCT_NAME = SAQICO.SERVICE_ID
                    WHERE SAQICO.QUOTE_RECORD_ID = '{QuoteRecordId}' AND SAQICO.QTEREV_RECORD_ID = '{QuoteRevisionRecordId}'
                    GROUP BY PRPRBM.SERVICE_PRODUCT_NAME, PRPRBM.TOOLCONFG, SAQICO.CpqTableEntryId
                )AS IQ ON SAQICO.CpqTableEntryId = IQ.CpqTableEntryId
                JOIN PRPRBM (NOLOCK) ON PRPRBM.TOOLCONFG = IQ.TOOLCONFG AND PRPRBM.SERVICE_PRODUCT_NAME = IQ.SERVICE_PRODUCT_NAME AND PRPRBM.CONTRACT_START_DATE = IQ.CONTRACT_START_DATE		
                WHERE SAQICO.QUOTE_RECORD_ID = '{QuoteRecordId}' AND SAQICO.QTEREV_RECORD_ID = '{QuoteRevisionRecordId}' AND ISNULL(SAQICO.BCHPGC,'')	= ''					
                """.format(QuoteRecordId=contract_quote_record_id,QuoteRevisionRecordId=contract_quote_revision_record_id))
        # Price Bench Marking - End
    # if pricing_offering:
    #     pricing_offering = pricing_offering + ('Z0123',)
    # if manual_pricing != 'True':
    #     where_condition = " AND SAQRIT.SERVICE_ID IN {pricing_offering}".format(pricing_offering =pricing_offering)
    
    if manual_pricing == 'True' and service_ids:
        pricing_offering = "('{}')".format("','".join(service_ids))
    ##updating saqrit
    # #2165
    if (Action == 'ANCILLARY_PRICING' and anc_service_id) or manual_pricing == 'True':
        if manual_pricing != 'True':
            where_condition = " AND SAQRIT.SERVICE_ID IN {pricing_offr}".format(pricing_offr =anc_service_id)
        Sql.RunQuery("""UPDATE SAQRIT 
                        SET NET_VALUE_INGL_CURR = IQ.NET_VALUE_INGL_CURR,
                        NET_VALUE = IQ.NET_VALUE,
                        TAX_AMOUNT_INGL_CURR = IQ.TAX_AMOUNT_INGL_CURR,
                        TAX_AMOUNT = IQ.TAX_AMOUNT,
                        ESTIMATED_VALUE = IQ.ESTIMATED_VALUE,
                        ESTVAL_INGL_CURR = IQ.ESTVAL_INGL_CURR,
                        TOTAL_AMOUNT_INGL_CURR = IQ.TOTAL_AMOUNT_INGL_CURR,
                        TOTAL_AMOUNT = IQ.TOTAL_AMOUNT,
                        TOTAL_MARGIN = IQ.TOTAL_MARGIN,
                        PEREVTPRC_INDT_CURR = CASE WHEN OBJECT_TYPE IN ('EVENT','KIT') THEN (  CASE WHEN BILLING_TYPE='VARIABLE' THEN IQ.ESTIMATED_VALUE ELSE IQ.NET_VALUE END) ELSE NULL END,
                        PEREVTPRC_INGL_CURR = CASE WHEN OBJECT_TYPE IN ('EVENT','KIT') THEN (  CASE WHEN BILLING_TYPE='VARIABLE' THEN IQ.ESTVAL_INGL_CURR ELSE IQ.NET_VALUE_INGL_CURR END) ELSE NULL END,
                        PEREVTCST_INDT_CURR = ISNULL(AICCPE,0) * {get_exch_rate},
                        PEREVTCST_INGL_CURR = ISNULL(AICCPE,0)
                        FROM SAQRIT
                            INNER JOIN (SELECT SAQICO.QUOTE_RECORD_ID, SAQICO.QTEREV_RECORD_ID,SAQICO.SERVICE_ID,SAQICO.GRNBOK,SAQICO.EQUIPMENT_ID,SAQICO.LINE,
                                    SUM(ISNULL(SAQICO.TNTVGC, 0)) as NET_VALUE_INGL_CURR,
                                    SUM(ISNULL(SAQICO.TNTVDC, 0)) as NET_VALUE,
                                    SUM(ISNULL(SAQICO.TAXVGC, 0)) as TAX_AMOUNT_INGL_CURR,
                                    SUM(ISNULL(SAQICO.TAXVDC, 0)) as TAX_AMOUNT,
                                    SUM(ISNULL(SAQICO.TENVDC, 0)) as ESTIMATED_VALUE,
                                    SUM(ISNULL(SAQICO.TENVGC, 0)) as ESTVAL_INGL_CURR,
                                    SUM(ISNULL(SAQICO.TAMTGC, 0)) as TOTAL_AMOUNT_INGL_CURR,
                                    SUM(ISNULL(SAQICO.TAMTDC, 0)) as TOTAL_AMOUNT,
                                    SUM(ISNULL(SAQICO.CNTMGN, 0)) as TOTAL_MARGIN,
                                    SUM(ISNULL(SAQICO.AICCPE, 0)) as AICCPE
                                    FROM SAQICO WHERE SAQICO.QUOTE_RECORD_ID = '{QuoteRecordId}' AND SAQICO.QTEREV_RECORD_ID = '{rev}'  GROUP BY SAQICO.QUOTE_RECORD_ID, SAQICO.QTEREV_RECORD_ID,SAQICO.SERVICE_ID,SAQICO.GRNBOK,SAQICO.EQUIPMENT_ID, SAQICO.LINE
                                    ) IQ ON SAQRIT.QUOTE_RECORD_ID = IQ.QUOTE_RECORD_ID AND SAQRIT.QTEREV_RECORD_ID = IQ.QTEREV_RECORD_ID AND SAQRIT.SERVICE_ID = IQ.SERVICE_ID AND IQ.GRNBOK = SAQRIT.GREENBOOK AND ISNULL(IQ.EQUIPMENT_ID,'') = ISNULL(SAQRIT.EQUIPMENT_ID,'') AND SAQRIT.LINE = IQ.LINE
                                WHERE SAQRIT.QUOTE_RECORD_ID = '{QuoteRecordId}' AND SAQRIT.QTEREV_RECORD_ID='{rev}' {where_condition}  """.format( QuoteRecordId= contract_quote_record_id ,rev =contract_quote_revision_record_id,where_condition=where_condition, get_exch_rate = get_exch_rate if get_exch_rate else 1))
        
    ##year field update for cpq pricing
    #if manual_pricing != 'True':
    
        
    Sql.RunQuery("""UPDATE SAQRIT 
    SET YEAR_1 = CASE WHEN SAQRIT.BILLING_TYPE = 'Variable' THEN SAQICO.TENVDC ELSE SAQICO.TNTVDC END,
    YEAR_1_INGL_CURR =  CASE WHEN SAQRIT.BILLING_TYPE = 'Variable' THEN SAQICO.TENVGC ELSE SAQICO.TNTVGC END 
    FROM SAQRIT (NOLOCK) 
        INNER JOIN SAQICO ON SAQRIT.QUOTE_RECORD_ID = SAQICO.QUOTE_RECORD_ID AND SAQRIT.QTEREV_RECORD_ID = SAQICO.QTEREV_RECORD_ID AND  SAQRIT.SERVICE_ID = SAQICO.SERVICE_ID AND SAQRIT.GREENBOOK = SAQICO.GRNBOK AND CNTYER = 'YEAR 1'  AND SAQRIT.LINE = SAQICO.LINE
    WHERE  SAQRIT.QUOTE_RECORD_ID = '{quote_rec_id}' AND SAQRIT.QTEREV_RECORD_ID = '{quote_revision_rec_id}' AND SAQRIT.SERVICE_ID IN {pricing_offering} AND CNTYER = 'YEAR 1' """.format(quote_rec_id = contract_quote_record_id ,quote_revision_rec_id = contract_quote_revision_record_id,pricing_offering=pricing_offering  ))

    Sql.RunQuery("""UPDATE SAQRIT 
    SET YEAR_2 = CASE WHEN SAQRIT.BILLING_TYPE = 'Variable' THEN SAQICO.TENVDC ELSE SAQICO.TNTVDC END,
    YEAR_2_INGL_CURR =  CASE WHEN SAQRIT.BILLING_TYPE = 'Variable' THEN SAQICO.TENVGC ELSE SAQICO.TNTVGC END 
    FROM SAQRIT (NOLOCK) 
        INNER JOIN SAQICO ON SAQRIT.QUOTE_RECORD_ID = SAQICO.QUOTE_RECORD_ID AND SAQRIT.QTEREV_RECORD_ID = SAQICO.QTEREV_RECORD_ID AND  SAQRIT.SERVICE_ID = SAQICO.SERVICE_ID AND SAQRIT.GREENBOOK = SAQICO.GRNBOK AND CNTYER = 'YEAR 2'  AND SAQRIT.LINE = SAQICO.LINE
    WHERE  SAQRIT.QUOTE_RECORD_ID = '{quote_rec_id}' AND SAQRIT.QTEREV_RECORD_ID = '{quote_revision_rec_id}' AND SAQRIT.SERVICE_ID IN {pricing_offering} AND CNTYER = 'YEAR 2' """.format(quote_rec_id = contract_quote_record_id ,quote_revision_rec_id = contract_quote_revision_record_id ,pricing_offering=pricing_offering ))

    Sql.RunQuery("""UPDATE SAQRIT 
    SET YEAR_3 = CASE WHEN SAQRIT.BILLING_TYPE = 'Variable' THEN SAQICO.TENVDC ELSE SAQICO.TNTVDC END,
    YEAR_3_INGL_CURR =  CASE WHEN SAQRIT.BILLING_TYPE = 'Variable' THEN SAQICO.TENVGC ELSE SAQICO.TNTVGC END 
    FROM SAQRIT (NOLOCK) 
        INNER JOIN SAQICO ON SAQRIT.QUOTE_RECORD_ID = SAQICO.QUOTE_RECORD_ID AND SAQRIT.QTEREV_RECORD_ID = SAQICO.QTEREV_RECORD_ID AND  SAQRIT.SERVICE_ID = SAQICO.SERVICE_ID AND SAQRIT.GREENBOOK = SAQICO.GRNBOK AND CNTYER = 'YEAR 3'  AND SAQRIT.LINE = SAQICO.LINE
    WHERE  SAQRIT.QUOTE_RECORD_ID = '{quote_rec_id}' AND SAQRIT.QTEREV_RECORD_ID = '{quote_revision_rec_id}' AND SAQRIT.SERVICE_ID IN {pricing_offering} AND CNTYER = 'YEAR 3' """.format(quote_rec_id = contract_quote_record_id ,quote_revision_rec_id = contract_quote_revision_record_id,pricing_offering=pricing_offering  ))

    Sql.RunQuery("""UPDATE SAQRIT 
    SET YEAR_4 = CASE WHEN SAQRIT.BILLING_TYPE = 'Variable' THEN SAQICO.TENVDC ELSE SAQICO.TNTVDC END,
    YEAR_4_INGL_CURR =  CASE WHEN SAQRIT.BILLING_TYPE = 'Variable' THEN SAQICO.TENVGC ELSE SAQICO.TNTVGC END 
    FROM SAQRIT (NOLOCK) 
        INNER JOIN SAQICO ON SAQRIT.QUOTE_RECORD_ID = SAQICO.QUOTE_RECORD_ID AND SAQRIT.QTEREV_RECORD_ID = SAQICO.QTEREV_RECORD_ID AND  SAQRIT.SERVICE_ID = SAQICO.SERVICE_ID AND SAQRIT.GREENBOOK = SAQICO.GRNBOK AND CNTYER = 'YEAR 4'  AND SAQRIT.LINE = SAQICO.LINE
    WHERE  SAQRIT.QUOTE_RECORD_ID = '{quote_rec_id}' AND SAQRIT.QTEREV_RECORD_ID = '{quote_revision_rec_id}' AND SAQRIT.SERVICE_ID IN {pricing_offering} AND CNTYER = 'YEAR 4' """.format(quote_rec_id = contract_quote_record_id ,quote_revision_rec_id = contract_quote_revision_record_id ,pricing_offering=pricing_offering ))

    Sql.RunQuery("""UPDATE SAQRIT 
    SET YEAR_5 = CASE WHEN SAQRIT.BILLING_TYPE = 'Variable' THEN SAQICO.TENVDC ELSE SAQICO.TNTVDC END,
    YEAR_5_INGL_CURR =  CASE WHEN SAQRIT.BILLING_TYPE = 'Variable' THEN SAQICO.TENVGC ELSE SAQICO.TNTVGC END 
    FROM SAQRIT (NOLOCK) 
        INNER JOIN SAQICO ON SAQRIT.QUOTE_RECORD_ID = SAQICO.QUOTE_RECORD_ID AND SAQRIT.QTEREV_RECORD_ID = SAQICO.QTEREV_RECORD_ID AND  SAQRIT.SERVICE_ID = SAQICO.SERVICE_ID AND SAQRIT.GREENBOOK = SAQICO.GRNBOK AND CNTYER = 'YEAR 5'  AND SAQRIT.LINE = SAQICO.LINE
    WHERE  SAQRIT.QUOTE_RECORD_ID = '{quote_rec_id}' AND SAQRIT.QTEREV_RECORD_ID = '{quote_revision_rec_id}' AND SAQRIT.SERVICE_ID IN {pricing_offering} AND CNTYER = 'YEAR 5' """.format(quote_rec_id = contract_quote_record_id ,quote_revision_rec_id = contract_quote_revision_record_id,pricing_offering=pricing_offering  ))
    if manual_pricing != 'True':
        Sql.RunQuery("UPDATE SAQRIT SET STATUS = 'ACQUIRED' WHERE SAQRIT.QUOTE_RECORD_ID = '{quote_rec_id}' AND SAQRIT.QTEREV_RECORD_ID = '{quote_revision_rec_id}' AND SAQRIT.SERVICE_ID IN {pricing_offering}".format(quote_rec_id = contract_quote_record_id ,quote_revision_rec_id = contract_quote_revision_record_id,pricing_offering=pricing_offering  ))
    ##decimal rounding for SAQICO
    #global currency
    Sql.RunQuery("""UPDATE SAQICO 
                    SET CNTMGN = IQ.CNTMGN,
                        INMP01 = IQ.INMP01,
                        INMP02 = IQ.INMP02,
                        FNMDPR = IQ.FNMDPR,
                        MTGPRC = IQ.MTGPRC,
                        MSLPRC = IQ.MSLPRC,
                        MBDPRC = IQ.MBDPRC,
                        MCLPRC = IQ.MCLPRC,
                        TRGPRC = IQ.TRGPRC,
                        SLSPRC = IQ.SLSPRC,
                        BDVPRC = IQ.BDVPRC,
                        CELPRC = IQ.CELPRC,
                        USRPRC = IQ.USRPRC,
                        CNTPRC = IQ.CNTPRC,
                        CNTCST = IQ.CNTCST,
                        SPCTPR = IQ.SPCTPR,
                        SPCTCS = IQ.SPCTCS,
                        TNTVGC = IQ.TNTVGC,
                        TNTMGC = IQ.TNTMGC,
                        TENVGC = IQ.TENVGC,
                        TAXVGC = IQ.TAXVGC,
                        TAMTGC = IQ.TAMTGC,
                        TNTVDC = IQ.TNTVDC,
                        TAXVDC = IQ.TAXVDC,
                        TAMTDC = IQ.TAMTDC
                    FROM SAQICO
                        INNER JOIN 
                            (SELECT SAQICO.QUOTE_RECORD_ID, SAQICO.QTEREV_RECORD_ID,SAQICO.SERVICE_ID,SAQICO.CpqTableEntryId ,
                            ROUND(ISNULL(CNTMGN,0),CONVERT(NUMERIC,ISNULL(PRCURR.ROUNDING_DECIMAL_PLACES,5)) ) as CNTMGN,
                            ROUND(ISNULL(INMP01,0),CONVERT(NUMERIC,ISNULL(PRCURR.ROUNDING_DECIMAL_PLACES,5)) ) as INMP01,
                            CASE WHEN INMP02 <> 0 THEN ROUND(INMP02,CONVERT(NUMERIC,ISNULL(PRCURR.ROUNDING_DECIMAL_PLACES,5)) ) else INMP02 end as INMP02,
                            ROUND(ISNULL(FNMDPR,0),CONVERT(NUMERIC,ISNULL(PRCURR.ROUNDING_DECIMAL_PLACES,5)) ) as FNMDPR,
                            CASE WHEN MTGPRC <> 0 THEN ROUND(MTGPRC,CONVERT(NUMERIC,ISNULL(PRCURR.ROUNDING_DECIMAL_PLACES,5)) ) else MTGPRC end as MTGPRC,
                            CASE WHEN MSLPRC <> 0 THEN ROUND(MSLPRC,CONVERT(NUMERIC,ISNULL(PRCURR.ROUNDING_DECIMAL_PLACES,5)) ) else MSLPRC end as MSLPRC,
                            ROUND(ISNULL(MBDPRC,0),CONVERT(NUMERIC,ISNULL(PRCURR.ROUNDING_DECIMAL_PLACES,5)) ) as MBDPRC,
                            CASE WHEN MCLPRC <> 0 THEN ROUND(MCLPRC,CONVERT(NUMERIC,ISNULL(PRCURR.ROUNDING_DECIMAL_PLACES,5)) ) else MCLPRC end as MCLPRC,
                            ROUND(ISNULL(TRGPRC,0),CONVERT(NUMERIC,ISNULL(PRCURR.ROUNDING_DECIMAL_PLACES,5)) ) as TRGPRC,
                            ROUND(ISNULL(SLSPRC,0),CONVERT(NUMERIC,ISNULL(PRCURR.ROUNDING_DECIMAL_PLACES,5)) ) as SLSPRC,
                            ROUND(ISNULL(BDVPRC,0),CONVERT(NUMERIC,ISNULL(PRCURR.ROUNDING_DECIMAL_PLACES,5)) ) as BDVPRC,
                            ROUND(ISNULL(CELPRC,0),CONVERT(NUMERIC,ISNULL(PRCURR.ROUNDING_DECIMAL_PLACES,5)) ) as CELPRC,
                            ROUND(ISNULL(USRPRC,0),CONVERT(NUMERIC,ISNULL(PRCURR.ROUNDING_DECIMAL_PLACES,5)) ) as USRPRC,
                            ROUND(ISNULL(CNTCST,0),CONVERT(NUMERIC,ISNULL(PRCURR.ROUNDING_DECIMAL_PLACES,5)) ) as CNTCST,
                            ROUND(ISNULL(CNTPRC,0),CONVERT(NUMERIC,ISNULL(PRCURR.ROUNDING_DECIMAL_PLACES,5)) ) as CNTPRC,
                            ROUND(ISNULL(SPCTPR,0),CONVERT(NUMERIC,ISNULL(PRCURR.ROUNDING_DECIMAL_PLACES,5)) ) as SPCTPR,
                            ROUND(ISNULL(SPCTCS,0),CONVERT(NUMERIC,ISNULL(PRCURR.ROUNDING_DECIMAL_PLACES,5)) ) as SPCTCS,
                            ROUND(ISNULL(TNTVGC,0),CONVERT(NUMERIC,ISNULL(PRCURR.ROUNDING_DECIMAL_PLACES,5)) ) as TNTVGC,
                            ROUND(ISNULL(TNTMGC,0),CONVERT(NUMERIC,ISNULL(PRCURR.ROUNDING_DECIMAL_PLACES,5)) ) as TNTMGC,
                            ROUND(ISNULL(TENVGC,0),CONVERT(NUMERIC,ISNULL(PRCURR.ROUNDING_DECIMAL_PLACES,5)) ) as TENVGC,
                            ROUND(ISNULL(TAXVGC,0),CONVERT(NUMERIC,ISNULL(PRCURR.ROUNDING_DECIMAL_PLACES,5)) ) as TAXVGC,
                            ROUND(ISNULL(TAMTGC,0),CONVERT(NUMERIC,ISNULL(PRCURR.ROUNDING_DECIMAL_PLACES,5)) ) as TAMTGC,
                            ROUND(ISNULL(TNTVDC,0),CONVERT(NUMERIC,ISNULL(PRCURR.ROUNDING_DECIMAL_PLACES,5)) ) as TNTVDC,
                            ROUND(ISNULL(TAXVDC,0),CONVERT(NUMERIC,ISNULL(PRCURR.ROUNDING_DECIMAL_PLACES,5)) ) as TAXVDC,
                            ROUND(ISNULL(TAMTDC,0),CONVERT(NUMERIC,ISNULL(PRCURR.ROUNDING_DECIMAL_PLACES,5)) ) as TAMTDC
                            FROM SAQICO 
                                INNER JOIN PRCURR ON GLOBAL_CURRENCY_RECORD_ID = CURRENCY_RECORD_ID AND CURRENCY = GLOBAL_CURRENCY
                                WHERE SAQICO.QUOTE_RECORD_ID = '{QuoteRecordId}' AND SAQICO.QTEREV_RECORD_ID = '{rev}' 
                            ) IQ ON SAQICO.QUOTE_RECORD_ID = IQ.QUOTE_RECORD_ID AND SAQICO.QTEREV_RECORD_ID = IQ.QTEREV_RECORD_ID AND SAQICO.SERVICE_ID = IQ.SERVICE_ID AND SAQICO.CpqTableEntryId = IQ.CpqTableEntryId 
                        WHERE SAQICO.QUOTE_RECORD_ID = '{QuoteRecordId}' AND SAQICO.QTEREV_RECORD_ID='{rev}' """.format( QuoteRecordId= contract_quote_record_id ,rev =contract_quote_revision_record_id))
    ##deciaml rounding for SAQRIT
    ##global currency
    Sql.RunQuery("""UPDATE SAQRIT 
                    SET TAX_AMOUNT_INGL_CURR = IQ.TAX_AMOUNT_INGL_CURR,
                        NET_PRICE_INGL_CURR = IQ.NET_PRICE_INGL_CURR,
                        COMVAL_INGL_CURR = IQ.COMVAL_INGL_CURR,
                        ESTVAL_INGL_CURR = IQ.ESTVAL_INGL_CURR,
                        NET_VALUE_INGL_CURR = IQ.NET_VALUE_INGL_CURR,
                        UNIT_PRICE_INGL_CURR = IQ.UNIT_PRICE_INGL_CURR,
                        YEAR_1_INGL_CURR = IQ.YEAR_1_INGL_CURR,
                        YEAR_2_INGL_CURR = IQ.YEAR_2_INGL_CURR,
                        YEAR_3_INGL_CURR = IQ.YEAR_3_INGL_CURR,
                        YEAR_4_INGL_CURR = IQ.YEAR_4_INGL_CURR,
                        YEAR_5_INGL_CURR = IQ.YEAR_5_INGL_CURR,
                        TOTAL_AMOUNT_INGL_CURR = IQ.TOTAL_AMOUNT_INGL_CURR,
                        PEREVTCST_INGL_CURR = IQ.PEREVTCST_INGL_CURR,
                        PEREVTPRC_INGL_CURR = IQ.PEREVTPRC_INGL_CURR
                    FROM SAQRIT
                        INNER JOIN 
                            (SELECT SAQRIT.QUOTE_RECORD_ID, SAQRIT.QTEREV_RECORD_ID,SAQRIT.SERVICE_ID,SAQRIT.LINE,SAQRIT.CpqTableEntryId,
                            ROUND(ISNULL(TAX_AMOUNT_INGL_CURR,0),CONVERT(NUMERIC,ISNULL(PRCURR.ROUNDING_DECIMAL_PLACES,5)) ) as TAX_AMOUNT_INGL_CURR,
                            ROUND(ISNULL(NET_PRICE_INGL_CURR,0),CONVERT(NUMERIC,ISNULL(PRCURR.ROUNDING_DECIMAL_PLACES,5)) ) as NET_PRICE_INGL_CURR,
                            ROUND(ISNULL(COMVAL_INGL_CURR,0),CONVERT(NUMERIC,ISNULL(PRCURR.ROUNDING_DECIMAL_PLACES,5)) ) as COMVAL_INGL_CURR,
                            ROUND(ISNULL(ESTVAL_INGL_CURR,0),CONVERT(NUMERIC,ISNULL(PRCURR.ROUNDING_DECIMAL_PLACES,5)) ) as ESTVAL_INGL_CURR,
                            ROUND(ISNULL(NET_VALUE_INGL_CURR,0),CONVERT(NUMERIC,ISNULL(PRCURR.ROUNDING_DECIMAL_PLACES,5)) ) as NET_VALUE_INGL_CURR,
                            ROUND(ISNULL(UNIT_PRICE_INGL_CURR,0),CONVERT(NUMERIC,ISNULL(PRCURR.ROUNDING_DECIMAL_PLACES,5)) ) as UNIT_PRICE_INGL_CURR,
                            ROUND(ISNULL(YEAR_1_INGL_CURR,0),CONVERT(NUMERIC,ISNULL(PRCURR.ROUNDING_DECIMAL_PLACES,5)) ) as YEAR_1_INGL_CURR,
                            ROUND(ISNULL(YEAR_2_INGL_CURR,0),CONVERT(NUMERIC,ISNULL(PRCURR.ROUNDING_DECIMAL_PLACES,5)) ) as YEAR_2_INGL_CURR,
                            ROUND(ISNULL(YEAR_3_INGL_CURR,0),CONVERT(NUMERIC,ISNULL(PRCURR.ROUNDING_DECIMAL_PLACES,5)) ) as YEAR_3_INGL_CURR,
                            ROUND(ISNULL(YEAR_4_INGL_CURR,0),CONVERT(NUMERIC,ISNULL(PRCURR.ROUNDING_DECIMAL_PLACES,5)) ) as YEAR_4_INGL_CURR,
                            ROUND(ISNULL(YEAR_5_INGL_CURR,0),CONVERT(NUMERIC,ISNULL(PRCURR.ROUNDING_DECIMAL_PLACES,5)) ) as YEAR_5_INGL_CURR,
                            ROUND(ISNULL(TOTAL_AMOUNT_INGL_CURR,0),CONVERT(NUMERIC,ISNULL(PRCURR.ROUNDING_DECIMAL_PLACES,5)) ) as TOTAL_AMOUNT_INGL_CURR,
                            ROUND(ISNULL(PEREVTCST_INGL_CURR,0),CONVERT(NUMERIC,ISNULL(PRCURR.ROUNDING_DECIMAL_PLACES,5)) ) as PEREVTCST_INGL_CURR,
                            ROUND(ISNULL(PEREVTPRC_INGL_CURR,0),CONVERT(NUMERIC,ISNULL(PRCURR.ROUNDING_DECIMAL_PLACES,5)) ) as PEREVTPRC_INGL_CURR
                            FROM SAQRIT 
                                INNER JOIN PRCURR ON GLOBAL_CURRENCY_RECORD_ID = CURRENCY_RECORD_ID AND CURRENCY = GLOBAL_CURRENCY
                                WHERE SAQRIT.QUOTE_RECORD_ID = '{QuoteRecordId}' AND SAQRIT.QTEREV_RECORD_ID = '{rev}' 
                            ) IQ ON SAQRIT.QUOTE_RECORD_ID = IQ.QUOTE_RECORD_ID AND SAQRIT.QTEREV_RECORD_ID = IQ.QTEREV_RECORD_ID AND SAQRIT.SERVICE_ID = IQ.SERVICE_ID AND SAQRIT.LINE = IQ.LINE AND SAQRIT.CpqTableEntryId = IQ.CpqTableEntryId
                        WHERE SAQRIT.QUOTE_RECORD_ID = '{QuoteRecordId}' AND SAQRIT.QTEREV_RECORD_ID='{rev}' """.format( QuoteRecordId= contract_quote_record_id ,rev =contract_quote_revision_record_id))
    ##doc currency
    Sql.RunQuery("""UPDATE SAQRIT 
                    SET TAX_AMOUNT = IQ.TAX_AMOUNT,
                        NET_PRICE = IQ.NET_PRICE,
                        COMMITTED_VALUE = IQ.COMMITTED_VALUE,
                        ESTIMATED_VALUE = IQ.ESTIMATED_VALUE,
                        NET_VALUE = IQ.NET_VALUE,
                        UNIT_PRICE = IQ.UNIT_PRICE,
                        YEAR_1 = IQ.YEAR_1,
                        YEAR_2 = IQ.YEAR_2,
                        YEAR_3 = IQ.YEAR_3,
                        YEAR_4 = IQ.YEAR_4,
                        YEAR_5 = IQ.YEAR_5,
                        TOTAL_AMOUNT = IQ.TOTAL_AMOUNT,
                        PEREVTCST_INDT_CURR = IQ.PEREVTCST_INDT_CURR,
                        PEREVTPRC_INDT_CURR = IQ.PEREVTPRC_INDT_CURR
                    FROM SAQRIT (NOLOCK)
                        INNER JOIN 
                            (SELECT SAQRIT.QUOTE_RECORD_ID, SAQRIT.QTEREV_RECORD_ID,SAQRIT.SERVICE_ID,SAQRIT.LINE,SAQRIT.CpqTableEntryId,
                            ROUND(ISNULL(TAX_AMOUNT,0),CONVERT(NUMERIC,ISNULL(PRCURR.ROUNDING_DECIMAL_PLACES,5)) ) as TAX_AMOUNT,
                            ROUND(ISNULL(NET_PRICE,0),CONVERT(NUMERIC,ISNULL(PRCURR.ROUNDING_DECIMAL_PLACES,5)) ) as NET_PRICE,
                            ROUND(ISNULL(COMMITTED_VALUE,0),CONVERT(NUMERIC,ISNULL(PRCURR.ROUNDING_DECIMAL_PLACES,5)) ) as COMMITTED_VALUE,
                            ROUND(ISNULL(ESTIMATED_VALUE,0),CONVERT(NUMERIC,ISNULL(PRCURR.ROUNDING_DECIMAL_PLACES,5)) ) as ESTIMATED_VALUE,
                            ROUND(ISNULL(NET_VALUE,0),CONVERT(NUMERIC,ISNULL(PRCURR.ROUNDING_DECIMAL_PLACES,5)) ) as NET_VALUE,
                            ROUND(ISNULL(UNIT_PRICE,0),CONVERT(NUMERIC,ISNULL(PRCURR.ROUNDING_DECIMAL_PLACES,5)) ) as UNIT_PRICE,
                            ROUND(ISNULL(YEAR_1,0),CONVERT(NUMERIC,ISNULL(PRCURR.ROUNDING_DECIMAL_PLACES,5)) ) as YEAR_1,
                            ROUND(ISNULL(YEAR_2,0),CONVERT(NUMERIC,ISNULL(PRCURR.ROUNDING_DECIMAL_PLACES,5)) ) as YEAR_2,
                            ROUND(ISNULL(YEAR_3,0),CONVERT(NUMERIC,ISNULL(PRCURR.ROUNDING_DECIMAL_PLACES,5)) ) as YEAR_3,
                            ROUND(ISNULL(YEAR_4,0),CONVERT(NUMERIC,ISNULL(PRCURR.ROUNDING_DECIMAL_PLACES,5)) ) as YEAR_4,
                            ROUND(ISNULL(YEAR_5,0),CONVERT(NUMERIC,ISNULL(PRCURR.ROUNDING_DECIMAL_PLACES,5)) ) as YEAR_5,
                            ROUND(ISNULL(TOTAL_AMOUNT,0),CONVERT(NUMERIC,ISNULL(PRCURR.ROUNDING_DECIMAL_PLACES,5)) ) as TOTAL_AMOUNT,
                            ROUND(ISNULL(PEREVTCST_INDT_CURR,0),CONVERT(NUMERIC,ISNULL(PRCURR.ROUNDING_DECIMAL_PLACES,5)) ) as PEREVTCST_INDT_CURR,
                            ROUND(ISNULL(PEREVTPRC_INDT_CURR,0),CONVERT(NUMERIC,ISNULL(PRCURR.ROUNDING_DECIMAL_PLACES,5)) ) as PEREVTPRC_INDT_CURR
                            FROM SAQRIT (NOLOCK)
                                INNER JOIN PRCURR (NOLOCK) ON DOCURR_RECORD_ID = CURRENCY_RECORD_ID AND CURRENCY = DOC_CURRENCY
                                WHERE SAQRIT.QUOTE_RECORD_ID = '{QuoteRecordId}' AND SAQRIT.QTEREV_RECORD_ID = '{rev}' 
                            ) IQ ON SAQRIT.QUOTE_RECORD_ID = IQ.QUOTE_RECORD_ID AND SAQRIT.QTEREV_RECORD_ID = IQ.QTEREV_RECORD_ID AND SAQRIT.SERVICE_ID = IQ.SERVICE_ID and SAQRIT.LINE = IQ.LINE AND SAQRIT.CpqTableEntryId = IQ.CpqTableEntryId
                        WHERE SAQRIT.QUOTE_RECORD_ID = '{QuoteRecordId}' AND SAQRIT.QTEREV_RECORD_ID='{rev}' """.format( QuoteRecordId= contract_quote_record_id ,rev =contract_quote_revision_record_id))					
    ##updating saqris
    Sql.RunQuery("""UPDATE SAQRIS 
                            SET UNIT_PRICE_INGL_CURR = IQ.UNIT_PRICE_INGL_CURR, 
                            NET_PRICE_INGL_CURR=IQ.NET_PRICE_INGL_CURR,
                            UNIT_PRICE = IQ.UNIT_PRICE, 
                            NET_PRICE=IQ.NET_PRICE, 
                            NET_VALUE = IQ.NET_VALUE,
                            NET_VALUE_INGL_CURR = IQ.NET_VALUE_INGL_CURR,
                            ESTIMATED_VALUE = IQ.ESTIMATED_VALUE,
                            ESTVAL_INGL_CURR = IQ.ESTVAL_INGL_CURR,
                            COMMITTED_VALUE = IQ.COMMITTED_VALUE,
                            TAX_AMOUNT_INGL_CURR = IQ.TAX_AMOUNT_INGL_CURR,
                            TAX_AMOUNT = IQ.TAX_AMOUNT,
                            TOTAL_AMOUNT = IQ.TOTAL_AMOUNT,
                            TOTAL_AMOUNT_INGL_CURR = IQ.TOTAL_AMOUNT_INGL_CURR

                            FROM SAQRIS (NOLOCK)
                                INNER JOIN (SELECT SAQRIT.QUOTE_RECORD_ID, SAQRIT.QTEREV_RECORD_ID,SAQRIT.SERVICE_ID,SAQRIT.QTEITMSUM_RECORD_ID,
                                SUM(ISNULL(SAQRIT.UNIT_PRICE_INGL_CURR, 0)) as UNIT_PRICE_INGL_CURR,
                                SUM(ISNULL(SAQRIT.NET_PRICE_INGL_CURR, 0)) as NET_PRICE_INGL_CURR,
                                SUM(ISNULL(SAQRIT.UNIT_PRICE, 0)) as UNIT_PRICE,
                                SUM(ISNULL(SAQRIT.NET_PRICE, 0)) as NET_PRICE,
                                SUM(ISNULL(SAQRIT.NET_VALUE, 0)) as NET_VALUE,
                                SUM(ISNULL(SAQRIT.NET_VALUE_INGL_CURR, 0)) as NET_VALUE_INGL_CURR,
                                SUM(ISNULL(SAQRIT.ESTIMATED_VALUE, 0)) as ESTIMATED_VALUE,
                                SUM(ISNULL(SAQRIT.ESTVAL_INGL_CURR, 0)) as ESTVAL_INGL_CURR,
                                SUM(ISNULL(SAQRIT.COMMITTED_VALUE, 0)) as COMMITTED_VALUE,
                                SUM(ISNULL(SAQRIT.TAX_AMOUNT_INGL_CURR, 0)) as TAX_AMOUNT_INGL_CURR,
                                SUM(ISNULL(SAQRIT.TAX_AMOUNT, 0)) as TAX_AMOUNT,
                                SUM(ISNULL(SAQRIT.TOTAL_AMOUNT, 0)) as TOTAL_AMOUNT,
                                SUM(ISNULL(SAQRIT.TOTAL_AMOUNT_INGL_CURR, 0)) as TOTAL_AMOUNT_INGL_CURR

                                FROM SAQRIT (NOLOCK)
                                WHERE SAQRIT.QUOTE_RECORD_ID = '{QuoteRecordId}' AND SAQRIT.QTEREV_RECORD_ID = '{rev}'  GROUP BY SAQRIT.QUOTE_RECORD_ID, SAQRIT.QTEREV_RECORD_ID,SAQRIT.SERVICE_ID,SAQRIT.QTEITMSUM_RECORD_ID) IQ ON SAQRIS.QUOTE_RECORD_ID = IQ.QUOTE_RECORD_ID AND SAQRIS.QTEREV_RECORD_ID = IQ.QTEREV_RECORD_ID AND SAQRIS.SERVICE_ID = IQ.SERVICE_ID AND SAQRIS.QUOTE_REV_ITEM_SUMMARY_RECORD_ID = IQ.QTEITMSUM_RECORD_ID
                        WHERE SAQRIS.QUOTE_RECORD_ID = '{QuoteRecordId}' AND SAQRIS.QTEREV_RECORD_ID='{rev}' """.format( QuoteRecordId= contract_quote_record_id ,rev =contract_quote_revision_record_id))						
    ##updating quote summary values in saqtrv
    total_credit = 0
    get_credit_val = Sql.GetFirst("""SELECT * FROM SAQRIS (NOLOCK) WHERE QUOTE_RECORD_ID = '{quote_rec_id}' AND QTEREV_RECORD_ID = '{quote_revision_rec_id}' AND SERVICE_ID='Z0116' """.format(quote_rec_id = contract_quote_record_id ,quote_revision_rec_id = contract_quote_revision_record_id ))
    if get_credit_val:
        if get_credit_val.NET_PRICE_INGL_CURR:
            total_credit = get_credit_val.NET_PRICE_INGL_CURR
    ##A055S000P01-13894	
    ##updating saqtrv
    Sql.RunQuery("""UPDATE SAQTRV
                        SET 
                        SAQTRV.TAX_AMOUNT_INGL_CURR = IQ.TAX_AMOUNT_INGL_CURR,						
                        SAQTRV.TOTAL_AMOUNT_INGL_CURR = IQ.TOTAL_AMOUNT_INGL_CURR,
                        SAQTRV.NET_VALUE_INGL_CURR = IQ.NET_VALUE_INGL_CURR,
                        SAQTRV.CREDIT_INGL_CURR	= """+str(total_credit)+""",
                        SAQTRV.ESTVAL_INGL_CURR = IQ.ESTVAL_INGL_CURR
                        FROM SAQTRV (NOLOCK)
                        INNER JOIN (SELECT SAQRIS.QUOTE_RECORD_ID, SAQRIS.QTEREV_RECORD_ID,
                                    SUM(ISNULL(SAQRIS.TAX_AMOUNT_INGL_CURR, 0)) as TAX_AMOUNT_INGL_CURR,
                                    SUM(ISNULL(SAQRIS.NET_PRICE_INGL_CURR, 0)) as NET_PRICE_INGL_CURR,
                                    SUM(ISNULL(SAQRIS.NET_PRICE, 0)) as NET_PRICE,
                                    SUM(ISNULL(SAQRIS.NET_VALUE, 0)) as NET_VALUE,
                                    SUM(ISNULL(SAQRIS.NET_VALUE_INGL_CURR, 0)) as NET_VALUE_INGL_CURR,
                                    SUM(ISNULL(SAQRIS.TAX_AMOUNT, 0)) as TAX_AMOUNT,
                                    SUM(ISNULL(SAQRIS.TOTAL_AMOUNT_INGL_CURR, 0)) as TOTAL_AMOUNT_INGL_CURR,
                                    SUM(ISNULL(SAQRIS.ESTVAL_INGL_CURR, 0)) as ESTVAL_INGL_CURR
                                    FROM SAQRIS (NOLOCK) WHERE SAQRIS.QUOTE_RECORD_ID = '{quote_rec_id}' AND SAQRIS.QTEREV_RECORD_ID = '{quote_revision_rec_id}' AND SERVICE_ID !='Z0117' GROUP BY SAQRIS.QTEREV_RECORD_ID, SAQRIS.QUOTE_RECORD_ID) IQ ON SAQTRV.QUOTE_RECORD_ID = IQ.QUOTE_RECORD_ID AND SAQTRV.QUOTE_REVISION_RECORD_ID = IQ.QTEREV_RECORD_ID
                        WHERE SAQTRV.QUOTE_RECORD_ID = '{quote_rec_id}' AND SAQTRV.QUOTE_REVISION_RECORD_ID = '{quote_revision_rec_id}' 	""".format(quote_rec_id = contract_quote_record_id ,quote_revision_rec_id = contract_quote_revision_record_id ) )
    Sql.RunQuery("""UPDATE SAQTRV
                        SET 
                        SAQTRV.CNTMRG_INGL_CURR = IQ. CNTMRG_INGL_CURR,						
                        SAQTRV.TOTAL_MARGIN_PERCENT = IQ. TOTAL_MARGIN_PERCENT
                        FROM SAQTRV (NOLOCK)
                        INNER JOIN (SELECT SAQICO.QUOTE_RECORD_ID, SAQICO.QTEREV_RECORD_ID,
                                    SUM(ISNULL(SAQICO.TNTVGC, 0)) - SUM(ISNULL(SAQICO.CNTCST, 0)) as CNTMRG_INGL_CURR,
                                    (SUM(ISNULL(SAQICO.CNTMGN, 0)) / SUM(ISNULL(SAQICO.TNTVGC, 1))) *100 as TOTAL_MARGIN_PERCENT
                                    FROM SAQICO (NOLOCK) WHERE SAQICO.QUOTE_RECORD_ID = '{quote_rec_id}' AND SAQICO.QTEREV_RECORD_ID = '{quote_revision_rec_id}' AND SERVICE_ID !='Z0117' GROUP BY SAQICO.QTEREV_RECORD_ID, SAQICO.QUOTE_RECORD_ID) IQ ON SAQTRV.QUOTE_RECORD_ID = IQ.QUOTE_RECORD_ID AND SAQTRV.QUOTE_REVISION_RECORD_ID = IQ.QTEREV_RECORD_ID
                        WHERE SAQTRV.QUOTE_RECORD_ID = '{quote_rec_id}' AND SAQTRV.QUOTE_REVISION_RECORD_ID = '{quote_revision_rec_id}' 	""".format(quote_rec_id = contract_quote_record_id ,quote_revision_rec_id = contract_quote_revision_record_id ) )
    _billing_generation(Qt_id)
    #updating value to quote summary ends

def quoteitemupdate(Qt_id):
    delete_saqris = Sql.RunQuery("DELETE FROM SAQRIS WHERE QUOTE_ID = '{}'".format(Qt_id))
    delete_saqrit = Sql.RunQuery("DELETE FROM SAQRIT WHERE QUOTE_ID = '{}'".format(Qt_id))
    delete_saqico = Sql.RunQuery("DELETE FROM SAQICO WHERE QUOTE_ID = '{}'".format(Qt_id))
    update_saqtrv = Sql.RunQuery("UPDATE SAQTRV SET TOTAL_AMOUNT_INGL_CURR=NULL, NET_VALUE_INGL_CURR=NULL WHERE QUOTE_ID = '{}'".format(Qt_id))
    _billing_generation(Qt_id)

def _billing_generation(Qt_id):
    Log.Info('Qt_id--CQIFWUDQTM-----'+str(Qt_id))
    get_rev_rec_id = Sql.GetFirst("SELECT QTEREV_RECORD_ID,QUOTE_CURRENCY,MASTER_TABLE_QUOTE_RECORD_ID FROM SAQTMT where QUOTE_ID = '{}'".format(Qt_id))
    contract_quote_rec_id = get_rev_rec_id.MASTER_TABLE_QUOTE_RECORD_ID
    quote_revision_rec_id = get_rev_rec_id.QTEREV_RECORD_ID
    LOGIN_CREDENTIALS = Sql.GetFirst("SELECT USER_NAME as Username,Password,Domain FROM SYCONF where Domain='AMAT_TST'")
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
        result = '''<?xml version="1.0" encoding="UTF-8"?><soapenv:Envelope	xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">	<soapenv:Body><CPQ_Columns>	<QUOTE_ID>{Qt_Id}</QUOTE_ID><REVISION_ID>{Rev_Id}</REVISION_ID></CPQ_Columns></soapenv:Body></soapenv:Envelope>'''.format( Qt_Id= contract_quote_rec_id,Rev_Id = quote_revision_rec_id)		
        LOGIN_CRE = Sql.GetFirst("SELECT URL FROM SYCONF where EXTERNAL_TABLE_NAME ='BILLING_MATRIX_ASYNC'")
        Async = webclient.UploadString(str(LOGIN_CRE.URL), str(result))
try: 
    Qt_id = Param.QT_REC_ID
except:
    Qt_id = ""
try:
    Action = Param.Operation
except:
    Action= ""
try:
    manual_pricing = Param.manual_pricing
except:
    manual_pricing = "False"
try:
    service_ids = Param.service_ids
except Exception:
    service_ids = []
try:
    anc_service_id = Param.ANC_SERVICE_ID
except:
    anc_service_id = ""
try:
    if Action == 'Delete':
        calling_function = quoteitemupdate(Qt_id)
    # elif  Action == 'VOUCHER_UPDATE':
    # 	voucher_amt_update(Qt_id)
    else:    
        calling_function = quote_items_pricing(Qt_id, service_ids)
        #voucher_amt_update(Qt_id)	
except Exception as e:
    Log.Info('pricing error-'+str(e))