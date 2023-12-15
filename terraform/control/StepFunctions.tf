# ロールの作成
resource "aws_iam_role" "step_functions_role" {
  name = "step_functions_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = "sts:AssumeRole",
        Effect = "Allow",
        Principal = {
          Service = "states.amazonaws.com"
        }
      },
    ]
  })
}

# IAMポリシーのアタッチ
data "aws_iam_policy_document" "step_functions_policy" {
  statement {
    actions = ["lambda:InvokeFunction", "glue:StartJobRun"]
    resources = [
      module.data_collection.lambda_function_arn,
      module.data_shape.my_crawler_before_etl_arn,
      module.data_shape.my_crawler_after_etl_arn
    ]
  }
}
resource "aws_iam_role_policy" "step_functions_policy" {
  role   = aws_iam_role.step_functions_role.id
  policy = data.aws_iam_policy_document.step_functions_policy.json
}
# Glueへのフルアクセス権を設定
resource "aws_iam_role_policy_attachment" "glue_console_access_attachment" {
  role       = aws_iam_role.step_functions_role.name
  policy_arn = "arn:aws:iam::aws:policy/AWSGlueConsoleFullAccess"
}


# Step Functionsステートマシンの定義
resource "aws_sfn_state_machine" "sfn_state_machine" {
  name     = "my_state_machine"
  role_arn = aws_iam_role.step_functions_role.arn

  definition = <<EOF
{
  "StartAt": "SaveToS3",
  "States": {
    "SaveToS3": {
      "Type": "Task",
      "Resource": "${module.data_collection.lambda_function_arn}",
      "Next": "RunGlueJob"
    },
    "RunGlueJob": {
      "Type": "Task",
      "Resource": "arn:aws:states:::glue:startJobRun.sync",
      "Parameters": {
        "JobName": "${module.data_shape.glue_job_name}"
      },
      "End": true
    }
  }
}
EOF
}
