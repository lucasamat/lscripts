# =========================================================================================================================================
#   __script_name : SYULODTREE.PY   DEV
#   __script_description : THIS SCRIPT IS USED TO LOAD THE LEFT SIDE TREE CONTROL IN ALL TABS. CURRENTLY WE CALL THE SCRIPT
#                           IN THE COMMISSIONS ADMIN AND ORDER MANAGEMENT APPS.
#   __primary_author__ : ASHA LYSANDAR
#   __create_date : 26/08/2020
#   Â© BOSTON HARBOR TECHNOLOGY LLC - ALL RIGHTS RESERVED
# ==========================================================================================================================================

import Webcom.Configurator.Scripting.Test.TestProduct
from SYDATABASE import SQL
import re

Sql = SQL()
get_ohold_pricing_status = ""

# node visibility query based on sales employee
get_node_visibility = Sql.GetFirst(
    "SELECT CP.permission_id from  CPQ_PERMISSIONS (NOLOCK) CP  INNER JOIN USERS_PERMISSIONS (NOLOCK) UP ON CP.PERMISSION_ID = UP.PERMISSION_ID  where user_id ='{login_user}' and CP.permission_id = '319'".format(
        login_user=User.Id
    )
)
try:
    get_pricing_status = Sql.GetFirst(
        "SELECT REVISION_STATUS FROM SAQTRV (NOLOCK) WHERE QUOTE_ID ='{}' AND ACTIVE = 1".format(Quote.CompositeNumber)
    )
    if get_pricing_status:
        get_ohold_pricing_status = get_pricing_status.REVISION_STATUS
except:
    pass
# node visibility query based on sales employee end

try:
    GetActiveRevision = Sql.GetFirst(
        "SELECT QUOTE_REVISION_RECORD_ID,QTEREV_ID FROM SAQTRV (NOLOCK) WHERE QUOTE_ID ='{}' AND ACTIVE = 1".format(Quote.CompositeNumber)
    )
except:
    # Trace.Write("EXCEPT: GetActiveRevision")
    GetActiveRevision = ""
if GetActiveRevision:
    Quote.SetGlobal("quote_revision_record_id", str(GetActiveRevision.QUOTE_REVISION_RECORD_ID))


