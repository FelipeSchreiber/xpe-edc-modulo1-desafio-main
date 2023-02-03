# # Bootcamp da Xpe
# ## Engenharia de Dados em Cloud
# ### Módulo 1: Fundamentos em Arquitetura de Dados e Soluções em Nuvem
# 
# ### Objetivos:
# >> Implementação de um Data Lake; <br>
# >> Armazenamento de dados em Storage camada Raw; <br>
# >> Armazenamento de dados em Storage camada Bronze; <br>
# >> Armazenamento de dados em Storage camada Silver; <br>
# >> Implementação de Processamento de Big Data; <br>
# >> IaC de toda estrutura com Terraform; <br>
# >> Esteiras de Deploy com Github. <br>
# 
# ### Esse notebook trata dos itens 2 e 3 do desafio
# 2. Realizar tratamento no dataset da RAIS 2020  <br>
#     a. Modifique os nomes das colunas, trocando espaços por “_”; <br>
#     b. Retire acentos e caracter especiais das colunas; <br>
#     c. Transforme todas as colunas em letras minúsculas; <br>
#     d. Crie uma coluna “uf” através da coluna "municipio"; <br>
#     e. Realize os ajustes no tipo de dado para as colunas de remuneração.
# 
# 3. Transformar os dados no formato parquet e escrevê-los na zona staging ou zona silver do seu Data Lake.

import pyspark
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lit, input_file_name, regexp_replace
from pyspark.sql import functions as spkFn
import unicodedata
import re
# #### Inicia uma `Session` do Spark
spark = (SparkSession.builder
                     .appName("readFile")
                     .getOrCreate())  
# #### Path para diretório source e target
## Ambiente Cloud AWS
## Path Cloud AWS
pathRaw    = f"s3://datalake-felipeschreiber-desafio/rais/raw-data/"
pathBronze = f"s3://datalake-felipeschreiber-desafio/rais/staging-zone/"

#### Schema DDL

fileNameSchema = "RAIS_VINC_PUB_NORTE.txt.gz"
filePathSchema = f"{pathRaw}/{fileNameSchema}"

fileDfSchema   = (spark.read
                       .format("csv")
                       .option("header","true")
                       .option("sep", ";")
                       .option("encoding", "latin1")
                       .option("inferSchema", "true")
                       .load(filePathSchema)
                       .schema)

schemaJson     = fileDfSchema.json()
schemaDDL      = spark.sparkContext._jvm.org.apache.spark.sql.types.DataType.fromJson(schemaJson).toDDL()

#### Ler arquivos com a API DataFrameRead
## Read
rais2020_csv = (spark.read
                     .format("csv")
                     .option("header","true")
                     .option("sep", ";")
                     .option("encoding", "latin1")
                     .option("inferSchema", "true")
                     .schema(schemaDDL)
                     .load(pathRaw)
                     .withColumn("file_name", lit(input_file_name())))

# ### Funções para normalizar as colunas
# 
# > ***normalizar_colunas***
# 1. Função para normalizar as colunas de um dataframe
#     - Retira espaços vazios e incluir um underline (Ex: `Sobre Nome -> Sobre_Nome`)
#     - Retira ponto e incluir um underline (Ex: `Sobre.Nome -> Sobre_Nome`)
#     - Formata todas as colunas com letras minúsculas (Ex: `Sobre_Nome -> sobre_nome`)
# 
# > ***normalizar_acentos***
# 2. Função para retirar os acentos de todas as colunas de um dataframe
#     - Remover espaços nas extremidades (Ex: `"  sobre_nome  " -> "sobre_nome"`)
#     - Replace de carácteres especiais por underline (Ex: `sobre@nome -> sobre_nome`)
#     - Remover underlines nas extremidades (Ex: `_sobre_nome_ -> sobre_nome`)
#     - Remover acentuação (Ex: `média_mês -> media_mes`)

