from django.db.models import Q
from rest_framework import viewsets

from .models import Cliente
from .serializers import ClienteSerializer


class ClienteViewSet(viewsets.ModelViewSet):
    serializer_class = ClienteSerializer

    def get_queryset(self):
        queryset = Cliente.objects.select_related("creado_por").all()
        if activo := self.request.query_params.get("activo"):
            queryset = queryset.filter(activo=activo.lower() in {"1", "true", "si"})
        if contract := self.request.query_params.get("contrato"):
            queryset = queryset.filter(contract=contract)
        if search := self.request.query_params.get("buscar"):
            queryset = queryset.filter(Q(customer_id__icontains=search) | Q(payment_method__icontains=search))
        return queryset

    def perform_create(self, serializer):
        serializer.save(creado_por=self.request.user)
