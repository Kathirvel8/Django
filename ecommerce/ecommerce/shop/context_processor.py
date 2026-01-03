from .models import CartItem

def get_cart_count(request):
    cart_count = 0
    if request.user.is_authenticated:
        cart_count = CartItem.objects.filter(cart_id=request.user.id).count()
        print(cart_count)
        return {'cart_count': cart_count}
    return {'cart_count': cart_count}