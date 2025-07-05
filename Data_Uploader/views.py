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
        #generating the set of order_number in file_2
        completed=set(df_2['商城订单号'].astype(str).str[-5:].tolist())
        #loop through file_1 to delete the completed orders
        for i in reversed(range(len(df_1['OrderNumber']))):
            order_number = str(df_1.loc[i, 'OrderNumber'])[-5:]
            if order_number in completed:
                df_1.drop(i, inplace=True)
        new_rows=[]
        for i in reversed(range(len(df_1))):
            num=df_1.loc[i,'TotalItems']
            if num >1:
                row_to_duplicate = df_1.loc[[i]]
            df_1=pd.concat([df_1]+new_rows,ignore_index=True)

        '''for i in reversed(range (len(df_1.loc[:,'Country']))):
            if not (df_1.loc[i,'Country'] == 'UNITED STATES' or df_1.loc[i,'Country']=='CANADA'):
                df_1.drop(i,inplace=True)'''

    return render(request,'Upload.html',{
        'rows_1':rows_1,
        'rows_2':rows_2,
        'rows_3':rows_3
    })# Create your views here.