class TreeView:
    def __init__(self):
        """Use for initialization"""
        self.exceptMessage = ""

    def CommonLeftTreeView(self):

        try:
            current_prod = Product.Name
        except Exception:
            current_prod = ""
        CurrentModuleObj = Sql.GetFirst("select * from SYAPPS (NOLOCK) where APP_LABEL = '" + str(current_prod) + "'")
        # crnt_prd_val = str(CurrentModuleObj.APP_ID) if CurrentModuleObj is not None else ""
        nodeId = 0
        Firstnode = str(TabName).strip() + " Information"
        returnList = []
        returnList.append({"text": Firstnode, "nodeId": 0})

        objrList = []

        REC_IDval = Sql.GetFirst(
            "SELECT * FROM SYTABS (nolock) WHERE SAPCPQ_ALTTAB_NAME='"
            + str(TabName).strip()
            + "' and APP_RECORD_ID='"
            + str(CurrentModuleObj.APP_RECORD_ID)
            + "' "
        )
        if REC_IDval is not None:
            getParentObjQuery = Sql.GetList(
                "SELECT TOP 1000 MR.RECORD_ID,MR.SAPCPQ_ATTRIBUTE_NAME,MR.PARENT_LOOKUP_REC_ID, MR.OBJ_REC_ID, MR.NAME, MR.COLUMN_REC_ID, MR.COLUMNS, MR.CAN_ADD, MR.CAN_EDIT, MR.CAN_DELETE, MR.RELATED_LIST_SINGULAR_NAME,"
                + " MR.DISPLAY_ORDER, MR.ORDERS_BY, SH.OBJECT_NAME FROM SYOBJR (NOLOCK) MR INNER JOIN SYOBJH (NOLOCK) SH ON SH.RECORD_ID = MR.OBJ_REC_ID WHERE MR.PARENT_LOOKUP_REC_ID ='"
                + str(REC_IDval.PRIMARY_OBJECT_RECORD_ID)
                + "'  AND MR.SAPCPQ_ATTRIBUTE_NAME NOT IN ('SYOBJR-94444','SYOBJR-93206','SYOBJR-94459','SYOBJR-94461','SYOBJR-94463','SYOBJR-20004','SYOBJR-90013','SYOBJR-30105','SYOBJR-95870')  ORDER BY abs(MR.DISPLAY_ORDER)  "
            )

            getParentsectionrecid = Sql.GetFirst(
                "SELECT SYSECT. * FROM SYSECT (NOLOCK) AS SYSECT INNER JOIN SYPAGE (NOLOCK) AS SYPAGE ON SYSECT.PAGE_RECORD_ID = SYPAGE.RECORD_ID WHERE SYSECT.SECTION_NAME='BASIC INFORMATION' AND SYPAGE.TAB_RECORD_ID = '"
                + str(REC_IDval.RECORD_ID)
                + "'"
            )

            if getParentObjQuery:
                for getParentObj in getParentObjQuery:
                    Wh_API_NAME = ""
                    objrList.append(getParentObj.NAME)
                    objd_where_obj = Sql.GetFirst(
                        "select * from  SYOBJD (nolock) where RECORD_ID = '" + str(getParentObj.COLUMN_REC_ID) + "'"
                    )
                    if objd_where_obj is not None:
                        Wh_API_NAME = objd_where_obj.API_NAME
                        # Wh_OBJECT_NAME = objd_where_obj.OBJECT_NAME
                    CurrentObj = Sql.GetFirst(
                        "select * from  SYOBJD (nolock) where PARENT_OBJECT_RECORD_ID = '"
                        + str(getParentObj.PARENT_LOOKUP_REC_ID)
                        + "' and DATA_TYPE ='AUTO NUMBER'"
                    )
                    if CurrentObj is not None:
                        CurrentObj_Recordno = CurrentObj.API_NAME
                        CurrentObj_Name = CurrentObj.OBJECT_NAME

                    Qstn_where_obj = Sql.GetFirst(
                        "select * from SYSEFL (nolock) where API_NAME = '"
                        + str(CurrentObj_Name)
                        + "' and API_FIELD_NAME = '"
                        + str(CurrentObj_Recordno).strip()
                        + "' AND  SECTION_RECORD_ID like'%"
                        + str(getParentsectionrecid.RECORD_ID)
                        + "%' "
                    )
                    RecAttValue = ""
                    if Qstn_where_obj is not None:
                        Qstn_REC_ID = Qstn_where_obj.SAPCPQ_ATTRIBUTE_NAME
                        if Qstn_REC_ID != "":
                            wh_Qstn_REC_ID = "QSTN_" + Qstn_REC_ID.replace("-", "_")
                            RecAttValue = ""
                            try:
                                RecAtt = Product.Attributes.GetByName(str(wh_Qstn_REC_ID))
                                if RecAtt is not None:
                                    RecAttValue = RecAtt.GetValue()
                            except Exception:
                                RecAttValue = ""
                    nodeId += 1
                    ProductDict = {}
                    ChildList = []
                    ProductDict["text"] = str(getParentObj.NAME)
                    ProductDict["id"] = str(getParentObj.SAPCPQ_ATTRIBUTE_NAME)
                    ProductDict["objname"] = str(getParentObj.OBJECT_NAME)
                    ProductDict["nodeId"] = int(nodeId)
                    getChildObjQuery = Sql.GetFirst(
                        "select * from SYOBJH (nolock) where RECORD_ID = '" + str(getParentObj.OBJ_REC_ID) + "'"
                    )
                    if getChildObjQuery is not None:
                        childRecName = str(getChildObjQuery.RECORD_NAME)
                        GetisKeyval = Sql.GetFirst(
                            "select * from  SYOBJD (nolock) where OBJECT_NAME = '"
                            + str(getChildObjQuery.OBJECT_NAME)
                            + "' and IS_KEY='True'"
                        )

                        childQuery = Sql.GetList(
                            "select * from "
                            + str(getChildObjQuery.OBJECT_NAME)
                            + " (nolock) where "
                            + str(Wh_API_NAME)
                            + " = '"
                            + str(RecAttValue)
                            + "' "
                        )
                        Product.SetGlobal("TreeClickVal", str(RecAttValue))
                        if (
                            childQuery is not None
                            and str(getParentObj.SAPCPQ_ATTRIBUTE_NAME) != "SYOBJR-91529"
                            and str(getParentObj.SAPCPQ_ATTRIBUTE_NAME) != "SYOBJR-90008"
                            and str(TabName).upper() != "REGION"
                        ):
                            # A043S001P01-10862 end
                            # Log.Info('Common Left Tree View3')
                            for childdata in childQuery:
                                ChildDict = {}
                                if GetisKeyval is not None:
                                    API_NAMEval = str(GetisKeyval.API_NAME)
                                    if str(API_NAMEval) == "COUNTRY_ISO_CODE":
                                        API_NAMEval = "COUNTRY_NAME"
                                    Attr_Text = eval("childdata." + str(API_NAMEval))

                                    if Attr_Text != "":
                                        nodeId += 1
                                        ChildDict["text"] = Attr_Text
                                        ChildDict["objname"] = str(getChildObjQuery.OBJECT_NAME)
                                        ChildDict["id"] = str(eval("childdata." + str(childRecName)))
                                        ChildDict["nodeId"] = int(nodeId)
                                else:
                                    # /A043S001P01-10791 Dhurga- start
                                    API_NAMEval = str(childRecName)
                                    Attr_Text = str(eval("childdata." + str(API_NAMEval)))
                                    if Attr_Text != "":
                                        nodeId += 1
                                        ChildDict["text"] = Attr_Text
                                        ChildDict["objname"] = str(getChildObjQuery.OBJECT_NAME)
                                        ChildDict["id"] = str(eval("childdata." + str(childRecName)))
                                        ChildDict["nodeId"] = int(nodeId)
                                    # /A043S001P01-10791 Dhurga- End
                                if len(ChildDict) > 0:  # 10829 start
                                    ChildList.append(ChildDict)
                    if len(ChildList) > 0:
                        ProductDict["nodes"] = list(ChildList)
                    returnList.append(ProductDict)  # 10928 end

        else:
            REC_IDval = Sql.GetFirst(
                "SELECT * FROM SYTABS (nolock) WHERE SAPCPQ_ALTTAB_NAME='"
                + str(TabName).strip()
                + "' and APP_RECORD_ID='"
                + str(CurrentModuleObj.APP_RECORD_ID)
                + "' "
            )
            if REC_IDval is not None:
                getParentObjQuery = Sql.GetList(
                    "SELECT TOP 1000 MR.RECORD_ID, MR.PARENT_LOOKUP_REC_ID, MR.OBJ_REC_ID, MR.NAME, MR.COLUMN_REC_ID, MR.COLUMNS, SR.VISIBLE,"
                    + " MR.CAN_ADD, MR.CAN_EDIT, MR.CAN_DELETE, MR.RELATED_LIST_SINGULAR_NAME,"
                    + " MR.DISPLAY_ORDER, MR.ORDERS_BY, SH.OBJECT_NAME FROM SYOBJR (NOLOCK) MR INNER JOIN SYOBJH (NOLOCK) SH ON SH.RECORD_ID = MR.OBJ_REC_ID WHERE MR.PARENT_LOOKUP_REC_ID ='"
                    + str(REC_IDval.PRIMARY_OBJECT_RECORD_ID)
                    + "' AND MR.SAPCPQ_ATTRIBUTE_NAME NOT IN ('SYOBJR-94444','SYOBJR-93206')  ORDER BY abs(MR.DISPLAY_ORDER) "
                )
                getParentsectionrecid = Sql.GetFirst(
                    "SELECT SYSECT. * FROM SYSECT (NOLOCK) AS SYSECT INNER JOIN SYPAGE (NOLOCK) AS SYPAGE ON SYSECT.PAGE_RECORD_ID = SYPAGE.RECORD_ID WHERE SYSECT.SECTION_NAME='BASIC INFORMATION' AND SYPAGE.TAB_RECORD_ID = '"
                    + str(REC_IDval.RECORD_ID)
                    + "'"
                )

                if getParentObjQuery is not None:
                    for getParentObj in getParentObjQuery:
                        Wh_API_NAME = ""
                        objrList.append(getParentObj.NAME)
                        objd_where_obj = Sql.GetFirst(
                            "select * from  SYOBJD (nolock) where RECORD_ID = '" + str(getParentObj.COLUMN_REC_ID) + "'"
                        )
                        if objd_where_obj is not None:
                            Wh_API_NAME = objd_where_obj.API_NAME
                            # Wh_OBJECT_NAME = objd_where_obj.OBJECT_NAME
                        CurrentObj = Sql.GetFirst(
                            "select * from  SYOBJD (nolock) where PARENT_OBJECT_RECORD_ID = '"
                            + str(getParentObj.PARENT_LOOKUP_REC_ID)
                            + "' and DATA_TYPE ='AUTO NUMBER'"
                        )
                        if CurrentObj is not None:
                            CurrentObj_Recordno = CurrentObj.API_NAME
                            CurrentObj_Name = CurrentObj.OBJECT_NAME

                        Qstn_where_obj = Sql.GetFirst(
                            "select * from SYSEFL (nolock) where API_NAME = '"
                            + str(CurrentObj_Name)
                            + "' and API_NAME = '"
                            + str(CurrentObj_Recordno).strip()
                            + "' AND  SECTION_RECORD_ID like'%"
                            + str(getParentsectionrecid.RECORD_ID)
                            + "%' "
                        )
                        RecAttValue = ""
                        if Qstn_where_obj is not None:
                            Qstn_REC_ID = Qstn_where_obj.SAPCPQ_ATTRIBUTE_NAME
                            if Qstn_REC_ID != "":
                                wh_Qstn_REC_ID = "QSTN_" + Qstn_REC_ID.replace("-", "_")
                                RecAttValue = ""
                                try:
                                    RecAtt = Product.Attributes.GetByName(str(wh_Qstn_REC_ID))
                                    if RecAtt is not None:
                                        RecAttValue = RecAtt.GetValue()
                                except Exception:
                                    RecAttValue = ""
                        nodeId += 1
                        ProductDict = {}
                        ChildList = []
                        ProductDict["text"] = str(getParentObj.NAME)
                        ProductDict["id"] = str(getParentObj.RECORD_ID)
                        ProductDict["objname"] = str(getParentObj.OBJECT_NAME)
                        ProductDict["nodeId"] = int(nodeId)
                        getChildObjQuery = Sql.GetFirst(
                            "select * from SYOBJH (nolock) where RECORD_ID = '" + str(getParentObj.OBJ_REC_ID) + "'"
                        )
                        if getChildObjQuery is not None:
                            childRecName = str(getChildObjQuery.RECORD_NAME)
                            GetisKeyval = Sql.GetFirst(
                                "select * from  SYOBJD (nolock) where OBJECT_NAME = '"
                                + str(getChildObjQuery.OBJECT_NAME)
                                + "' and IS_KEY='True'"
                            )

                            childQuery = Sql.GetList(
                                "select * from "
                                + str(getChildObjQuery.OBJECT_NAME)
                                + " (nolock) where "
                                + str(Wh_API_NAME)
                                + " = '"
                                + str(RecAttValue)
                                + "' "
                            )

                            if childQuery is not None:
                                for childdata in childQuery:
                                    nodeId += 1
                                    ChildDict = {}
                                    if GetisKeyval is not None:
                                        API_NAMEval = str(GetisKeyval.API_NAME)
                                        if str(API_NAMEval) == "COUNTRY_ISO_CODE":
                                            API_NAMEval = "COUNTRY_NAME"
                                        Attr_Text = str(eval("childdata." + str(API_NAMEval)))
                                        if Attr_Text != "":
                                            # nodeId +=1
                                            ChildDict["text"] = Attr_Text
                                            ChildDict["objname"] = str(getChildObjQuery.OBJECT_NAME)
                                            ChildDict["id"] = str(eval("childdata." + str(childRecName)))
                                            ChildDict["nodeId"] = int(nodeId)

                                    else:
                                        Attr_Text = str(eval("childdata." + str(childRecName)))
                                        if Attr_Text != "":
                                            ChildDict["text"] = Attr_Text
                                            ChildDict["objname"] = str(getChildObjQuery.OBJECT_NAME)
                                            ChildDict["id"] = str(eval("childdata." + str(childRecName)))
                                            ChildDict["nodeId"] = int(nodeId)
                                    if len(ChildDict) > 0:
                                        ChildList.append(ChildDict)

                        if len(ChildList) > 0:
                            ProductDict["nodes"] = list(ChildList)
                        returnList.append(ProductDict)

        Product.SetGlobal("CommonTreeList", str(returnList))
        # Trace.Write("returnList-->" + str(returnList))
        return returnList, objrList

    def RoleTreeView(self):
        TabName = "Role"
        current_prod = "SYSTEM ADMIN"
        CurrentModuleObj = Sql.GetFirst("select APP_ID from SYAPPS (NOLOCK) where APP_LABEL = '" + str(current_prod) + "'")
        crnt_prd_val = str(CurrentModuleObj.APP_ID)
        ParentLookup = "SYOBJ-00424"
        returnList = []
        basicDict = {}
        roles_list = []
        basicDict["text"] = "Role Information"
        basicDict["nodeId"] = 0
        nodeId = 1
        if len(roles_list) > 0:
            basicDict["nodes"] = list(roles_list)
        returnList.append(basicDict)

        objrList = []
        AllObj = Sql.GetFirst(
            "SELECT SYSECT.PRIMARY_OBJECT_RECORD_ID, SYSEFL.RECORD_ID,  SYOBJD.OBJECT_NAME FROM SYTABS (nolock) INNER JOIN SYPAGE (nolock) on SYTABS.RECORD_ID = SYPAGE.TAB_RECORD_ID INNER JOIN SYSECT ON SYSECT.PAGE_RECORD_ID = SYPAGE.RECORD_ID INNER JOIN SYSEFL (nolock) on SYSEFL.SECTION_RECORD_ID = SYSECT.RECORD_ID INNER JOIN  SYOBJD (nolock) on  SYOBJD.API_NAME = SYSEFL.API_FIELD_NAME and  SYOBJD.OBJECT_NAME = SYSEFL.API_NAME WHERE SYTABS.SAPCPQ_ALTTAB_NAME='"
            + str(TabName).strip()
            + "' AND SYSECT.SECTION_NAME = 'BASIC INFORMATION' AND  SYOBJD.DATA_TYPE = 'AUTO NUMBER' AND SYSEFL.SAPCPQ_ATTRIBUTE_NAME like '%"
            + str(crnt_prd_val)
            + "%' "
        )
        if AllObj is not None:
            QuestionRecId = str(AllObj.RECORD_ID)
            ObjectRecId = str(AllObj.PRIMARY_OBJECT_RECORD_ID)
            ObjectName = str(AllObj.OBJECT_NAME)
            wh_Qstn_REC_ID = "QSTN_" + str(QuestionRecId).replace("-", "_")
            RecAttValue = ""
            try:
                RecAtt = Product.Attributes.GetByName(str(wh_Qstn_REC_ID))
                if RecAtt is not None:
                    RecAttValue = RecAtt.GetValue()
            except Exception:
                RecAttValue = ""

        getParentObjQuery = Sql.GetList(
            "SELECT TOP 1000 MR.RECORD_ID, MR.PARENT_LOOKUP_REC_ID, MR.OBJ_REC_ID, MR.NAME, MR.COLUMN_REC_ID, MR.COLUMNS, "
            + " MR.CAN_ADD, MR.CAN_EDIT, MR.CAN_DELETE, MR.RELATED_LIST_SINGULAR_NAME,"
            + " MR.DISPLAY_ORDER, MR.ORDERS_BY, SH.OBJECT_NAME FROM SYOBJR (NOLOCK) MR INNER JOIN SYOBJH (NOLOCK) SH ON SH.RECORD_ID = MR.OBJ_REC_ID WHERE MR.PARENT_LOOKUP_REC_ID ='"
            + str(ParentLookup)
            + "' AND MR.RECORD_ID NOT in ('SYOBJR-93191','SYOBJR-93197','SYOBJR-93198','SYOBJR-94449')"
            + "  ORDER BY abs(MR.DISPLAY_ORDER) "
        )
        if getParentObjQuery is not None:
            for getParentObj in getParentObjQuery:
                nodeId += 1
                ProductDict = {}
                ChildList = []
                ProductDict["text"] = str(getParentObj.NAME)
                ProductDict["id"] = str(getParentObj.RECORD_ID)
                ProductDict["nodeId"] = int(nodeId)
                objrList.append(getParentObj.NAME)
                try:
                    objd_where_obj = Sql.GetFirst(
                        "select * from  SYOBJD (nolock) where RECORD_ID = '" + str(getParentObj.COLUMN_REC_ID) + "'"
                    )
                except Exception:
                    objd_where_obj = ""
                if objd_where_obj is not None:
                    Wh_API_NAME = objd_where_obj.API_NAME
                    # Wh_OBJECT_NAME = objd_where_obj.OBJECT_NAME
                getChildObjQuery = Sql.GetFirst("select * from SYOBJH (nolock) where RECORD_ID = '" + str(getParentObj.OBJ_REC_ID) + "'")
                UsersList = []
                if getChildObjQuery is not None:
                    ProductDict["objname"] = str(getChildObjQuery.OBJECT_NAME)
                    # Change the if condition if you need child node in the Approver Node
                    if str(ParentLookup) == "SYOBJ-00424":
                        GetUser = Sql.GetList(
                            "Select DISTINCT ROLE_USER_RECORD_ID, USER_NAME,USER_RECORD_ID from SYROUS (nolock) WHERE ROLE_RECORD_ID = '"
                            + str(RecAttValue)
                            + "' "
                        )
                        # Trace.Write(
                        # 	"@@@@@@@@"
                        # 	+ str(
                        # 		"Select DISTINCT ROLE_USER_RECORD_ID, USER_NAME,USER_RECORD_ID from SYROUS (nolock) WHERE ROLE_RECORD_ID = '"
                        # 		+ str(RecAttValue)
                        # 		+ "' "
                        # 	)
                        # )
                        if GetUser is not None:
                            for Approve in GetUser:
                                nodeId += 1
                                ChildList = {}
                                ChildList["text"] = str(Approve.USER_NAME)
                                ChildList["id"] = str(Approve.ROLE_USER_RECORD_ID)
                                ChildList["AutoKey"] = str("ROLE_USER_RECORD_ID")
                                ChildList["nodeId"] = int(nodeId)
                                ChildList["objname"] = "SYROUS"
                                UsersList.append(ChildList)
                if len(ChildList) > 0:
                    ProductDict["nodes"] = list(UsersList)
                returnList.append(ProductDict)
        Product.SetGlobal("CommonTreeList", str(returnList))
        # Trace.Write("returnList-----> " + str(returnList))
        return returnList, objrList

    def CommonDynamicLeftTreeView(self):
        try:
            current_prod = Product.Name
        except Exception:
            current_prod = "Sales"
        CurrentModuleObj = Sql.GetFirst("select APP_ID from SYAPPS (NOLOCK) where APP_LABEL = '" + str(current_prod) + "'")
        try:
            TestProduct = Webcom.Configurator.Scripting.Test.TestProduct()
            tab_name = TestProduct.CurrentTab
            TabName = str(tab_name)
            crnt_prd_val = str(CurrentModuleObj.APP_ID)
        except:
            TestProduct = "Sales"
            try:
                tab_name = Param.sales_current_tab
            except:
                tab_name = "Quote"

            if tab_name == "Contracts":
                tab_name = "Contract"
                TabName = "Contract"
            else:
                tab_name = "Quote"
                TabName = "Quote"
            crnt_prd_val = "QT"
        if tab_name == "Quote" and current_prod == "Sales":
            try:
                GetActiveRevision = Sql.GetFirst(
                    "SELECT QUOTE_REVISION_RECORD_ID,QTEREV_ID FROM SAQTRV (NOLOCK) WHERE QUOTE_ID ='{}' AND ACTIVE = 1".format(
                        Quote.CompositeNumber
                    )
                )
            except:
                GetActiveRevision = ""
            if GetActiveRevision:
                Quote.SetGlobal("quote_revision_record_id", str(GetActiveRevision.QUOTE_REVISION_RECORD_ID))
                Quote.SetGlobal("quote_rev_id", str(GetActiveRevision.QTEREV_ID))
            # 	quote_revision_record_id = Quote.GetGlobal("quote_revision_record_id")
            try:
                getQuote = Sql.GetFirst(
                    "SELECT MASTER_TABLE_QUOTE_RECORD_ID,QTEREV_RECORD_ID,QTEREV_ID FROM SAQTMT(NOLOCK) WHERE QUOTE_ID = '{}' AND QTEREV_RECORD_ID = '{}'".format(
                        Quote.CompositeNumber, GetActiveRevision.QUOTE_REVISION_RECORD_ID
                    )
                )
                Quote.SetGlobal("contract_quote_record_id", getQuote.MASTER_TABLE_QUOTE_RECORD_ID)
            except:
                getQuote = ""

            try:
                contract_quote_record_id = Quote.GetGlobal("contract_quote_record_id")
                quote_revision_record_id = Quote.GetGlobal("quote_revision_record_id")
            except Exception:
                contract_quote_record_id = ""
                quote_revision_record_id = ""
        returnList = []
        nodeId = 0

        AllObj = Sql.GetFirst(
            "SELECT SYSECT.PRIMARY_OBJECT_RECORD_ID, SYSEFL.SAPCPQ_ATTRIBUTE_NAME, SYSEFL.RECORD_ID, SYOBJD.OBJECT_NAME FROM SYTABS (nolock) INNER JOIN SYPAGE (nolock) on SYTABS.RECORD_ID = SYPAGE.TAB_RECORD_ID INNER JOIN SYSECT ON SYSECT.PAGE_RECORD_ID = SYPAGE.RECORD_ID INNER JOIN SYSEFL (nolock) on SYSEFL.SECTION_RECORD_ID = SYSECT.RECORD_ID INNER JOIN  SYOBJD (nolock) on  SYOBJD.API_NAME = SYSEFL.API_FIELD_NAME and  SYOBJD.OBJECT_NAME = SYSEFL.API_NAME WHERE SYTABS.SAPCPQ_ALTTAB_NAME='"
            + str(TabName).strip()
            + "' AND SYSECT.SECTION_NAME = 'BASIC INFORMATION' AND  SYOBJD.DATA_TYPE = 'AUTO NUMBER' AND SYSEFL.SAPCPQ_ATTRIBUTE_NAME like '%"
            + str(crnt_prd_val)
            + "%' "
        )
        if AllObj is not None:
            QuestionRecId = str(AllObj.SAPCPQ_ATTRIBUTE_NAME)
            ObjectRecId = str(AllObj.PRIMARY_OBJECT_RECORD_ID)
            ObjectName = str(AllObj.OBJECT_NAME)
            wh_Qstn_REC_ID = "QSTN_" + str(QuestionRecId).replace("-", "_")
            RecAttValue = ""
            try:
                RecAtt = Product.Attributes.GetByName(str(wh_Qstn_REC_ID))
                if RecAtt is not None:
                    RecAttValue = RecAtt.GetValue()
                else:  # Fix for cart item insert
                    if TabName == "Quote":
                        RecAttValue = contract_quote_record_id
            except Exception:
                if TabName == "Quote":
                    RecAttValue = contract_quote_record_id
                else:
                    RecAttValue = ""

            getParentObjQuery = Sql.GetList(
                "SELECT top 1000 * FROM SYTRND (nolock) where TREE_NAME = '"
                + str(TabName)
                + "' AND NODE_TYPE = 'STATIC' AND PARENT_NODE_RECORD_ID ='' ORDER BY abs(DISPLAY_ORDER)"
            )
            if getParentObjQuery is not None:
                for getParentObj in getParentObjQuery:
                    ##adding image along with tree params
                    # 12096 start-quote item visibility start
                    if (
                        get_node_visibility
                        and str(get_ohold_pricing_status).upper() == "ON HOLD - COSTING"
                        and str(getParentObj.NODE_NAME) == "Quote Items"
                    ):
                        continue
                    # 12096 start-quote item visibility end
                    if str(getParentObj.TREEIMAGE_URL):
                        image_url = str(getParentObj.TREEIMAGE_URL)
                        image_url = '<img class="leftside-bar-icons" src="/mt/appliedmaterials_tst/Additionalfiles/AMAT/Quoteimages/{image_url}"/>'.format(
                            image_url=image_url
                        )
                        active_image_url = str(getParentObj.ACTIVE_TREEIMAGE_URL)
                        active_image_url = '<img class="activeimage-leftside-bar-icons" src="/mt/appliedmaterials_tst/Additionalfiles/AMAT/Quoteimages/{image_url}"/>'.format(
                            image_url=active_image_url
                        )
                    else:
                        image_url = active_image_url = ""
                    ProductDict = {}
                    ChildListData = []
                    SubTabList = []
                    NewList = []

                    RecId = str(getParentObj.TREE_NODE_RECORD_ID)
                    NodeText = image_url + active_image_url + str(getParentObj.NODE_NAME)
                    ProductDict["text"] = NodeText
                    ProductDict["nodeId"] = int(getParentObj.NODE_ID)
                    PageRecId = str(getParentObj.NODE_PAGE_RECORD_ID)
                    pageDetails = Sql.GetFirst("select * from SYPAGE (nolock) where RECORD_ID = '" + str(PageRecId) + "'")
                    if pageDetails is not None:
                        ObjName = pageDetails.OBJECT_APINAME
                        ProductDict["objname"] = ObjName
                        ProductDict["id"] = pageDetails.OBJECT_RECORD_ID

                    getParentObjRightView = Sql.GetList(
                        "SELECT top 1000 * FROM SYSTAB (nolock) where TREE_NODE_RECORD_ID = '"
                        + str(RecId)
                        + "' ORDER BY abs(DISPLAY_ORDER) "
                    )
                    if ProductDict.get("objname") == "ACAPTX" and ProductDict.get("text") == "Approval History":
                        approval_transaction_obj = Sql.GetFirst(
                            "SELECT count(CpqTableEntryId) as cnt FROM ACAPTX (NOLOCK) WHERE APPROVAL_TRANSACTION_RECORD_ID = '{}'".format(
                                Product.GetGlobal("team_approval_record_id")
                            )
                        )
                        if approval_transaction_obj is not None:
                            related_obj = Sql.GetFirst(
                                "SELECT ACAPCH.APRCHN_DESCRIPTION FROM ACAPCH (NOLOCK) JOIN ACAPMA (NOLOCK) ON ACAPCH.APPROVAL_CHAIN_RECORD_ID = ACAPMA.APRCHN_RECORD_ID"
                            )
                            if related_obj:
                                type = "OBJECT RELATED LAYOUT"
                                subTabName = related_obj.APRCHN_DESCRIPTION
                                ObjRecId = "59C058FD-628D-4EBD-85B2-DF5CE00F977F"
                                RelatedId = ""
                                RelatedName = ""
                                SubTabList.append(self.getSubtabRelatedDetails(subTabName, type, ObjRecId, RelatedId, RelatedName))
                    if getParentObjRightView is not None and len(getParentObjRightView) > 0:
                        for getRightView in getParentObjRightView:
                            type = str(getRightView.SUBTAB_TYPE)
                            subTabName = str(getRightView.SUBTAB_NAME)
                            ObjRecId = getRightView.OBJECT_RECORD_ID
                            RelatedId = getRightView.RELATED_RECORD_ID
                            RelatedName = getRightView.RELATED_LIST_NAME
                            ProductDict["id"] = RelatedId
                            # contract_quote_record_id = Quote.GetGlobal("contract_quote_record_id")
                            # quote_revision_record_id = Quote.GetGlobal("quote_revision_record_id")

                            if subTabName:
                                if subTabName == "Spare Parts Line Item Details":
                                    subTabName = ""
                                    spare_parts_object = Sql.GetFirst(
                                        "SELECT count(CpqTableEntryId) as cnt FROM SAQIFP (NOLOCK) WHERE QUOTE_RECORD_ID = '{}' AND QTEREV_RECORD_ID = '{}'".format(
                                            contract_quote_record_id, quote_revision_record_id
                                        )
                                    )
                                    if spare_parts_object is not None:
                                        if spare_parts_object.cnt > 0:
                                            subTabName = str(getRightView.SUBTAB_NAME)
                                SubTabList.append(self.getSubtabRelatedDetails(subTabName, type, ObjRecId, RelatedId, RelatedName))
                        # Billing Matrix Dynamic Tabs - Start
                        if ProductDict.get("objname") == "SAQRIB" and ProductDict.get("text") == "Billing":
                            item_billing_plan_obj = Sql.GetFirst(
                                "SELECT count(CpqTableEntryId) as cnt FROM SAQIBP (NOLOCK) WHERE QUOTE_RECORD_ID = '{}' AND QTEREV_RECORD_ID = '{}' GROUP BY EQUIPMENT_ID,SERVICE_ID".format(
                                    contract_quote_record_id, quote_revision_record_id
                                )
                            )
                            if item_billing_plan_obj is not None:
                                quotient, remainder = divmod(item_billing_plan_obj.cnt, 12)
                                years = quotient + (1 if remainder > 0 else 0)
                                if not years:
                                    years = 1
                                ObjRecId = RelatedId = None
                                related_obj = Sql.GetFirst(
                                    """SELECT SYOBJR.OBJ_REC_ID, SYOBJR.SAPCPQ_ATTRIBUTE_NAME, SYOBJR.NAME FROM SYOBJH (NOLOCK)
												JOIN SYOBJR (NOLOCK) ON SYOBJR.OBJ_REC_ID = SYOBJH.RECORD_ID
												WHERE SYOBJH.OBJECT_NAME = 'SAQIBP'"""
                                )
                                if related_obj:
                                    ObjRecId = related_obj.OBJ_REC_ID
                                    RelatedId = related_obj.SAPCPQ_ATTRIBUTE_NAME
                                    RelatedName = related_obj.NAME
                                for index in range(1, years + 1):
                                    type = "OBJECT RELATED LAYOUT"
                                    subTabName = "Year {}".format(index)
                                    # Trace.Write('subTabName--'+str(subTabName))
                                    if ObjRecId and RelatedId:
                                        SubTabList.append(self.getSubtabRelatedDetails(subTabName, type, ObjRecId, RelatedId, RelatedName))
                        # Billing Matrix Dynamic Tabs - End
                    else:
                        if pageDetails is not None:
                            pageType = pageDetails.PAGE_TYPE
                            subTabName = "No SubTab"
                            objRecId = pageDetails.OBJECT_RECORD_ID
                            if NodeText == "Variable":
                                querystr = "AND NAME = '" + str(NodeText) + "'"
                            else:
                                querystr = ""
                            SubTabList.append(self.getPageRelatedDetails(subTabName, pageType, objRecId, ObjectRecId, querystr))
                            RelatedObj = Sql.GetFirst(
                                "SELECT RECORD_ID, SAPCPQ_ATTRIBUTE_NAME, NAME FROM SYOBJR(NOLOCK) WHERE PARENT_LOOKUP_REC_ID = '"
                                + str(ObjectRecId)
                                + "' AND OBJ_REC_ID = '"
                                + str(objRecId)
                                + "' AND VISIBLE = 'True'"
                            )
                            if RelatedObj is not None:
                                ProductDict["id"] = RelatedObj.SAPCPQ_ATTRIBUTE_NAME

                    ProductDict["SubTabs"] = SubTabList
                    # if TabName == "Quote":

                    findChildOneObj = Sql.GetList(
                        "SELECT TOP 1000 * FROM SYTRND (nolock) WHERE PARENT_NODE_RECORD_ID='"
                        + str(RecId)
                        + "' AND DISPLAY_CRITERIA != 'DYNAMIC' ORDER BY abs(DISPLAY_ORDER) "
                    )

                    try:
                        getZ0009 = Sql.GetFirst(
                            "SELECT CpqTableEntryId,SERVICE_ID FROM SAQTSV (NOLOCK) WHERE SERVICE_ID IN ('Z0009','Z0010','Z0128') AND QUOTE_RECORD_ID = '{}' AND QTEREV_RECORD_ID = '{}'".format(
                                contract_quote_record_id, quote_revision_record_id
                            )
                        )
                        if getZ0009 is not None:
                            is_pmsa = self.PMSATree(getZ0009.SERVICE_ID)
                        else:
                            is_pmsa = 0
                    except:
                        is_pmsa = 0
                    if is_pmsa:
                        if RecId in (
                            "1F47A350-4E38-41C9-A5C5-F53DC9BB3DB8",
                            "B7BC662B-91A4-42C0-A2D9-B1E713D59E18",
                            "1CE55561-F2DF-4A05-A21B-82AF08C23215",
                            "1D531821-21B2-4F5F-8579-9724F10F8911",
                            "5C5AA48D-6598-4B55-91BB-1D043575C3B7",
                            "72FC842D-99A8-430C-A689-6DBB093015B5",
                            "11C3DA16-72B3-49A8-8B80-23637D0D499E",
                            "EBC61A4C-18C8-4374-9BDD-17BB93172453",
                            "B9E7FF3A-CD32-4414-8036-A4310FB4A80E",
                        ):
                            findChildOneObj = Sql.GetList(
                                "SELECT TOP 1000 * FROM SYTRND (nolock) WHERE PARENT_NODE_RECORD_ID='"
                                + str(RecId)
                                + "' AND DISPLAY_CRITERIA = 'DYNAMIC' ORDER BY abs(DISPLAY_ORDER) "
                            )
                    if findChildOneObj is not None:
                        for findChildOne in findChildOneObj:
                            parobj = str(findChildOne.PARENTNODE_OBJECT)
                            NodeType = str(findChildOne.NODE_TYPE)
                            NodeApiName = str(findChildOne.NODE_DISPLAY_NAME)
                            DynamicQuery = str(findChildOne.DYNAMIC_NODEDATA_QUERY)
                            PageRecId = str(findChildOne.NODE_PAGE_RECORD_ID)
                            ordersBy = str(findChildOne.ORDERS_BY)
                            nodeId = str(findChildOne.NODE_ID)
                            where_string = " 1=1 "
                            if parobj == "True" and ACTION != "ADDNEW":
                                ChildListData = self.getChildFromParentObj(
                                    NodeText,
                                    NodeType,
                                    NodeName,
                                    RecAttValue,
                                    nodeId,
                                    ParRecId,
                                    DynamicQuery,
                                    ObjectName,
                                    RecId,
                                    where_string,
                                    PageRecId,
                                    ObjectRecId,
                                    NodeApiName,
                                    ordersBy,
                                )
                            else:
                                if ACTION != "ADDNEW":
                                    NodeName = str(findChildOne.NODE_DISPLAY_NAME)
                                    ParRecId = str(findChildOne.TREE_NODE_RECORD_ID)
                                    DynamicQuery = str(findChildOne.DYNAMIC_NODEDATA_QUERY)
                                    NodeType = str(findChildOne.NODE_TYPE)
                                    PageRecId = str(findChildOne.NODE_PAGE_RECORD_ID)
                                    nodeId = str(findChildOne.NODE_ID)
                                    where_string = " 1 = 1 "
                                    if TabName == "Profile":
                                        ChildListData = self.getProfileChildOne(
                                            NodeType,
                                            NodeName,
                                            RecAttValue,
                                            nodeId,
                                            ParRecId,
                                            DynamicQuery,
                                            ObjectName,
                                            RecId,
                                            where_string,
                                            PageRecId,
                                            ObjectRecId,
                                            ordersBy,
                                        )
                                    else:
                                        if ACTION != "ADDNEW":
                                            ChildListData = self.getChildOne(
                                                NodeType,
                                                NodeName,
                                                RecAttValue,
                                                nodeId,
                                                NodeText,
                                                ParRecId,
                                                DynamicQuery,
                                                ObjectName,
                                                RecId,
                                                where_string,
                                                PageRecId,
                                                ObjectRecId,
                                                ordersBy,
                                            )
                            if len(ChildListData) > 0:
                                NewList.append(ChildListData)
                                list2 = []
                                for sublist in NewList:
                                    for item in sublist:
                                        list2.append(item)
                                ProductDict["nodes"] = list2
                        returnList.append(ProductDict)
        Product.SetGlobal("CommonTreeList", str(returnList))
        # Trace.Write("returnList----------------> " + str(returnList))
        cbc_subtab = ""
        try:
            user_id = ScriptExecutor.ExecuteGlobal("SYUSDETAIL", "USERNAME")
            salesteam_obj = Sql.GetList(
                " SELECT MEMBER_ID FROM SAQDLT (NOLOCK) WHERE QUOTE_RECORD_ID = '{qte_rec_id}' AND QTEREV_RECORD_ID = '{revision_rec_id}' AND C4C_PARTNERFUNCTION_ID = 'CONTRACT MANAGER' AND MEMBER_ID = '{UserId}'".format(
                    qte_rec_id=contract_quote_record_id, revision_rec_id=quote_revision_record_id, UserId=user_id
                )
            )
            # A055S000P01-17166 start
            get_status = Sql.GetFirst(
                "SELECT WORKFLOW_STATUS from SAQTRV where QUOTE_RECORD_ID='{contract_quote_rec_id}' AND QTEREV_RECORD_ID = '{quote_revision_rec_id}'".format(
                    contract_quote_rec_id=contract_quote_record_id, quote_revision_rec_id=quote_revision_record_id
                )
            )
            if get_status:
                if get_status.WORKFLOW_STATUS == "LEGAL-SOW":
                    update_rev_status = "UPDATE SAQTRV SET WORKFLOW_STATUS = 'CLEAN BOOKING CHECKLIST',REVISION_STATUS = 'CBC-PREPARING CBC' where QUOTE_RECORD_ID='{contract_quote_rec_id}' AND QTEREV_RECORD_ID = '{quote_revision_rec_id}'".format(
                        contract_quote_rec_id=contract_quote_record_id, quote_revision_rec_id=quote_revision_record_id
                    )
                    # A055S000P01-17166 end
                    Sql.RunQuery(update_rev_status)
            if salesteam_obj:
                cbc_subtab = "Yes"
            else:
                cbc_subtab = "No"
        except:
            Trace.Write("CBC_Subtab_Exception")
        return returnList, "", cbc_subtab

    def getProfileChildOne(
        self,
        NodeType,
        NodeName,
        RecAttValue,
        nodeId,
        ParRecId,
        DynamicQuery,
        ObjectName,
        RecId,
        where_string,
        PageRecId,
        ObjectRecId,
        ordersBy,
    ):
        NodeValue = ""
        NodeText1 = ""
        ChildList = []
        NewList = []

        if str(NodeType) == "DYNAMIC":
            try:
                ContAtt = Product.Attributes.GetByName("QSTN_SYSEFL_QT_016909")
                ContAttValue = ContAtt.GetValue()
            except:
                ContAtt = ""
                ContAttValue = ""

            pageDetails = Sql.GetFirst("select * from SYPAGE (nolock) where RECORD_ID = '" + str(PageRecId) + "'")
            if pageDetails is not None:
                OBJECT_RECORD_ID = pageDetails.OBJECT_RECORD_ID
                ObjName = pageDetails.OBJECT_APINAME
                CurrentTabName = pageDetails.TAB_NAME

                if str(ObjName) == "USERS" and str(ObjectName) == "cpq_permissions":
                    objd_where_obj = Sql.GetFirst("select * from SYOBJD (nolock) where OBJECT_NAME = '" + str(ObjName) + "'")
                elif str(ObjName).strip() == "SYPRSF":
                    objd_where_obj = Sql.GetFirst(
                        "select * from SYOBJD (nolock) where OBJECT_NAME = '"
                        + str(ObjName)
                        + "' AND LOOKUP_OBJECT = '"
                        + str(ObjectName)
                        + "'"
                    )
                elif str(ObjName).strip() == "SYPSAC" and CurrentTabName == "App":
                    getsectrec = Product.GetGlobal("NodeRecIdS")
                    where_string += " AND SECTION_RECORD_ID = '" + str(getsectrec) + "'"
                elif str(ObjName).strip() == "SYPSAC":
                    ObjectName = "SYSECT"
                    objd_where_obj = Sql.GetFirst(
                        "select * from SYOBJD (nolock) where OBJECT_NAME = '"
                        + str(ObjName)
                        + "' AND LOOKUP_OBJECT = '"
                        + str(ObjectName)
                        + "'"
                    )
                else:
                    objd_where_obj = Sql.GetFirst(
                        "select * from SYOBJD (nolock) where OBJECT_NAME = '"
                        + str(ObjName)
                        + "' AND LOOKUP_OBJECT = '"
                        + str(ObjectName)
                        + "'"
                    )

                CurrentTabName = TestProduct.CurrentTab

                if objd_where_obj is not None:
                    if str(ObjName) == "USERS" and str(ObjectName) == "cpq_permissions":
                        Wh_API_NAME = ""
                        where_string = where_string
                    elif str(ObjName).strip() == "SYPRTB":
                        RecAttValue = Product.Attributes.GetByName("QSTN_SYSEFL_SY_00125").GetValue()
                        where_string = "1=1 AND"
                        getapptext = Product.GetGlobal("setappname")
                        where_string += "  APP_ID = '" + str(getapptext) + "' AND  PROFILE_RECORD_ID = '" + str(RecAttValue) + "'"
                    elif str(ObjName).strip() == "SYPRSN":
                        RecAttValue = Product.Attributes.GetByName("QSTN_SYSEFL_SY_00125").GetValue()
                        where_string = "1=1 AND"
                        gettabtext = Product.GetGlobal("settabname")
                        getpagename = Sql.GetFirst("select TAB_RECORD_ID from SYPRTB(NOLOCK) where TAB_ID = '" + str(gettabtext) + "'")
                        if getpagename:
                            where_string += (
                                " PROFILE_RECORD_ID = '"
                                + str(RecAttValue)
                                + "' and TAB_RECORD_ID = '"
                                + str(getpagename.TAB_RECORD_ID)
                                + "'"
                            )
                        else:
                            where_string += " PROFILE_RECORD_ID = '" + str(RecAttValue) + "'"
                    elif str(ObjName).strip() == "SYPRSF" and CurrentTabName == "Profile":
                        RecAttValue = Product.Attributes.GetByName("QSTN_SYSEFL_SY_00125").GetValue()
                        where_string = "1=1 AND"
                        gettabtext = Product.GetGlobal("settabname")
                        getsectid = Product.GetGlobal("NodeSecRecIdS")

                        getsectname = Sql.GetFirst(
                            "select SECTION_RECORD_ID from SYPRSN(NOLOCK) where PROFILE_SECTION_RECORD_ID = '"
                            + str(getsectid)
                            + "' and PROFILE_RECORD_ID = '"
                            + str(RecAttValue)
                            + "'"
                        )
                        if getsectname:
                            where_string += (
                                " PROFILE_RECORD_ID = '"
                                + str(RecAttValue)
                                + "' and SECTION_RECORD_ID = '"
                                + str(getsectname.SECTION_RECORD_ID)
                                + "' ORDER BY SECTION_FIELD_ID ASC"
                            )
                        else:
                            where_string += (
                                " PROFILE_RECORD_ID = '"
                                + str(RecAttValue)
                                + "' and SECTION_RECORD_ID = '"
                                + str(getsectname.SECTION_RECORD_ID)
                                + "' ORDER BY SECTION_FIELD_ID ASC"
                            )
                    else:
                        Wh_API_NAME = objd_where_obj.API_NAME
                        if RecAttValue:
                            where_string = " " + str(where_string) + " AND " + str(Wh_API_NAME) + " = '" + str(RecAttValue) + "'"
                        else:
                            where_string = where_string

                    childRecName = Sql.GetFirst(
                        "select * from SYOBJD (nolock) where OBJECT_NAME = '" + str(ObjName) + "' AND DATA_TYPE = 'AUTO NUMBER'"
                    )

                    if DynamicQuery is not None and len(DynamicQuery) > 0:
                        DynamicQuery = (
                            DynamicQuery.replace("{", "")
                            .replace("}", "")
                            .replace("RecAttValue", RecAttValue)
                            .replace("ContAttValue", ContAttValue)
                            .replace("where_string", where_string)
                        )
                        childQuery = Sql.GetList("" + str(DynamicQuery) + "")
                    else:
                        if NodeName.find("-") == -1:
                            NodeValue = NodeName
                        else:
                            NodeValuesplit = NodeName.split("-")
                            if len(NodeValuesplit) > 1:
                                NodeValue = NodeValuesplit[1]
                        if ordersBy:
                            ordersByQuery = " ORDER BY " + str(ordersBy)
                            if NodeValue != ordersBy:
                                childQuery = Sql.GetList(
                                    "select distinct top 1000 "
                                    + str(NodeValue)
                                    + ", "
                                    + str(ordersBy)
                                    + " from "
                                    + str(ObjName)
                                    + " (nolock) where "
                                    + str(where_string)
                                    + " "
                                    + str(ordersByQuery)
                                    + ""
                                )
                            else:
                                childQuery = Sql.GetList(
                                    "select distinct top 1000 "
                                    + str(NodeValue)
                                    + " from "
                                    + str(ObjName)
                                    + " (nolock) where "
                                    + str(where_string)
                                    + " "
                                    + str(ordersByQuery)
                                    + ""
                                )
                        elif str(ObjName) == "SYPSAC":
                            where_string = where_string
                            ordersByQuery = ""
                            childQuery = Sql.GetList(
                                "select "
                                + str(NodeName)
                                + " from "
                                + str(ObjName)
                                + " (nolock) where "
                                + str(where_string)
                                + " "
                                + str(ordersByQuery)
                                + ""
                            )
                        elif str(ObjName).strip() == "SYPGAC":
                            ordersByQuery = ""
                            childQuery = Sql.GetList(
                                "select "
                                + str(NodeName)
                                + " from "
                                + str(ObjName)
                                + " (nolock) where "
                                + str(where_string)
                                + " "
                                + str(ordersByQuery)
                                + ""
                            )
                        elif str(ObjName) == "SYPRSF":
                            where_string += where_string
                            ordersByQuery = ""
                            childQuery = Sql.GetList(
                                "select top 1000 "
                                + str(NodeName)
                                + " from "
                                + str(ObjName)
                                + " (nolock) where "
                                + str(where_string)
                                + " "
                                + str(ordersByQuery)
                                + ""
                            )
                        # SUBNODE IS NOT LOADING ISSUE FOR SECTIONS NODE IN PAGES TAB - START
                        elif str(ObjName) == "SYSECT":
                            where_string = " PAGE_RECORD_ID = '" + str(RecAttValue) + "'"
                            ordersByQuery = ""
                            childQuery = Sql.GetList(
                                "select "
                                + str(NodeName)
                                + " from "
                                + str(ObjName)
                                + " (nolock) where "
                                + str(where_string)
                                + " "
                                + str(ordersByQuery)
                                + ""
                            )
                        # SUBNODE IS NOT LOADING ISSUE FOR SECTIONS NODE IN PAGES TAB - END
                        elif str(ObjName) == "USERS":
                            ordersByQuery = ""
                            childQuery = Sql.GetList(
                                "SELECT DISTINCT top 1000 UPPER(US.USERNAME) AS USERNAME,US.ID,US.NAME,US.ACTIVE FROM USERS US WITH (NOLOCK) inner join users_permissions up on us.id = up.user_id inner join cpq_permissions cp on cp.permission_id = up.permission_id where cp.permission_type= '0' and up.permission_id = '"
                                + str(RecAttValue)
                                + "' order by USERNAME"
                            )

                        elif str(ObjName) == "SYPRAP":
                            ordersByQuery = ""
                            childQuery = Sql.GetList(
                                "select top 1000 "
                                + str(NodeName)
                                + " from "
                                + str(ObjName)
                                + " (nolock) where "
                                + str(where_string)
                                + " "
                                + str(ordersByQuery)
                                + ""
                            )
                        else:
                            ordersByQuery = ""
                            childQuery = Sql.GetList(
                                "select distinct "
                                + str(NodeName)
                                + " from "
                                + str(ObjName)
                                + " (nolock) where "
                                + str(where_string)
                                + " "
                                + str(ordersByQuery)
                                + ""
                            )
                    flag = 1
                    if childQuery is not None:
                        for childdata in childQuery:
                            ChildDict = {}
                            SubChildData = []

                            if NodeName.find(",") == -1 and NodeName.find("-") == -1:
                                if str(NodeName) == "OBJECT_NAME" and TabName == "Profile":
                                    NodeText = str(eval("childdata." + str(NodeName)))
                                else:
                                    NodeText = str(eval("childdata." + str(NodeName))).upper()

                                if str(NodeName) == "APP_ID" and TabName == "Profile":
                                    Product.SetGlobal("setappname", str(NodeText))
                                elif str(NodeName) == "TAB_ID" and TabName == "Profile":
                                    Product.SetGlobal("settabname", str(NodeText))

                                childQueryObj = Sql.GetFirst(
                                    "select * from "
                                    + str(ObjName)
                                    + " (nolock) where "
                                    + str(where_string)
                                    + " AND "
                                    + str(NodeName)
                                    + " = '"
                                    + str(NodeText)
                                    + "'"
                                )
                            elif NodeName.find(",") > 0:
                                Nodesplit = NodeName.split(",")
                                if len(Nodesplit) > 1:
                                    NodeName1 = Nodesplit[0]
                                    NodeText = str(eval("childdata." + str(NodeName1))).title()
                                    childQueryObj = Sql.GetFirst(
                                        "select * from "
                                        + str(ObjName)
                                        + " (nolock) where "
                                        + str(where_string)
                                        + " AND "
                                        + str(NodeName1)
                                        + " = '"
                                        + (NodeText)
                                        + "'"
                                    )
                                    NodeText += " - "
                                    NodeName1 = Nodesplit[1]
                                    NodeText += str(eval("childdata." + str(NodeName1)))
                                    childQueryObj = SqlHelper.GetFirst(
                                        "select * from "
                                        + str(ObjName)
                                        + " (nolock) where "
                                        + str(where_string)
                                        + " AND "
                                        + str(NodeName1)
                                        + " = '"
                                        + str(eval("childdata." + str(NodeName1)))
                                        + "'"
                                    )
                            elif NodeName.find("-") > 0:
                                Nodesplit = NodeName.split("-")
                                if len(Nodesplit) > 1:
                                    NodeName1 = Nodesplit[0]
                                    NodeName2 = Nodesplit[1]
                                    NodeText1 = str(eval("childdata." + str(NodeName2))).title()
                                    NodeText = NodeName1 + "-" + NodeText1
                                    childQueryObj = Sql.GetFirst(
                                        "select * from "
                                        + str(ObjName)
                                        + " (nolock) where "
                                        + str(where_string)
                                        + " AND "
                                        + str(NodeName2)
                                        + " = '"
                                        + str(NodeText1)
                                        + "'"
                                    )

                            if childQueryObj is not None:
                                NodeRecId = str(eval("childQueryObj." + str(childRecName.API_NAME)))
                                ChildDict["id"] = str(NodeRecId)
                                if str(NodeName) == "SECTION_ID" and TabName == "Profile":
                                    Product.SetGlobal("NodeSecRecIdS", NodeRecId)
                            if NodeText == "True":
                                NodeRecId = ""
                                ChildDict["text"] = "Active"
                            elif NodeText == "False":
                                NodeRecId = ""
                                ChildDict["text"] = "Inactive"
                            else:
                                NodeRecId = ""
                                ChildDict["text"] = NodeText
                            ChildDict["nodeId"] = int(nodeId)
                            objQuery = Sql.GetFirst(
                                "SELECT OBJECT_NAME FROM SYOBJH(NOLOCK) WHERE RECORD_ID = '" + str(OBJECT_RECORD_ID) + "'"
                            )
                            if objQuery is not None:
                                ChildDict["objname"] = objQuery.OBJECT_NAME
                                parObjName = objQuery.OBJECT_NAME
                            SubTabList = []
                            getParentObjRightView = Sql.GetList(
                                "SELECT top 1000 * FROM SYSTAB (nolock) where TREE_NODE_RECORD_ID = '"
                                + str(ParRecId)
                                + "' ORDER BY abs(DISPLAY_ORDER) "
                            )
                            if getParentObjRightView is not None and len(getParentObjRightView) > 0:
                                for getRightView in getParentObjRightView:
                                    type = str(getRightView.SUBTAB_TYPE)
                                    subTabName = str(getRightView.SUBTAB_NAME)
                                    ObjRecId = getRightView.OBJECT_RECORD_ID

                                    RelatedId = getRightView.RELATED_RECORD_ID
                                    RelatedName = getRightView.RELATED_LIST_NAME

                                    if subTabName:
                                        SubTabList.append(self.getSubtabRelatedDetails(subTabName, type, ObjRecId, RelatedId, RelatedName))
                            else:
                                if pageDetails is not None:
                                    pageType = pageDetails.PAGE_TYPE
                                    subTabName = "No SubTab"
                                    objRecId = pageDetails.OBJECT_RECORD_ID
                                    querystr = ""
                                    SubTabList.append(self.getPageRelatedDetails(subTabName, pageType, objRecId, ObjectRecId, querystr))
                            ChildDict["SubTabs"] = SubTabList

                            findSubChildAvailable = Sql.GetList(
                                "SELECT TOP 1000 * FROM SYTRND (nolock) WHERE PARENT_NODE_RECORD_ID='"
                                + str(ParRecId)
                                + "' AND DISPLAY_CRITERIA != 'DYNAMIC' ORDER BY abs(DISPLAY_ORDER) "
                            )

                            # PROFILE EXPLORER
                            if NodeText == "SYSTEM ADMIN":
                                Product.SetGlobal("APPS", NodeText)

                            # To fetch pages based on Tabs in System Admin
                            pages_tab = Sql.GetList("SELECT TAB_LABEL,PRIMARY_OBJECT_NAME FROM SYTABS (NOLOCK)")
                            tab_list = [(tab.TAB_LABEL).upper() for tab in pages_tab]
                            object_list = [tab.PRIMARY_OBJECT_NAME for tab in pages_tab]
                            tab_obj_dict = {tab_list[i]: object_list[i] for i in range(len(tab_list))}

                            if NodeText in tab_list:
                                Product.SetGlobal("page_tab", NodeText)
                                Product.SetGlobal("object_name", tab_obj_dict[NodeText])

                            if findSubChildAvailable is not None:
                                for findSubChildOne in findSubChildAvailable:
                                    parobj = str(findSubChildOne.PARENTNODE_OBJECT)
                                    NodeType = str(findSubChildOne.NODE_TYPE)
                                    NodeApiName = str(findSubChildOne.NODE_DISPLAY_NAME)
                                    DynamicQuery = str(findSubChildOne.DYNAMIC_NODEDATA_QUERY)
                                    PageRecId = str(findSubChildOne.NODE_PAGE_RECORD_ID)
                                    ordersBy = str(findSubChildOne.ORDERS_BY)
                                    if parobj == "True":
                                        if NodeValue != "":
                                            Node_name = NodeValue
                                        else:
                                            Node_name = NodeName
                                        if NodeText1 != "":
                                            NodeText = NodeText1
                                        childwhere_string = (
                                            " " + str(where_string) + " AND " + str(Node_name) + " = '" + str(NodeText) + "'"
                                        )
                                        SubChildData = self.getChildFromParentObj(
                                            NodeText,
                                            NodeType,
                                            Node_name,
                                            RecAttValue,
                                            nodeId,
                                            ParRecId,
                                            DynamicQuery,
                                            ObjectName,
                                            RecId,
                                            childwhere_string,
                                            PageRecId,
                                            ObjectRecId,
                                            NodeApiName,
                                            ordersBy,
                                        )
                                    else:
                                        SubNodeName = str(findSubChildOne.NODE_DISPLAY_NAME)
                                        SubParRecId = str(findSubChildOne.TREE_NODE_RECORD_ID)
                                        SubChildDynamicQuery = str(findSubChildOne.DYNAMIC_NODEDATA_QUERY)
                                        SubNodeType = str(findSubChildOne.NODE_TYPE)
                                        nodeId = str(findSubChildOne.NODE_ID)
                                        PageRecId = str(findSubChildOne.NODE_PAGE_RECORD_ID)
                                        RecAttValue = NodeRecId
                                        ObjectName = parObjName
                                        Subwhere_string = "" + str(where_string) + ""

                                        SubChildData = self.getProfileChildOne(
                                            SubNodeType,
                                            SubNodeName,
                                            RecAttValue,
                                            nodeId,
                                            SubParRecId,
                                            SubChildDynamicQuery,
                                            ObjectName,
                                            ParRecId,
                                            Subwhere_string,
                                            PageRecId,
                                            ObjectRecId,
                                            ordersBy,
                                        )

                                    if len(SubChildData) > 0:
                                        NewList.append(SubChildData)
                                        list2 = []
                                        for sublist in NewList:
                                            for item in sublist:
                                                list2.append(item)
                                        ChildDict["nodes"] = list2
                                NewList = []
                                ChildList.append(ChildDict)

        else:
            findChildOneObj = Sql.GetList(
                "SELECT top 1000 * FROM SYTRND (nolock) where TREE_NODE_RECORD_ID = '"
                + str(ParRecId)
                + "' AND DISPLAY_CRITERIA != 'DYNAMIC' AND NODE_TYPE = 'STATIC'"
            )
            if findChildOneObj is not None and len(findChildOneObj) > 0:
                for findChildOne in findChildOneObj:
                    if DynamicQuery is not None and len(DynamicQuery) > 0:
                        DynamicQuery = (
                            DynamicQuery.replace("{", "")
                            .replace("}", "")
                            .replace("RecAttValue", RecAttValue)
                            .replace("where_string", where_string)
                        )
                        childQuery = Sql.GetList("" + str(DynamicQuery) + "")
                    ChildDict = {}
                    SubChildData = []
                    ParRecId = str(findChildOne.TREE_NODE_RECORD_ID)
                    NodeText = str(findChildOne.NODE_DISPLAY_NAME)
                    ChildDict["text"] = NodeText
                    ChildDict["id"] = str(ParRecId)
                    ChildDict["nodeId"] = str(findChildOne.NODE_ID)
                    ParpageRecId = str(findChildOne.NODE_PAGE_RECORD_ID)
                    pageDetails = Sql.GetFirst("select * from SYPAGE (nolock) where RECORD_ID = '" + str(ParpageRecId) + "'")
                    if pageDetails is not None:
                        objRecId = pageDetails.OBJECT_RECORD_ID
                        objQuery = Sql.GetFirst("SELECT OBJECT_NAME FROM SYOBJH(NOLOCK) WHERE RECORD_ID = '" + str(objRecId) + "'")
                        if objQuery is not None:
                            ChildDict["objname"] = objQuery.OBJECT_NAME
                    SubTabList = []
                    getParentObjRightView = Sql.GetList(
                        "SELECT top 1000 * FROM SYSTAB (nolock) where TREE_NODE_RECORD_ID = '"
                        + str(ParRecId)
                        + "' ORDER BY abs(DISPLAY_ORDER) "
                    )
                    if getParentObjRightView is not None and len(getParentObjRightView) > 0:
                        for getRightView in getParentObjRightView:
                            type = str(getRightView.SUBTAB_TYPE)
                            subTabName = str(getRightView.SUBTAB_NAME)
                            ObjRecId = getRightView.OBJECT_RECORD_ID
                            RelatedId = getRightView.RELATED_RECORD_ID
                            RelatedName = getRightView.RELATED_LIST_NAME
                            ChildDict["id"] = RelatedId
                            if subTabName:
                                SubTabList.append(self.getSubtabRelatedDetails(subTabName, type, ObjRecId, RelatedId, RelatedName))
                    else:
                        if pageDetails is not None:
                            pageType = pageDetails.PAGE_TYPE
                            subTabName = "No SubTab"
                            objRecId = pageDetails.OBJECT_RECORD_ID
                            if NodeText == "Variable":
                                querystr = "AND NAME = '" + str(NodeText) + "'"
                            else:
                                querystr = ""
                            SubTabList.append(self.getPageRelatedDetails(subTabName, pageType, objRecId, ObjectRecId, querystr))
                            RelatedObj = Sql.GetFirst(
                                "SELECT RECORD_ID, SAPCPQ_ATTRIBUTE_NAME, NAME FROM SYOBJR(NOLOCK) WHERE PARENT_LOOKUP_REC_ID = '"
                                + str(ObjectRecId)
                                + "' AND OBJ_REC_ID = '"
                                + str(objRecId)
                                + "' AND VISIBLE = 'True'"
                            )
                            if RelatedObj is not None:
                                ChildDict["id"] = RelatedObj.SAPCPQ_ATTRIBUTE_NAME
                    ChildDict["SubTabs"] = SubTabList

                    findSubChildAvailable = Sql.GetList(
                        "SELECT TOP 1000 * FROM SYTRND (nolock) WHERE PARENT_NODE_RECORD_ID='"
                        + str(ParRecId)
                        + "' AND DISPLAY_CRITERIA != 'DYNAMIC' ORDER BY abs(DISPLAY_ORDER) "
                    )

                    if findSubChildAvailable is not None:
                        for findSubChildOne in findSubChildAvailable:
                            parobj = str(findSubChildOne.PARENTNODE_OBJECT)
                            NodeType = str(findSubChildOne.NODE_TYPE)
                            NodeApiName = str(findSubChildOne.NODE_DISPLAY_NAME)
                            DynamicQuery = str(findSubChildOne.DYNAMIC_NODEDATA_QUERY)
                            PageRecId = str(findSubChildOne.NODE_PAGE_RECORD_ID)
                            ordersBy = str(findSubChildOne.ORDERS_BY)
                            ParRecId = str(findSubChildOne.TREE_NODE_RECORD_ID)
                            if parobj == "True":
                                childwhere_string = " " + str(where_string) + ""

                                SubChildData = self.getChildFromParentObj(
                                    NodeText,
                                    NodeType,
                                    NodeName,
                                    RecAttValue,
                                    nodeId,
                                    ParRecId,
                                    DynamicQuery,
                                    ObjectName,
                                    RecId,
                                    childwhere_string,
                                    PageRecId,
                                    ObjectRecId,
                                    NodeApiName,
                                    ordersBy,
                                )
                            else:
                                SubNodeName = str(findSubChildOne.NODE_DISPLAY_NAME)
                                SubParRecId = str(findSubChildOne.TREE_NODE_RECORD_ID)

                                subDynamicQuery = str(findSubChildOne.DYNAMIC_NODEDATA_QUERY)
                                SubNodeType = str(findSubChildOne.NODE_TYPE)
                                nodeId = str(findSubChildOne.NODE_ID)
                                where_string = " 1=1"
                                Subwhere_string = str(where_string)
                                # Filter based on service type - Services Node - Start

                                CurrentTabName = TestProduct.CurrentTab

                                if NodeText in ("Actions", "Tabs"):
                                    if NodeText == "Tabs":
                                        apps = Product.GetGlobal("APPS")
                                        Subwhere_string += " AND APP_ID ='{}'".format(str(apps))
                                    else:
                                        Subwhere_string += " AND SERVICE_TYPE = '{}'".format(NodeText)
                                elif NodeText in ("Pages"):
                                    if NodeText == "Pages":
                                        page_tab = Product.GetGlobal("page_tab")
                                        Subwhere_string += " AND TAB_LABEL = '{}'".format(page_tab)

                                elif NodeText in ("Tree Node"):
                                    RecAttValue = Product.Attributes.GetByName("QSTN_SYSEFL_SY_01110").GetValue()
                                    getpagename = Sql.GetList(
                                        "select TREE_RECORD_ID from SYTREE(NOLOCK) where PAGE_RECORD_ID = '" + str(RecAttValue) + "'"
                                    )
                                    for tree in getpagename:

                                        Tree_Node = str(tree.TREE_RECORD_ID)
                                    Subwhere_string += " AND TREE_RECORD_ID = '" + str(Tree_Node) + "'"

                                PageRecId = str(findSubChildOne.NODE_PAGE_RECORD_ID)
                                # Filter based on service type - Services Node - End
                                SubChildData = self.getProfileChildOne(
                                    SubNodeType,
                                    SubNodeName,
                                    RecAttValue,
                                    nodeId,
                                    SubParRecId,
                                    subDynamicQuery,
                                    ObjectName,
                                    RecId,
                                    Subwhere_string,
                                    PageRecId,
                                    ObjectRecId,
                                    ordersBy,
                                )

                            if len(SubChildData) > 0:
                                NewList.append(SubChildData)
                                list2 = []
                                for sublist in NewList:
                                    for item in sublist:
                                        list2.append(item)
                                ChildDict["nodes"] = list2
                    NewList = []
                    ChildList.append(ChildDict)
        return ChildList

    def getChildOne(
        self,
        NodeType,
        NodeName,
        RecAttValue,
        nodeId,
        NodeText,
        ParRecId,
        DynamicQuery,
        ObjectName,
        RecId,
        where_string,
        PageRecId,
        ObjectRecId,
        ordersBy,
    ):
        NodeValue = ""
        NodeText1 = ""
        NodeText_temp = ""
        ChildList = []
        NewList = []

        try:
            contract_quote_record_id = Quote.GetGlobal("contract_quote_record_id")
            quote_revision_record_id = Quote.GetGlobal("quote_revision_record_id")
            getAccounts = Sql.GetFirst(
                "SELECT CpqTableEntryId FROM SAQTIP (NOLOCK) WHERE CPQ_PARTNER_FUNCTION = 'RECEIVING ACCOUNT' AND QUOTE_RECORD_ID = '{}'".format(
                    contract_quote_record_id
                )
            )
        except:
            contract_quote_record_id = ""
            quote_revision_record_id = ""
            getAccounts = ""

        if str(NodeType) == "DYNAMIC":
            try:
                ContAtt = Product.Attributes.GetByName("QSTN_SYSEFL_QT_016909")
            except:
                ContAtt = ""
            try:
                ContAttValue = ContAtt.GetValue()
            except Exception:
                try:
                    ContAttValue = Quote.GetGlobal("contract_record_id")
                except:
                    ContAttValue = ""
            pageDetails = Sql.GetFirst("select * from SYPAGE (nolock) where RECORD_ID = '" + str(PageRecId) + "'")
            if pageDetails is not None:
                OBJECT_RECORD_ID = pageDetails.OBJECT_RECORD_ID
                ObjName = pageDetails.OBJECT_APINAME
                CurrentTabName = pageDetails.TAB_NAME
                if str(ObjName) == "USERS" and str(ObjectName) == "cpq_permissions":
                    objd_where_obj = Sql.GetFirst("select * from SYOBJD (nolock) where OBJECT_NAME = '" + str(ObjName) + "'")
                elif str(ObjName).strip() == "SAQSFB" and str(NodeName).strip() == "FABLOCATION_ID":
                    ObjectName = "SAQTMT"
                    objd_where_obj = Sql.GetFirst(
                        "select * from SYOBJD (nolock) where OBJECT_NAME = '"
                        + str(ObjName)
                        + "' AND LOOKUP_OBJECT = '"
                        + str(ObjectName)
                        + "'"
                    )
                elif str(ObjName).strip() == "SYPRSF":
                    objd_where_obj = Sql.GetFirst(
                        "select * from SYOBJD (nolock) where OBJECT_NAME = '"
                        + str(ObjName)
                        + "' AND LOOKUP_OBJECT = '"
                        + str(ObjectName)
                        + "'"
                    )
                elif str(ObjName).strip() == "SAQFBL" and str(NodeName).strip() == "FABLOCATION_ID":
                    ObjectName = "SAQTMT"
                    objd_where_obj = Sql.GetFirst(
                        "select * from SYOBJD (nolock) where OBJECT_NAME = '"
                        + str(ObjName)
                        + "' AND LOOKUP_OBJECT = '"
                        + str(ObjectName)
                        + "'"
                    )
                elif str(ObjName).strip() == "SAQSSF" and str(NodeName).strip() == "SNDFBL_ID":
                    ObjectName = "SAQTMT"
                    objd_where_obj = Sql.GetFirst(
                        "select * from SYOBJD (nolock) where OBJECT_NAME = '"
                        + str(ObjName)
                        + "' AND LOOKUP_OBJECT = '"
                        + str(ObjectName)
                        + "'"
                    )
                elif str(ObjName).strip() == "SYPSAC" and CurrentTabName == "App":
                    getsectrec = Product.GetGlobal("NodeRecIdS")
                    where_string += " AND SECTION_RECORD_ID = '" + str(getsectrec) + "'"
                elif str(ObjName).strip() == "SYPSAC":
                    ObjectName = "SYSECT"
                    objd_where_obj = Sql.GetFirst(
                        "select * from SYOBJD (nolock) where OBJECT_NAME = '"
                        + str(ObjName)
                        + "' AND LOOKUP_OBJECT = '"
                        + str(ObjectName)
                        + "'"
                    )
                elif str(ObjName).strip() == "ACAPMA" and str(NodeName).strip() == "APRCHN_ID":
                    objd_where_obj = Sql.GetFirst("select * from SYOBJD (nolock) where OBJECT_NAME = '" + str(ObjName) + "'")
                elif (
                    str(ObjName).strip() == "ACACST" and str(NodeName).strip() == "APRCHNSTP_NAME" and str(ProductName).upper() == "SALES"
                ):
                    objd_where_obj = Sql.GetFirst("select * from SYOBJD (nolock) where OBJECT_NAME = '" + str(ObjName) + "'")
                # A055S000P01-3618 code starts..
                elif (
                    str(ObjName).strip() == "ACACHR" and str(NodeName).strip() == "APPROVAL_ROUND" and str(ProductName).upper() == "SALES"
                ):
                    objd_where_obj = Sql.GetFirst("select * from SYOBJD (nolock) where OBJECT_NAME = '" + str(ObjName) + "'")
                # A055S000P01-3618 code ends..
                elif (
                    str(ObjName).strip() == "ACAPTX"
                    and str(NodeName).strip() == "APRCHNSTP_APPROVER_ID"
                    and str(ProductName).upper() == "SALES"
                ):
                    objd_where_obj = Sql.GetFirst("select * from SYOBJD (nolock) where OBJECT_NAME = '" + str(ObjName) + "'")
                elif (
                    str(ObjName).strip() == "ACAPTF"
                    and str(ProductName).upper() == "APPROVAL CENTER"
                    and (str(NodeName).strip() == "TRKOBJ_NAME" or str(NodeName).strip() == "TRKOBJ_TRACKEDFIELD_LABEL")
                ):
                    objd_where_obj = Sql.GetFirst("select * from SYOBJD (nolock) where OBJECT_NAME = '" + str(ObjName) + "'")
                elif str(ObjName).strip() == "CTCSGB":
                    ObjectName = "CTCNRT"
                    objd_where_obj = Sql.GetFirst(
                        "select * from SYOBJD (nolock) where OBJECT_NAME = '"
                        + str(ObjName)
                        + "' AND LOOKUP_OBJECT = '"
                        + str(ObjectName)
                        + "'"
                    )
                else:
                    objd_where_obj = Sql.GetFirst(
                        "select * from SYOBJD (nolock) where OBJECT_NAME = '"
                        + str(ObjName)
                        + "' AND LOOKUP_OBJECT = '"
                        + str(ObjectName)
                        + "'"
                    )
                try:
                    CurrentTabName = TestProduct.CurrentTab
                except:
                    CurrentTabName = "Quotes"
                if CurrentTabName in ("Quotes", "Quote"):
                    quote_obj = Sql.GetFirst(
                        "select QUOTE_ID,MASTER_TABLE_QUOTE_RECORD_ID from SAQTMT (NOLOCK) where MASTER_TABLE_QUOTE_RECORD_ID = '{}' AND QTEREV_RECORD_ID ='{}'".format(
                            contract_quote_record_id, quote_revision_record_id
                        )
                    )
                    if quote_obj:
                        quote_id = quote_obj.QUOTE_ID
                if objd_where_obj is not None:
                    if str(ObjName) == "USERS" and str(ObjectName) == "cpq_permissions":
                        Wh_API_NAME = ""
                        where_string = where_string
                    elif str(ObjName).strip() == "SAQSSF" and str(NodeName).strip() == "SNDFBL_ID":
                        where_string = " QUOTE_RECORD_ID = '{quote}' AND SERVICE_ID = '{service}' AND QTEREV_RECORD_ID = '{quote_revision_record_id}'".format(
                            contract_quote_record_id, service=Quote.GetGlobal("SERVICE"), quote_revision_record_id=quote_revision_record_id
                        )
                    elif str(ObjName).strip() == "SAQSFB" and str(NodeName).strip() == "FABLOCATION_ID":
                        where_string = " QUOTE_RECORD_ID = '{quote}' AND SERVICE_ID = '{service}' AND FABLOCATION_ID != '' AND QTEREV_RECORD_ID = '{quote_revision_record_id}'".format(
                            quote=contract_quote_record_id,
                            service=Quote.GetGlobal("SERVICE"),
                            quote_revision_record_id=quote_revision_record_id,
                        )
                    elif str(ObjName).strip() == "ACACSA" and str(NodeName).strip() == "APRCHNSTP_APPROVER_ID":
                        where_string = where_string
                    elif str(ObjName).strip() == "ACAPMA" and str(NodeName).strip() == "APRCHN_ID":
                        where_string = "ACAPMA.APRTRXOBJ_RECORD_ID = '{}'".format(quote_revision_record_id)
                        Product.SetGlobal("aprchn_id", "yes")
                    # A055S000P01-3618 code starts..
                    elif (
                        str(ObjName).strip() == "ACACHR"
                        and str(NodeName).strip() == "APPROVAL_ROUND"
                        and str(ProductName).upper() == "SALES"
                    ):
                        where_string += (
                            " AND ACACHR.APPROVAL_ID LIKE '%{quote_id}%' ORDER BY ACACHR.APPROVAL_ROUND DESC,ACACHR.APPROVAL_CHAIN_ROUND_RECORD_ID, ACACHR.APPROVAL_ID"
                            "".format(quote_id=quote_id)
                        )
                    # A055S000P01-3618 code ends..
                    if str(ObjName).strip() == "SAQSAO":
                        where_string = where_string
                        where_string += """ AND QUOTE_RECORD_ID = '{contract_quote_record_id}' AND QTEREV_RECORD_ID = '{quote_revision_record_id}'""".format(
                            contract_quote_record_id=contract_quote_record_id, quote_revision_record_id=quote_revision_record_id
                        )
                    elif str(ObjName).strip() == "SYPRTB":
                        RecAttValue = Product.Attributes.GetByName("QSTN_SYSEFL_SY_00125").GetValue()
                        where_string = "1=1 AND"
                        getapptext = Product.GetGlobal("setappname")
                        where_string += "  APP_ID = '" + str(getapptext) + "' AND  PROFILE_RECORD_ID = '" + str(RecAttValue) + "'"
                    elif str(ObjName).strip() == "SYPRSN":
                        RecAttValue = Product.Attributes.GetByName("QSTN_SYSEFL_SY_00125").GetValue()
                        where_string = "1=1 AND"
                        gettabtext = Product.GetGlobal("settabname")
                        getpagename = Sql.GetFirst("select TAB_RECORD_ID from SYPRTB (NOLOCK) where TAB_ID = '" + str(gettabtext) + "'")
                        if getpagename:
                            where_string += (
                                " PROFILE_RECORD_ID = '"
                                + str(RecAttValue)
                                + "' and TAB_RECORD_ID = '"
                                + str(getpagename.TAB_RECORD_ID)
                                + "'"
                            )
                        else:
                            where_string += " PROFILE_RECORD_ID = '" + str(RecAttValue) + "'"
                    elif str(ObjName).strip() == "SYPRSF" and CurrentTabName == "Profile":
                        RecAttValue = Product.Attributes.GetByName("QSTN_SYSEFL_SY_00125").GetValue()
                        where_string = "1=1 AND"
                        gettabtext = Product.GetGlobal("settabname")
                        getsectid = Product.GetGlobal("NodeSecRecIdS")

                        getsectname = Sql.GetFirst(
                            "select SECTION_RECORD_ID from SYPRSN(NOLOCK) where PROFILE_SECTION_RECORD_ID = '"
                            + str(getsectid)
                            + "' and PROFILE_RECORD_ID = '"
                            + str(RecAttValue)
                            + "'"
                        )
                        if getsectname:
                            where_string += (
                                " PROFILE_RECORD_ID = '"
                                + str(RecAttValue)
                                + "' and SECTION_RECORD_ID = '"
                                + str(getsectname.SECTION_RECORD_ID)
                                + "'"
                            )
                        else:
                            where_string += (
                                " PROFILE_RECORD_ID = '"
                                + str(RecAttValue)
                                + "' and SECTION_RECORD_ID = '"
                                + str(getsectname.SECTION_RECORD_ID)
                                + "'"
                            )
                    elif str(ObjName).strip() == "SYSECT" and CurrentTabName == "App":
                        getnodetext = Product.GetGlobal("setnodetextname")
                        where_string += " AND PAGE_LABEL = '" + str(getnodetext) + "'"
                    elif str(ObjName).strip() == "SYSEFL" and CurrentTabName == "App":
                        getsectrec = Product.GetGlobal("NodeRecIdS")
                        where_string += " AND SECTION_RECORD_ID = '" + str(getsectrec) + "'"
                    elif str(NodeName).strip() == "PAGE_LABEL" and CurrentTabName == "App":
                        where_string = where_string
                    elif str(ObjName).strip() == "SYPGAC" and CurrentTabName == "App":
                        getnodetext = Product.GetGlobal("setnodetextname")
                        getpagename = Sql.GetFirst("select PAGE_NAME from SYPAGE (NOLOCK) where PAGE_LABEL = '" + str(getnodetext) + "'")
                        if getpagename:
                            where_string += " AND PAGE_NAME = '" + str(getpagename.PAGE_NAME) + "'"
                        else:
                            where_string = where_string
                    elif str(ObjName).strip() == "SYPAGE" and str(NodeName).strip() == "PAGE_NAME" and CurrentTabName == "Tab":
                        RecAttValue = Product.Attributes.GetByName("QSTN_SYSEFL_SY_03295").GetValue()
                        Product.SetGlobal("TabId", str(RecAttValue))
                        where_string = where_string
                        where_string += " AND TAB_RECORD_ID = '" + str(RecAttValue) + "'"
                    elif NodeName == "ACTION_NAME" and str(ObjName).strip() == "SYPGAC" and CurrentTabName == "Tab":
                        RecAttValue = Product.Attributes.GetByName("QSTN_SYSEFL_SY_03295").GetValue()
                        where_string = " TAB_RECORD_ID = '{}' AND PAGE_NAME = '{}'".format(RecAttValue, Product.GetGlobal("pagename"))
                        where_string = where_string
                    elif str(ObjName).strip() == "SYTRND" and str(NodeName).strip() == "NODE_NAME" and CurrentTabName == "Page":
                        RecAttValue = Product.Attributes.GetByName("QSTN_SYSEFL_SY_01110").GetValue()
                        where_string += " AND NODE_PAGE_RECORD_ID = '" + str(RecAttValue) + "' "
                    elif str(ObjName).strip() == "SAQTIP" and str(NodeName).strip() == "PARTY_ID":
                        where_string += " AND QUOTE_RECORD_ID ='{}' AND (CPQ_PARTNER_FUNCTION LIKE '%SENDING%' OR CPQ_PARTNER_FUNCTION LIKE '%RECEIVING%')  AND QTEREV_RECORD_ID = '{}'".format(
                            contract_quote_record_id, quote_revision_record_id
                        )
                    elif str(ObjName).strip() == "SAQRGG" and str(NodeName).strip() == "GOT_CODE":
                        greenbook = Quote.GetGlobal("Z0009_Greenbook")
                        where_string = "QUOTE_RECORD_ID ='{}' AND GREENBOOK = '{}' AND QTEREV_RECORD_ID = '{}'".format(
                            contract_quote_record_id, greenbook, quote_revision_record_id
                        )
                    elif str(NodeName).strip() == "PM_ID":
                        greenbook = Quote.GetGlobal("Z0009_Greenbook")
                        gotcode = Quote.GetGlobal("Z0009_Gotcode")
                        where_string = "QUOTE_RECORD_ID ='{}' AND GREENBOOK = '{}' AND QTEREV_RECORD_ID = '{}' AND GOT_CODE = '{}'".format(
                            contract_quote_record_id, greenbook, quote_revision_record_id, gotcode
                        )
                    elif str(ObjName).strip() == "SAQFBL" and str(NodeName).strip() == "FABLOCATION_ID":
                        send_receive_node_text = Product.GetGlobal("setnodetextname")
                        if send_receive_node_text.startswith("Sending"):
                            where_string = (
                                " QUOTE_RECORD_ID ='{}' AND RELOCATION_FAB_TYPE = 'SENDING FAB' AND QTEREV_RECORD_ID = '{}'".format(
                                    contract_quote_record_id, quote_revision_record_id
                                )
                            )
                        elif send_receive_node_text.startswith("Receiving"):
                            where_string = (
                                " QUOTE_RECORD_ID ='{}' AND RELOCATION_FAB_TYPE = 'RECEIVING FAB' AND QTEREV_RECORD_ID = '{}'".format(
                                    contract_quote_record_id, quote_revision_record_id
                                )
                            )
                        else:
                            where_string = " QUOTE_RECORD_ID ='{}' AND QTEREV_RECORD_ID = '{}'".format(
                                contract_quote_record_id, quote_revision_record_id
                            )
                    else:
                        Wh_API_NAME = objd_where_obj.API_NAME
                        if RecAttValue and str(NodeName).strip() != "APRCHN_ID" and str(ObjName).strip() != "ACAPMA":
                            where_string = " " + str(where_string) + " AND " + str(Wh_API_NAME) + " = '" + str(RecAttValue) + "'"
                        else:
                            where_string = where_string

                    childRecName = Sql.GetFirst(
                        "select * from SYOBJD (nolock) where OBJECT_NAME = '" + str(ObjName) + "' AND DATA_TYPE = 'AUTO NUMBER'"
                    )
                    if CurrentTabName != "Approval Chain":
                        if (
                            "QTEREV_RECORD_ID" not in where_string
                            and "ACAPMA" not in where_string
                            and "ACACHR" not in where_string
                            and "ACAPTX" not in where_string
                        ):

                            where_string += " AND QTEREV_RECORD_ID = '" + str(quote_revision_record_id) + "' "
                    if DynamicQuery is not None and len(DynamicQuery) > 0:
                        DynamicQuery = (
                            DynamicQuery.replace("{", "")
                            .replace("}", "")
                            .replace("RecAttValue", RecAttValue)
                            .replace("ContAttValue", ContAttValue)
                            .replace("where_string", where_string)
                        )
                        # ("DynamicQueryCHK1"+str(DynamicQuery))
                        childQuery = Sql.GetList("" + str(DynamicQuery) + "")
                    else:
                        if NodeName.find("-") == -1:
                            NodeValue = NodeName
                        else:
                            NodeValuesplit = NodeName.split("-")
                            if len(NodeValuesplit) > 1:
                                NodeValue = NodeValuesplit[1]
                        if ordersBy:
                            ordersByQuery = " ORDER BY " + str(ordersBy)
                            if NodeValue != ordersBy:
                                childQuery = Sql.GetList(
                                    "select distinct top 1000 "
                                    + str(NodeValue)
                                    + ", "
                                    + str(ordersBy)
                                    + " from "
                                    + str(ObjName)
                                    + " (nolock) where "
                                    + str(where_string)
                                    + " "
                                    + str(ordersByQuery)
                                    + ""
                                )
                            else:
                                childQuery = Sql.GetList(
                                    "select distinct top 1000 "
                                    + str(NodeValue)
                                    + " from "
                                    + str(ObjName)
                                    + " (nolock) where "
                                    + str(where_string)
                                    + " "
                                    + str(ordersByQuery)
                                    + ""
                                )
                        elif str(ObjName) == "SYPSAC":
                            if CurrentTabName == "Tab":
                                RecAttValue = Product.Attributes.GetByName("QSTN_SYSEFL_SY_03319").GetValue()
                                where_string += " TAB_NAME = '" + str(RecAttValue) + "'"
                            elif TabName == "Script":
                                where_string += " AND SCRIPT_RECORD_ID = '" + str(RecAttValue) + "'"
                            else:
                                where_string = where_string
                            ordersByQuery = ""
                            childQuery = Sql.GetList(
                                "select "
                                + str(NodeName)
                                + " from "
                                + str(ObjName)
                                + " (nolock) where "
                                + str(where_string)
                                + " "
                                + str(ordersByQuery)
                                + ""
                            )
                        elif str(ObjName).strip() == "SYPGAC":
                            if TabName == "Tab":
                                RecAttValue = Product.Attributes.GetByName("QSTN_SYSEFL_SY_03295").GetValue()
                                where_string = " TAB_RECORD_ID = '{}' AND PAGE_NAME = '{}'".format(
                                    RecAttValue, Product.GetGlobal("pagename")
                                )
                            ordersByQuery = ""
                            childQuery = Sql.GetList(
                                "select "
                                + str(NodeName)
                                + " from "
                                + str(ObjName)
                                + " (nolock) where "
                                + str(where_string)
                                + " "
                                + str(ordersByQuery)
                                + ""
                            )
                        elif str(ObjName) == "SYPRSF":
                            where_string += where_string
                            ordersByQuery = ""
                            childQuery = Sql.GetList(
                                "select "
                                + str(NodeName)
                                + " from "
                                + str(ObjName)
                                + " (nolock) where "
                                + str(where_string)
                                + " "
                                + str(ordersByQuery)
                                + ""
                            )
                        # SUBNODE IS NOT LOADING ISSUE FOR SECTIONS NODE IN PAGES TAB - START
                        elif str(ObjName) == "SYSECT":
                            where_string = " PAGE_RECORD_ID = '" + str(RecAttValue) + "'"
                            ordersByQuery = ""
                            childQuery = Sql.GetList(
                                "select "
                                + str(NodeName)
                                + " from "
                                + str(ObjName)
                                + " (nolock) where "
                                + str(where_string)
                                + " "
                                + str(ordersByQuery)
                                + ""
                            )
                        # SUBNODE IS NOT LOADING ISSUE FOR SECTIONS NODE IN PAGES TAB - END
                        elif str(ObjName) == "USERS":
                            ordersByQuery = ""
                            childQuery = Sql.GetList(
                                "SELECT DISTINCT top 1000 UPPER(US.USERNAME) AS USERNAME,US.ID,US.NAME,US.ACTIVE FROM USERS US WITH (NOLOCK) inner join users_permissions up on us.id = up.user_id inner join cpq_permissions cp on cp.permission_id = up.permission_id where cp.permission_type= '0' and up.permission_id = '"
                                + str(RecAttValue)
                                + "' order by USERNAME"
                            )
                        else:
                            ordersByQuery = ""
                            childQuery = Sql.GetList(
                                "select distinct "
                                + str(NodeName)
                                + " from "
                                + str(ObjName)
                                + " (nolock) where "
                                + str(where_string)
                                + " "
                                + str(ordersByQuery)
                                + ""
                            )
                    flag = 1
                    if str(ObjName).strip() == "SAQTIP" and str(NodeName).strip() == "PARTY_ID" and flag != 2:
                        flag = 1
                    if childQuery is not None:
                        for childdata in childQuery:
                            ChildDict = {}
                            SubChildData = []
                            aprchn_id = ""
                            if str(ObjName).strip() == "ACAPMA" and str(NodeName).strip() == "APRCHN_ID":
                                NodeText = str(eval("childdata." + str(NodeName)))
                                childQueryObj = Sql.GetFirst(
                                    "select DISTINCT TOP 10 ACAPMA.APPROVAL_RECORD_ID,ACAPCH.APRCHN_ID as APRLID, ACAPMA.APRCHN_RECORD_ID as APRL_REC_ID,ACAPCH.APPROVAL_CHAIN_RECORD_ID FROM ACAPMA (nolock) inner join ACAPCH (nolock) on ACAPCH.APPROVAL_CHAIN_RECORD_ID = ACAPMA.APRCHN_RECORD_ID  where "
                                    + str(where_string)
                                    + " AND ACAPMA.APRCHN_ID = '"
                                    + str(NodeText)
                                    + "' ORDER BY ACAPCH.APRCHN_ID,ACAPMA.APRCHN_RECORD_ID"
                                )
                            elif (
                                str(ObjName).strip() == "SAQSFB"
                                and str(NodeName).strip() == "FABLOCATION_ID"
                                and str(ProductName).upper() == "SALES"
                            ):
                                NodeText = str(eval("childdata." + str(NodeName)))
                                # Product.SetGlobal('fablocation_id_for_parts_list',str(NodeText))
                                childQueryObj = Sql.GetFirst(
                                    "select  SAQSCO.FABLOCATION_ID,SAQSFB.QUOTE_SERVICE_FAB_LOCATION_RECORD_ID from SAQSCO (nolock) INNER JOIN SAQSFB ON SAQSCO.QUOTE_RECORD_ID = SAQSFB.QUOTE_RECORD_ID AND SAQSFB.QTEREV_RECORD_ID = SAQSCO.QTEREV_RECORD_ID WHERE  SAQSFB.QUOTE_RECORD_ID = '{quote}' AND SAQSCO.SERVICE_ID = '{service}' AND SAQSCO.FABLOCATION_ID != '' AND SAQSFB.QTEREV_RECORD_ID = '{quote_revision_record_id}' and SAQSFB.FABLOCATION_ID = '{NodeText}'  ".format(
                                        quote=contract_quote_record_id,
                                        service=Quote.GetGlobal("SERVICE"),
                                        quote_revision_record_id=quote_revision_record_id,
                                        NodeText=NodeText,
                                    )
                                )
                            elif (
                                str(ObjName).strip() == "ACACHR"
                                and str(NodeName).strip() == "APPROVAL_ROUND"
                                and str(ProductName).upper() == "SALES"
                            ):  # A055S000P01-3618 code starts..
                                NodeText = "Round " + str(eval("childdata." + str(NodeName))).title()
                                childQueryObj = Sql.GetFirst(
                                    "select DISTINCT TOP 10 ACACHR.APPROVAL_CHAIN_ROUND_RECORD_ID,ACACHR.APPROVAL_ROUND, ACACHR.APPROVAL_ID,ACACHR.CpqTableEntryId FROM ACACHR (nolock) inner join ACAPTX (nolock) on ACAPTX.APRCHN_ID = ACACHR.APRCHN_ID where ACACHR.APPROVAL_ROUND = '{approval_round}' AND ".format(
                                        approval_round=NodeText.split(" ")[1]
                                    )
                                    + str(where_string)
                                )
                                ##for showing relevent subtab for approval in quote starts
                                try:
                                    if "APRCHN_ID" in str(where_string).strip().split(" ")[0]:
                                        aprchn_id = "AND ACAPCH.APRCHN_ID = {}".format(str(where_string).strip().split(" ")[2])
                                    else:
                                        aprchn_id = ""
                                except:
                                    aprchn_id = ""
                                ##for showing relevent subtab for approval in quote ends
                                ###A055S000P01-3618 code ends..
                            elif (
                                str(ObjName).strip() == "ACACSA"
                                and str(NodeName).strip() == "APRCHNSTP_APPROVER_ID"
                                and str(ProductName).upper() == "APPROVAL CENTER"
                            ):
                                NodeText = str(eval("childdata." + str(NodeName)))
                                childQueryObj = Sql.GetFirst(
                                    "select TOP 10 ACACSA.APPROVAL_CHAIN_STEP_APPROVER_RECORD_ID, ACACSA.APRCHN_ID,ACACSA.APRCHNSTP_RECORD_ID FROM ACACSA (nolock) inner join ACACST (nolock) on ACACST.APPROVAL_CHAIN_STEP_RECORD_ID = ACACSA.APRCHNSTP_RECORD_ID  AND "
                                    + str(NodeName)
                                    + " = '"
                                    + str(NodeText)
                                    + "'"
                                )
                            elif (
                                str(ObjName).strip() == "ACAPTF"
                                and str(NodeName).strip() == "TRKOBJ_TRACKEDFIELD_LABEL"
                                and str(ProductName).upper() == "APPROVAL CENTER"
                            ):
                                NodeText = str(eval("childdata." + str(NodeName)))
                                childQueryObj = Sql.GetFirst(
                                    "select distinct TRKOBJ_TRACKEDFIELD_LABEL,APPROVAL_TRACKED_FIELD_RECORD_ID FROM ACAPTF (NOLOCK) INNER JOIN ACAPTX ON ACAPTF.APRCHN_ID = ACAPTX.APRCHN_ID WHERE ACAPTX.APPROVAL_TRANSACTION_RECORD_ID = '"
                                    + str(RecAttValue)
                                    + "' AND "
                                    + str(NodeName)
                                    + " = '"
                                    + str(NodeText)
                                    + "'"
                                )
                            elif str(ObjName).strip() == "ACAPTX" and str(NodeName).strip() == "APPROVAL_ID":
                                childQueryObj = None
                                if TabName == "My Approvals Queue":
                                    Wherecondition = "AND ACAPTX.APPROVAL_RECIPIENT_RECORD_ID = '" + str(User.Id) + "' "
                                else:
                                    Wherecondition = "AND ACAPTX.APPROVAL_RECIPIENT_RECORD_ID <> '" + str(User.Id) + "' "
                                GetTranscationQuery = Sql.GetList(
                                    "SELECT DISTINCT convert(varchar(10), ACAPMA.CUR_APRCHNSTP_ENTRYDATE, 112) "
                                    + " as CUR_APRCHNSTP_ENTRYDATE, ACAPTX.APPROVALSTATUS, ACAPTX.APRCHNSTP_APPROVER_ID"
                                    + " ,ACAPTX.APPROVAL_RECIPIENT, ACAPTX.APPROVAL_TRANSACTION_RECORD_ID FROM ACAPTX "
                                    + " (nolock) inner join ACAPMA (nolock) on ACAPTX.APPROVAL_RECORD_ID = ACAPMA.APPROVAL_RECORD_ID"
                                    + " WHERE ACAPTX.APPROVAL_RECORD_ID = '{0}'".format(str(RecAttValue))
                                )
                                if GetTranscationQuery is not None:
                                    TracsactionList = []
                                    for datasaddr in GetTranscationQuery:
                                        ChildDict = {}
                                        nodeId = int(nodeId) + 1
                                        if str(datasaddr.APPROVALSTATUS) == "APPROVED":
                                            colorClass = "color: green; font-weight: bold;"
                                        elif str(datasaddr.APPROVALSTATUS) == "REJECTED":
                                            colorClass = "color: red; font-weight: bold;"
                                        else:
                                            colorClass = "color: gray; font-weight: bold;"
                                        APPROVALSTATUS = (
                                            '<span style="' + str(colorClass) + '">' + str(datasaddr.APPROVALSTATUS) + "</span>"
                                        )

                                        if User.Name == datasaddr.APPROVAL_RECIPIENT:
                                            NodeText = (
                                                str(datasaddr.CUR_APRCHNSTP_ENTRYDATE)
                                                + "-"
                                                + str(APPROVALSTATUS)
                                                + "-"
                                                + str(datasaddr.APRCHNSTP_APPROVER_ID)
                                                + "-"
                                                + str(datasaddr.APPROVAL_RECIPIENT)
                                            )
                                        else:
                                            NodeText = ""
                                        ChildDict["text"] = NodeText
                                        ChildDict["id"] = str(datasaddr.APPROVAL_TRANSACTION_RECORD_ID)
                                        ChildDict["nodeId"] = int(nodeId)
                                        ChildDict["objname"] = "ACAPTX"

                                        # ChildList.append(ChildDict)
                            elif NodeName.find(",") == -1 and NodeName.find("-") == -1:
                                Trace.Write("Node name--------1" + str(NodeName))
                                if str(NodeName) == "OBJECT_NAME" and TabName == "Profile":
                                    NodeText = str(eval("childdata." + str(NodeName)))
                                elif str(NodeName) == "PARTY_ID":
                                    if flag == 1:
                                        NodeText = "Sending Account - " + str(eval("childdata." + str(NodeName)))
                                        flag = 2
                                        Product.SetGlobal("setnodetextname", str(NodeText))
                                    else:
                                        NodeText = "Receiving Account - " + str(eval("childdata." + str(NodeName)))
                                        Product.SetGlobal("setnodetextname", str(NodeText))
                                else:
                                    NodeText = str(eval("childdata." + str(NodeName))).upper()
                                if str(NodeName) == "PAGE_NAME" and CurrentTabName.strip() == "Tab":
                                    Product.SetGlobal("pagename", str(NodeText))
                                if str(NodeName) == "PAGE_LABEL" and TabName == "App":
                                    Product.SetGlobal("setnodetextname", str(NodeText))
                                elif str(NodeName) == "APP_ID" and TabName == "Profile":
                                    Product.SetGlobal("setappname", str(NodeText))
                                elif str(NodeName) == "TAB_ID" and TabName == "Profile":
                                    Product.SetGlobal("settabname", str(NodeText))
                                elif str(NodeName) == "SERVICE_ID":
                                    Quote.SetGlobal("SERVICE", NodeText)
                                elif str(NodeName) in ["Sending Equipment", "Receiving Equipment"]:
                                    Quote.SetGlobal("Equipment", NodeText)
                                elif str(NodeName) == "GREENBOOK":
                                    Quote.SetGlobal("Z0009_Greenbook", NodeText)
                                elif str(NodeName) == "GOT_CODE":
                                    Quote.SetGlobal("Z0009_Gotcode", NodeText)
                                """ elif str(NodeName) == "TAB_NAME" and TabName == "App":
									Product.SetGlobal('apptabname',str(NodeText)) """
                                childQueryObj = Sql.GetFirst(
                                    "select * from "
                                    + str(ObjName)
                                    + " (nolock) where "
                                    + str(where_string)
                                    + " AND "
                                    + str(NodeName)
                                    + " = '"
                                    + str(NodeText)
                                    + "'"
                                )
                                if str(NodeName) == "TREE_NAME":
                                    Product.SetGlobal("TreeName", str(NodeText))
                            elif NodeName.find(",") > 0:
                                Trace.Write("Node name--------2" + str(NodeName))
                                Nodesplit = NodeName.split(",")
                                if len(Nodesplit) > 1:
                                    NodeName1 = Nodesplit[0]
                                    NodeText = str(eval("childdata." + str(NodeName1))).title()
                                    childQueryObj = Sql.GetFirst(
                                        "select * from "
                                        + str(ObjName)
                                        + " (nolock) where "
                                        + str(where_string)
                                        + " AND "
                                        + str(NodeName1)
                                        + " = '"
                                        + (NodeText)
                                        + "'"
                                    )
                                    NodeText += " - "
                                    NodeName1 = Nodesplit[1]
                                    NodeText += str(eval("childdata." + str(NodeName1)))
                                    childQueryObj = Sql.GetFirst(
                                        "select * from "
                                        + str(ObjName)
                                        + " (nolock) where "
                                        + str(where_string)
                                        + " AND "
                                        + str(NodeName1)
                                        + " = '"
                                        + str(eval("childdata." + str(NodeName1)))
                                        + "'"
                                    )
                            elif NodeName.find("-") > 0:
                                Trace.Write("Node name--------3" + str(NodeName))
                                Nodesplit = NodeName.split("-")
                                if len(Nodesplit) > 1:
                                    NodeName1 = Nodesplit[0]
                                    NodeName2 = Nodesplit[1]
                                    NodeText1 = str(eval("childdata." + str(NodeName2))).title()
                                    NodeText = NodeName1 + "-" + NodeText1
                                    childQueryObj = Sql.GetFirst(
                                        "select * from "
                                        + str(ObjName)
                                        + " (nolock) where "
                                        + str(where_string)
                                        + " AND "
                                        + str(NodeName2)
                                        + " = '"
                                        + str(NodeText1)
                                        + "'"
                                    )

                            if childQueryObj is not None:
                                NodeRecId = str(eval("childQueryObj." + str(childRecName.API_NAME)))
                                ChildDict["id"] = str(NodeRecId)
                                if str(NodeName) == "SECTION_NAME" and TabName == "App":
                                    Product.SetGlobal("NodeRecIdS", NodeRecId)
                                elif str(NodeName) == "SECTION_ID" and TabName == "Profile":
                                    Product.SetGlobal("NodeSecRecIdS", NodeRecId)
                            if NodeText == "True":
                                NodeRecId = ""
                                ChildDict["text"] = "Active"
                            elif NodeText == "False":
                                NodeRecId = ""
                                ChildDict["text"] = "Inactive"
                            else:
                                NodeRecId = ""
                                if (
                                    str(ObjectName).strip() == "ACAPCH"
                                    and str(NodeName) == "APRCHNSTP_NAME"
                                    and str(ProductName).upper() == "APPROVAL CENTER"
                                ):
                                    NodeText = "Step " + str(childdata.APRCHNSTP_NUMBER) + " : " + str(NodeText)
                                ##showing config status along with offering
                                if str(ObjName).strip() == "SAQTSV" and str(NodeName) == "SERVICE_ID":
                                    service_id = NodeText
                                    image_url = ""
                                    try:
                                        get_status = Sql.GetFirst(
                                            "SELECT CONFIGURATION_STATUS FROM SAQTSE(NOLOCK) WHERE QUOTE_RECORD_ID = '{}' AND QTEREV_RECORD_ID = '{}' AND SERVICE_ID ='{}'".format(
                                                contract_quote_record_id, quote_revision_record_id, NodeText
                                            )
                                        )
                                        if get_status:
                                            if get_status.CONFIGURATION_STATUS == "COMPLETE":
                                                image_url = "config_status_icon.png"
                                            elif get_status.CONFIGURATION_STATUS == "INCOMPLETE":
                                                image_url = "config_pend_status_icon.png"
                                            elif get_status.CONFIGURATION_STATUS == "ERROR":
                                                image_url = "config_incomp_status_icon.png"
                                    except:
                                        image_url = ""
                                    if image_url:
                                        image_url = '<img class="leftside-bar-status_icon" src="/mt/appliedmaterials_tst/Additionalfiles/AMAT/Quoteimages/{image_url}"/>'.format(
                                            image_url=image_url
                                        )
                                        NodeText = image_url + NodeText
                                ##concatenate name with ID
                                if (str(ObjName).strip() == "SAQFBL" or str(ObjName).strip() == "SAQSFB") and str(
                                    NodeName
                                ) == "FABLOCATION_ID":
                                    get_fab_name = Sql.GetFirst(
                                        "SELECT * FROM {} (NOLOCK) WHERE {} AND FABLOCATION_ID = '{}'".format(
                                            ObjName, where_string, NodeText
                                        )
                                    )
                                    if get_fab_name:
                                        NodeText_temp = NodeText + " - " + get_fab_name.FABLOCATION_NAME
                                elif str(ObjName).strip() == "SAQRIB" and str(NodeName) == "PRDOFR_ID":
                                    get_service_name_bill = Sql.GetFirst(
                                        "SELECT * FROM SAQTSV(NOLOCK) WHERE {} AND SERVICE_ID = '{}'".format(where_string, NodeText)
                                    )
                                    if get_service_name_bill:
                                        NodeText_temp = NodeText + " - " + get_service_name_bill.SERVICE_DESCRIPTION
                                if NodeText_temp:
                                    ChildDict["text"] = NodeText_temp
                                else:
                                    ChildDict["text"] = NodeText
                            ChildDict["nodeId"] = int(nodeId)
                            objQuery = Sql.GetFirst(
                                "SELECT OBJECT_NAME FROM SYOBJH(NOLOCK) WHERE RECORD_ID = '" + str(OBJECT_RECORD_ID) + "'"
                            )
                            if objQuery is not None:
                                ChildDict["objname"] = objQuery.OBJECT_NAME
                                parObjName = objQuery.OBJECT_NAME
                            SubTabList = []
                            getParentObjRightView = Sql.GetList(
                                "SELECT top 1000 * FROM SYSTAB (nolock) where TREE_NODE_RECORD_ID = '"
                                + str(ParRecId)
                                + "' ORDER BY abs(DISPLAY_ORDER) "
                            )
                            if getParentObjRightView is not None and len(getParentObjRightView) > 0:
                                for getRightView in getParentObjRightView:
                                    type = str(getRightView.SUBTAB_TYPE)
                                    subTabName = str(getRightView.SUBTAB_NAME)
                                    ObjRecId = getRightView.OBJECT_RECORD_ID
                                    if (
                                        str(ObjRecId) == "354C16C4-BDCA-4045-BC4A-40F1A6600AFD"
                                        and str(getRightView.SUBTAB_TYPE) == "OBJECT SECTION LAYOUT"
                                    ):
                                        subTabName = str(NodeText) + " : " + str(subTabName)
                                    elif (
                                        str(ObjRecId) == "354C16C4-BDCA-4045-BC4A-40F1A6600AFD"
                                        and str(getRightView.SUBTAB_TYPE) == "OBJECT RELATED LAYOUT"
                                    ):
                                        subTabName = str(NodeText) + " : " + str(subTabName)
                                    elif getAccounts is None and (
                                        subTabName == "Sending Equipment" or subTabName == "Receiving Equipment"
                                    ):
                                        subTabName = ""
                                    # A055S000P01-14557 - New Parts, Inclusion , Exclusion Subtabs starts
                                    elif subTabName in (
                                        "Events",
                                        "Service New Parts",
                                        "Service Parts List",
                                        "Service Inclusions",
                                        "Greenbook Inclusions",
                                        "Green Parts List",
                                        "Green New Parts",
                                    ):
                                        ent_table_list = ["SAQTSE"]
                                        subtab_temp_variable = subTabName
                                        whr_str_greenbook = ""
                                        ent_table = ""
                                        subTabName = ""
                                        ent_value_dict = {}
                                        service_id = Quote.GetGlobal("SERVICE")
                                        if subtab_temp_variable in ("Greenbook Inclusions", "Green Parts List", "Green New Parts"):
                                            whr_str_greenbook = " AND GREENBOOK = '{}'".format(NodeText)
                                            ent_table_list.append("SAQSGE")
                                        ent_value_dict["SAQSGE"] = ""
                                        ent_value_dict["SAQTSE"] = ""
                                        for ent_table in ent_table_list:
                                            get_entitlement_xml = Sql.GetFirst(
                                                """select ENTITLEMENT_XML from {ent_table} (NOLOCK) WHERE QUOTE_RECORD_ID = '{QuoteRecordId}' AND QTEREV_RECORD_ID = '{RevisionRecordId}' AND SERVICE_ID = '{service_id}' {whr_str_greenbook}""".format(
                                                    QuoteRecordId=contract_quote_record_id,
                                                    RevisionRecordId=quote_revision_record_id,
                                                    service_id=service_id,
                                                    ent_table=ent_table,
                                                    whr_str_greenbook=whr_str_greenbook if ent_table == "SAQSGE" else "",
                                                )
                                            )
                                            if get_entitlement_xml:
                                                pattern_tag = re.compile(r"(<QUOTE_ITEM_ENTITLEMENT>[\w\W]*?</QUOTE_ITEM_ENTITLEMENT>)")
                                                pattern_id = ""
                                                pattern_name = ""
                                                subtab_temp = ""
                                                if subtab_temp_variable == "Events" and ent_table == "SAQTSE" and service_id != "Z0010":
                                                    pattern_id = re.compile(r"<ENTITLEMENT_ID>AGS_[^>]*?_NET_PRMALB</ENTITLEMENT_ID>")
                                                    pattern_name = re.compile(
                                                        r"<ENTITLEMENT_DISPLAY_VALUE>(?:Included - All PM|Included - Monthly and Above|Included - Quarterly and Above|Included - All PM (PDC/MPS)|Included - Qtrly and Above|Included - &lt; Quarterly)</ENTITLEMENT_DISPLAY_VALUE>"
                                                    )
                                                    subtab_temp = "Events"
                                                elif subtab_temp_variable == "Events" and service_id in ("Z0010", "Z0128"):
                                                    subtab_temp = "Events"
                                                elif subtab_temp_variable in ("Service Inclusions", "Greenbook Inclusions"):
                                                    pattern_id = re.compile(
                                                        r"<ENTITLEMENT_ID>(?:AGS_"
                                                        + str(service_id)
                                                        + "_TSC_NONCNS|AGS_"
                                                        + str(service_id)
                                                        + "_TSC_CONADD|AGS_"
                                                        + str(service_id)
                                                        + "_TSC_CONSUM|AGS_"
                                                        + str(service_id)
                                                        + "_NON_CONSUMABLE)</ENTITLEMENT_ID>"
                                                    )
                                                    pattern_name = re.compile(
                                                        r"<ENTITLEMENT_DISPLAY_VALUE>Some Inclusions</ENTITLEMENT_DISPLAY_VALUE>"
                                                    )
                                                    subtab_temp = "Inclusions"
                                                elif subtab_temp_variable in ("Service New Parts", "Green New Parts"):
                                                    pattern_id = re.compile(r"<ENTITLEMENT_ID>AGS_[^>]*?_TSC_RPPNNW</ENTITLEMENT_ID>")
                                                    pattern_name = re.compile(
                                                        r"<ENTITLEMENT_DISPLAY_VALUE>Yes</ENTITLEMENT_DISPLAY_VALUE>"
                                                    )
                                                    subtab_temp = "New Parts"
                                                elif subtab_temp_variable in ("Service Parts List", "Green Parts List"):
                                                    pattern_id = re.compile(
                                                        r"<ENTITLEMENT_ID>(?:AGS_"
                                                        + str(service_id)
                                                        + "_TSC_NONCNS|AGS_"
                                                        + str(service_id)
                                                        + "_TSC_CONADD|AGS_"
                                                        + str(service_id)
                                                        + "_TSC_CONSUM|AGS_"
                                                        + str(service_id)
                                                        + "_NON_CONSUMABLE)</ENTITLEMENT_ID>"
                                                    )
                                                    pattern_name = re.compile(
                                                        r"<ENTITLEMENT_DISPLAY_VALUE>Some Exclusions</ENTITLEMENT_DISPLAY_VALUE>"
                                                    )
                                                    subtab_temp = "Exclusions"
                                                if pattern_id and pattern_name:
                                                    updateentXML = get_entitlement_xml.ENTITLEMENT_XML
                                                    flag_excluse = 0
                                                    for m in re.finditer(pattern_tag, updateentXML):
                                                        sub_string = m.group(1)
                                                        get_ent_id = re.findall(pattern_id, sub_string)
                                                        get_ent_name = re.findall(pattern_name, sub_string)
                                                        if get_ent_id and get_ent_name:
                                                            flag_excluse = 1
                                                            break
                                                    if flag_excluse == 1 and subtab_temp:
                                                        ent_value_dict[ent_table] = subtab_temp

                                        if (
                                            subtab_temp_variable in ("Events", "Service Parts List", "Service New Parts")
                                            and service_id != "Z0010"
                                        ):
                                            subTabName = ent_value_dict["SAQTSE"]
                                        if subtab_temp_variable in ("Events") and service_id in ("Z0010", "Z0128"):
                                            subTabName = "Events"

                                        if entitlement_level_flag and (
                                            subtab_temp_variable in ("Green Parts List", "Green New Parts", "Greenbook Inclusions")
                                        ):
                                            if entitlement_level_flag == "SAQTSE":
                                                subTabName = ent_value_dict["SAQTSE"]
                                            elif entitlement_level_flag == "SAQSGE":
                                                subTabName = ent_value_dict["SAQSGE"]
                                        else:
                                            if (
                                                subtab_temp_variable in ("Green Parts List", "Green New Parts", "Greenbook Inclusions")
                                            ) and "SAQSGE" in ent_value_dict.keys():
                                                subTabName = ent_value_dict["SAQSGE"]
                                    # A055S000P01-14557 - New Parts, Inclusion , Exclusion Subtabs ends
                                    elif subTabName == "Equipment" and str(ObjName).strip() == "SAQITM" and "BASE" in NodeText:
                                        subTabName = ""
                                        service_id = NodeText.split("-")[1].strip()
                                        spare_parts_object = Sql.GetFirst(
                                            "SELECT count(CpqTableEntryId) as cnt FROM SAQICO (NOLOCK) WHERE QUOTE_RECORD_ID = '{}' AND QTEREV_RECORD_ID = '{}' and SERVICE_ID = '{}'".format(
                                                contract_quote_record_id, quote_revision_record_id, service_id
                                            )
                                        )
                                        if spare_parts_object is not None:
                                            if spare_parts_object.cnt > 0:
                                                subTabName = str(getRightView.SUBTAB_NAME)
                                    ##A055S000P01-14790 code starts..
                                    elif subTabName == "Applied Events":
                                        subTabName = "Events"
                                    ##A055S000P01-14790 code ends...
                                    elif (subTabName == "Spare Parts") and str(NodeName) == "SERVICE_ID" and str(ObjName) == "SAQTSV":
                                        doc_type = Sql.GetFirst(
                                            "SELECT DOCTYP_ID FROM SAQTRV (NOLOCk) WHERE QUOTE_RECORD_ID = '{}' AND QTEREV_RECORD_ID = '{}'".format(
                                                contract_quote_record_id, quote_revision_record_id
                                            )
                                        )
                                        subTabName = str(getRightView.SUBTAB_NAME) if str(doc_type.DOCTYP_ID) == "ZWK1" else ""
                                    elif (subTabName == "Periods") and str(NodeName) == "SERVICE_ID" and str(ObjName) == "SAQTSV":
                                        doc_type = Sql.GetFirst(
                                            "SELECT DOCTYP_ID FROM SAQTRV (NOLOCK) WHERE QUOTE_RECORD_ID = '{}' AND QTEREV_RECORD_ID = '{}'".format(
                                                contract_quote_record_id, quote_revision_record_id
                                            )
                                        )
                                        subTabName = (
                                            str(getRightView.SUBTAB_NAME)
                                            if str(doc_type.DOCTYP_ID) == "ZWK1" and Quote.GetGlobal("SERVICE") == "Z0108"
                                            else ""
                                        )
                                    elif subTabName == "Equipment" and Product.GetGlobal("ParentNodeLevel") == "Complementary Products":
                                        doc_type = Sql.GetFirst(
                                            "SELECT DOCTYP_ID FROM SAQTRV (NOLOCK) WHERE QUOTE_RECORD_ID = '{}' AND QTEREV_RECORD_ID = '{}'".format(
                                                contract_quote_record_id, quote_revision_record_id
                                            )
                                        )
                                        subTabName = "" if str(doc_type.DOCTYP_ID) == "ZWK1" else str(getRightView.SUBTAB_NAME)
                                        Product.SetGlobal("ParentNodeLevel", "")

                                    else:
                                        subTabName = str(getRightView.SUBTAB_NAME)
                                    RelatedId = getRightView.RELATED_RECORD_ID
                                    RelatedName = getRightView.RELATED_LIST_NAME
                                    if subTabName:
                                        # Trace.Write("Events subtab-----"+str(subTabName)+"NodeText--->"+str(NodeText)+" ===> Service"+Quote.GetGlobal("SERVICE"))
                                        if subTabName == "Events" and Quote.GetGlobal("SERVICE") == "Z0009":
                                            service_entitlement_object = Sql.GetFirst(
                                                """select ENTITLEMENT_XML from SAQTSE (nolock) where QUOTE_RECORD_ID = '{QuoteRecordId}' AND QTEREV_RECORD_ID = '{RevisionRecordId}' and SERVICE_ID = '{service_id}' """.format(
                                                    QuoteRecordId=contract_quote_record_id,
                                                    RevisionRecordId=quote_revision_record_id,
                                                    service_id=Quote.GetGlobal("SERVICE"),
                                                )
                                            )
                                            if service_entitlement_object is not None:
                                                pattern_tag = re.compile(r"(<QUOTE_ITEM_ENTITLEMENT>[\w\W]*?</QUOTE_ITEM_ENTITLEMENT>)")
                                                quote_type_attribute = re.compile(
                                                    r"<ENTITLEMENT_ID>AGS_[^>]*?_PQB_QTETYP</ENTITLEMENT_ID>"
                                                )
                                                quote_type_attribute_value = re.compile(
                                                    r"<ENTITLEMENT_DISPLAY_VALUE>([^>]*?)</ENTITLEMENT_DISPLAY_VALUE>"
                                                )
                                                XML = service_entitlement_object.ENTITLEMENT_XML
                                                for values in re.finditer(pattern_tag, XML):
                                                    sub_string = values.group(1)
                                                    quotetype_id = re.findall(quote_type_attribute, sub_string)
                                                    if quotetype_id:
                                                        quotetype_value = re.findall(quote_type_attribute_value, sub_string)
                                                        if quotetype_value != ["Tool based"]:
                                                            ObjRecId = "0975E1E2-9D30-4928-AB0A-4DA54537A67A"
                                                            RelatedId = "SYOBJR-95556"
                                                            RelatedName = "Events"
                                                            break
                                                        else:
                                                            ObjRecId = "271F55CA-C844-43C5-99AB-806A72152F25"
                                                            RelatedId = "SYOBJR-00011"
                                                            RelatedName = "Events"
                                                            break
                                        elif subTabName == "Events" and (Quote.GetGlobal("SERVICE") == "Z0010" or Quote.GetGlobal("SERVICE") == "Z0128"):##added the code to show the events nested grid for Z0128 product offerings...
                                            ObjRecId = "0975E1E2-9D30-4928-AB0A-4DA54537A67A"
                                            RelatedId = "SYOBJR-95556"
                                            RelatedName = "Events"

                                        SubTabList.append(self.getSubtabRelatedDetails(subTabName, type, ObjRecId, RelatedId, RelatedName))
                                        # Trace.Write("SubTabList --->"+str(SubTabList))
                                    if str(ObjRecId) == "01C264E8-9B64-4F99-B05C-D61ECD2C4D27":
                                        item_billing_plan_obj = Sql.GetFirst(
                                            "SELECT count(CpqTableEntryId) as cnt FROM SAQIBP (NOLOCK) WHERE QUOTE_RECORD_ID = '{}' AND SERVICE_ID = '{}' AND QTEREV_RECORD_ID = '{}' GROUP BY EQUIPMENT_ID,SERVICE_ID,LINE".format(
                                                contract_quote_record_id, str(NodeText), quote_revision_record_id
                                            )
                                        )
                                        if item_billing_plan_obj is not None:
                                            if str(NodeText) == "Z0117":
                                                years = item_billing_plan_obj.cnt
                                            elif str(NodeText) == "Z0010":
                                                #A055S000P01-17627 start
                                                get_billing_cycle = Sql.GetFirst("select ENTITLEMENT_XML from SAQITE where QUOTE_RECORD_ID = '{qtid}' AND QTEREV_RECORD_ID = '{qt_rev_id}' and SERVICE_ID = '{get_service}'".format(qtid =contract_quote_record_id,qt_rev_id=quote_revision_record_id,get_service = str(NodeText).strip()))
                                                if get_billing_cycle:
                                                    updateentXML = get_billing_cycle.ENTITLEMENT_XML
                                                    pattern_tag = re.compile(r'(<QUOTE_ITEM_ENTITLEMENT>[\w\W]*?</QUOTE_ITEM_ENTITLEMENT>)')
                                                    pattern_id = re.compile(r'<ENTITLEMENT_ID>(AGS_'+str(NodeText)+'_PQB_BILCYC)</ENTITLEMENT_ID>')
                                                    pattern_name = re.compile(r'<ENTITLEMENT_DISPLAY_VALUE>([^>]*?)</ENTITLEMENT_DISPLAY_VALUE>')
                                                    for m in re.finditer(pattern_tag, updateentXML):
                                                        sub_string = m.group(1)
                                                        get_ent_id = re.findall(pattern_id,sub_string)						
                                                        get_ent_val= re.findall(pattern_name,sub_string)
                                                        if get_ent_id:
                                                            get_ent_val = str(get_ent_val[0])
                                                            if get_ent_val.upper()  == "WEEKLY":
                                                                if item_billing_plan_obj.cnt <= 52:
                                                                    years = 1
                                                                    
                                                                else:
                                                                    quotient, remainder =  divmod(item_billing_plan_obj.cnt, 52)
                                                                    Trace.Write('quotient--'+str(quotient))
                                                                    years = quotient + (1 if remainder > 0 else 0)
                                                            else:
                                                                quotient, remainder = divmod(item_billing_plan_obj.cnt, 12)
                                                                years = quotient + (1 if remainder > 0 else 0)
                                                                if not years:
                                                                    years = 1
                                                #A055S000P01-17627 end
                                            else:
                                                quotient, remainder = divmod(item_billing_plan_obj.cnt, 12)
                                                years = quotient + (1 if remainder > 0 else 0)
                                                if not years:
                                                    years = 1
                                            ObjRecId = RelatedId = None
                                            related_obj = Sql.GetFirst(
                                                """SELECT SYOBJR.OBJ_REC_ID, SYOBJR.SAPCPQ_ATTRIBUTE_NAME, SYOBJR.NAME FROM SYOBJH (NOLOCK)
															JOIN SYOBJR (NOLOCK) ON SYOBJR.OBJ_REC_ID = SYOBJH.RECORD_ID
															WHERE SYOBJH.OBJECT_NAME = 'SAQIBP'"""
                                            )
                                            if related_obj:
                                                ObjRecId = related_obj.OBJ_REC_ID
                                                RelatedId = related_obj.SAPCPQ_ATTRIBUTE_NAME
                                                RelatedName = related_obj.NAME
                                            for index in range(1, years + 1):
                                                type = "OBJECT RELATED LAYOUT"
                                                subTabName = "Year {}".format(index)
                                                if ObjRecId and RelatedId:
                                                    SubTabList.append(
                                                        self.getSubtabRelatedDetails(subTabName, type, ObjRecId, RelatedId, RelatedName)
                                                    )
                                    # Trace.Write("SUBTAB_LIST_J "+str(SubTabList))
                                ## Approvals Dynamic Subtab Code starts..##Dynamic chain subtabs in round node...
                                # A055S000P01-3618 code starts..
                                if "Round" in ChildDict.get("text"):
                                    quote_approval_chains_obj = Sql.GetList(
                                        "select DISTINCT TOP 10 ACACST.APRCHNSTP_NAME,ACAPCH.APRCHN_ID,ACACST.APRCHNSTP_NUMBER,ACAPMA.APRCHN_RECORD_ID FROM ACAPMA (nolock) inner join ACAPCH (nolock) on ACAPCH.APPROVAL_CHAIN_RECORD_ID = ACAPMA.APRCHN_RECORD_ID inner join ACACST(nolock) on ACACST.APRCHN_ID = ACAPCH.APRCHN_ID and ACACST.APRCHN_RECORD_ID = ACAPCH.APPROVAL_CHAIN_RECORD_ID where ACAPMA.APRTRXOBJ_RECORD_ID = '{}' {} ORDER BY ACACST.APRCHNSTP_NUMBER,ACACST.APRCHNSTP_NAME,ACAPCH.APRCHN_ID, ACAPMA.APRCHN_RECORD_ID ".format(
                                            quote_revision_record_id, aprchn_id
                                        )
                                    )
                                    if quote_approval_chains_obj is not None:
                                        related_obj = Sql.GetFirst(
                                            """SELECT SYOBJR.OBJ_REC_ID, SYOBJR.SAPCPQ_ATTRIBUTE_NAME, SYOBJR.NAME FROM SYOBJH (NOLOCK)
												JOIN SYOBJR (NOLOCK) ON SYOBJR.OBJ_REC_ID = SYOBJH.RECORD_ID
												WHERE SYOBJH.OBJECT_NAME = 'ACAPTX'"""
                                        )
                                        for quote_approval_chain_obj in quote_approval_chains_obj:
                                            chain_step_name = quote_approval_chain_obj.APRCHNSTP_NAME
                                            chain_step_number = quote_approval_chain_obj.APRCHNSTP_NUMBER
                                            ObjRecId = RelatedId = None
                                            if related_obj:
                                                ObjRecId = related_obj.OBJ_REC_ID
                                                RelatedId = related_obj.SAPCPQ_ATTRIBUTE_NAME
                                                RelatedName = related_obj.NAME
                                                type = "OBJECT RELATED LAYOUT"
                                                subTabName = str(NodeText) + " : " + "Step " + str(chain_step_number)
                                                if ObjRecId and RelatedId:
                                                    SubTabList.append(
                                                        self.getSubtabRelatedDetails(subTabName, type, ObjRecId, RelatedId, RelatedName)
                                                    )
                                ## Approvals Dynamic Subtab Code starts.. Dynamic chain subtabs in round node...
                                # A055S000P01-3618 code ends..
                            else:
                                if pageDetails is not None:
                                    pageType = pageDetails.PAGE_TYPE
                                    subTabName = "No SubTab"
                                    objRecId = pageDetails.OBJECT_RECORD_ID
                                    querystr = ""
                                    SubTabList.append(self.getPageRelatedDetails(subTabName, pageType, objRecId, ObjectRecId, querystr))
                            ChildDict["SubTabs"] = SubTabList

                            findSubChildAvailable = Sql.GetList(
                                "SELECT TOP 1000 * FROM SYTRND (nolock) WHERE PARENT_NODE_RECORD_ID='"
                                + str(ParRecId)
                                + "' AND DISPLAY_CRITERIA != 'DYNAMIC' ORDER BY abs(DISPLAY_ORDER) "
                            )
                            try:
                                getZ0009 = Sql.GetFirst(
                                    "SELECT CpqTableEntryId,SERVICE_ID FROM SAQTSV (NOLOCK) WHERE SERVICE_ID IN ('Z0009','Z0010','Z0128') AND QUOTE_RECORD_ID = '{}' AND QTEREV_RECORD_ID = '{}'".format(
                                        contract_quote_record_id, quote_revision_record_id
                                    )
                                )
                                if getZ0009 is not None:
                                    is_pmsa = self.PMSATree(getZ0009.SERVICE_ID)
                                else:
                                    is_pmsa = 0
                            except:
                                is_pmsa = ""
                            Product.SetGlobal("PMSA_TREE", str(is_pmsa))
                            if is_pmsa:
                                if ParRecId in (
                                    "1F47A350-4E38-41C9-A5C5-F53DC9BB3DB8",
                                    "B7BC662B-91A4-42C0-A2D9-B1E713D59E18",
                                    "1CE55561-F2DF-4A05-A21B-82AF08C23215",
                                    "1D531821-21B2-4F5F-8579-9724F10F8911",
                                    "5C5AA48D-6598-4B55-91BB-1D043575C3B7",
                                    "72FC842D-99A8-430C-A689-6DBB093015B5",
                                    "11C3DA16-72B3-49A8-8B80-23637D0D499E",
                                    "EBC61A4C-18C8-4374-9BDD-17BB93172453",
                                    "B9E7FF3A-CD32-4414-8036-A4310FB4A80E",
                                ):
                                    findSubChildAvailable = Sql.GetList(
                                        "SELECT TOP 1000 * FROM SYTRND (nolock) WHERE PARENT_NODE_RECORD_ID='"
                                        + str(ParRecId)
                                        + "' AND DISPLAY_CRITERIA = 'DYNAMIC'  ORDER BY abs(DISPLAY_ORDER) "
                                    )
                            # Getting parent node for Add-On Products
                            if NodeText in (
                                "Z0091",
                                "Z0009",
                                "Z0092",
                                "Z0035",
                                "Z0004",
                                "Z0100",
                                "Z0110",
                                "Z0006",
                                "Z0007",
                                "Z0010",
                                "Z0016",
                                "Z0128"
                            ):
                                Quote.SetGlobal("SERVICE", NodeText)
                            # PROFILE EXPLORER
                            if NodeText in ("APPROVAL CENTER", "SALES", "MATERIALS", "PRICE MODELS", "PRICE MODELS", "SYSTEM ADMIN"):
                                Product.SetGlobal("APPS", NodeText)

                            pages_tab = Sql.GetList("SELECT TAB_LABEL,PRIMARY_OBJECT_NAME FROM SYTABS (NOLOCK)")
                            tab_list = [(tab.TAB_LABEL).upper() for tab in pages_tab]
                            object_list = [tab.PRIMARY_OBJECT_NAME for tab in pages_tab]
                            tab_obj_dict = {tab_list[i]: object_list[i] for i in range(len(tab_list))}
                            Trace.Write("NodeText--" + str(NodeText))
                            if NodeText in tab_list:
                                Product.SetGlobal("page_tab", NodeText)
                                Product.SetGlobal("object_name", tab_obj_dict[NodeText])

                            if findSubChildAvailable is not None:
                                for findSubChildOne in findSubChildAvailable:
                                    parobj = str(findSubChildOne.PARENTNODE_OBJECT)
                                    NodeType = str(findSubChildOne.NODE_TYPE)
                                    NodeApiName = str(findSubChildOne.NODE_DISPLAY_NAME)
                                    DynamicQuery = str(findSubChildOne.DYNAMIC_NODEDATA_QUERY)
                                    PageRecId = str(findSubChildOne.NODE_PAGE_RECORD_ID)
                                    ordersBy = str(findSubChildOne.ORDERS_BY)
                                    Trace.Write("NodeApiName--" + str(NodeApiName))
                                    if parobj == "True":
                                        if NodeValue != "":
                                            Node_name = NodeValue
                                        else:
                                            Node_name = NodeName
                                        if NodeText1 != "":
                                            NodeText = NodeText1
                                        childwhere_string = (
                                            " " + str(where_string) + " AND " + str(Node_name) + " = '" + str(NodeText) + "'"
                                        )
                                        SubChildData = self.getChildFromParentObj(
                                            NodeText,
                                            NodeType,
                                            Node_name,
                                            RecAttValue,
                                            nodeId,
                                            ParRecId,
                                            DynamicQuery,
                                            ObjectName,
                                            RecId,
                                            childwhere_string,
                                            PageRecId,
                                            ObjectRecId,
                                            NodeApiName,
                                            ordersBy,
                                        )
                                    else:
                                        SubNodeName = str(findSubChildOne.NODE_DISPLAY_NAME)
                                        SubParRecId = str(findSubChildOne.TREE_NODE_RECORD_ID)
                                        SubChildDynamicQuery = str(findSubChildOne.DYNAMIC_NODEDATA_QUERY)
                                        SubNodeType = str(findSubChildOne.NODE_TYPE)
                                        nodeId = str(findSubChildOne.NODE_ID)
                                        PageRecId = str(findSubChildOne.NODE_PAGE_RECORD_ID)
                                        RecAttValue = NodeRecId
                                        ObjectName = parObjName
                                        Subwhere_string = "" + str(where_string) + ""
                                        # Trace.Write('Subwhere_string---'+str(Subwhere_string))
                                        # Trace.Write('SubNodeName---'+str(SubNodeName))
                                        addon_obj = None
                                        if NodeText.startswith("Z"):
                                            addon_obj = Sql.GetFirst(
                                                "SELECT * FROM SAQSAO (NOLOCK) WHERE QUOTE_RECORD_ID = '{}' AND ADNPRD_ID = '{}' AND QTEREV_RECORD_ID = '{}'".format(
                                                    contract_quote_record_id, NodeText, quote_revision_record_id
                                                )
                                            )
                                        if SubNodeName == "GREENBOOK":
                                            if ">" in NodeText:
                                                serviceid = NodeText.split(">")[1]
                                            else:
                                                serviceid = NodeText
                                            Subwhere_string += " AND SERVICE_ID = '{}' ".format(serviceid)
                                            Quote.SetGlobal("SERVICE", serviceid)
                                        if NodeText in ("Z0091", "Z0009", "Z0092", "Z0035", "Z0016", "Z0007", "Z0016_AG", "Z0007_AG","Z0128"):
                                            Subwhere_string += " AND SERVICE_ID = '{}' ".format(NodeText)
                                            Quote.SetGlobal("SERVICE", NodeText)
                                        elif addon_obj:
                                            if "SERVICE_ID" in Subwhere_string:
                                                Subwhere_string = Subwhere_string.replace("SERVICE_ID", "PAR_SERVICE_ID")
                                                Subwhere_string += " AND SERVICE_ID = '{}'".format(NodeText)
                                        if NodeName == "APRCHN_ID" and str(ProductName).upper() == "SALES":
                                            Subwhere_string = " ACACHR.APRCHN_ID = '{}'".format(NodeText)
                                        if (" - ") in NodeText:
                                            temp_node = []
                                            if "-" in NodeText:
                                                temp_node = NodeText.split("-")
                                                if str(len(temp_node)) == "4":
                                                    Subwhere_string += (
                                                        " AND QUOTE_RECORD_ID = '"
                                                        + str(contract_quote_record_id)
                                                        + "' AND QTEREV_RECORD_ID = '{}' AND SERVICE_ID = '{}'".format(
                                                            quote_revision_record_id, temp_node[-2].strip()
                                                        )
                                                    )
                                                else:
                                                    Subwhere_string += (
                                                        " AND QUOTE_RECORD_ID = '"
                                                        + str(contract_quote_record_id)
                                                        + "'  AND QTEREV_RECORD_ID = '{}' AND SERVICE_ID = '{}' AND SERVICE_ID != 'Z0101'".format(
                                                            quote_revision_record_id, temp_node[1].strip()
                                                        )
                                                        + " AND LINE_ITEM_ID = '{}'".format(temp_node[0].strip())
                                                    )
                                        if parObjName == "ACACST" and str(ProductName).upper() == "APPROVAL CENTER":
                                            Chain_step = Sql.GetFirst(
                                                "SELECT APRCHNSTP_NUMBER FROM ACACST (NOLOCK) WHERE APRCHNSTP_NAME = '"
                                                + str(NodeText)
                                                + "' AND APRCHN_RECORD_ID = '"
                                                + Product.Attributes.GetByName("QSTN_SYSEFL_AC_00001").GetValue()
                                                + "'"
                                            )
                                            Subwhere_string += " AND APRCHNSTP = '" + str(Chain_step.APRCHNSTP_NUMBER) + "'"
                                        if NodeName == "PAGE_NAME" and CurrentTabName == "Tab":
                                            Subwhere_string += " AND  PAGE_NAME = '" + str(NodeText) + "'"
                                        elif NodeName == "Actions" and CurrentTabName == "Tab":
                                            Subwhere_string = Subwhere_string
                                        if ACTION != "ADDNEW":
                                            SubChildData = self.getChildOne(
                                                SubNodeType,
                                                SubNodeName,
                                                RecAttValue,
                                                nodeId,
                                                NodeText,
                                                SubParRecId,
                                                SubChildDynamicQuery,
                                                ObjectName,
                                                ParRecId,
                                                Subwhere_string,
                                                PageRecId,
                                                ObjectRecId,
                                                ordersBy,
                                            )

                                    if len(SubChildData) > 0:
                                        NewList.append(SubChildData)
                                        list2 = []
                                        for sublist in NewList:
                                            for item in sublist:
                                                list2.append(item)
                                        ChildDict["nodes"] = list2
                                NewList = []
                                ChildList.append(ChildDict)
        else:

            findChildOneObj = Sql.GetList(
                "SELECT top 1000 * FROM SYTRND (nolock) where TREE_NODE_RECORD_ID = '"
                + str(ParRecId)
                + "' AND DISPLAY_CRITERIA != 'DYNAMIC' AND NODE_TYPE = 'STATIC'"
            )
            if Product.GetGlobal("PMSA_TREE") == "1" and ParRecId in (
                "4237BF62-7934-4CFF-811A-7A64282CE693",
                "FE46CADE-B72F-46FF-9E01-1699D2955E6B",
            ):
                findChildOneObj = Sql.GetList(
                    "SELECT top 1000 * FROM SYTRND (nolock) where TREE_NODE_RECORD_ID = '"
                    + str(ParRecId)
                    + "' AND DISPLAY_CRITERIA = 'DYNAMIC' AND NODE_TYPE = 'STATIC'"
                )
            try:
                getZ0009 = Sql.GetFirst(
                    "SELECT CpqTableEntryId,SERVICE_ID FROM SAQTSV (NOLOCK) WHERE SERVICE_ID IN ('Z0009','Z0010','Z0128') AND QUOTE_RECORD_ID = '{}' AND QTEREV_RECORD_ID = '{}'".format(
                        contract_quote_record_id, quote_revision_record_id
                    )
                )
                if getZ0009 is not None:
                    is_pmsa = self.PMSATree(getZ0009.SERVICE_ID)
                else:
                    is_pmsa = 0
            except:
                is_pmsa = 0
            if is_pmsa:
                if ParRecId in (
                    "1F47A350-4E38-41C9-A5C5-F53DC9BB3DB8",
                    "B7BC662B-91A4-42C0-A2D9-B1E713D59E18",
                    "1CE55561-F2DF-4A05-A21B-82AF08C23215",
                    "1D531821-21B2-4F5F-8579-9724F10F8911",
                    "5C5AA48D-6598-4B55-91BB-1D043575C3B7",
                    "72FC842D-99A8-430C-A689-6DBB093015B5",
                    "11C3DA16-72B3-49A8-8B80-23637D0D499E",
                    "EBC61A4C-18C8-4374-9BDD-17BB93172453",
                    "B9E7FF3A-CD32-4414-8036-A4310FB4A80E",
                ):
                    findSubChildAvailable = Sql.GetList(
                        "SELECT TOP 1000 * FROM SYTRND (nolock) WHERE PARENT_NODE_RECORD_ID='"
                        + str(ParRecId)
                        + "' AND DISPLAY_CRITERIA = 'DYNAMIC' ORDER BY abs(DISPLAY_ORDER) "
                    )
            if findChildOneObj is not None and len(findChildOneObj) > 0:
                for findChildOne in findChildOneObj:
                    if DynamicQuery is not None and len(DynamicQuery) > 0:
                        DynamicQuery = (
                            DynamicQuery.replace("{", "")
                            .replace("}", "")
                            .replace("RecAttValue", RecAttValue)
                            .replace("where_string", where_string)
                        )
                        childQuery = Sql.GetList("" + str(DynamicQuery) + "")
                    ChildDict = {}
                    SubChildData = []
                    ParRecId = str(findChildOne.TREE_NODE_RECORD_ID)
                    NodeText = str(findChildOne.NODE_DISPLAY_NAME)
                    ChildDict["text"] = NodeText
                    ChildDict["id"] = str(ParRecId)
                    ChildDict["nodeId"] = str(findChildOne.NODE_ID)
                    ParpageRecId = str(findChildOne.NODE_PAGE_RECORD_ID)
                    pageDetails = Sql.GetFirst("select * from SYPAGE (nolock) where RECORD_ID = '" + str(ParpageRecId) + "'")
                    if pageDetails is not None:
                        objRecId = pageDetails.OBJECT_RECORD_ID
                        objQuery = Sql.GetFirst("SELECT OBJECT_NAME FROM SYOBJH(NOLOCK) WHERE RECORD_ID = '" + str(objRecId) + "'")
                        if objQuery is not None:
                            ChildDict["objname"] = objQuery.OBJECT_NAME
                    SubTabList = []
                    getParentObjRightView = Sql.GetList(
                        "SELECT top 1000 * FROM SYSTAB (nolock) where TREE_NODE_RECORD_ID = '"
                        + str(ParRecId)
                        + "' ORDER BY abs(DISPLAY_ORDER) "
                    )
                    if getParentObjRightView is not None and len(getParentObjRightView) > 0:
                        for getRightView in getParentObjRightView:
                            type = str(getRightView.SUBTAB_TYPE)
                            subTabName = str(getRightView.SUBTAB_NAME)
                            ObjRecId = getRightView.OBJECT_RECORD_ID
                            RelatedId = getRightView.RELATED_RECORD_ID
                            RelatedName = getRightView.RELATED_LIST_NAME
                            ChildDict["id"] = RelatedId
                            if subTabName:
                                if getAccounts is None and (subTabName == "Sending Equipment" or subTabName == "Receiving Equipment"):
                                    subTabName = ""
                                elif subTabName == "Spare Parts Line Item Details":
                                    subTabName = ""
                                    spare_parts_object = Sql.GetFirst(
                                        "SELECT count(CpqTableEntryId) as cnt FROM SAQIFP (NOLOCK) WHERE QUOTE_RECORD_ID = '{}' AND QTEREV_RECORD_ID = '{}'".format(
                                            contract_quote_record_id, quote_revision_record_id
                                        )
                                    )
                                    if spare_parts_object is not None:
                                        if spare_parts_object.cnt > 0:
                                            subTabName = str(getRightView.SUBTAB_NAME)
                                SubTabList.append(self.getSubtabRelatedDetails(subTabName, type, ObjRecId, RelatedId, RelatedName))
                    else:
                        if pageDetails is not None:
                            pageType = pageDetails.PAGE_TYPE
                            subTabName = "No SubTab"
                            objRecId = pageDetails.OBJECT_RECORD_ID
                            if NodeText == "Variable":
                                querystr = "AND NAME = '" + str(NodeText) + "'"
                            else:
                                querystr = ""
                            SubTabList.append(self.getPageRelatedDetails(subTabName, pageType, objRecId, ObjectRecId, querystr))
                            RelatedObj = Sql.GetFirst(
                                "SELECT RECORD_ID, SAPCPQ_ATTRIBUTE_NAME, NAME FROM SYOBJR (NOLOCK) WHERE PARENT_LOOKUP_REC_ID = '"
                                + str(ObjectRecId)
                                + "' AND OBJ_REC_ID = '"
                                + str(objRecId)
                                + "' AND VISIBLE = 'True'"
                            )
                            if RelatedObj is not None:
                                ChildDict["id"] = RelatedObj.SAPCPQ_ATTRIBUTE_NAME
                    ChildDict["SubTabs"] = SubTabList

                    findSubChildAvailable = Sql.GetList(
                        "SELECT TOP 1000 * FROM SYTRND (nolock) WHERE PARENT_NODE_RECORD_ID='"
                        + str(ParRecId)
                        + "' AND DISPLAY_CRITERIA != 'DYNAMIC' ORDER BY abs(DISPLAY_ORDER) "
                    )
                    try:
                        getZ0009 = Sql.GetFirst(
                            "SELECT CpqTableEntryId,SERVICE_ID FROM SAQTSV (NOLOCK) WHERE SERVICE_ID IN ('Z0009','Z0010','Z0128') AND QUOTE_RECORD_ID = '{}' AND QTEREV_RECORD_ID = '{}'".format(
                                contract_quote_record_id, quote_revision_record_id
                            )
                        )
                        if getZ0009 is not None:
                            is_pmsa = self.PMSATree(getZ0009.SERVICE_ID)
                        else:
                            is_pmsa = 0
                    except:
                        is_pmsa = 0
                    if is_pmsa is not None:
                        if ParRecId in (
                            "1F47A350-4E38-41C9-A5C5-F53DC9BB3DB8",
                            "B7BC662B-91A4-42C0-A2D9-B1E713D59E18",
                            "1CE55561-F2DF-4A05-A21B-82AF08C23215",
                            "1D531821-21B2-4F5F-8579-9724F10F8911",
                            "5C5AA48D-6598-4B55-91BB-1D043575C3B7",
                            "72FC842D-99A8-430C-A689-6DBB093015B5",
                            "11C3DA16-72B3-49A8-8B80-23637D0D499E",
                            "EBC61A4C-18C8-4374-9BDD-17BB93172453",
                            "B9E7FF3A-CD32-4414-8036-A4310FB4A80E",
                        ):
                            findSubChildAvailable = Sql.GetList(
                                "SELECT TOP 1000 * FROM SYTRND (nolock) WHERE PARENT_NODE_RECORD_ID='"
                                + str(ParRecId)
                                + "' AND DISPLAY_CRITERIA = 'DYNAMIC' ORDER BY abs(DISPLAY_ORDER) "
                            )
                    if findSubChildAvailable is not None:
                        for findSubChildOne in findSubChildAvailable:
                            if str(findSubChildOne.TREEIMAGE_URL):
                                image_url = str(findSubChildOne.TREEIMAGE_URL)
                            parobj = str(findSubChildOne.PARENTNODE_OBJECT)
                            NodeType = str(findSubChildOne.NODE_TYPE)
                            NodeApiName = str(findSubChildOne.NODE_DISPLAY_NAME)
                            DynamicQuery = str(findSubChildOne.DYNAMIC_NODEDATA_QUERY)
                            PageRecId = str(findSubChildOne.NODE_PAGE_RECORD_ID)
                            ordersBy = str(findSubChildOne.ORDERS_BY)
                            ParRecId = str(findSubChildOne.TREE_NODE_RECORD_ID)
                            if parobj == "True":
                                childwhere_string = " " + str(where_string) + ""
                                SubChildData = self.getChildFromParentObj(
                                    NodeText,
                                    NodeType,
                                    NodeName,
                                    RecAttValue,
                                    nodeId,
                                    ParRecId,
                                    DynamicQuery,
                                    ObjectName,
                                    RecId,
                                    childwhere_string,
                                    PageRecId,
                                    ObjectRecId,
                                    NodeApiName,
                                    ordersBy,
                                )
                            else:
                                SubNodeName = str(findSubChildOne.NODE_DISPLAY_NAME)
                                SubParRecId = str(findSubChildOne.TREE_NODE_RECORD_ID)
                                subDynamicQuery = str(findSubChildOne.DYNAMIC_NODEDATA_QUERY)
                                SubNodeType = str(findSubChildOne.NODE_TYPE)
                                nodeId = str(findSubChildOne.NODE_ID)
                                where_string = " 1=1"
                                Subwhere_string = str(where_string)
                                # Filter based on service type - Services Node - Start
                                try:
                                    CurrentTabName = TestProduct.CurrentTab
                                except:
                                    CurrentTabName = "Quotes"
                                if NodeText in (
                                    "Actions",
                                    "Tabs",
                                    "Add-On Products",
                                    "Comprehensive Services",
                                    "Complementary Products",
                                    "Other Products",
                                    "Billing",
                                ):
                                    if Currenttab == "Contracts":
                                        Subwhere_string += " AND PRODUCT_TYPE = '{}'".format(NodeText)
                                    elif NodeText == "Add-On Products":
                                        service_id = Quote.GetGlobal("SERVICE")
                                        Subwhere_string += " AND SERVICE_ID = '{}'".format(str(service_id))
                                    elif NodeText == "Tabs":
                                        apps = Product.GetGlobal("APPS")
                                        Subwhere_string += " AND APP_ID ='{}'".format(str(apps))
                                    else:
                                        Product.SetGlobal("ParentNodeLevel", NodeText)
                                        # A055S000P01-9646 CODE STARTS..
                                        Trace.Write("2840--" + str(NodeText))

                                        Subwhere_string += " AND SERVICE_TYPE = '{}' AND QTEREV_RECORD_ID = '{}' AND SERVICE_ID != 'Z0046' AND SERVICE_ID != 'Z0101'".format(
                                            NodeText, quote_revision_record_id
                                        )
                                        # A055S000P01-9646 CODE ENDS..
                                elif NodeText in ("Pages"):
                                    # Trace.Write("NodeText"+str(NodeText)+"---")
                                    if NodeText == "Pages":
                                        page_tab = Product.GetGlobal("page_tab")
                                        # Trace.Write("page_tab"+str(page_tab)+"---")
                                        Subwhere_string += " AND TAB_LABEL = '{}'".format(page_tab)

                                elif NodeText in ("Tree Node"):
                                    RecAttValue = Product.Attributes.GetByName("QSTN_SYSEFL_SY_01110").GetValue()
                                    getpagename = Sql.GetList(
                                        "select TREE_RECORD_ID from SYTREE (NOLOCK) where PAGE_RECORD_ID = '"
                                        + str(RecAttValue)
                                        + "' and TREE_NAME = '"
                                        + str(Product.GetGlobal("TreeName"))
                                        + "'"
                                    )
                                    if getpagename:
                                        for tree in getpagename:
                                            # where_string =  where_string
                                            Tree_Node = str(tree.TREE_RECORD_ID)
                                        Subwhere_string += " AND TREE_RECORD_ID = '" + str(Tree_Node) + "'"
                                elif str(NodeText) in ["Sending Equipment", "Receiving Equipment"]:
                                    Quote.SetGlobal("Equipment", NodeText)
                                PageRecId = str(findSubChildOne.NODE_PAGE_RECORD_ID)
                                # Filter based on service type - Services Node - End
                                # Trace.Write("check----"+str(NodeText))
                                try:
                                    CurrentTabName = TestProduct.CurrentTab
                                except:
                                    CurrentTabName = ""
                                if CurrentTabName == "Profile":
                                    SubChildData = self.getProfileChildOne(
                                        SubNodeType,
                                        SubNodeName,
                                        RecAttValue,
                                        nodeId,
                                        SubParRecId,
                                        subDynamicQuery,
                                        ObjectName,
                                        RecId,
                                        Subwhere_string,
                                        PageRecId,
                                        ObjectRecId,
                                        ordersBy,
                                    )
                                else:
                                    # Trace.Write('2358'+str(Product.GetGlobal('TreeName')))
                                    if ACTION != "ADDNEW":
                                        SubChildData = self.getChildOne(
                                            SubNodeType,
                                            SubNodeName,
                                            RecAttValue,
                                            nodeId,
                                            NodeText,
                                            SubParRecId,
                                            subDynamicQuery,
                                            ObjectName,
                                            RecId,
                                            Subwhere_string,
                                            PageRecId,
                                            ObjectRecId,
                                            ordersBy,
                                        )

                            # Trace.Write("SubChildData---1940"+str(SubChildData))
                            # Trace.Write("NewList---1940"+str(NewList))
                            if len(SubChildData) > 0:
                                NewList.append(SubChildData)
                                list2 = []
                                for sublist in NewList:
                                    for item in sublist:
                                        list2.append(item)
                                ChildDict["nodes"] = list2
                    NewList = []
                    ChildList.append(ChildDict)
        # Trace.Write("ChildList"+str(ChildList))
        # ent_temp_drop = Sql.GetFirst("sp_executesql @T=N'IF EXISTS (SELECT ''X'' FROM SYS.OBJECTS WHERE NAME= ''"+str(ent_temp)+"'' ) BEGIN DROP TABLE "+str(ent_temp)+" END  ' ")
        return ChildList

    def getChildFromParentObj(
        self,
        NodeText,
        NodeType,
        NodeName,
        RecAttValue,
        nodeId,
        ParRecId,
        DynamicQuery,
        ObjectName,
        RecId,
        where_string,
        PageRecId,
        ObjectRecId,
        NodeApiName,
        ordersBy,
    ):
        try:
            getAccounts = Sql.GetFirst(
                "SELECT CpqTableEntryId FROM SAQTIP (NOLOCK) WHERE CPQ_PARTNER_FUNCTION = 'RECEIVING ACCOUNT' AND QUOTE_RECORD_ID = '{}'".format(
                    Quote.GetGlobal("contract_quote_record_id")
                )
            )
        except:
            getAccounts = ""

        # NewList = []
        NodeNameValue = ""
        NodeTextValue = ""
        contract_quote_record_id = Quote.GetGlobal("contract_quote_record_id")
        quote_revision_record_id = Quote.GetGlobal("quote_revision_record_id")
        if str(NodeType) == "DYNAMIC":
            pageDetails = Sql.GetFirst("select * from SYPAGE (nolock) where RECORD_ID = '" + str(PageRecId) + "'")
            if pageDetails is not None:
                OBJECT_RECORD_ID = pageDetails.OBJECT_RECORD_ID
                ObjName = pageDetails.OBJECT_APINAME
                childRecName = Sql.GetFirst(
                    "select * from SYOBJD (nolock) where OBJECT_NAME = '" + str(ObjName) + "' AND DATA_TYPE = 'AUTO NUMBER'"
                )
                if DynamicQuery is not None and len(DynamicQuery) > 0:

                    DynamicQuery = (
                        DynamicQuery.replace("{", "")
                        .replace("}", "")
                        .replace("RecAttValue", RecAttValue)
                        .replace("NodeText", str(NodeText))
                        .replace("where_string", where_string)
                    )
                    childQuery = Sql.GetList("" + str(DynamicQuery) + "")
                    # Trace.Write("@2449----------->" + str(DynamicQuery) + "")
                else:
                    # Trace.Write("@2442---")
                    if (str(ObjName).strip() != "SAQSGB" and str(NodeApiName) != "FABLOCATION_ID") or (
                        str(ObjName).strip() != "SAQFGB" and str(NodeApiName) != "GREENBOOK"
                    ):
                        # Trace.Write("@2444---")
                        childQuery = Sql.GetList("select * from " + str(ObjName) + " (nolock) where " + str(where_string) + "")
                    if str(ObjName).strip() != "CTCSGB" and str(NodeApiName) != "FABLOCATION_ID":
                        childQuery = Sql.GetList("select * from " + str(ObjName) + " (nolock) where " + str(where_string) + "")
                    else:
                        if str(ObjName).strip() == "SAQFGB":
                            childQuery = Sql.GetList(
                                "select  GREENBOOK from " + str(ObjName) + " (nolock) where " + str(where_string) + " GROUP BY GREENBOOK"
                            )
                # getAccounts = Sql.GetFirst("SELECT CpqTableEntryId FROM SAQTIP WHERE CPQ_PARTNER_FUNCTION = 'RECEIVING ACCOUNT' AND QUOTE_RECORD_ID = '{}' AND QTEREV_RECORD_ID = '{}'".format(Quote.GetGlobal("contract_quote_record_id"),quote_revision_record_id))
                # if getAccounts is None:
                findSubChildAvailable = Sql.GetList(
                    "SELECT TOP 1000 * FROM SYTRND (nolock) WHERE PARENT_NODE_RECORD_ID='"
                    + str(ParRecId)
                    + "' AND DISPLAY_CRITERIA != 'DYNAMIC' ORDER BY abs(DISPLAY_ORDER) "
                )

                try:
                    getZ0009 = Sql.GetFirst(
                        "SELECT CpqTableEntryId,SERVICE_ID FROM SAQTSV (NOLOCK) WHERE SERVICE_ID IN ('Z0009','Z0010','Z0128') AND QUOTE_RECORD_ID = '{}' AND QTEREV_RECORD_ID = '{}'".format(
                            contract_quote_record_id, quote_revision_record_id
                        )
                    )
                    if getZ0009 is not None:
                        is_pmsa = self.PMSATree(getZ0009.SERVICE_ID)
                    else:
                        is_pmsa = 0
                except:
                    is_pmsa = 0
                if is_pmsa:
                    if ParRecId in (
                        "1F47A350-4E38-41C9-A5C5-F53DC9BB3DB8",
                        "B7BC662B-91A4-42C0-A2D9-B1E713D59E18",
                        "1CE55561-F2DF-4A05-A21B-82AF08C23215",
                        "1D531821-21B2-4F5F-8579-9724F10F8911",
                        "5C5AA48D-6598-4B55-91BB-1D043575C3B7",
                        "72FC842D-99A8-430C-A689-6DBB093015B5",
                        "11C3DA16-72B3-49A8-8B80-23637D0D499E",
                        "EBC61A4C-18C8-4374-9BDD-17BB93172453",
                        "B9E7FF3A-CD32-4414-8036-A4310FB4A80E",
                    ):
                        findSubChildAvailable = Sql.GetList(
                            "SELECT TOP 1000 * FROM SYTRND (nolock) WHERE PARENT_NODE_RECORD_ID='"
                            + str(ParRecId)
                            + "' AND DISPLAY_CRITERIA = 'DYNAMIC' ORDER BY abs(DISPLAY_ORDER) "
                        )
                if childQuery is not None:
                    ChildList = []
                    for childdata in childQuery:
                        ChildDict = {}
                        SubChildData = []
                        if NodeApiName.find(",") == -1 and NodeApiName.find("-") == -1:
                            NodeText = str(eval("childdata." + str(NodeApiName)))
                        elif NodeApiName.find("-") > 0:
                            Nodesplit = NodeApiName.split("-")
                            if len(Nodesplit) > 1:
                                NodeName1 = Nodesplit[0]
                                NodeNameValue = Nodesplit[1]
                                NodeTextValue = str(eval("childdata." + str(NodeNameValue))).title()
                                NodeText = NodeName1 + "-" + NodeTextValue
                        try:
                            NodeRecId = str(eval("childdata." + str(childRecName.API_NAME)))
                        except Exception:
                            if str(ObjName).strip() == "SAQSGB":
                                if NodeApiName == "FABLOCATION_ID":
                                    NodeRecId = str(eval("childdata.FABLOCATION_ID"))
                                    nodeId = 32
                                elif NodeApiName == "GREENBOOK":
                                    try:
                                        NodeRecId = str(eval("childdata.GREENBOOK"))
                                    except:
                                        NodeRecId = "-"
                            elif str(ObjName).strip() == "SAQFGB":
                                NodeRecId = str(eval("childdata.GREENBOOK"))
                            elif str(ObjName).strip() == "ACAPTF":
                                if NodeApiName == "TRKOBJ_TRACKEDFIELD_LABEL":
                                    NodeRecId = str(eval("childdata.TRKOBJ_TRACKEDFIELD_LABEL"))
                            else:
                                NodeRecId = str(eval("childdata.REC_ID"))

                        ChildDict["text"] = str(NodeText)
                        ChildDict["id"] = str(NodeRecId)
                        ChildDict["nodeId"] = int(nodeId)
                        ChildDict["id"] = str(NodeRecId)
                        oldNodeApiName = NodeApiName
                        objQuery = Sql.GetFirst("SELECT OBJECT_NAME FROM SYOBJH(NOLOCK) WHERE RECORD_ID = '" + str(OBJECT_RECORD_ID) + "'")
                        if objQuery is not None:
                            ChildDict["objname"] = objQuery.OBJECT_NAME
                            parObjName = objQuery.OBJECT_NAME

                        SubTabList = []
                        getParentObjRightView = Sql.GetList(
                            "SELECT top 1000 * FROM SYSTAB (nolock) where TREE_NODE_RECORD_ID = '"
                            + str(ParRecId)
                            + "' ORDER BY abs(DISPLAY_ORDER) "
                        )
                        if getParentObjRightView is not None and len(getParentObjRightView) > 0:
                            for getRightView in getParentObjRightView:
                                type = str(getRightView.SUBTAB_TYPE)
                                subTabName = str(getRightView.SUBTAB_NAME)
                                ObjRecId = getRightView.OBJECT_RECORD_ID
                                RelatedId = getRightView.RELATED_RECORD_ID
                                RelatedName = getRightView.RELATED_LIST_NAME
                                # ChildDict["id"] = RelatedId
                                if subTabName == "Green Parts List":
                                    subTabName = ""
                                    # service_id = Product.GetGlobal("SERVICE")
                                    greenbook_entitlement_object = Sql.GetFirst(
                                        """select ENTITLEMENT_XML from SAQSGE (nolock) where QUOTE_RECORD_ID = '{quote_id}' AND QTEREV_RECORD_ID = '{quote_rev_id}' and SERVICE_ID = '{service_id}' and GREENBOOK = '{NodeText}' """.format(
                                            quote_id=contract_quote_record_id,
                                            quote_rev_id=quote_revision_record_id,
                                            service_id=Quote.GetGlobal("SERVICE"),
                                            NodeText=NodeText,
                                        )
                                    )
                                    if greenbook_entitlement_object is not None:
                                        updateentXML = greenbook_entitlement_object.ENTITLEMENT_XML
                                        flag_excluse = 0
                                        pattern_tag = re.compile(r"(<QUOTE_ITEM_ENTITLEMENT>[\w\W]*?</QUOTE_ITEM_ENTITLEMENT>)")
                                        pattern_id = re.compile(
                                            r"<ENTITLEMENT_ID>(?:AGS_[^>]*?_TSC_NONCNS|AGS_[^>]*?_TSC_CONSUM|AGS_[^>]*?_NON_CONSUMABLE|AGS_[^>]*?_TSC_RPPNNW|AGS_[^>]*?_TSC_CONADD)</ENTITLEMENT_ID>"
                                        )
                                        pattern_name = re.compile(
                                            r"<ENTITLEMENT_DISPLAY_VALUE>(?:Some Exclusions|Some Inclusions|Yes)</ENTITLEMENT_DISPLAY_VALUE>"
                                        )
                                        for m in re.finditer(pattern_tag, updateentXML):
                                            sub_string = m.group(1)
                                            get_ent_id = re.findall(pattern_id, sub_string)
                                            get_ent_name = re.findall(pattern_name, sub_string)
                                            if get_ent_id and get_ent_name:
                                                flag_excluse = 1
                                                break
                                        if flag_excluse == 1:
                                            subTabName = "Parts List"
                                if subTabName:
                                    if getAccounts is None and (subTabName == "Sending Equipment" or subTabName == "Receiving Equipment"):
                                        subTabName = ""
                                    SubTabList.append(self.getSubtabRelatedDetails(subTabName, type, ObjRecId, RelatedId, RelatedName))
                        else:
                            if pageDetails is not None:
                                pageType = pageDetails.PAGE_TYPE
                                subTabName = "No SubTab"
                                objRecId = pageDetails.OBJECT_RECORD_ID
                                querystr = ""
                                SubTabList.append(self.getPageRelatedDetails(subTabName, pageType, objRecId, ObjectRecId, querystr))

                        ChildDict["SubTabs"] = SubTabList
                        # getAccounts = Sql.GetFirst("SELECT CpqTableEntryId FROM SAQTIP WHERE CPQ_PARTNER_FUNCTION = 'RECEIVING ACCOUNT' AND QUOTE_RECORD_ID = '{}' AND QTEREV_RECORD_ID = '{}'".format(Quote.GetGlobal("contract_quote_record_id"),quote_revision_record_id))
                        # if getAccounts is None:
                        findSubChildAvailable = Sql.GetList(
                            "SELECT TOP 1000 * FROM SYTRND (nolock) WHERE PARENT_NODE_RECORD_ID='"
                            + str(ParRecId)
                            + "' AND DISPLAY_CRITERIA != 'DYNAMIC' ORDER BY abs(DISPLAY_ORDER) "
                        )

                        try:
                            getZ0009 = Sql.GetFirst(
                                "SELECT CpqTableEntryId,SERVICE_ID FROM SAQTSV (NOLOCK) WHERE SERVICE_ID IN ('Z0009','Z0010','Z0128') AND QUOTE_RECORD_ID = '{}' AND QTEREV_RECORD_ID = '{}'".format(
                                    contract_quote_record_id, quote_revision_record_id
                                )
                            )
                            if getZ0009 is not None:
                                is_pmsa = self.PMSATree(getZ0009.SERVICE_ID)
                            else:
                                is_pmsa = 0
                        except:
                            is_pmsa = 0
                        if is_pmsa:
                            if ParRecId in (
                                "1F47A350-4E38-41C9-A5C5-F53DC9BB3DB8",
                                "B7BC662B-91A4-42C0-A2D9-B1E713D59E18",
                                "1CE55561-F2DF-4A05-A21B-82AF08C23215",
                                "1D531821-21B2-4F5F-8579-9724F10F8911",
                                "5C5AA48D-6598-4B55-91BB-1D043575C3B7",
                                "72FC842D-99A8-430C-A689-6DBB093015B5",
                                "11C3DA16-72B3-49A8-8B80-23637D0D499E",
                                "EBC61A4C-18C8-4374-9BDD-17BB93172453",
                                "B9E7FF3A-CD32-4414-8036-A4310FB4A80E",
                            ):
                                findSubChildAvailable = Sql.GetList(
                                    "SELECT TOP 1000 * FROM SYTRND (nolock) WHERE PARENT_NODE_RECORD_ID='"
                                    + str(ParRecId)
                                    + "' AND DISPLAY_CRITERIA = 'DYNAMIC' ORDER BY abs(DISPLAY_ORDER) "
                                )
                        if findSubChildAvailable is not None:
                            for findSubChildOne in findSubChildAvailable:
                                NewList = []
                                ParRecId = str(findSubChildOne.TREE_NODE_RECORD_ID)
                                # if getAccounts is None:
                                findSubChildAvailable1 = Sql.GetList(
                                    "SELECT TOP 1000 * FROM SYTRND (nolock) WHERE PARENT_NODE_RECORD_ID='"
                                    + str(ParRecId)
                                    + "' AND DISPLAY_CRITERIA != 'DYNAMIC' ORDER BY abs(DISPLAY_ORDER) "
                                )

                                try:
                                    getZ0009 = Sql.GetFirst(
                                        "SELECT CpqTableEntryId,SERVICE_ID FROM SAQTSV (NOLOCK) WHERE SERVICE_ID IN ('Z0009','Z0010','Z0128') AND QUOTE_RECORD_ID = '{}' AND QTEREV_RECORD_ID = '{}'".format(
                                            Quote.GetGlobal("contract_quote_record_id"), Quote.GetGlobal("quote_revision_record_id")
                                        )
                                    )
                                    if getZ0009 is not None:
                                        is_pmsa = self.PMSATree(getZ0009.SERVICE_ID)
                                    else:
                                        is_pmsa = 0
                                except:
                                    is_pmsa = 0
                                if is_pmsa:
                                    if ParRecId in (
                                        "1F47A350-4E38-41C9-A5C5-F53DC9BB3DB8",
                                        "B7BC662B-91A4-42C0-A2D9-B1E713D59E18",
                                        "1CE55561-F2DF-4A05-A21B-82AF08C23215",
                                        "1D531821-21B2-4F5F-8579-9724F10F8911",
                                        "5C5AA48D-6598-4B55-91BB-1D043575C3B7",
                                        "72FC842D-99A8-430C-A689-6DBB093015B5",
                                        "11C3DA16-72B3-49A8-8B80-23637D0D499E",
                                        "EBC61A4C-18C8-4374-9BDD-17BB93172453",
                                        "B9E7FF3A-CD32-4414-8036-A4310FB4A80E",
                                    ):
                                        findSubChildAvailable = Sql.GetList(
                                            "SELECT TOP 1000 * FROM SYTRND (nolock) WHERE PARENT_NODE_RECORD_ID='"
                                            + str(ParRecId)
                                            + "' AND DISPLAY_CRITERIA = 'DYNAMIC' ORDER BY abs(DISPLAY_ORDER) "
                                        )
                                if findSubChildAvailable1 is not None:
                                    for findSubChildOne in findSubChildAvailable1:
                                        parobj = str(findSubChildOne.PARENTNODE_OBJECT)
                                        NodeType = str(findSubChildOne.NODE_TYPE)
                                        NodeApiName = str(findSubChildOne.NODE_DISPLAY_NAME)
                                        DynamicQuery = str(findSubChildOne.DYNAMIC_NODEDATA_QUERY)
                                        PageRecId = str(findSubChildOne.NODE_PAGE_RECORD_ID)
                                        ordersBy = str(findSubChildOne.ORDERS_BY)
                                        ParRecId = str(findSubChildOne.TREE_NODE_RECORD_ID)
                                        if parobj == "True":
                                            where_string = (
                                                " " + str(where_string) + " AND " + str(oldNodeApiName) + " = '" + str(NodeText) + "'"
                                            )
                                            SubChildData = self.getChildFromParentObj(
                                                NodeText,
                                                NodeType,
                                                NodeName,
                                                RecAttValue,
                                                nodeId,
                                                ParRecId,
                                                DynamicQuery,
                                                ObjectName,
                                                RecId,
                                                where_string,
                                                PageRecId,
                                                ObjectRecId,
                                                NodeApiName,
                                                ordersBy,
                                            )
                                        else:
                                            if NodeNameValue != "":
                                                Node_name = NodeNameValue
                                            else:
                                                Node_name = oldNodeApiName
                                            if NodeTextValue != "":
                                                NodeText = NodeTextValue
                                            SubNodeName = str(findSubChildOne.NODE_DISPLAY_NAME)
                                            SubNodeName = str(findSubChildOne.NODE_DISPLAY_NAME)
                                            SubParRecId = str(findSubChildOne.TREE_NODE_RECORD_ID)
                                            subDynamicQuery = str(findSubChildOne.DYNAMIC_NODEDATA_QUERY)
                                            SubNodeType = str(findSubChildOne.NODE_TYPE)
                                            nodeId = str(findSubChildOne.NODE_ID)
                                            where_string = (
                                                " " + str(where_string) + " AND " + str(Node_name) + " = '" + str(NodeText) + "'"
                                            )
                                            Subwhere_string = str(where_string)
                                            PageRecId = str(findSubChildOne.NODE_PAGE_RECORD_ID)
                                            if ACTION != "ADDNEW":
                                                SubChildData = self.getChildOne(
                                                    SubNodeType,
                                                    SubNodeName,
                                                    RecAttValue,
                                                    nodeId,
                                                    NodeText,
                                                    SubParRecId,
                                                    subDynamicQuery,
                                                    ObjectName,
                                                    RecId,
                                                    Subwhere_string,
                                                    PageRecId,
                                                    ObjectRecId,
                                                    ordersBy,
                                                )
                                        if len(SubChildData) > 0:
                                            NewList.append(SubChildData)
                                            list2 = []
                                            for sublist in NewList:
                                                for item in sublist:
                                                    list2.append(item)
                                            ChildDict["nodes"] = list2

                            ChildList.append(ChildDict)

                    return ChildList

    def getSubtabRelatedDetails(self, subTabName, type, ObjRecId, RelatedId, RelatedName):
        SubTabDict = {}
        DetailList = []
        DetailDict = {}
        if type == "OBJECT SECTION LAYOUT":
            sectObj = Sql.GetList(
                "SELECT DISTINCT SYSECT.RECORD_ID FROM SYSECT (NOLOCK) WHERE SYSECT.PRIMARY_OBJECT_RECORD_ID = '"
                + str(ObjRecId)
                + "' AND SYSECT.PAGE_RECORD_ID = ''"
            )
            if sectObj is not None:
                for section in sectObj:
                    DetailList.append(section.RECORD_ID)
                DetailDict.update({"Detail": DetailList})
                # syojhObj=Sql.GetFirst("SELECT OBJECT_NAME FROM SYOBJH (NOLOCK) WHERE RECORD_ID='"+str(ObjRecId) +"'")
                # if syojhObj is not None:
                # DetailDict.update({"ObjectName": syojhObj.OBJECT_NAME})
                SubTabDict.update({subTabName: DetailDict})

        if type == "OBJECT RELATED LAYOUT":
            RelatedDict = {}
            RelatedDict.update({str(RelatedId): str(RelatedName)})
            SubTabDict = {}
            RelatedList = []
            RelatedList.append(RelatedDict)
            RelDict = {}
            RelDict.update({"Related": RelatedList})
            SubTabDict.update({subTabName: RelDict})
        Trace.Write("SubTabDict------>"+str(SubTabDict))
        return SubTabDict

    def getPageRelatedDetails(self, subTabName, pageType, objRecId, ObjectRecId, querystr):
        SubTabDict = {}
        DetailList = []
        DetailDict = {}
        if pageType == "OBJECT PAGE LISTGRID":
            RelatedObj = Sql.GetList(
                "SELECT RECORD_ID, SAPCPQ_ATTRIBUTE_NAME, NAME FROM SYOBJR (NOLOCK) WHERE PARENT_LOOKUP_REC_ID = '"
                + str(ObjectRecId)
                + "' AND OBJ_REC_ID = '"
                + str(objRecId)
                + "' AND VISIBLE = 'True' "
                + str(querystr)
                + ""
            )
            if RelatedObj is not None:
                RelatedDict = {}
                for rel in RelatedObj:
                    RelatedDict = {}
                    RelatedDict.update({rel.SAPCPQ_ATTRIBUTE_NAME: rel.NAME})
                SubTabDict = {}
                RelatedList = []
                RelatedList.append(RelatedDict)
                RelDict = {}
                RelDict.update({"Related": RelatedList})
                SubTabDict.update({subTabName: RelDict})

        if pageType == "OBJECT PAGE LAYOUT":
            sectObj = Sql.GetList(
                "SELECT DISTINCT SYSECT.RECORD_ID FROM SYSECT (NOLOCK) WHERE SYSECT.PRIMARY_OBJECT_RECORD_ID = '"
                + str(objRecId)
                + "' AND SYSECT.PAGE_RECORD_ID = ''"
            )
            if sectObj is not None:
                for section in sectObj:
                    DetailList.append(section.RECORD_ID)
                DetailDict.update({"Detail": DetailList})
                SubTabDict.update({subTabName: DetailDict})
        # Trace.Write("=====================> SubTabDict"+str(SubTabDict))
        return SubTabDict

    # A055S000P01-4578 starts
    def pricing_picklist(self):
        if ACTION == "VIEW":
            try:
                picklist = Quote.GetCustomField("PRICING_PICKLIST").Content
            except:
                picklist = ""
            return picklist
        elif ACTION == "ONCHANGE":
            try:
                picklist_value = Param.picklist_value
            except:
                picklist_value = ""
            Quote.GetCustomField("PRICING_PICKLIST").Content = picklist_value
            return True

    # A055S000P01-4578 ends

    def PMSATree(self, TreeParam):
        flag = 0
        if str(Quote.GetGlobal("SERVICE")) == "Z0009" or str(Quote.GetGlobal("SERVICE")) == "Z0010" or str(Quote.GetGlobal("SERVICE")) == "Z0128":
            TableName = "SAQTSE"
            contract_quote_record_id = Quote.GetGlobal("contract_quote_record_id")
            quote_revision_record_id = Quote.GetGlobal("quote_revision_record_id")
            entitlement_obj = SqlHelper.GetFirst(
                "select replace(ENTITLEMENT_XML,'&',';#38') as ENTITLEMENT_XML from {} (nolock) where QUOTE_RECORD_ID = '{}' AND QTEREV_RECORD_ID = '{}' and SERVICE_ID = '{}' ".format(
                    TableName, contract_quote_record_id, quote_revision_record_id, TreeParam
                )
            )

            quote_item_tag = re.compile(r"(<QUOTE_ITEM_ENTITLEMENT>[\w\W]*?</QUOTE_ITEM_ENTITLEMENT>)")
            pattern_consumable = re.compile(r"<ENTITLEMENT_ID>AGS_[^>]*?_PQB_QTETYP</ENTITLEMENT_ID>")
            pattern_new_parts_only_yes = re.compile(r"<ENTITLEMENT_DISPLAY_VALUE>Flex Event Based</ENTITLEMENT_DISPLAY_VALUE>")
            pattern_new_parts_only = re.compile(r"<ENTITLEMENT_DISPLAY_VALUE>Event Based</ENTITLEMENT_DISPLAY_VALUE>")
            pattern_new_parts_Z0010 = re.compile(r"<ENTITLEMENT_DISPLAY_VALUE>Event based</ENTITLEMENT_DISPLAY_VALUE>")
            # Trace.Write("PMSA----->"+str(pattern_new_parts_only_yes))
            entitlement_xml = entitlement_obj.ENTITLEMENT_XML
            for m in re.finditer(quote_item_tag, entitlement_xml):
                sub_string = m.group(1)
                # Trace.Write("substring----->"+str(sub_string))
                attribute_id = re.findall(pattern_consumable, sub_string)
                attribute = re.findall(pattern_new_parts_only, sub_string)
                attribute_value = re.findall(pattern_new_parts_only_yes, sub_string)
                attribute_Z0010 = re.findall(pattern_new_parts_Z0010, sub_string)
                # Trace.Write("attrvalue----->"+str(attribute_value))
                if len(attribute_id) != 0 and (len(attribute_value) != 0 or len(attribute) != 0 or len(attribute_Z0010) != 0):
                    Trace.Write("YES 3440")
                    flag = 1
                    break
        if flag == 1:
            return 1
        else:
            return 0


