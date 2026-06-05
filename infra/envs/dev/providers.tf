terraform {
  required_version = ">= 1.8.0"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.0"
    }
  }

  # Configure an azurerm backend here when you are ready to persist state remotely.
  # backend "azurerm" {}
}

provider "azurerm" {
  features {}
}

