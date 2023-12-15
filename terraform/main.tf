terraform {
  required_version = "= 1.7.0"
}

provider "aws" {
  region = "us-east-1"
}

module "control" {
  source = "./control"
  bucket_name = var.bucket_name
}