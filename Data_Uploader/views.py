import pandas
from django.shortcuts import render
import csv
import io
import pandas as pd
def get_upload_page(request):
    rows_1=[]
    rows_2=[]
    rows_3=[]
    if request.method=="POST":
        file_1=request.FILES['file_1']
        file_2=request.FILES['file_2']
        file_3=request.FILES['file_3']
        decoded_file_1=file_1.read().decode('utf-8')
        decoded_file_2=file_2.read().decode('utf-8')
        decoded_file_3=file_3.read().decode('utf-8')
        df_1=pd.read_csv(io.StringIO(decoded_file_1))
        df_2=pd.read_csv(io.StringIO(decoded_file_2))
        df_3=pd.read_csv(io.StringIO(decoded_file_3))
        rows_1 = df_1.values.tolist()
        rows_2 = df_2.values.tolist()
        rows_3 = df_3.values.tolist()
        print('file_1',df_1)
        print('file_2',df_2)
        print('file_3',df_3)

    return render(request,'Upload.html',{
        'rows_1':rows_1,
        'rows_2':rows_2,
        'rows_3':rows_3
    })# Create your views here.
