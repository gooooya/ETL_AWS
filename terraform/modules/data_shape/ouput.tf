output "glue_job_name" {
  value = aws_glue_job.my_job.name
}

output "my_crawler_before_etl_arn" {
  value = aws_glue_crawler.my_crawler_before_etl.arn
}
output "my_crawler_after_etl_arn" {
  value = aws_glue_crawler.my_crawler_after_etl.arn
}

output "glue_role_name" {
  value = aws_iam_role.glue_role.name
}


# TODO;Athena