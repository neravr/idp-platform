resource "helm_release" "prometheus_stack" {
  name             = "prometheus"
  repository       = "https://prometheus-community.github.io/helm-charts"
  chart            = "kube-prometheus-stack"
  version          = "55.5.0"
  namespace        = "monitoring"
  create_namespace = true

  values = [yamlencode({
    grafana = {
      adminPassword = var.grafana_admin_password
      ingress = {
        enabled     = true
        annotations = { "kubernetes.io/ingress.class" = "azure/application-gateway" }
        hosts       = ["grafana.${var.domain}"]
      }
    }
    prometheus = {
      prometheusSpec = {
        retention = "15d"
        storageSpec = {
          volumeClaimTemplate = {
            spec = {
              resources = {
                requests = { storage = "20Gi" }
              }
            }
          }
        }
      }
    }
  })]
}