terraform {
  required_version = ">= 1.1.1"
}

variable "message" {
    default = "Hello World!"
    type = string
}

output "uptime_url" {
  value = "Your message was ${var.message}."
}
