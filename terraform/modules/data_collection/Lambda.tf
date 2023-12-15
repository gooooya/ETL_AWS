# lambda_roleの作成
resource "aws_iam_role" "lambda_role" {
  name = "lambda_role"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF
}

# S3への書き込み権を設定
resource "aws_iam_role_policy_attachment" "lambda_s3_policy" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
}

# lambdaの内容をアップロード
resource "aws_lambda_function" "scrapy_lambda" {
  function_name = "scrapy_lambda"
  role          = aws_iam_role.lambda_role.arn
  handler       = "suumo/suumo/spiders/my_scrapy.lambda_handler"
  runtime       = "python3.11"
  filename      = "../tmp/scrapy.zip"
  layers        = [aws_lambda_layer_version.scrapy_layer.arn]
  timeout       = 900
  memory_size   = 512

  environment {
    variables = {
      MY_S3_BUCKET_PATH = "${var.bucket_name}"
    }
  }
}

# 依存の解決を行うレイヤをアップロード
resource "aws_lambda_layer_version" "scrapy_layer" {
  layer_name = "scrapy_layer"
  filename      = "../tmp/layer.zip"
  compatible_runtimes = ["python3.11"]
  compatible_architectures = ["x86_64"]
}
