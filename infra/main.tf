provider "google" {
  project = "anz-data-platform"  # Replace with your actual Project ID
  region  = "us-central1"
}

# Storage for raw data
resource "google_storage_bucket" "raw_data" {
  name          = "anz-raw-data-${var.project_id}"
  location      = "US"
  force_destroy = true
}

# BigQuery dataset
resource "google_bigquery_dataset" "analytics" {
  dataset_id = "anz_analytics"
  location   = "US"
}

# Dataflow-specific resources
resource "google_project_service" "dataflow" {
  service = "dataflow.googleapis.com"
}

# Service account for Dataflow
resource "google_service_account" "dataflow_sa" {
  account_id   = "anz-dataflow-sa"
  display_name = "Dataflow Service Account"
}

resource "google_project_iam_binding" "dataflow_roles" {
  project = var.project_id
  role    = "roles/dataflow.worker"
  members = [
    "serviceAccount:${google_service_account.dataflow_sa.email}"
  ]
}
