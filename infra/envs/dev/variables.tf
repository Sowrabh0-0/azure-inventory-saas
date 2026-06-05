variable "name_prefix" {
  type    = string
  default = "azinv-dev"
}

variable "location" {
  type    = string
  default = "eastus"
}

variable "address_space" {
  type    = string
  default = "10.40.0.0/16"
}

variable "subnet_prefix" {
  type    = string
  default = "10.40.1.0/24"
}

variable "ssh_source_address_prefix" {
  type        = string
  description = "Restrict this to your own IP for safer dev testing."
}

variable "vm_size" {
  type    = string
  default = "Standard_D2s_v3"
}

variable "availability_zone" {
  type    = string
  default = "3"
}

variable "admin_username" {
  type    = string
  default = "azureuser"
}

variable "admin_password" {
  type        = string
  sensitive   = true
  description = "Dev VM password. Store only in ignored tfvars or your secret manager."
}
