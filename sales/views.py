from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from accounts.permissions import AdminRequiredMixin, CanDeleteMixin
from .models import Product, Sale, Return
from .forms import ProductForm, SaleForm, ReturnForm
from .mixins import ProductListMixin, ProductDetailMixin, ProductCreateMixin, ProductUpdateMixin, ProductDeleteMixin
from django.db.models import Q
from django.utils import timezone

class ProductListView(LoginRequiredMixin, ProductListMixin):
    model = Product
    template_name = 'sales/product_list.html'
    success_url = reverse_lazy('product_list')

class ProductDetailView(LoginRequiredMixin, ProductDetailMixin):
    model = Product
    template_name = 'sales/product_detail.html'

class ProductCreateView(LoginRequiredMixin, ProductCreateMixin):
    model = Product
    template_name = 'sales/product_form.html'
    form_class = ProductForm
    success_url = reverse_lazy('product_list')

class ProductUpdateView(LoginRequiredMixin, ProductUpdateMixin):
    model = Product
    template_name = 'sales/product_form.html'
    form_class = ProductForm
    success_url = reverse_lazy('product_list')

class ProductDeleteView(LoginRequiredMixin, ProductDeleteMixin):
    model = Product
    template_name = 'sales/product_confirm_delete.html'
    success_url = reverse_lazy('product_list')

class SaleListView(LoginRequiredMixin, ListView):
    model = Sale
    template_name = 'sales/sale_list.html'
    context_object_name = 'sales'
    ordering = ['-sale_date']  # Show newest sales first
    paginate_by = 50  # Show 50 sales per page
    
    def get_queryset(self):
        from datetime import datetime, timedelta
        queryset = super().get_queryset()
        from django.db.models import Exists, OuterRef, Q
        
        # Add return status filtering
        return_status = self.request.GET.get('return_status', '').strip()
        if return_status == 'returned':
            # Show only sales with approved/completed returns
            approved_returns = Return.objects.filter(
                sale=OuterRef('pk'),
                status__in=['approved', 'completed']
            )
            queryset = queryset.filter(Exists(approved_returns))
        elif return_status == 'pending':
            # Show only sales with pending returns
            pending_returns = Return.objects.filter(
                sale=OuterRef('pk'),
                status='pending'
            )
            queryset = queryset.filter(Exists(pending_returns))
        elif return_status == 'approved':
            # Show only sales with approved returns
            approved_returns = Return.objects.filter(
                sale=OuterRef('pk'),
                status='approved'
            )
            queryset = queryset.filter(Exists(approved_returns))
        elif return_status == 'rejected':
            # Show only sales with rejected returns
            rejected_returns = Return.objects.filter(
                sale=OuterRef('pk'),
                status='rejected'
            )
            queryset = queryset.filter(Exists(rejected_returns))
        else:
            # Default: exclude fully returned sales (approved/completed)
            approved_returns = Return.objects.filter(
                sale=OuterRef('pk'),
                status__in=['approved', 'completed']
            )
            queryset = queryset.exclude(Exists(approved_returns))
        
        # Add search functionality
        search_query = self.request.GET.get('search', '').strip()
        if search_query:
            queryset = queryset.filter(
                Q(product__name__icontains=search_query) |
                Q(customer_name__icontains=search_query) |
                Q(id__icontains=search_query)
            )
        
        # Add date range filtering
        date_range = self.request.GET.get('date_range', '').strip()
        if date_range:
            if date_range == 'today':
                from django.utils import timezone
                today = timezone.now().date()
                queryset = queryset.filter(sale_date__date=today)
            elif date_range == 'week':
                from django.utils import timezone
                today = timezone.now().date()
                start_of_week = today - timedelta(days=today.weekday())
                queryset = queryset.filter(sale_date__date__gte=start_of_week)
            elif date_range == 'month':
                from django.utils import timezone
                today = timezone.now().date()
                start_of_month = today.replace(day=1)
                queryset = queryset.filter(sale_date__date__gte=start_of_month)
            elif date_range == 'quarter':
                from django.utils import timezone
                today = timezone.now().date()
                quarter = (today.month - 1) // 3
                start_of_quarter = today.replace(month=quarter * 3 + 1, day=1)
                queryset = queryset.filter(sale_date__date__gte=start_of_quarter)
            elif date_range == 'year':
                from django.utils import timezone
                today = timezone.now().date()
                start_of_year = today.replace(month=1, day=1)
                queryset = queryset.filter(sale_date__date__gte=start_of_year)
            elif date_range == 'custom':
                # Handle custom date range
                start_date = self.request.GET.get('start_date', '').strip()
                end_date = self.request.GET.get('end_date', '').strip()
                if start_date:
                    try:
                        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
                        queryset = queryset.filter(sale_date__date__gte=start_date_obj)
                    except ValueError:
                        pass
                if end_date:
                    try:
                        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
                        queryset = queryset.filter(sale_date__date__lte=end_date_obj)
                    except ValueError:
                        pass
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['date_range'] = self.request.GET.get('date_range', '')
        context['start_date'] = self.request.GET.get('start_date', '')
        context['end_date'] = self.request.GET.get('end_date', '')
        context['return_status'] = self.request.GET.get('return_status', '')
        
        # Calculate totals for the filtered sales
        from django.db.models import Sum
        queryset = self.get_queryset()
        totals = queryset.aggregate(
            total_quantity=Sum('quantity'),
            total_revenue=Sum('total_price')
        )
        context['total_quantity'] = totals['total_quantity'] or 0
        context['total_revenue'] = totals['total_revenue'] or 0
        
        return context

