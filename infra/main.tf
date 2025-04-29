provider "google" {
  project = "anz-data-platform"
  region  = "us-central1"
}

# Enable required APIs
resource "google_project_service" "apis" {
  for_each = toset([
    "dataflow.googleapis.com",
    "composer.googleapis.com",
    "storage.googleapis.com",
    "bigquery.googleapis.com"
  ])
  service = each.key
}

# Storage buckets
resource "google_storage_bucket" "raw_data" {
  name          = "anz-raw-data-${var.project_id}"
  location      = "US"
  force_destroy = true
}

resource "google_storage_bucket" "dataflow_templates" {
  name          = "anz-dataflow-templates-${var.project_id}"
  location      = "US"
}

resource "google_storage_bucket" "composer_dags" {
  name          = "anz-composer-dags-${var.project_id}"
  location      = "US"
}

# BigQuery dataset
resource "google_bigquery_dataset" "analytics" {
  dataset_id = "anz_analytics"
  location   = "US"
}

# Service accounts
resource "google_service_account" "dataflow_sa" {
  account_id   = "anz-dataflow-sa"
  display_name = "Dataflow Service Account"
}

resource "google_service_account" "composer_sa" {
  account_id   = "anz-composer-sa"
  display_name = "Composer Service Account"
}

# IAM bindings
resource "google_project_iam_binding" "dataflow_roles" {
  project = var.project_id
  role    = "roles/dataflow.worker"
  members = [
    "serviceAccount:${google_service_account.dataflow_sa.email}"
  ]
}

resource "google_project_iam_binding" "composer_roles" {
  project = var.project_id
  role    = "roles/composer.worker"
  members = [
    "serviceAccount:${google_service_account.composer_sa.email}"
  ]
}

# Composer environment
resource "google_composer_environment" "production" {
  name   = "anz-composer-env"
  region = "us-central1"

  config {
    node_count = 3
    node_config {
      machine_type = "n1-standard-2"
      service_account = google_service_account.composer_sa.email
    }

    software_config {
      image_version = "composer-2-airflow-2"
      pypi_packages = {
        "apache-airflow-providers-google" = ">=8.0.0"
        "apache-airflow-providers-http"   = ">=5.2.2"
      }
    }
  }

  depends_on = [google_project_service.apis]
}
