# eventbridge_roleの作成
resource "aws_iam_role" "eventbridge_role" {
  name = "eventbridge_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Principal = {
          Service = "events.amazonaws.com"
        },
        Action = "sts:AssumeRole"
      }
    ]
  })
}

# StepFunctionsの呼び出し権
resource "aws_iam_role_policy_attachment" "sfn_eventbridge_policy" {
  role       = aws_iam_role.eventbridge_role.id
  policy_arn = "arn:aws:iam::aws:policy/AWSStepFunctionsFullAccess"
}

# 実行タイミング定義
resource "aws_cloudwatch_event_rule" "my_scheduled_rule" {
  name                = "scraping-interval"
  description         = "Trigger sfn on a schedule"
  schedule_expression = "cron(0 0 ? * 2 *)"
}

# 実行対象定義
resource "aws_cloudwatch_event_target" "example_target" {
  rule      = aws_cloudwatch_event_rule.my_scheduled_rule.name
  target_id = "step-functions"
  arn       = aws_sfn_state_machine.sfn_state_machine.arn
  role_arn  = aws_iam_role.eventbridge_role.arn
}