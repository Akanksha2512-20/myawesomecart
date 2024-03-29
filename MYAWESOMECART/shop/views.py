from django.shortcuts import render
from . models import Product,Contact,Orders, OrderUpdate
from math import ceil
import json
from django.views.decorators.csrf import csrf_exempt
# from PayTm import Checksum
# Create your views here.

MERCHANT_KEY = 'Your-Merchant-Key-Here'

# Create your views here.
from django.http import HttpResponse
# Create your views here.
def index(request):
    products= Product.objects.all()
    n= len(products)
    nSlides= n//4 + ceil((n/4) - (n//4))
    allProds=[[products, range(1, nSlides), nSlides],[products, range(1, nSlides), nSlides],[products, range(1,nSlides ), nSlides],
              [products, range(1, nSlides), nSlides]]
    params={'allProds':allProds }
    return render(request,'shop/index.html',params)
def about(request):
    return render(request,'shop/about.html')
def contact(request):
    thank=False
    if request.method=="POST":
        print(request)
        name=request.POST.get('name', '')
        email=request.POST.get('email', '')
        phone=request.POST.get('phone', '')
        desc=request.POST.get('desc', '')
        print(name,email,phone, desc )
        contact = Contact(name=name, email=email, phone=phone, desc=desc)
        contact.save()
        thank=True
    return render(request, "shop/contact.html",{'thank':thank})

def searchMatch(query, item):
    query=query.lower()
    if query in item.product_name.lower() or query in item.category.lower() or query in item.desc.lower() or query in item.sub_category.lower():
        return True
    else:
        return False

def search(request):
    query = request.GET.get('search')
    allProds = []
    catprods = Product.objects.values('sub_category', 'id')
    cats = {item['sub_category'] for item in catprods}
    for cat in cats:
        prodtemp = Product.objects.filter(sub_category=cat)
        prod = [item for item in prodtemp if searchMatch(query, item)]
        #prod = []
        for item in prodtemp:
            if query in item.product_name.lower() or query in item.desc.lower():
                prod.append(item)
        n = len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        if len(prod) != 0:
            allProds.append([prod, range(1, nSlides), nSlides])
    params = {'allProds': allProds, "msg": ""}
    if len(allProds) == 0 or len(query)<2:
        params = {'msg': "Please make sure to enter relevant search query"}
    return render(request, 'shop/index.html', params)


def tracker(request):
    if request.method=="POST":
        orderId = request.POST.get('orderId', '')
        email = request.POST.get('email', '')
        try:
            order = Orders.objects.filter(order_id=orderId, email=email)
            if len(order)>0:
                update = OrderUpdate.objects.filter(order_id=orderId)
                updates = []
                for item in update:
                    updates.append({'text': item.update_desc, 'time': item.timestamp})
                    response = json.dumps([updates, order[0].items_json], default=str)
                return HttpResponse(response)
            else:
                return HttpResponse('{}')
        except Exception as e:
            return HttpResponse('{}')

    return render(request, 'shop/tracker.html')
    # return  render(request,'shop/tracker.html')

# def search(request):
#     return  render(request,'shop/search.html')
def productview(request, myid):
    # Fetch the product using the id
    product = Product.objects.filter(id=myid)
    return render(request, 'shop/productview.html', {'product':product[0]})

def checkout(request):
    if request.method=="POST":
        items_json = request.POST.get('itemsJson', '')
        name = request.POST.get('name', '')
        amount = request.POST.get('amount', '')
        email = request.POST.get('email', '')
        address = request.POST.get('address1', '') + " " + request.POST.get('address2', '')
        city = request.POST.get('city', '')
        state = request.POST.get('state', '')
        zip_code = request.POST.get('zip_code', '')
        phone = request.POST.get('phone', '')
        order = Orders(items_json=items_json, name=name, email=email, address=address, city=city,
                       state=state, zip_code=zip_code, phone=phone)
        order.save()
        update = OrderUpdate(order_id=order.order_id, update_desc="The order has been placed")
        update.save()
        thank = True
        id = order.order_id
        return render(request, 'shop/checkout.html', {'thank':thank, 'id': id})
    return render(request, 'shop/checkout.html')