## Função para normalizar as colunas de um dataframe
def normalizar_colunas(df):
  try:
    new_column_spaces_lower = (list(map(lambda x: x.replace(" ", "_")
                                                   .replace(".", "_")
                                                   .lower(),
                                                 df.columns)))
    return df.toDF(*new_column_spaces_lower) 
  except Exception as err:
        error_message = f"Erro ao normalizar nomes das colunas: {str(err)}"
        print(error_message)
        raise ValueError(error_message)

## Função para retirar os acentos de todas as colunas de um dataframe
def normalizar_acentos(str):
  try:
    new_str = str
    # Remover espaços nas extremidades
    new_str = new_str.strip()
    # Replace de carácteres especiais por underline
    new_str = re.sub(r"[^\w]", "_", new_str)
    # Remover underlines nas extremidades
    new_str = new_str.strip("_")
    # Remover 2 underlines juntos e deixar apenas 1
    new_str = new_str.replace("__", "_")
    # Remover acentuação
    new_str = unicodedata.normalize('NFKD', new_str)
    new_str = u"".join([c for c in new_str if not unicodedata.combining(c)])
    return new_str
  except Exception as err:
    error_message = f"Erro ao normalizar nomes das colunas: {str(err)}"
    print(error_message)
    raise ValueError(error_message)

renamed_df = normalizar_colunas(rais2020_csv)

rais2020_renamed = renamed_df.select([spkFn.col(col).alias(normalizar_acentos(col)) for col in renamed_df.columns])
rais2020_fim = (
                 rais2020_renamed
                        .withColumn("ano", lit("2020").cast('int'))
                        .withColumn("uf", col("municipio").cast('string').substr(1,2).cast('int'))
                        .withColumn("mes_desligamento", col('mes_desligamento').cast('int'))
                        .withColumn("vl_remun_dezembro_nom", regexp_replace("vl_remun_dezembro_nom", ',', '.').cast('double'))
                        .withColumn("vl_remun_dezembro_sm", regexp_replace("vl_remun_dezembro_sm", ',', '.').cast('double'))
                        .withColumn("vl_remun_media_nom", regexp_replace("vl_remun_media_nom", ',', '.').cast('double'))
                        .withColumn("vl_remun_media_sm", regexp_replace("vl_remun_media_sm", ',', '.').cast('double'))
                        .withColumn("vl_rem_janeiro_sc", regexp_replace("vl_rem_janeiro_sc", ',', '.').cast('double'))
                        .withColumn("vl_rem_fevereiro_sc", regexp_replace("vl_rem_fevereiro_sc", ',', '.').cast('double'))
                        .withColumn("vl_rem_marco_sc", regexp_replace("vl_rem_marco_sc", ',', '.').cast('double'))
                        .withColumn("vl_rem_abril_sc", regexp_replace("vl_rem_abril_sc", ',', '.').cast('double'))
                        .withColumn("vl_rem_maio_sc", regexp_replace("vl_rem_maio_sc", ',', '.').cast('double'))
                        .withColumn("vl_rem_junho_sc", regexp_replace("vl_rem_junho_sc", ',', '.').cast('double'))
                        .withColumn("vl_rem_julho_sc", regexp_replace("vl_rem_julho_sc", ',', '.').cast('double'))
                        .withColumn("vl_rem_agosto_sc", regexp_replace("vl_rem_agosto_sc", ',', '.').cast('double'))
                        .withColumn("vl_rem_setembro_sc", regexp_replace("vl_rem_setembro_sc", ',', '.').cast('double'))
                        .withColumn("vl_rem_outubro_sc", regexp_replace("vl_rem_outubro_sc", ',', '.').cast('double'))
                        .withColumn("vl_rem_novembro_sc", regexp_replace("vl_rem_novembro_sc", ',', '.').cast('double'))
                        .drop("vl_remun_dezembro__sm", "vl_remun_media__sm")
                )

(
    rais2020_fim.write
                .format('parquet')
                .mode('overwrite')
                .partitionBy('ano', 'uf')
                .save(pathBronze)
)

rais2020_parquet = (
                      spark.read
                           .format('parquet')
                           .load(pathBronze)
                   )   