variable "prefix" {
  type        = string
  description = "Short name prefix for all resources"
}

variable "env" {
  type        = string
  description = "Environment tier: dev, staging, prod"
}

variable "location" {
  type        = string
  description = "Azure region"
  default     = "eastus"
}

variable "vnet_cidr" {
  type    = string
  default = "10.0.0.0/16"
}

variable "aks_subnet_cidr" {
  type    = string
  default = "10.0.1.0/24"
}

variable "appgw_subnet_cidr" {
  type    = string
  default = "10.0.2.0/24"
}

variable "user_node_vm_size" {
  type    = string
  default = "Standard_D4s_v3"
}

variable "node_min_count" {
  type    = number
  default = 2
}

variable "node_max_count" {
  type    = number
  default = 10
}

variable "domain" {
  type    = string
  default = "demo.example.com"
}

variable "grafana_admin_password" {
  type      = string
  sensitive = true
  default   = "Admin1234!"
}

variable "tags" {
  type    = map(string)
  default = {}
}