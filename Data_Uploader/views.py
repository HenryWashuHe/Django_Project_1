from django.shortcuts import render
from django.http import HttpResponse
import io
import pandas as pd

def get_upload_page(request):
    if request.method == "POST":
        file_1 = request.FILES["file_1"]
        file_2 = request.FILES["file_2"]
        file_3 = request.FILES["file_3"]

        df_1 = pd.read_csv(io.StringIO(file_1.read().decode("utf-8")))
        df_2 = pd.read_csv(io.StringIO(file_2.read().decode("utf-8")))
        df_3 = pd.read_csv(io.StringIO(file_3.read().decode("utf-8")))

        df_1 = df_1[df_1["Country"].isin(["UNITED STATES", "CANADA"])]
        completed = set(df_2["商城订单号"].astype(str).str[-5:])
        df_1 = df_1.sort_values(by=['OrderId'])
        for i in reversed(range(len(df_1))):
            order_number = str(df_1.iloc[i]["OrderNumber"])[-5:]
            if order_number in completed:
                df_1.drop(df_1.index[i], inplace=True)

        df_1 = df_1.sort_values(by=['OrderId'])
        df_1["OrderItems"] = df_1["OrderItems"].str.split(";")
        df_1 = df_1.explode("OrderItems")
        df_1 = df_1[df_1["OrderItems"].str.strip() != ""]
        df_1["Description"] = df_1["OrderItems"].str.split(":").str[-1].str.strip()
        df_3 = df_3.rename(columns={
            "商品名称": "Description",
            "商品编码": "Barcode",  # fallback
            "*商品编码": "Barcode",  # your actual header
            "可用库存（在库）": "AvailableStock"
        })

        df_1 = df_1.merge(
            df_3[["Description", "Barcode", "AvailableStock"]],
            on="Description", how="left"
        )
        df_1["Qty"] = 1
        df_1["Warning"] = df_1.apply(
            lambda r: "⚠️库存不足"
            if pd.notnull(r["AvailableStock"]) and r["Qty"] > r["AvailableStock"]
            else "",
            axis=1
        )
        df_1["Shortage"] = df_1["Warning"].replace({"⚠️库存不足": "YES"})

        # build your export
        out = pd.DataFrame({
            "*客户": ["CAMPBELL"] * len(df_1),
            "*商城订单编号": df_1["OrderNumber"].astype(str).str.replace("_", "", regex=False),
            "平台": ["Others"] * len(df_1),
            "平台店铺": [""] * len(df_1),
            "*发货仓": ["LA-WLE1"] * len(df_1),
            "*派送渠道编码": ["US_FEDEX_GROUND"] * len(df_1),
            "加急类型": [""] * len(df_1),
            "*签名服务": ["不需要签名"] * len(df_1),
            "*保险服务": ["否"] * len(df_1),
            "特殊备注": [""] * len(df_1),
            "*收件人姓名": df_1["FirstName"].fillna("") + " " + df_1["LastName"].fillna(""),
            "公司名称": [""] * len(df_1),
            "联系方式": df_1["Phone"].fillna(""),
            "*国家": df_1["Country"].map({"UNITED STATES": "US", "CANADA": "CA"}).fillna(""),
            "*州": df_1["County"].fillna(""),
            "*城市": df_1["Town"].fillna(""),
            "*街道1": df_1["Address1"].fillna(""),
            "街道2": df_1["Address2"].fillna(""),
            "门牌号": df_1["Address3"].fillna(""),
            "*收件人邮编": df_1["PostCode"].fillna(""),
            "收件人邮箱": df_1["Email"].fillna(""),
            "*商品编码": df_1["Barcode"],
            "*数量": ["1"] * len(df_1),
            "Shortage": df_1["Shortage"],
        })
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="2a_export.csv"'
        out.to_csv(response, index=False, encoding="utf-8-sig", lineterminator='\n')
        return response

    return render(request, "Upload.html")
