provider "aws" {
  region = var.aws_region
}
# Centralizar o arquivo de controle de estado do terraform
terraform {
  backend "s3" {
    bucket = "terraform-state-felipe"
    key    = "state/edc/mod1/terraform.tfstate"
    region = "us-east-2"
  }
}