tree = TreeView()
try:
    quote_revision_record_id = Quote.GetGlobal("quote_revision_record_id")
except:
    try:
        GetActiveRevision = Sql.GetFirst(
            "SELECT QUOTE_REVISION_RECORD_ID,QTEREV_ID FROM SAQTRV (NOLOCK) WHERE QUOTE_ID ='{}' AND ACTIVE = 1".format(
                Quote.CompositeNumber
            )
        )
        if GetActiveRevision:
            Quote.SetGlobal("quote_revision_record_id", GetActiveRevision.QUOTE_REVISION_RECORD_ID)
            Quote.SetGlobal("quote_rev_id", str(GetActiveRevision.QTEREV_ID))
            quote_revision_record_id = Quote.GetGlobal("quote_revision_record_id")
    except Exception as e:
        Trace.Write("error------" + str(e))
        quote_revision_record_id = ""
if not quote_revision_record_id and quote_revision_record_id != "":
    try:
        GetActiveRevision = Sql.GetFirst(
            "SELECT QUOTE_REVISION_RECORD_ID,QTEREV_ID FROM SAQTRV (NOLOCK) WHERE QUOTE_ID ='{}' AND ACTIVE = 1".format(
                Quote.CompositeNumber
            )
        )
    except:
        GetActiveRevision = ""
    if GetActiveRevision:
        Quote.SetGlobal("quote_revision_record_id", GetActiveRevision.QUOTE_REVISION_RECORD_ID)
        Quote.SetGlobal("quote_rev_id", str(GetActiveRevision.QTEREV_ID))
        quote_revision_record_id = Quote.GetGlobal("quote_revision_record_id")

