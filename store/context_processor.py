from store import models as store_models
from store.models import Category



def default(request):
    categories = Category.objects.all()
    
    try:
        cart_id = request.session['cart_id']
        total_cart_items = store_models.Cart.objects.filter(cart_id=cart_id)
      
    except:
        total_cart_items = 0
        

    return {
        "total_cart_items": total_cart_items,
        'categories': categories,
        
    }

