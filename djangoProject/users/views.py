from django.shortcuts import render

# Create your views here.
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import UserRegisterSerializer, UserLoginSerializer, UserProfileSerializer
from ml_models.stock_lstm import get_training_data_lstm, train, predict_next_price, LOOK_BACK

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)
@method_decorator(csrf_exempt, name='dispatch')
class TrainAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        stock = request.data.get("stock", "").lower()
        model_type = request.data.get("model", "lstm").lower()

        if not stock:
            return Response({"error": "Missing 'stock' field."}, status=status.HTTP_400_BAD_REQUEST)

        if model_type != "lstm":
            return Response({"error": f"Model '{model_type}' is not supported yet."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            X_train, X_test, y_train, y_test = get_training_data_lstm(stock, LOOK_BACK)
            if isinstance(X_train, str):
                return Response({"error": X_train}, status=status.HTTP_400_BAD_REQUEST)

            rmse, mae, r2 = train(X_train, y_train, X_test, y_test,stock)

            return Response({
                "message": f"{model_type.upper()} model trained successfully for {stock}",
                "rmse": rmse,
                "mae": mae,
                "r2": r2
            })

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@method_decorator(csrf_exempt, name='dispatch')
class PredictAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        stock = request.data.get("stock", "").lower()
        model_type = request.data.get("model", "lstm").lower()

        if not stock:
            return Response({"error": "Missing 'stock' field."}, status=status.HTTP_400_BAD_REQUEST)

        if model_type != "lstm":
            return Response({"error": f"Model '{model_type}' is not supported yet."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            prediction = predict_next_price(stock)
            return Response({
                "stock": stock,
                "model": model_type,
                "predicted_price": prediction
            })
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)