class SaleDetailView(LoginRequiredMixin, DetailView):
    model = Sale
    template_name = 'sales/sale_detail.html'

class SaleCreateView(LoginRequiredMixin, CreateView):
    model = Sale
    template_name = 'sales/sale_form.html'
    form_class = SaleForm
    success_url = reverse_lazy('sale_list')

    def form_valid(self, form):
        messages.success(self.request, "Sale created successfully.")
        return super().form_valid(form)

class SaleUpdateView(LoginRequiredMixin, UpdateView):
    model = Sale
    template_name = 'sales/sale_form.html'
    form_class = SaleForm
    success_url = reverse_lazy('sale_list')

    def form_valid(self, form):
        messages.success(self.request, "Sale updated successfully.")
        return super().form_valid(form)


class POSView(LoginRequiredMixin, TemplateView):
    """
    Point of Sale (POS) Terminal View
    
    Optimized for retail speed with:
    - Quick product search and selection
    - Real-time cart management
    - Keyboard shortcuts (Ctrl+N for new transaction)
    - Barcode scanner support
    - Fast payment processing
    - Transaction summary
    """
    template_name = 'sales/pos.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from inventory.models import Stock
        from django.db.models import OuterRef, Subquery
        
        # Get products with stock quantity
        stock_subquery = Stock.objects.filter(product=OuterRef('pk')).values('quantity')[:1]
        products = Product.objects.annotate(
            stock_quantity=Subquery(stock_subquery)
        ).order_by('name')
        context['products'] = products
        return context


class POSTestView(LoginRequiredMixin, TemplateView):
    """Test view for debugging POS transactions"""
    template_name = 'sales/pos_test.html'


@require_http_methods(["GET"])
def search_products(request):
    """
    AJAX endpoint for real-time product search
    Returns matching products as JSON for autocomplete
    """
    from inventory.models import Stock
    from django.db.models import OuterRef, Subquery
    
    query = request.GET.get('q', '').strip()
    
    if len(query) < 1:
        return JsonResponse({'results': []})
    
    stock_subquery = Stock.objects.filter(product=OuterRef('pk')).values('quantity')[:1]
    products = Product.objects.filter(
        name__icontains=query
    ).annotate(
        stock_quantity=Subquery(stock_subquery)
    ).values('id', 'name', 'price', 'stock_quantity').order_by('name')[:10]
    
    results = [
        {
            'id': p['id'],
            'name': p['name'],
            'price': str(p['price']),
            'stock': p['stock_quantity'] or 0
        }
        for p in products
    ]
    
    return JsonResponse({'results': results})


@require_http_methods(["GET"])
def get_sale_details(request, sale_id):
    """
    AJAX endpoint to get sale details for return form
    Returns sale info including product price for refund calculation
    """
    try:
        sale = Sale.objects.select_related('product').get(id=sale_id)
        unit_price = float(sale.total_price) / sale.quantity if sale.quantity > 0 else 0
        
        return JsonResponse({
            'success': True,
            'sale': {
                'id': sale.id,
                'product_name': sale.product.name,
                'quantity': sale.quantity,
                'unit_price': round(unit_price, 2),
                'total_price': float(sale.total_price),
                'customer_name': sale.customer_name or 'N/A',
                'sale_date': sale.sale_date.strftime('%b %d, %Y'),
            }
        })
    except Sale.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Sale not found'
        }, status=404)


