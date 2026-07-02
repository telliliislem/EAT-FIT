from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from order.models import OrderItem, Order
from .forms import BusinessOwnerForm
from .models import BusinessOwner


@login_required
def create_or_edit_business(request):

    # Only Business Owners can access
    if request.user.role != 'business_owner':
        return redirect('index')

    # Try to get business profile
    try:
        business = request.user.businessowner
    except BusinessOwner.DoesNotExist:
        business = None

    # Form (edit or create)
    if request.method == "POST":
        form = BusinessOwnerForm(request.POST, request.FILES, instance=business)

        if form.is_valid():
            new_business = form.save(commit=False)
            new_business.user = request.user
            new_business.save()
            return redirect('create_business')
    else:
        form = BusinessOwnerForm(instance=business)

    # Load orders for this business owner
    if business:
        orders = OrderItem.objects.filter(
            business_owner=business
        ).select_related("order", "product")
    else:
        orders = []

    return render(
        request,
        'businessowner/businessowner.html',
        {
            'form': form,
            'orders': orders,
        }
    )


# -------------------------------
# ORDER ACTIONS
# -------------------------------

@login_required
def mark_order_done(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    order.is_processed = True
    order.save()

    messages.success(request, "Order marked as completed.")
    return redirect('create_business')


@login_required
def delete_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.delete()

    messages.warning(request, "Order deleted.")
    return redirect('create_business')
