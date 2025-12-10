#!/bin/bash
# Diagnostic script for AI Republic deployment

echo "=== Checking AI Republic Kubernetes Deployment ==="
echo ""

echo "1. Checking namespace..."
kubectl get namespace airepubliq

echo ""
echo "2. Checking pods..."
kubectl get pods -n airepubliq

echo ""
echo "3. Checking services..."
kubectl get svc -n airepubliq

echo ""
echo "4. Checking ingress..."
kubectl get ingress -n airepubliq

echo ""
echo "5. Checking pod status details..."
kubectl get pods -n airepubliq -o wide

echo ""
echo "6. Frontend pod logs (last 30 lines)..."
FRONTEND_POD=$(kubectl get pods -n airepubliq -l app=frontend -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
if [ -n "$FRONTEND_POD" ]; then
    kubectl logs -n airepubliq $FRONTEND_POD --tail=30
else
    echo "No frontend pods found"
fi

echo ""
echo "7. Backend pod logs (last 30 lines)..."
BACKEND_POD=$(kubectl get pods -n airepubliq -l app=backend -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
if [ -n "$BACKEND_POD" ]; then
    kubectl logs -n airepubliq $BACKEND_POD --tail=30
else
    echo "No backend pods found"
fi

echo ""
echo "8. Checking pod events..."
kubectl get events -n airepubliq --sort-by='.lastTimestamp' | tail -20

echo ""
echo "9. Checking secrets..."
kubectl get secrets -n airepubliq

echo ""
echo "=== Diagnostic Complete ==="
