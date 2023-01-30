provider "aws" {
  region = var.aws_region
}

terraform {
  backend "s3" {
    bucket = "terraform-state-felipe"
    key = "state/mod1-desafio/terraform.tfstate"
    region = "us-east-2"
  }
}