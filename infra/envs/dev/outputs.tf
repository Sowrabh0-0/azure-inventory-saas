output "public_ip_address" {
  value = module.vm.public_ip_address
}

output "public_base_url" {
  value = "http://${module.vm.public_ip_address}"
}

output "microsoft_redirect_uri" {
  value = "http://${module.vm.public_ip_address}/auth/callback"
}

output "ssh_command" {
  value = module.vm.ssh_command
}
