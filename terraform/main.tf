terraform {
  required_version = ">= 1.1.1"
}

variable "image_tag" {
    default = "1.2.3"
    type = string
}

output "uptime_url" {
  value = "Your image was ${var.image_tag}."
}