LOAD = Param.LOAD
try:
    ACTION = Param.ACTION
except:
    ACTION = ""
try:
    Currenttab = Param.Currenttab
except:
    Currenttab = ""
try:
    TestProduct = Webcom.Configurator.Scripting.Test.TestProduct()
    TabName = str(TestProduct.CurrentTab)
    ProductName = str(TestProduct.Name)
except Exception:
    TabName = "Quote"
    ProductName = "Sales"

    variable_type_selectval = childQuery = ""
try:
    entitlement_level_flag = Param.entitlement_level_flag
except:
    entitlement_level_flag = ""

if LOAD == "Treeload":
    if str(ProductName).upper() == "SYSTEM ADMIN":
        if str(TabName) in [
            "Tab",
            "Action",
            "Section",
            "Section Field",
            "Message",
            "Object",
            "Script",
            "Variable",
            "Role",
            "Error Log",
            "Page",
            "Profile",
        ]:
            ApiResponse = ApiResponseFactory.JsonResponse(tree.CommonDynamicLeftTreeView())
        elif str(TabName) == "App":
            ApiResponse = ApiResponseFactory.JsonResponse(tree.CommonDynamicLeftTreeView())
        elif str(TabName) == "Profile":
            ApiResponse = ApiResponseFactory.JsonResponse(tree.CommonDynamicLeftTreeView())
        else:
            ApiResponse = ApiResponseFactory.JsonResponse(tree.CommonLeftTreeView())
    elif str(ProductName).upper() == "SALES" or str(ProductName).upper() == "APPROVAL CENTER":
        ApiResponse = ApiResponseFactory.JsonResponse(tree.CommonDynamicLeftTreeView())
    elif str(ProductName).upper() == "PRICE MODELS":
        ApiResponse = ApiResponseFactory.JsonResponse(tree.CommonDynamicLeftTreeView())
    else:
        ApiResponse = ApiResponseFactory.JsonResponse(tree.CommonDynamicLeftTreeView())
