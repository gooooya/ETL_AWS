# glue_roleの作成
resource "aws_iam_role" "glue_role" {
  name = "glue_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = "sts:AssumeRole",
        Effect = "Allow",
        Principal = {
          Service = "glue.amazonaws.com"
        },
      },
    ],
  })
}

# MetricDataの出力を許可するポリシー
resource "aws_iam_policy" "cloudwatch_put_metric_policy" {
  name        = "CloudWatchPutMetricPolicy"
  description = "Allow PutMetricData to CloudWatch"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = "cloudwatch:PutMetricData",
        Effect = "Allow",
        Resource = "*"
      }
    ]
  })
}


# Glueへのフルアクセス権を設定
resource "aws_iam_role_policy_attachment" "glue_console_access_attachment" {
  role       = aws_iam_role.glue_role.name
  policy_arn = "arn:aws:iam::aws:policy/AWSGlueConsoleFullAccess"
}
# S3へのフルアクセス権を設定
resource "aws_iam_role_policy_attachment" "glue_s3_policy" {
  role       = aws_iam_role.glue_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
}
# ログへのフルアクセス権を設定
resource "aws_iam_role_policy_attachment" "glue_log_policy" {
  role       = aws_iam_role.glue_role.name
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchLogsFullAccess"
}
# ログへのMetricData出力権を設定
resource "aws_iam_role_policy_attachment" "cloudwatch_put_metric_policy_attachment" {
  role       = aws_iam_role.glue_role.name
  policy_arn = aws_iam_policy.cloudwatch_put_metric_policy.arn
}


# Glue Crawlerの設定
# ETL前用
resource "aws_glue_crawler" "my_crawler_before_etl" {
  name          = "my_crawler_before_etl"
  database_name = "my_database"
  role          = aws_iam_role.glue_role.arn

  s3_target {
    path = "s3://${var.bucket_name}/outputs/"
  }
}

# ETL後用
resource "aws_glue_crawler" "my_crawler_after_etl" {
  name          = "my_crawler_after_etl"
  database_name = "my_database"
  role          = aws_iam_role.glue_role.arn

  s3_target {
    path = "s3://${var.bucket_name}/etl_outputs/"
  }
}

# Glue Jobの設定
resource "aws_glue_job" "my_job" {
  name     = "my-job"
  role_arn = aws_iam_role.glue_role.arn

  command {
    script_location = "s3://${var.bucket_name}/scripts/Transform.py"
    python_version  = "3"
  }

  default_arguments = {
    "--job-bookmark-option"           = "job-bookmark-enable"
     "--continuous-log-logGroup"      = aws_cloudwatch_log_group.glue_logs.name
    "--enable-continuous-cloudwatch-log" = "true"
    "--enable-metrics"                = "true"
    "--continuous-log-logStreamPrefix"= "glue"
    "--environment-variables" = jsonencode({
    "BUCKET_NAME" = "s3://${var.bucket_name}",
    "CRAWLER_NAME" = var.crawler_name})
  }
  
  max_capacity = 2.0
  timeout = 60
  glue_version = "4.0" 
}

resource "aws_cloudwatch_log_group" "glue_logs" {
  name = "/aws-glue/jobs"
}
