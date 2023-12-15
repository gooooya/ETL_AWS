resource "aws_s3_bucket" "common_output" {
  bucket = var.bucket_name
}

resource "aws_s3_object" "glue_job_script" {
  bucket = aws_s3_bucket.common_output.bucket
  key    = "scripts/Transform.py"
  source = "../tmp/Transform.py"
  etag   = filemd5("../tmp/Transform.py")
}