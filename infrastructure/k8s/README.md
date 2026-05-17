# Kubernetes Deployment

## Talab

- Kubernetes 1.27+ kluster
- `kubectl` CLI
- nginx-ingress-controller
- cert-manager (Let's Encrypt uchun)

## Deploy

```bash
# 1. Namespace
kubectl apply -f namespace.yaml

# 2. Secrets (avval edit qiling!)
cp secrets.example.yaml secrets.yaml
nano secrets.yaml  # parollarni o'zgartiring
kubectl apply -f secrets.yaml

# 3. Postgres
kubectl apply -f postgres-statefulset.yaml

# 4. Backend + Frontend
kubectl apply -f backend-deployment.yaml
kubectl apply -f frontend-deployment.yaml

# 5. Ingress (HTTPS bilan)
kubectl apply -f ingress.yaml

# 6. Status tekshirish
kubectl get pods -n unianalytics
kubectl get svc -n unianalytics
kubectl get ingress -n unianalytics
```

## Logs

```bash
kubectl logs -n unianalytics deployment/backend -f
kubectl logs -n unianalytics statefulset/postgres-oltp
```

## Scale

```bash
kubectl scale -n unianalytics deployment/backend --replicas=5
```

## Cloud providers

### DigitalOcean K8s
- Cluster yarating (3 node × $24/oy = $72/oy)
- Doctl orqali kubectl ulang
- Load Balancer: $12/oy

### Google GKE
- Standard cluster
- Autopilot mode ham mavjud

### AWS EKS
- Eng qimmat (~$73/oy control plane + nodes)
