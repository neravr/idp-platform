resource "helm_release" "argocd" {
  name             = "argocd"
  repository       = "https://argoproj.github.io/argo-helm"
  chart            = "argo-cd"
  version          = "5.51.6"
  namespace        = "argocd"
  create_namespace = true

  values = [yamlencode({
    server = {
      ingress = {
        enabled     = true
        annotations = { "kubernetes.io/ingress.class" = "azure/application-gateway" }
        hosts       = ["argocd.${var.domain}"]
      }
    }
  })]
}
