data "azurerm_client_config" "current" {}

resource "azurerm_key_vault" "main" {
  name                       = "kv-${var.prefix}-${var.env}"
  location                   = var.location
  resource_group_name        = var.resource_group_name
  tenant_id                  = data.azurerm_client_config.current.tenant_id
  sku_name                   = "standard"
  soft_delete_retention_days = 7
  purge_protection_enabled   = true
  enable_rbac_authorization  = true
  tags                       = var.tags
}

resource "azurerm_role_assignment" "aks_kv_secrets" {
  scope                = azurerm_key_vault.main.id
  role_definition_name = "Key Vault Secrets User"
  principal_id         = var.kubelet_identity_id
}

resource "azurerm_resource_group_policy_assignment" "k8s_baseline" {
  name                 = "k8s-guardrails-${var.env}"
  resource_group_id    = var.resource_group_id
  policy_definition_id = "/providers/Microsoft.Authorization/policySetDefinitions/a8640138-9b0a-4a28-b8cb-1666c838647d"
  display_name         = "Kubernetes pod security baseline"
}

resource "helm_release" "gatekeeper" {
  name             = "gatekeeper"
  repository       = "https://open-policy-agent.github.io/gatekeeper/charts"
  chart            = "gatekeeper"
  version          = "3.14.0"
  namespace        = "gatekeeper-system"
  create_namespace = true

  set {
    name  = "auditInterval"
    value = "30"
  }
  set {
    name  = "emitAdmissionEvents"
    value = "true"
  }
}