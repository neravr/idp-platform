resource "azurerm_kubernetes_cluster" "main" {
  name                = "aks-${var.prefix}-${var.env}"
  location            = var.location
  resource_group_name = var.resource_group_name
  dns_prefix          = "${var.prefix}-${var.env}"
  kubernetes_version  = var.kubernetes_version

  oidc_issuer_enabled       = true
  workload_identity_enabled = true

  default_node_pool {
    name           = "system"
    node_count     = var.system_node_count
    vm_size        = "Standard_D2s_v3"
    vnet_subnet_id = var.aks_subnet_id
    type           = "VirtualMachineScaleSets"
    upgrade_settings {
      max_surge = "10%"
    }
  }

  identity {
    type = "SystemAssigned"
  }

  network_profile {
    network_plugin    = "azure"
    network_policy    = "calico"
    load_balancer_sku = "standard"
  }


  tags = var.tags
}

resource "azurerm_kubernetes_cluster_node_pool" "user" {
  name                  = "user"
  kubernetes_cluster_id = azurerm_kubernetes_cluster.main.id
  vm_size               = var.user_node_vm_size
  min_count             = var.node_min_count
  max_count             = var.node_max_count
  enable_auto_scaling   = true
  vnet_subnet_id        = var.aks_subnet_id
  mode                  = "User"
  tags                  = var.tags
}