output "cluster_id" {
  value = azurerm_kubernetes_cluster.main.id
}
output "cluster_name" {
  value = azurerm_kubernetes_cluster.main.name
}
output "kube_config" {
  value     = azurerm_kubernetes_cluster.main.kube_config[0]
  sensitive = true
}
output "oidc_issuer_url" {
  value = azurerm_kubernetes_cluster.main.oidc_issuer_url
}
output "kubelet_identity" {
  value = azurerm_kubernetes_cluster.main.kubelet_identity[0].object_id
}