import hashlib

from django.shortcuts import render
from django.core.paginator import Paginator
from django.shortcuts import HttpResponseRedirect

from Store.models import *

def loginValid(fun):
    def inner(request,*args,**kwargs):
        c_user = request.COOKIES.get("username")
        s_user = request.session.get("username")
        if c_user and s_user and c_user == s_user:
            user = Seller.objects.filter(username=c_user).first()
            if user:
                return fun(request,*args,**kwargs)
        return HttpResponseRedirect("/Store/login/")
    return inner

def set_password(password):
    md5 = hashlib.md5()
    md5.update(password.encode())
    rusult = md5.hexdigest()
    return rusult

def register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        psaaword = request.POST.get("password")
        if username and psaaword:
            seller = Seller()
            seller.username = username
            seller.password = set_password(psaaword)
            seller.nickname = username
            seller.save()
            return HttpResponseRedirect("/Store/login/")
    return render(request,"store/register.html")

def login(request):
    response = render(request,"store/login.html")
    response.set_cookie("login_from","login_page")
    if request.method == "POST":
        username = request.POST.get("username")
        psaaword = request.POST.get("password")
        if username and psaaword:
            user = Seller.objects.filter(username = username).first()
            if user:
                web_password = set_password(psaaword)
                cookies = request.COOKIES.get("login_from")
                if user.password == web_password and cookies == "login_page":
                    response = HttpResponseRedirect("/Store/index/")
                    response.set_cookie("username",username)
                    response.set_cookie("user_id",user.id)
                    request.session["username"] = username
                    store = Store.objects.filter(user_id=user.id).first()
                    if store:
                        response.set_cookie("has_store",store.id)
                    else:
                        response.set_cookie("has_store","")
                    return response
    return response

@loginValid
def index(request):
    user_id = request.COOKIES.get("user_id")
    if user_id:
        user_id = int(user_id)
    else:
        user_id = 0
    store = Store.objects.filter(user_id=user_id).first()
    if store:
        is_store = 1
    else:
        is_store = 0
    return render(request,"store/index.html",{"is_store":is_store})

def base(request):
    return render(request,"store/base.html")

@loginValid
def register_store(request):
    type_list = StoreType.objects.all()
    if request.method == "POST":
        post_data = request.POST
        store_name = post_data.get("store_name")

        store_descripton = post_data.get("store_descripton")
        store_phone = post_data.get("store_phone")
        store_money = post_data.get("store_money")
        store_address = post_data.get("store_address")
        user_id = int(request.COOKIES.get("user_id"))
        type_lists = post_data.getlist("type")

        store_logo = request.FILES.get("store_logo")

        store = Store()
        store.store_name = store_name
        store.store_descripton = store_descripton
        store.store_phone = store_phone
        store.store_money = store_money
        store.store_address = store_address
        store.user_id = user_id
        store.store_logo = store_logo
        store.save()

        for i in type_lists:
            print(i)
            store_type = StoreType.objects.get(id = i)
            store.type.add(store_type)
        store.save()
    return render(request,"store/register_store.html",locals())


@loginValid
def add_goods(request):
    if request.method == "POST":
        goods_name = request.POST.get("goods_name")
        goods_price = request.POST.get("goods_price")
        goods_number = request.POST.get("goods_number")
        goods_description = request.POST.get("goods_description")
        goods_date = request.POST.get("goods_date")
        goods_safeDate = request.POST.get("goods_safeDate")
        # goods_store = request.COOKIES.get("has_store")
        goods_store = request.POST.get("goods_store")
        goods_image = request.FILES.get("goods_image")

        goods = Goods()
        goods.goods_name = goods_name
        goods.goods_price = goods_price
        goods.goods_number = goods_number
        goods.goods_description = goods_description
        goods.goods_date = goods_date
        goods.goods_safeDate = goods_safeDate
        goods.goods_image = goods_image
        goods.save()

        goods.store_id.add(
            Store.objects.get(id = int(goods_store))
        )
        goods.save()
        return HttpResponseRedirect("/Store/list_goods/")
    return render(request,"store/add_goods.html")
# Create your views here.

@loginValid
def list_goods(request):
    keywords = request.GET.get("keywords","")
    page_num = request.GET.get("page_num",1)
    store_id = request.COOKIES.get("has_store")
    store = Store.objects.get(id =int(store_id))
    if keywords:
        goods_list = store.goods_set.filter(goods_name__contains=keywords)
    else:
        goods_list = store.goods_set.all()
    paginator = Paginator(goods_list,3)
    page = paginator.page(int(page_num))
    page_range = paginator.page_range
    return render(request,"store/goods_list.html",{"page":page,"page_range":page_range,"keywords":keywords})


@loginValid
def goods(request,goods_id):
    goods_data = Goods.objects.filter(id = goods_id).first()
    return render(request,"store/goods.html",locals())

@loginValid
def update_goods(request,goods_id):
    goods_data = Goods.objects.filter(id = goods_id).first()
    if request.method == "POST":
        goods_name = request.POST.get("goods_name")
        goods_price = request.POST.get("goods_price")
        goods_number = request.POST.get("goods_number")
        goods_description = request.POST.get("goods_description")
        goods_date = request.POST.get("goods_date")
        goods_safeDate = request.POST.get("goods_safeDate")
        goods_image = request.FILES.get("goods_image")

        goods = Goods.objects.get(id = int(goods_id))
        goods.goods_name = goods_name
        goods.goods_price = goods_price
        goods.goods_number = goods_number
        goods.goods_description = goods_description
        goods.goods_date = goods_date
        goods.goods_safeDate = goods_safeDate
        if goods_image:
            goods.goods_image = goods_image
        goods.save()
        return HttpResponseRedirect("/Store/goods/%s/"%goods_id)
    return render(request,"store/update_goods.html",locals())
