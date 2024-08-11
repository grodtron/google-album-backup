# backend.tf

#provider "aws" {
#  region = "us-west-2"  # Change to your preferred AWS region
#}

# Create S3 bucket for storing Terraform state
resource "aws_s3_bucket" "terraform_state" {
  bucket = "google-photos-album-backup-terraform-state"  # Change this to a unique bucket name

  lifecycle {
    prevent_destroy = true
  }

  tags = {
    Name        = "terraform-state"
    Environment = "production"
  }
}


resource "aws_s3_bucket_versioning" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id

  versioning_configuration {
    status = "Enabled"
  }
}

# Create DynamoDB table for state locking
resource "aws_dynamodb_table" "terraform_locks" {
  name         = "google-photos-album-backup-terraform-locks"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }

  tags = {
    Name        = "terraform-locks"
    Environment = "production"
  }
}

# Configure the backend to use S3 and DynamoDB for state and locking
terraform {
  backend "s3" {
    bucket         = "google-photos-album-backup-terraform-state"
    key            = "terraform.tfstate"
    region         = "eu-north-1"
    dynamodb_table = "google-photos-album-backup-terraform-locks"
    encrypt        = true
  }
}

