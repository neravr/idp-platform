variable "prefix"              { type = string }
variable "env"                 { type = string }
variable "location"            { type = string }
variable "resource_group_name" { type = string }
variable "kubelet_identity_id" { type = string }
variable "tags" {
  type    = map(string)
  default = {}
}