import boto3
import os
from urllib.request import urlretrieve
#import py7zr
from io import BytesIO
import zipfile

bucketName = "datalake-felipeschreiber-desafio"
basepath = "./"
dlpath = f"{basepath}/rais"
## Create bucket
s3_resource = boto3.resource('s3')
try:
	s3_resource.create_bucket(Bucket=bucketName, CreateBucketConfiguration={
    	'LocationConstraint': 'us-east-2'})
except Exception:
	print("Bucket já criado")
	pass

names = [
     #"RAIS_VINC_PUB_CENTRO_OESTE.7z",
     "RAIS_VINC_PUB_NORDESTE.7z",
     "RAIS_VINC_PUB_NORTE.7z",
     "RAIS_VINC_PUB_SUL.7z",
     "RAIS_VINC_PUB_MG_ES_RJ.7z",
     "RAIS_VINC_PUB_SP.7z",
]
urls = [
    #"ftp://ftp.mtps.gov.br/pdet/microdados/RAIS/2020/RAIS_VINC_PUB_CENTRO_OESTE.7z",
    "ftp://ftp.mtps.gov.br/pdet/microdados/RAIS/2020/RAIS_VINC_PUB_NORDESTE.7z",
    "ftp://ftp.mtps.gov.br/pdet/microdados/RAIS/2020/RAIS_VINC_PUB_NORTE.7z",
    "ftp://ftp.mtps.gov.br/pdet/microdados/RAIS/2020/RAIS_VINC_PUB_SUL.7z",
    "ftp://ftp.mtps.gov.br/pdet/microdados/RAIS/2020/RAIS_VINC_PUB_MG_ES_RJ.7z",
    "ftp://ftp.mtps.gov.br/pdet/microdados/RAIS/2020/RAIS_VINC_PUB_SP.7z",
]

def obter_dados(url, name):
    filename = dlpath + '/' + name
    urlretrieve(url, filename=filename)
    #print(filename)
    #archive = py7zr.SevenZipFile(filename)
    zip_obj = s3_resource.Object(bucket_name=bucketName, key=name)
    buffer = BytesIO(zip_obj.get()["Body"].read())
    z = zipfile.ZipFile(buffer)
    for filename in z.namelist():
        #file_info = z.getinfo(filename)
        s3_resource.meta.client.upload_fileobj(
        z.open(filename),
        Bucket=bucketName,
        Key=f'{filename}'
    )

for i in range(len(urls)):
    obter_dados(urls[i], names[i])
# s3_client = boto3.client("s3",region_name="us-east-2")
# def uploadDirectory(path,bucketname):
# 	for root,dirs,files in os.walk(path):
# 		for file in files:
# 			s3_client.upload_file(os.path.join(root,file),bucketname,"rais/"+file)
print("A")
# uploadDirectory(filepath,bucketName)