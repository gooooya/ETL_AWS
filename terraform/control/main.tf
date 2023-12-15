module "common" {
  source = "../modules/common"
  bucket_name = var.bucket_name
}

module "data_collection" {
  source = "../modules/data_collection"
  bucket_name = var.bucket_name
}

module "data_shape" {
  source = "../modules/data_shape"
  bucket_name = var.bucket_name
  crawler_name = "my-crawler"
}
