from django.shortcuts import render
import csv
import io
import pandas as pd
def get_upload_page(request):
    rows_1=[]
    rows_2=[]
    rows_3=[]
    if request.method=="POST":
        #grabiing files from the request
        file_1=request.FILES['file_1']
        file_2=request.FILES['file_2']
        file_3=request.FILES['file_3']
        #decode the byte file into strings
        decoded_file_1=file_1.read().decode('utf-8')
        decoded_file_2=file_2.read().decode('utf-8')
        decoded_file_3=file_3.read().decode('utf-8')
        #convert it into file_like file so pandas reader can read
        df_1=pd.read_csv(io.StringIO(decoded_file_1))
        df_2=pd.read_csv(io.StringIO(decoded_file_2))
        df_3=pd.read_csv(io.StringIO(decoded_file_3))
        #keeping only rows that is in US or CN
        df_1=df_1[df_1['Country'].isin(['UNITED STATES', 'CANADA'])]
        '''for i in reversed(range (len(df_1.loc[:,'Country']))):
                    if not (df_1.loc[i,'Country'] == 'UNITED STATES' or df_1.loc[i,'Country']=='CANADA'):
                        df_1.drop(i,inplace=True)'''
        #generating the set of order_number in file_2
        completed=set(df_2['商城订单号'].astype(str).str[-5:])
        #loop through file_1 to delete the completed orders
        for i in reversed(range(len(df_1['OrderNumber']))):
            order_number = str(df_1.loc[i, 'OrderNumber'])[-5:]
            if order_number in completed:
                df_1.drop(i, inplace=True)
        new_rows=[]
        for i in reversed(range(len(df_1))):
            num=df_1.loc[i,'TotalItems']
            if num>1:
                row_to_duplicate = df_1.loc[[i]]
                duplicates= pd.concat([row_to_duplicate] * (num - 1), ignore_index=True)
                new_rows.append(duplicates)
        if new_rows:
            df_1=pd.concat([df_1]+new_rows,ignore_index=True)
        df_1=df_1.sort_values(by=['OrderID'], ascending=True)
        df_1['OrderItems']=df_1['OrderItems'].str.split(';')
        df_1 = df_1.explode('OrderItems')  # One row per item
        df_1['Description'] = df_1['OrderItems'].str.split(':').str[-1].str.strip()
        df_3 = df_3.rename(columns={'商品名称': 'Description'})  # 🔧 FIXED
        df_1 = df_1.merge(df_3[['Description', 'Barcode', '可用库存（在库）']], on='Description', how='left')  # 🔧 FIXED

        # new: compare qty with stock and flag warning
        df_1['Qty'] = 1  # assume each exploded item = 1
        df_1['Warning'] = df_1.apply(
            lambda row: '⚠️库存不足' if pd.notnull(row['可用库存（在库）']) and row['Qty'] > row['可用库存（在库）'] else '',axis=1)
        df_1['Shortage'] = df_1.apply(
            lambda row: 'YES' if pd.notnull(row['ATP']) and row['Qty'] > row['ATP'] else '',
            axis=1
        )
        df = pd.DataFrame()
        df["*客户"] = ["CAMPBELL"] * len(df_merged)
        df["*商城订单编号"] = df_merged["OrderNumber"].str.replace("_", "", regex=False)
        df["平台"] = ["Others"] * len(df_merged)
        df["平台店铺"] = ["" for _ in range(len(df_merged))]
        df["*发货仓"] = ["LA-WLE1"] * len(df_merged)
        df["*派送渠道编码"] = ["US_FEDEX_GROUND"] * len(df_merged)
        df["加急类型"] = ["" for _ in range(len(df_merged))]
        df["*签名服务"] = ["不需要签名"] * len(df_merged)
        df["*保险服务"] = ["否"] * len(df_merged)
        df["特殊备注"] = ["" for _ in range(len(df_merged))]
        df["*收件人姓名"] = df_merged["FirstName"].fillna("") + " " + df_merged["LastName"].fillna("")
        df["公司名称"] = ["不填"] * len(df_merged)
        df["联系方式"] = df_merged["Phone"].fillna("")
        df["*国家"] = df_merged["Country"].replace({"UNITED STATES": "US", "CANADA": "CA"}).fillna("")
        df["*州"] = df_merged["County"].fillna("")
        df["*城市"] = df_merged["Town"].fillna("")
        df["*街道1"] = df_merged["Address1"].fillna("")
        df["街道2"] = df_merged["Address2"].fillna("")
        df["门牌号"] = df_merged["Address3"].fillna("")
        df["*收件人邮编"] = df_merged["PostCode"].fillna("")
        df["收件人邮箱"] = df_merged["Email"].fillna("")
        df["*商品编码"] = df_merged["商品编码"].fillna("#NAME?")
        df["*数量"] = ["1"] * len(df_merged)

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="2a_export.csv"'
        df.to_csv(response, index=False, encoding="utf-8-sig")
        return response


    return render(request, "Upload.html.html")# Create your views here.
def download_csv(request):
    csv_data = request.session.get("csv_data")
    if not csv_data:
        return HttpResponse("No file prepared.", status=400)

    response = HttpResponse(csv_data, content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="2a_export.csv"'
    return response
