resource "huaweicloud_asm_mesh" "test" {
  name = var.mesh_name

  extend_params {
    clusters {
      cluster_id = var.cluster_id

      installation {
        nodes {
          field_selector {
            key      = "UID"
            operator = "In"
            values   = [var.node_id]
          }
        }
      }
    }
  }
}
