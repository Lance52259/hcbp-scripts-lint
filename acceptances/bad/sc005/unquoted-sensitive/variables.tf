# Unquoted sensitive variable name must still trigger SC.005
variable api_token {
  description = "API access token"
  type        = string
}