elif LOAD == "CommonGlobalSet":
    AllTreeParamsValue = {
        "TreeParam": "",
        "TreeParentLevel0": "",
        "TreeParentLevel1": "",
        "TreeParentLevel2": "",
        "TreeParentLevel3": "",
        "TreeParentLevel4": "",
        "TreeParentLevel5": "",
        "TreeParentLevel6": "",
        "TreeParentLevel7": "",
        "TreeParentLevel8": "",
    }
    for key, value in AllTreeParamsValue.items():
        Product.SetGlobal(str(key), "")
    AllTreeParams = Param.AllTreeParams
    AllTreeParamsValue = eval(AllTreeParams)
    # Trace.Write("GetTreeParamValues" + str(AllTreeParams))
    for key, value in AllTreeParamsValue.items():
        # Trace.Write("check12345"+str(value))
        Product.SetGlobal(str(key), str(value))
elif LOAD == "GlobalSet":
    try:
        TreeParam = Param.TreeParam
    except Exception:
        TreeParam = ""
    try:
        TreeParentParam = Param.TreeParentParam
    except Exception:
        TreeParentParam = ""
    try:
        TreeSuperParentParam = Param.TreeSuperParentParam
    except Exception:
        TreeSuperParentParam = ""
    try:
        TreeTopSuperParentParam = Param.TreeTopSuperParentParam
    except Exception:
        TreeTopSuperParentParam = ""
    try:
        TreeSuperTopParentParam = Param.TreeSuperTopParentParam
    except Exception:
        TreeSuperTopParentParam = ""

    try:
        TreeFirstSuperTopParentParam = Param.TreeFirstSuperTopParentParam
    except Exception:
        TreeFirstSuperTopParentParam = ""

    Product.SetGlobal("CommonTreeParam", str(TreeParam))
    Product.SetGlobal("CommonTreeParentParam", str(TreeParentParam))
    Product.SetGlobal("CommonTreeSuperParentParam", str(TreeSuperParentParam))
    Product.SetGlobal("CommonTreeTopSuperParentParam", str(TreeTopSuperParentParam))
    Product.SetGlobal("CommonTopTreeSuperParentParam", str(TreeSuperTopParentParam))
    Product.SetGlobal("CommonTreeFirstSuperTopParentParam", str(TreeFirstSuperTopParentParam))

# A055S000P01-4578 starts
elif LOAD == "PRICING PICKLIST":
    ApiResponse = ApiResponseFactory.JsonResponse(tree.pricing_picklist())
##A055S000P01-4578 ends
##else:
##Trace.Write("elsee")
# ApiResponse = ApiResponseFactory.JsonResponse(tree.CommonLeftTreeView())