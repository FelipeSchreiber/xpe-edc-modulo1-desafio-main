# criar bucket
resource "aws_s3_bucket" "datalake" {
  # parametros do objeto criado
  acl = "private"
  bucket = "${var.base_bucket_name}"

  tags = {
    CURSO     = "EDC"
    MODULO    = "1"
    USE_CASE  = "DESAFIO"
  }

}

# cria configuração de criptografia do bucket
resource "aws_s3_bucket_server_side_encryption_configuration" "datalake-config" {
  
  bucket = aws_s3_bucket.datalake.id
  
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }

}

# # cria config acl do bucket
# resource "aws_s3_bucket_acl" "datalake-acl" {
  
#   bucket  = aws_s3_bucket.datalake.id
#   acl     = "private"

# }