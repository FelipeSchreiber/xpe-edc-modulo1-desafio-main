import boto3
import os
import py7zr
import zipfile
import gzip
import shutil

bucketName = "datalake-felipeschreiber-desafio"
filepath = "/home/felipe/ftp.mtps.gov.br/pdet/microdados/RAIS/2020/"
## Create bucket
s3_resource = boto3.resource('s3')
try:
	s3_resource.create_bucket(Bucket=bucketName, CreateBucketConfiguration={
    	'LocationConstraint': 'us-east-2'})
except Exception:
	print("Bucket já criado")
	pass

## Extract files
# for root,dirs,files in os.walk(filepath):
# 	for file in files:
# 		archive = py7zr.SevenZipFile(filepath+file)
# 		print(filepath+file)
# 		archive.extractall(path=filepath)
# 		archive.close()
# 		os.remove(filepath+file)

## Pass to .gzip
for namefile in os.listdir(path=filepath):
    if namefile.endswith(".txt"):
        with open(f"{filepath}/{namefile}", 'rb') as f_in:
            with gzip.open(f"{filepath}/{namefile}" + ".gz", 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
## Upload file
s3_client = boto3.client("s3",region_name="us-east-2")
def uploadDirectory(path,bucketname):
	for root,dirs,files in os.walk(path):
		for file_ in files:
			if file_.endswith(".gz"):
				s3_client.upload_file(os.path.join(root,file_),bucketname,"rais/raw-data/"+file_)

uploadDirectory(filepath,bucketName)
