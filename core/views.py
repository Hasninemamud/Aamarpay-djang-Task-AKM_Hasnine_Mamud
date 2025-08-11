import requests
import uuid
from django.conf import settings
from django.shortcuts import render, redirect
from django.http import JsonResponse
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from .models import FileUpload, PaymentTransaction, ActivityLog
from .serializers import FileUploadSerializer, PaymentTransactionSerializer, ActivityLogSerializer
from .tasks import process_file_word_count_with_content

class FileUploadViewSet(viewsets.ModelViewSet):
    serializer_class = FileUploadSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return FileUpload.objects.filter(user=self.request.user)
    
    def create(self, request, *args, **kwargs):
        # Check if user has made a successful payment
        has_successful_payment = PaymentTransaction.objects.filter(
            user=request.user, 
            status='success'
        ).exists()
        
        if not has_successful_payment:
            return Response(
                {"error": "Payment required before uploading files"}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            # Get the file from request.FILES
            if 'file' not in request.FILES:
                return Response(
                    {"error": "No file provided"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create a copy of request data
            data = request.data.copy()
            
            # Pass the request context to the serializer
            serializer = self.get_serializer(data=data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def perform_create(self, serializer):
        file_upload = serializer.save(user=self.request.user, status='processing')
        
        ActivityLog.objects.create(
            user=self.request.user,
            action='file_uploaded',
            metadata={
                'file_id': file_upload.id,
                'filename': file_upload.filename
            }
        )
        
        process_file_word_count_with_content.delay(file_upload.id)

class PaymentTransactionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PaymentTransactionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return PaymentTransaction.objects.filter(user=self.request.user)

class ActivityLogViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ActivityLogSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return ActivityLog.objects.filter(user=self.request.user)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def initiate_payment(request):
    try:
        # Generate unique transaction ID
        transaction_id = f"txn_{uuid.uuid4().hex[:8]}"
        
        # Create payment transaction
        payment = PaymentTransaction.objects.create(
            user=request.user,
            transaction_id=transaction_id,
            amount=100,
            status='pending'
        )
        
        # Log activity
        ActivityLog.objects.create(
            user=request.user,
            action='payment_initiated',
            metadata={'transaction_id': transaction_id, 'amount': 100}
        )
        
        # Prepare payment data
        payment_data = {
            'store_id': settings.AAMARPAY_CONFIG['store_id'],
            'signature_key': settings.AAMARPAY_CONFIG['signature_key'],
            'tran_id': transaction_id,
            'success_url': settings.AAMARPAY_CONFIG['success_url'],
            'fail_url': settings.AAMARPAY_CONFIG['fail_url'],
            'cancel_url': settings.AAMARPAY_CONFIG['cancel_url'],
            'amount': settings.AAMARPAY_CONFIG['amount'],
            'currency': settings.AAMARPAY_CONFIG['currency'],
            'desc': 'Payment for file upload service',
            'cus_name': request.user.get_full_name() or request.user.username,
            'cus_email': request.user.email or 'test@example.com',
            'cus_phone': '01800000000',
            'type': 'json',
            'cus_add1': 'Dhaka',
            'cus_city': 'Dhaka',
            'cus_country': 'Bangladesh',
            'cus_postcode': '1000',
        }
        
        # Make request to aamarPay
        response = requests.post(
            settings.AAMARPAY_CONFIG['endpoint'],
            json=payment_data,
            headers={'Content-Type': 'application/json'}
        )
        
        # Parse response
        response_data = response.json()
        payment.gateway_response = response_data
        payment.save()
        
        # Check result
        if response_data.get('result') == 'true':
            return Response({
                'payment_url': response_data.get('payment_url'),
                'transaction_id': transaction_id
            })
        else:
            error_msg = response_data.get('error', response_data.get('message', 'Unknown error'))
            return Response({'error': f'Payment gateway error: {error_msg}'}, status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def _handle_payment_callback(request, status_type):
    """Helper function to handle payment callbacks"""
    # Get transaction ID
    transaction_id = request.GET.get('mer_txnid') if request.method == 'GET' else request.POST.get('mer_txnid')
    
    if not transaction_id:
        return JsonResponse({'error': 'Transaction ID missing'}, status=400)
    
    try:
        # Find payment transaction
        payment = PaymentTransaction.objects.get(transaction_id=transaction_id)
        payment.status = status_type
        payment.save()
        
        # Log activity
        ActivityLog.objects.create(
            user=payment.user,
            action=f'payment_{status_type}',
            metadata={'transaction_id': transaction_id, 'amount': float(payment.amount)}
        )
        
        # Redirect to dashboard
        return redirect(f'/dashboard/?payment_status={status_type}&transaction_id={transaction_id}')
    
    except PaymentTransaction.DoesNotExist:
        return JsonResponse({'error': 'Invalid transaction ID'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def payment_success(request):
    return _handle_payment_callback(request, 'success')

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def payment_fail(request):
    return _handle_payment_callback(request, 'failed')

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def payment_cancel(request):
    return _handle_payment_callback(request, 'cancelled')

from django.contrib.auth.decorators import login_required

@login_required
def dashboard(request):
    user = request.user
    has_successful_payment = PaymentTransaction.objects.filter(user=user, status='success').exists()
    
    # Get or create token for the user
    token, created = Token.objects.get_or_create(user=user)
    
    context = {
        'user': user,
        'has_successful_payment': has_successful_payment,
        'files': FileUpload.objects.filter(user=user).order_by('-upload_time'),
        'activities': ActivityLog.objects.filter(user=user).order_by('-timestamp')[:10],
        'payments': PaymentTransaction.objects.filter(user=user).order_by('-timestamp'),
        'auth_token': token.key,
        'payment_status': request.GET.get('payment_status'),
        'transaction_id': request.GET.get('transaction_id'),
    }
    
    return render(request, 'core/dashboard.html', context)