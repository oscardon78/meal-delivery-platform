from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render ,redirect,get_object_or_404
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import *
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.db.models import Count
from django import forms

def login_page(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        if not User.objects.filter(username=username).exists():
           messages.info(request, "Incorrect Username")
           return redirect("/login/")
        user= authenticate(request, username=username,password=password)
        if user is None:
            print(f"Login failed for username: {username} with password: {password} ,{user}")
            messages.info(request, "Incorrect Password")
            return redirect("/login/")
        else:
            login(request,user)
            context={"user":user}
            return redirect("/",context)
    return render(request,"login.html")

def logout_page(request):
    logout(request)
    return redirect("/login")

def register(request):
    if request.method=='POST':

        name= request.POST.get("username")
        email = request.POST.get("email")
        username= request.POST.get("email")
        password = request.POST.get("password")
        user= User.objects.filter(username=username)
        if user.exists():
            messages.error(request, "This email is already registered.")
            return redirect("/register/")
        new_user=User.objects.create_user(
            username=username,
            first_name=name,
            email=email,
            password=password
        )
        messages.success(request, "You're registered.")
    return render(request,'register.html')


@login_required(login_url="/login/")
def Menu(request,id):
    user = request.user
    try:
        cart_items = CartItem.objects.filter(cart__user=user,quantity__gt=0)
        cart = Cart.objects.get(user=request.user)
        cart.cart_total()
    except Cart.DoesNotExist:
        # Create a new Cart object for the user and save it
        new_cart = Cart.objects.create(user=request.user)
        orderInfo = OrderInfo.objects.create(customer=request.user)
        orderInfo2 = OrderInfo.objects.create(customer=request.user)
        new_cart.save()
        orderInfo2.save()
        orderInfo.save()
    foods=Food.objects.filter(restaurant__id=id)
    restaurant=Restaurant.objects.filter(id=id)#only for the restaurant card
    restaurant=restaurant[0]#only for the restaurant card
    category=Category.objects.all().distinct()
    cart_items = {}
    user = request.user
    if user.is_authenticated:
        cart_items_query = CartItem.objects.filter(cart__user=user)
        for item in cart_items_query:
            cart_items[item.food_id] = item.quantity 
    
    if request.method=='POST':
        category_name = request.POST.get('category_id')
        foods=Food.objects.filter(restaurant__id=id,catagory__catagory__icontains=category_name)
    foods={'foods':foods,'restaurant':restaurant,'cart_items':cart_items,'category':category}
    return render(request,'menu.html',foods,)


def about(request):
    return render(request,'about.html')

def homepage(request):
    restaurants=Restaurant.objects.all()
    restaurants={'restaurants':restaurants}
    return render(request,'index.html',restaurants)

@login_required(login_url="/login/")
def cart(request):
    user = request.user
    try:
        cart_items = CartItem.objects.filter(cart__user=user,quantity__gt=0)
        cart = Cart.objects.get(user=request.user)
        cart.cart_total()
    except Cart.DoesNotExist:
        # Create a new Cart object for the user and save it
        new_cart = Cart.objects.create(user=request.user)
        orderInfo = OrderInfo.objects.create(customer=request.user)
        orderInfo2 = OrderInfo.objects.create(customer=request.user)
        new_cart.save()
        orderInfo2.save()
        orderInfo.save()
        cart_items = CartItem.objects.filter(cart__user=user,quantity__gt=0)
    cart = Cart.objects.get(user=request.user)
    cart.cart_total()
    for item in cart_items:
        item.total=item.food.cost * item.quantity
        # cart_total= cart_total+item.total
    context={'item': cart_items,'cart':cart}
    return render(request, 'cart.html',context )

@login_required(login_url="/login/")
def orders(request):
    user = request.user
    print(user.id)
    # Retrieve orders for the current user
    orders = Orders.objects.filter(order_info__customer=user).order_by('-date_created')

    print(orders)
    return render(request, 'orders.html', {'orders': orders})


# CSRF-exempt decorator is used to allow AJAX requests without CSRF tokens
@csrf_exempt
def decrement_quantity(request):
    if request.method == 'POST':
        food_id = request.POST.get('food_id')
        if food_id:
            try:
                food_item = Food.objects.get(pk=food_id)
                cart_item = CartItem.objects.get(food=food_item, cart=request.user.cart)
                if cart_item.quantity > 0:
                    cart_item.quantity -= 1
                    cart_item.save()
                    cost=food_item.cost
                    cart = Cart.objects.get(user=request.user)
                    cart_total=cart.cart_total()
                    return JsonResponse({'success': True, 'food_id': food_id, 'quantity': cart_item.quantity,'cost':cost,'cart_total':cart_total })
            except (Food.DoesNotExist, CartItem.DoesNotExist):
                pass
    return JsonResponse({'success': False})


@csrf_exempt
def increment_quantity(request):
    # Check if the request method is POST
    if request.method == 'POST':
        # Retrieve the food ID from the POST data
        food_id = request.POST.get('food_id')
        food_item=Food.objects.get(pk=food_id)
        if food_id:
            try:
                cart_item, created = CartItem.objects.get_or_create(food=food_item, cart=request.user.cart)
                cart_item.quantity += 1
                cart_item.save()
                cost=food_item.cost
                cart = Cart.objects.get(user=request.user)
                cart_total=cart.cart_total()
                return JsonResponse({'success': True, 'food_id': food_id, 'quantity': cart_item.quantity,'cost':cost,'cart_total':cart_total })
            except Food.DoesNotExist:
                pass
    # If the request method is not POST or an error occurs, return a JSON response indicating failure
    return JsonResponse({'success': False})

@login_required(login_url="/login/")
def create_order_from_cart(request):
    user = request.user
    # Retrieve cart items for the current user
    cart_items = CartItem.objects.filter(cart__user=user,quantity__gt=0)

    order_items = []
    total_cost = 0

    # Create order items for each cart item
    for cart_item in cart_items:
        food = cart_item.food
        quantity = cart_item.quantity
        cost = food.cost
        total_cost += quantity * cost

        # Create order item
        order_items.append(OrderItem(
            food=food,
            quantity=quantity
        ))

    # Create the order info
    info_id = request.POST.get('chosen_order')
    print(info_id)
    order_info=OrderInfo.objects.get(pk=info_id)
    # Create the order
    order = Orders.objects.create(
        order_info=order_info,
        total=total_cost,
        status="Pending"
    )

    # Associate order items with the order
    for order_item in order_items:
        order_item.order = order
        order_item.save()

    # Calculate total for the order
    order.calculate_total()
    for cart_item in cart_items:
        cart_item.quantity=0
        cart_item.save()
    # Return the created order
    return order

@login_required(login_url="/login/")
def create_order(request):
    # Create order from cart
    order = create_order_from_cart(request)

    # Redirect to orders page
    return redirect(reverse('orders'))

@login_required(login_url="/login/")
def order_details(request, id):
    # Retrieve the order based on the order_id
    order = Orders.objects.get(id=id)

    # Access related information
    order_info = order.order_info
    customer = order_info.customer
    order_items = order.order_items.all()  # Access all related order items
    total_cost = order.total

    # Render the template with the retrieved data
    return render(request, 'order_details.html', {
        'order': order,
        'order_info': order_info,
        'customer': customer,
        'order_items': order_items,
        'total_cost': total_cost
    })

@login_required(login_url="/login/")
def add_details(request):
    user=request.user
    infos=OrderInfo.objects.filter(customer=user)
    infos={'infos':infos}
    return render(request,'add_details.html',infos)


class OrderForm(forms.ModelForm):
    class Meta:
        model = OrderInfo
        fields = ['customer', 'name', 'location', 'phone']

@login_required(login_url="/login/")
def edit_order(request, order_id):
    """
    A view function to edit an existing order, requiring login authentication. 
    Parameters:
        request: HttpRequest object
        order_id: ID of the order to be edited
    Returns:
        HttpResponse object
    """
    order = get_object_or_404(OrderInfo, pk=order_id)
    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            return redirect('add_details')
    else:
        form = OrderForm(instance=order)
    return render(request, 'edit_order.html', {'form': form})

