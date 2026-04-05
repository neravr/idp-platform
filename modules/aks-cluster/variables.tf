variable "prefix"              { type = string }
variable "env"                 { type = string }
variable "location"            { type = string }
variable "resource_group_name" { type = string }
variable "aks_subnet_id"       { type = string }
variable "kubernetes_version" {
  type    = string
  default = "1.28"
}
variable "system_node_count" {
  type    = number
  default = 2
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
variable "tags" {
  type    = map(string)
  default = {}
}