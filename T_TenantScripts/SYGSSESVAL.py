# =========================================================================================================================================
#   __script_name : SYGSSESVAL.PY
#   __script_description : THIS SCRIPT IS USED TO SET THE VALUE OF CERTAIN VARIABLES THROUGHOUT THE SESSION OF AN APP.
#   __primary_author__ : LEO JOSEPH
#   __create_date :
#   Â© BOSTON HARBOR TECHNOLOGY LLC - ALL RIGHTS RESERVED
# ==========================================================================================================================================
from SYDATABASE import SQL
import Webcom.Configurator.Scripting.Test.TestProduct
Sql = SQL()


current_prod = Product.Name
TreeParentParam = ""
TreeSuperParentParam = ""
TopSuperParentParam = ""
TreeParam = Param.TreeParam
TreeParam = TreeParam.decode("unicode_escape").encode("utf-8").decode("unicode_escape").encode("utf-8")

try:
    TreeParentParam = Param.TreeParentParam
    TreeSuperParentParam = Param.TreeSuperParentParam
    TopSuperParentParam = Param.TopSuperParentParam
    Trace.Write("TreeParentParamTreeParentParam" + str(TreeParentParam))
    Trace.Write("TreeSuperParentParamTreeSuperParentParam" + str(TreeSuperParentParam))
    Trace.Write("TopSuperParentParamTopSuperParentParam" + str(TopSuperParentParam))
except:
    Trace.Write("error in param")

try:
    Product.SetGlobal("INCLUDE_EXCLUDE", "")
    Product.SetGlobal("PLN_ID", "")
    Product.SetGlobal("SORG_ID", "")
    Product.SetGlobal("Curr_OM_Node", "Sales_Line_Rollup")
    Product.SetGlobal("Curr_Pric_Val", "")
except:
    Trace.Write("error")
    Product.SetGlobal("Curr_OM_Node", "Sales_Line")
    Product.SetGlobal("Curr_Pric_Val", "")


Selected_Node = Product.GetGlobal("SEL_NODE_LIST")
Selected_Node_List = {}

if str(Selected_Node) != "":
    
    Selected_Node_List = eval(Selected_Node)

if current_prod != "":
    Product_Code = Sql.GetFirst("select APP_ID from SYAPPS (NOLOCK) where APP_LABEL='" + str(current_prod) + "' ")
    if Product_Code is not None:
        Pro_code = Product_Code.APP_ID
        TreeParam = Pro_code + TreeParam.replace(" ", "")
        Product.SetGlobal("CurrTreeParamVal", TreeParam)
        Trace.Write(TreeParam)
        if TreeParam in Selected_Node_List:
            Selected_Node_List[TreeParam] = "2"
            Product.SetGlobal("EXECUTION", "2")
        else:
            Product.SetGlobal("EXECUTION", "1")
            Selected_Node_List[TreeParam] = "1"
        Product.SetGlobal("SEL_NODE_LIST", str(Selected_Node_List))