resource "azurerm_resource_group" "main" {
  name     = "rg-${var.prefix}-${var.env}"
  location = var.location
  tags     = merge(var.tags, { "created-at" = timestamp() })
}

module "networking" {
  source              = "./modules/networking"
  prefix              = var.prefix
  env                 = var.env
  location            = var.location
  resource_group_name = azurerm_resource_group.main.name
  vnet_cidr           = var.vnet_cidr
  aks_subnet_cidr     = var.aks_subnet_cidr
  appgw_subnet_cidr   = var.appgw_subnet_cidr
  tags                = var.tags
}

module "aks_cluster" {
  source              = "./modules/aks-cluster"
  prefix              = var.prefix
  env                 = var.env
  location            = var.location
  resource_group_name = azurerm_resource_group.main.name
  aks_subnet_id       = module.networking.aks_subnet_id
  user_node_vm_size   = var.user_node_vm_size
  node_min_count      = var.node_min_count
  node_max_count      = var.node_max_count
  tags                = var.tags
}

module "acr" {
  source              = "./modules/acr"
  prefix              = var.prefix
  env                 = var.env
  location            = var.location
  resource_group_name = azurerm_resource_group.main.name
  kubelet_identity_id = module.aks_cluster.kubelet_identity
  tags                = var.tags
}

module "security" {
  source              = "./modules/security"
  prefix              = var.prefix
  env                 = var.env
  location            = var.location
  resource_group_name = azurerm_resource_group.main.name
  resource_group_id   = azurerm_resource_group.main.id
  kubelet_identity_id = module.aks_cluster.kubelet_identity
  tags                = var.tags
}

module "monitoring" {
  source                 = "./modules/monitoring"
  domain                 = var.domain
  grafana_admin_password = var.grafana_admin_password
}

module "ingress" {
  source              = "./modules/ingress"
  prefix              = var.prefix
  env                 = var.env
  location            = var.location
  resource_group_name = azurerm_resource_group.main.name
  appgw_subnet_id     = module.networking.appgw_subnet_id
  tags                = var.tags
}

module "argocd" {
  source          = "./modules/argocd"
  domain          = var.domain
  env             = var.env
  gitops_repo_url = "https://github.com/neravr/idp-gitops"
}

module "vault" {
  source          = "./modules/vault"
  domain          = var.domain
  env             = var.env
  kube_host       = module.aks_cluster.kube_config.host
  oidc_issuer_url = module.aks_cluster.oidc_issuer_url
}