@require_http_methods(["POST"])
@csrf_exempt
def process_transaction(request):
    """
    AJAX endpoint for processing POS transactions
    Receives cart items and creates sale records
    Also updates inventory stock levels
    """
    import json
    import sys
    
    try:
        # Handle request body
        if request.body:
            data = json.loads(request.body.decode('utf-8'))
        else:
            print("Empty request body", file=sys.stderr)
            return JsonResponse({
                'success': False,
                'error': 'Empty request body'
            }, status=400)
        
        print(f"Transaction data received: {data}", file=sys.stderr)
        
        cart_items = data.get('items', [])
        customer_name = data.get('customer_name', '').strip() if data.get('customer_name') else ''
        transaction_date = data.get('transaction_date', None)
        payment_method = data.get('payment_method', 'cash')
        amount_paid = data.get('amount_paid', 0)
        change_amount = data.get('change_amount', 0)
        discount = data.get('discount', 0)
                # Convert to Decimal for database storage
        from decimal import Decimal
        try:
            amount_paid = Decimal(str(amount_paid)) if amount_paid else Decimal('0')
            change_amount = Decimal(str(change_amount)) if change_amount else Decimal('0')
            discount = Decimal(str(discount)) if discount else Decimal('0')
        except:
            amount_paid = Decimal('0')
            change_amount = Decimal('0')
            discount = Decimal('0')
        
        # Validate payment method
        valid_methods = ['cash', 'card', 'check']
        if payment_method not in valid_methods:
            payment_method = 'cash'
        
        if not cart_items or len(cart_items) == 0:
            return JsonResponse({
                'success': False,
                'error': 'Cart is empty'
            }, status=400)
        
        created_sales = []
        total_amount = 0
        
        for item in cart_items:
            try:
                product_id = int(item.get('product_id'))
                quantity = int(item.get('quantity', 1))
                unit_price = float(item.get('price', 0))
                item_total = quantity * unit_price
                
                print(f"Processing item: product_id={product_id}, qty={quantity}, price={unit_price}", file=sys.stderr)
                
                product = Product.objects.get(id=product_id)
                
                sale = Sale.objects.create(
                    product=product,
                    quantity=quantity,
                    total_price=item_total,
                    customer_name=customer_name,
                    transaction_date=transaction_date,
                    payment_method=payment_method,
                    amount_paid=amount_paid,
                    change_amount=change_amount,
                    discount=discount
                )
                
                # Update stock inventory
                from inventory.models import Stock
                try:
                    stock = Stock.objects.get(product=product)
                    old_quantity = stock.quantity
                    stock.quantity = max(0, stock.quantity - quantity)  # Don't go below 0
                    stock.save()
                    print(f"Stock updated for product {product_id}: {old_quantity} -> {stock.quantity}", file=sys.stderr)
                except Stock.DoesNotExist:
                    print(f"No stock record found for product {product_id}", file=sys.stderr)
                
                created_sales.append({
                    'id': sale.id,
                    'product': product.name,
                    'quantity': quantity,
                    'price': str(unit_price),
                    'total': str(item_total)
                })
                
                total_amount += item_total
                
            except (Product.DoesNotExist, ValueError, KeyError) as e:
                print(f"Item processing error: {str(e)}", file=sys.stderr)
                return JsonResponse({
                    'success': False,
                    'error': f'Invalid item: {str(e)}'
                }, status=400)
        
        response_data = {
            'success': True,
            'transaction_id': created_sales[0]['id'] if created_sales else None,
            'items': created_sales,
            'total_amount': str(total_amount),
            'message': f'Transaction completed: {len(created_sales)} item(s)'
        }
        
        print(f"Transaction success: {response_data}", file=sys.stderr)
        
        return JsonResponse(response_data)
        
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {str(e)}", file=sys.stderr)
        return JsonResponse({
            'success': False,
            'error': f'Invalid JSON: {str(e)}'
        }, status=400)
    except Exception as e:
        print(f"Server error: {str(e)}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'error': f'Server error: {str(e)}'
        }, status=500)


class SaleReceiptView(LoginRequiredMixin, DetailView):
    """
    Receipt View for Printing/Viewing Sales
    
    Displays a professional receipt for the sale transaction.
    Includes:
    - Receipt number (Sale ID)
    - Date and time of transaction
    - Product details (name, quantity, price)
    - Total amount
    - Customer name (if provided)
    - Print-friendly styling
    """
    model = Sale
    template_name = 'sales/receipt.html'
    context_object_name = 'sale'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context


