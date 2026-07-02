# products/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from .models import Product, Rating
from .forms import ProductForm, RatingForm
from businessowner.models import BusinessOwner


def product_list(request):
    products = Product.objects.all()

    # If BUSINESS OWNER → show ONLY his products
    if request.user.is_authenticated and request.user.role == 'business_owner':
        try:
            owner = request.user.businessowner
            products = products.filter(business_owner=owner)
        except BusinessOwner.DoesNotExist:
            products = Product.objects.none()

    # ----- Filters -----
    search = request.GET.get('search')
    category = request.GET.get('category')
    business = request.GET.get('business')
    sort = request.GET.get('sort')

    if search:
        products = products.filter(product_name__icontains=search)

    if category:
        products = products.filter(category=category)

    # Business filter only for NORMAL users
    if business and not (request.user.is_authenticated and request.user.role == 'business_owner'):
        products = products.filter(business_owner_id=business)

    if sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')

    # Dropdowns
    categories = [c[0] for c in Product.CATEGORY_CHOICES]
    businesses = BusinessOwner.objects.all()

    return render(request, 'products/product_list.html', {
        'products': products,
        'categories': categories,
        'businesses': businesses,
    })


@login_required
def product_create(request):
    # Prevent normal users from creating products
    if request.user.role != 'business_owner':
        return redirect('product_list')

    try:
        owner = request.user.businessowner
    except BusinessOwner.DoesNotExist:
        return redirect('product_list')

    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False)
            product.business_owner = owner
            product.save()
            return redirect('product_list')
    else:
        form = ProductForm()

    return render(request, 'products/product_form.html', {'form': form})


@login_required
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)

    # Owner security check
    if request.user.role != 'business_owner' or product.business_owner.user != request.user:
        return redirect('product_list')

    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = ProductForm(instance=product)

    return render(request, 'products/product_form.html', {'form': form})


@login_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)

    # Owner security check
    if request.user.role != 'business_owner' or product.business_owner.user != request.user:
        return redirect('product_list')

    product.delete()
    return redirect('product_list')


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)

    similar_products = Product.objects.filter(
        Q(category=product.category) | Q(business_owner=product.business_owner)
    ).exclude(pk=product.pk)[:3]

    form = None
    if request.user.is_authenticated:

        if request.method == 'POST':
            form = RatingForm(request.POST)
            if form.is_valid():
                Rating.objects.update_or_create(
                    product=product,
                    user=request.user,
                    defaults={
                        'rating': form.cleaned_data['rating'],
                        'comment': form.cleaned_data['comment']
                    }
                )
                return redirect('product_detail', pk=pk)

        else:
            try:
                user_rating = Rating.objects.get(product=product, user=request.user)
                form = RatingForm(instance=user_rating)
            except Rating.DoesNotExist:
                form = RatingForm()

    return render(request, 'products/product_detail.html', {
        'product': product,
        'similar_products': similar_products,
        'form': form
    })
