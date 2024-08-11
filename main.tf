terraform {
  required_version = ">= 1.5.0, < 2.0.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 4.0.0, < 5.0.0"
    }
    null = {
      source  = "hashicorp/null"
      version = ">= 3.0.0, < 4.0.0"
    }
  }
}


provider "aws" {
  region = "eu-north-1"  # Change to your preferred AWS region

  default_tags {
    tags = {
      Project     = "GooglePhotosAlbumBackup"
    }
  }
}

# S3 Bucket
resource "aws_s3_bucket" "google_photos_album_backup_bucket" {
  bucket = "google-photos-album-backup"  # Change this to a unique bucket name
}

# Secrets Manager Secret
resource "aws_secretsmanager_secret" "google_photos_album_backup_secret" {
  name        = "google-photos-album-backup-secret"
  description = "An example secret"
}

#resource "aws_secretsmanager_secret_version" "google_photos_album_backup_secret_version" {
#  secret_id     = aws_secretsmanager_secret.google_photos_album_backup_secret.id
#  secret_string = "my-plaintext-secret"  # Replace with your secret value
#}

# IAM Role for Lambda
resource "aws_iam_role" "lambda_exec_role" {
  name = "lambda_exec_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action    = "sts:AssumeRole",
        Effect    = "Allow",
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

# IAM Policy for Lambda Execution Role
resource "aws_iam_policy" "lambda_exec_policy" {
  name = "lambda_exec_policy"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action   = [
          "s3:PutObject",
          "s3:GetObject",
          "s3:ListBucket"
        ],
        Effect   = "Allow",
        Resource = [
          aws_s3_bucket.google_photos_album_backup_bucket.arn,
          "${aws_s3_bucket.google_photos_album_backup_bucket.arn}/*"
        ]
      },
      {
        Action   = "secretsmanager:GetSecretValue",
        Effect   = "Allow",
        Resource = aws_secretsmanager_secret.google_photos_album_backup_secret.arn
      }
    ]
  })
}

# Attach the policy to the role
resource "aws_iam_role_policy_attachment" "lambda_exec_policy_attachment" {
  role       = aws_iam_role.lambda_exec_role.name
  policy_arn = aws_iam_policy.lambda_exec_policy.arn
}

# Lambda Function
resource "aws_lambda_function" "google_photos_album_backup_lambda" {
  function_name = "google_photos_album_backup_lambda"
  role          = aws_iam_role.lambda_exec_role.arn
  handler       = "index.handler"
  runtime       = "nodejs18.x"

  # Zip file containing your Lambda function code
  filename = "lambda_function_payload.zip"

  # Environment variables
  environment {
    variables = {
      SECRET_NAME = aws_secretsmanager_secret.google_photos_album_backup_secret.name
      BUCKET_NAME = aws_s3_bucket.google_photos_album_backup_bucket.bucket
    }
  }
}

# Optional: S3 Bucket Policy to allow Lambda function access (if needed)
resource "aws_s3_bucket_policy" "google_photos_album_backup_bucket_policy" {
  bucket = aws_s3_bucket.google_photos_album_backup_bucket.id

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action    = "s3:*",
        Effect    = "Allow",
        Resource  = [
          aws_s3_bucket.google_photos_album_backup_bucket.arn,
          "${aws_s3_bucket.google_photos_album_backup_bucket.arn}/*"
        ],
        Principal = {
          AWS = aws_iam_role.lambda_exec_role.arn
        }
      }
    ]
  })
}
