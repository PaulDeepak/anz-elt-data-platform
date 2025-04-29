output "composer_environment_name" {
  value = google_composer_environment.production.name
}

output "dataflow_service_account" {
  value = google_service_account.dataflow_sa.email
}
