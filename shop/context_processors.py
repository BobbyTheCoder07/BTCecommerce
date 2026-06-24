from .models import Product

def cart_processor(request):
    cart = request.session.get('cart', {})
    cart_items = []
    cart_subtotal = 0.00
    cart_total_count = 0

    if cart:
        product_ids = cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        for product in products:
            qty = cart[str(product.id)]
            price = float(product.current_price)
            item_total = price * qty
            cart_subtotal += item_total
            cart_total_count += qty
            cart_items.append({
                'product': product,
                'quantity': qty,
                'total_price': item_total
            })

    return {
        'cart_items': cart_items,
        'cart_subtotal': cart_subtotal,
        'cart_total_count': cart_total_count,
    }
