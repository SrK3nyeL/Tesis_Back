from django.contrib.auth import authenticate
from rest_framework import generics, status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from .models import Usuario
from .serializers import LoginSerializer, UsuarioCreateSerializer, UsuarioSerializer


class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(
            request=request,
            username=serializer.validated_data["username"],
            password=serializer.validated_data["password"],
        )
        if user is None or not user.is_active:
            return Response({"detalle": "Credenciales invalidas o cuenta inactiva."}, status=status.HTTP_401_UNAUTHORIZED)
        token, _ = Token.objects.get_or_create(user=user)
        return Response({"token": token.key, "usuario": UsuarioSerializer(user).data})


class LogoutView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        Token.objects.filter(user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PerfilView(generics.RetrieveUpdateAPIView):
    serializer_class = UsuarioSerializer

    def get_object(self):
        return self.request.user


class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        queryset = super().get_queryset()
        if role := self.request.query_params.get("rol"):
            queryset = queryset.filter(rol=role)
        if active := self.request.query_params.get("activo"):
            queryset = queryset.filter(is_active=active.lower() in {"1", "true", "si"})
        return queryset

    def get_serializer_class(self):
        return UsuarioCreateSerializer if self.action == "create" else UsuarioSerializer

    @action(detail=True, methods=["post"])
    def activar(self, request, pk=None):
        user = self.get_object()
        user.is_active = True
        user.save(update_fields=["is_active"])
        return Response(UsuarioSerializer(user).data)

    @action(detail=True, methods=["post"])
    def desactivar(self, request, pk=None):
        user = self.get_object()
        if user == request.user:
            return Response({"detalle": "No puede desactivar su propia cuenta."}, status=400)
        user.is_active = False
        Token.objects.filter(user=user).delete()
        user.save(update_fields=["is_active"])
        return Response(UsuarioSerializer(user).data)
