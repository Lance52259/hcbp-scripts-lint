variable "microphone" {
  description = "Audio device name — must not match phone via contains"
  type        = string
  default     = "default"
}

variable "speakerphone" {
  description = "Another substring that previously matched phone"
  type        = string
  default     = "off"
}
