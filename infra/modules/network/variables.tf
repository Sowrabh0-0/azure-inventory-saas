variable "name_prefix" { type = string }
variable "location" { type = string }
variable "resource_group_name" { type = string }
variable "address_space" { type = string }
variable "subnet_prefix" { type = string }
variable "ssh_source_address_prefix" { type = string }
variable "tags" { type = map(string) }

