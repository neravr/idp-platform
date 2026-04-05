output "vault_url"  { value = "https://vault.${var.domain}" }
output "vault_path" { value = "secret/data/${var.env}" }