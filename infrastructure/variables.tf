variable "base_bucket_name" {
  default = "datalake-felipeschreiber-desafio"
}

variable "aws_region" {
  default = "us-east-2"
}

variable "lambda_function_name" {
  default = "DesafioExecutaEMR"
}

variable "account_id" {
  description = "identifica o account id"
  type        = string
  default     = "689150947157"
}