class SalePrintReportView(LoginRequiredMixin, TemplateView):
    """
    Print Sales Report View
    
    Generates a print-friendly report of sales filtered by date range.
    Allows printing:
    - Current month sales
    - Custom date range sales
    - All sales history
    """
    template_name = 'sales/print_report.html'
    
    def get_context_data(self, **kwargs):
        from datetime import datetime, timedelta
        context = super().get_context_data(**kwargs)
        
        queryset = Sale.objects.all()
        
        # Exclude fully returned sales
        from django.db.models import Exists, OuterRef
        approved_returns = Return.objects.filter(
            sale=OuterRef('pk'),
            status__in=['approved', 'completed']
        )
        queryset = queryset.exclude(Exists(approved_returns))
        
        # Determine report type
        report_type = self.request.GET.get('report_type', 'month')
        
        if report_type == 'month':
            # Current month
            today = timezone.now().date()
            start_of_month = today.replace(day=1)
            queryset = queryset.filter(sale_date__date__gte=start_of_month)
            context['report_title'] = f"Sales Report - {start_of_month.strftime('%B %Y')}"
        elif report_type == 'custom':
            # Custom date range
            start_date = self.request.GET.get('start_date', '').strip()
            end_date = self.request.GET.get('end_date', '').strip()
            
            if start_date:
                try:
                    start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
                    queryset = queryset.filter(sale_date__date__gte=start_date_obj)
                    context['start_date'] = start_date_obj.strftime('%B %d, %Y')
                except ValueError:
                    pass
            
            if end_date:
                try:
                    end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
                    queryset = queryset.filter(sale_date__date__lte=end_date_obj)
                    context['end_date'] = end_date_obj.strftime('%B %d, %Y')
                except ValueError:
                    pass
            
            if start_date and end_date:
                context['report_title'] = f"Sales Report - {context.get('start_date')} to {context.get('end_date')}"
            else:
                context['report_title'] = "Sales Report - Custom Period"
        else:  # all
            context['report_title'] = "Complete Sales History"
        
        # Order by date descending
        queryset = queryset.order_by('-sale_date')
        
        # Calculate totals
        from django.db.models import Sum, Count
        totals = queryset.aggregate(
            total_sales=Count('id'),
            total_quantity=Sum('quantity'),
            total_revenue=Sum('total_price'),
            total_discount=Sum('discount')
        )
        
        context['sales'] = queryset
        context['total_sales'] = totals['total_sales'] or 0
        context['total_quantity'] = totals['total_quantity'] or 0
        context['total_revenue'] = totals['total_revenue'] or 0
        context['total_discount'] = totals['total_discount'] or 0
        context['report_type'] = report_type
        
        return context


# Return Views
class ReturnListView(LoginRequiredMixin, ListView):
    model = Return
    template_name = 'sales/return_list.html'
    context_object_name = 'returns'
    ordering = ['-return_date']
    paginate_by = 50
    
    def get_queryset(self):
        queryset = super().get_queryset()
        status = self.request.GET.get('status')
        search = self.request.GET.get('search')
        
        if status:
            queryset = queryset.filter(status=status)
        
        if search:
            queryset = queryset.filter(
                Q(sale__id__icontains=search) |
                Q(sale__product__name__icontains=search) |
                Q(sale__customer_name__icontains=search)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = Return.STATUS_CHOICES
        context['selected_status'] = self.request.GET.get('status', '')
        return context


class ReturnDetailView(LoginRequiredMixin, DetailView):
    model = Return
    template_name = 'sales/return_detail.html'
    context_object_name = 'return'


class ReturnCreateView(LoginRequiredMixin, CreateView):
    model = Return
    template_name = 'sales/return_form.html'
    form_class = ReturnForm
    success_url = reverse_lazy('return_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sales'] = Sale.objects.all().order_by('-sale_date')[:100]
        return context
    
    def form_valid(self, form):
        # Double-check for duplicate returns (in case of race condition)
        sale = form.cleaned_data.get('sale')
        if sale:
            active_returns = Return.objects.filter(
                sale=sale,
                status__in=['pending', 'approved', 'completed']
            ).exists()
            
            if active_returns:
                form.add_error('sale', 
                    f"A return request already exists for this sale. "
                    f"Please check the return status or contact an administrator."
                )
                return self.form_invalid(form)
        
        # Set processed_by to current user
        form.instance.processed_by = self.request.user.username
        messages.success(self.request, "Return request created successfully.")
        return super().form_valid(form)


class ReturnUpdateView(LoginRequiredMixin, UpdateView):
    model = Return
    template_name = 'sales/return_form.html'
    fields = ['status', 'refund_payment_method', 'reason_details', 'refund_amount']
    success_url = reverse_lazy('return_list')
    
    def dispatch(self, request, *args, **kwargs):
        # Only admin/superuser can update return status
        if not (request.user.is_staff and request.user.is_superuser):
            messages.error(request, "Only administrators can approve or update return status.")
            return redirect('return_list')
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        # Update processed date when status changes
        if 'status' in form.changed_data:
            form.instance.processed_date = timezone.now()
            form.instance.processed_by = self.request.user.username
            
            new_status = form.cleaned_data.get('status')
            if new_status == 'rejected':
                messages.warning(self.request, f"Return #{self.object.id} has been REJECTED.")
            elif new_status == 'completed':
                messages.success(self.request, f"Return #{self.object.id} has been marked as COMPLETED. Refund of ₱{self.object.refund_amount} processed.")
            else:
                messages.info(self.request, "Return updated successfully.")
        else:
            messages.success(self.request, "Return updated successfully.")
        return super().form_valid(form)

