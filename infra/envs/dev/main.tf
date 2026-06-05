resource "azurerm_resource_group" "this" {
  name     = "${var.name_prefix}-rg"
  location = var.location
  tags     = local.tags
}

module "network" {
  source                    = "../../modules/network"
  name_prefix               = var.name_prefix
  location                  = var.location
  resource_group_name       = azurerm_resource_group.this.name
  address_space             = var.address_space
  subnet_prefix             = var.subnet_prefix
  ssh_source_address_prefix = var.ssh_source_address_prefix
  tags                      = local.tags
}

module "vm" {
  source              = "../../modules/vm"
  name_prefix         = var.name_prefix
  location            = var.location
  resource_group_name = azurerm_resource_group.this.name
  subnet_id           = module.network.subnet_id
  vm_size             = var.vm_size
  availability_zone   = var.availability_zone
  admin_username      = var.admin_username
  admin_password      = var.admin_password
  tags                = local.tags
}

locals {
  tags = {
    app         = "azure-inventory"
    environment = "dev"
    managed_by  = "terraform"
  }
}
