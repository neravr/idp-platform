# IDP Platform

An Internal Developer Platform built on Azure that lets engineers provision fully configured, policy-compliant Kubernetes environments by describing what they need in plain English — no DevOps ticket, no waiting, no manual configuration.

Built as a portfolio project to demonstrate end-to-end cloud infrastructure engineering: infrastructure as code, GitOps, secrets management, policy enforcement, and AI-assisted automation.

---

## The problem this solves

At most companies, getting a new cloud environment means opening a ticket and waiting for a DevOps engineer. It takes days. The environment comes back with inconsistent configuration, missing monitoring, and security settings that vary from team to team.

This platform eliminates that entirely. A developer describes what they need. The AI figures out the right configuration. Ten minutes later they have a fully provisioned AKS cluster with monitoring, secrets management, and compliance policies already in place — identical every time.

---

## How it works

```
Developer types:
"I need a staging environment for a data pipeline, ml-platform team"

         ↓ Claude API parses intent

AI extracts:
  team      → ml-platform
  tier      → staging
  template  → data-pipeline

         ↓ GitHub Actions triggers Terraform

Infrastructure created:
  - AKS cluster (memory-optimized nodes for data workloads)
  - Azure Key Vault + RBAC
  - Prometheus + Grafana
  - ArgoCD (GitOps)
  - HashiCorp Vault (secret injection)
  - OPA Gatekeeper (compliance enforcement)
  - App Gateway + WAF

         ↓ Slack notification with cluster details

Developer receives:
  cluster endpoint, Grafana URL, Vault path, ArgoCD URL
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Developer request                         │
│         "dev env for payments API team"                      │
└──────────────────────────┬──────────────────────────────────┘
                           │
                    ┌──────▼──────┐
                    │  Claude API  │  parses intent → JSON config
                    └──────┬──────┘
                           │
              ┌────────────▼────────────┐
              │   GitHub Actions        │
              │   ai-provision.yml      │  triggers provision.yml
              └────────────┬────────────┘
                           │
              ┌────────────▼────────────┐
              │   Terraform modules     │
              │                         │
              │  networking  aks-cluster │
              │  security    monitoring  │
              │  ingress     acr         │
              │  argocd      vault       │
              └────────────┬────────────┘
                           │
              ┌────────────▼────────────┐
              │   Azure AKS Cluster     │
              │                         │
              │  OPA Gatekeeper         │  blocks non-compliant workloads
              │  ArgoCD                 │  deploys from Git automatically
              │  HashiCorp Vault        │  injects secrets at runtime
              │  Prometheus + Grafana   │  monitoring from day one
              └─────────────────────────┘
```

---

## Tech stack

| Layer | Technology |
|-------|-----------|
| Cloud | Azure (AKS, Key Vault, App Gateway WAF, ACR, VNET) |
| Infrastructure as Code | Terraform (8 reusable modules) |
| Container Orchestration | Kubernetes (AKS) |
| GitOps | ArgoCD — App of Apps pattern |
| Secrets Management | HashiCorp Vault — Kubernetes auth + agent injection |
| Policy Enforcement | OPA Gatekeeper — admission webhooks |
| Monitoring | Prometheus + Grafana |
| CI/CD | GitHub Actions |
| AI Layer | Claude API (Anthropic) — natural language provisioning |
| TLS / Ingress | cert-manager + Azure App Gateway |

---

## Environment templates

Rather than asking developers to configure infrastructure, they pick a workload type and get pre-validated defaults:

| Template | Use case | Node pool | Ingress |
|----------|----------|-----------|---------|
| `api-service` | REST APIs, web backends | Standard_D4s_v3, 2–6 nodes | Enabled |
| `data-pipeline` | Batch jobs, ETL, workers | Standard_E8s_v3, 2–8 nodes | Disabled |
| `ml-workload` | Model training, inference | Standard_NC6s_v3, 1–4 nodes | Enabled |

---

## Repository structure

```
idp-platform/
├── modules/
│   ├── networking/       # VNET, subnets, NSGs
│   ├── aks-cluster/      # AKS, node pools, OIDC, workload identity
│   ├── security/         # Key Vault, IAM, Azure Policy, OPA Gatekeeper
│   ├── monitoring/       # Prometheus + Grafana
│   ├── ingress/          # App Gateway WAF, cert-manager
│   ├── acr/              # Azure Container Registry
│   ├── argocd/           # ArgoCD GitOps bootstrap
│   └── vault/            # HashiCorp Vault HA
├── environments/
│   ├── dev.tfvars
│   ├── staging.tfvars
│   └── prod.tfvars
├── templates/
│   ├── api-service.tfvars
│   ├── data-pipeline.tfvars
│   └── ml-workload.tfvars
├── ai/
│   ├── system_prompt.py    # Platform knowledge encoded for Claude
│   ├── ai_provisioner.py   # Natural language → structured config
│   └── trigger_workflow.py # GitHub API workflow trigger
├── gatekeeper/
│   └── no-latest-tag.yaml  # OPA constraint templates
├── .github/workflows/
│   ├── ai-provision.yml    # AI-powered self-service entry point
│   ├── provision.yml       # Core provisioning workflow
│   ├── pr-validate.yml     # PR validation + cost estimation
│   └── lifecycle.yml       # TTL + auto-destroy
├── backend.tf
├── main.tf
└── variables.tf
```

---

## Running it yourself

**Prerequisites:** Azure CLI, Terraform, kubectl, Helm, Python 3.11+

**1. Bootstrap remote state**
```bash
az group create --name rg-idp-tfstate --location eastus
az storage account create --name <unique-name> --resource-group rg-idp-tfstate --sku Standard_LRS
az storage container create --name tfstate --account-name <unique-name>
```

**2. Configure backend**

Update `backend.tf` with your storage account name.

**3. Add GitHub secrets**
```
AZURE_CLIENT_ID
AZURE_CLIENT_SECRET
AZURE_TENANT_ID
AZURE_SUBSCRIPTION_ID
ANTHROPIC_API_KEY
GH_DISPATCH_TOKEN
GH_GITOPS_TOKEN
```

**4. Plan infrastructure**
```bash
terraform init
terraform plan -var="prefix=myteam" -var="env=dev"
```

**5. Provision via AI**

Go to Actions → AI environment provisioner → Run workflow

Type: `"dev environment for a Python API, payments team"`

---

## What I'd add next

- Private endpoints for Key Vault and ACR (zero public exposure)
- Infracost PR comments showing monthly cost delta before merge
- Multi-region failover with Azure Traffic Manager
- Backstage integration as a developer portal frontend
- Network policies between namespaces (zero-trust pod communication)
