from django.shortcuts import render
from django.shortcuts import HttpResponseRedirect

from Buyer.models import *
from Store.models import *
from alipay import AliPay
from Store.views import set_password

def loginValid(fun):
    def inner(request,*args,**kwargs):
        c_user = request.COOKIES.get("username")
        s_user = request.session.get("username")
        if c_user and s_user and c_user == s_user:
            return fun(request,*args,**kwargs)
        else:
            return HttpResponseRedirect("/Buyer/login/")
    return inner

def register(request):
    if request.method == "POST":
        username = request.POST.get("user_name")
        password = request.POST.get("pwd")
        email = request.POST.get("email")

        buyer = Buyer()
        buyer.username = username
        buyer.password = set_password(password)
        buyer.email = email
        buyer.save()
        return HttpResponseRedirect("/Buyer/login/")
    return render(request,"buyer/register.html")

def login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("pwd")
        if username and password:
            user = Buyer.objects.filter(username=username).first()
            if user:
                web_password = set_password(password)
                if user.password == web_password:
                    response = HttpResponseRedirect("/Buyer/index/")
                    response.set_cookie("username",user.username)
                    request.session["username"] = user.username
                    response.set_cookie("user_id",user.id)
                    return response
    return render(request,"buyer/login.html")

@loginValid
def index(request):
    result_list = []
    goods_type_list = GoodsType.objects.all()
    for goods_type in goods_type_list:
        goods_list = goods_type.goods_set.values()[:4]
        if goods_list:
            goodsType = {
                "id":goods_type.id,
                "name":goods_type.name,
                "description":goods_type.description,
                "picture":goods_type.picture,
                "goods_list":goods_list
            }
            result_list.append(goodsType)
    return render(request,"buyer/index.html",locals())

def logout(request):
    response = HttpResponseRedirect("/Buyer/login/")
    for key in request.COOKIES:
        response.delete_cookie(key)
    del request.session["username"]
    return response

def goods_list(request):
    goodsList =[]
    type_id = request.GET.get("type_id")
    goods_type = GoodsType.objects.filter(id = type_id).first()
    if goods_type:
        goodsList = goods_type.goods_set.filter(goods_under=1)
    return render(request,"buyer/goods_list.html",locals())

def base(request):
    return render(request,"buyer/base.html")


def pay_order(request):
    money = request.GET.get("money")
    order_id = request.GET.get("order_id")
    alipay_public_key_string = """-----BEGIN PUBLIC KEY-----
    MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAtIhOD9M7bgYNAD/oRA8QjiCZSW9R1wVi6s1dzskH2nWvmimNuuSIC6zqPhp0XD/6vl57kBAApGtSCpyK60K/fwfu2dBOX8bSBn4gy+C+6cSMfvKKFAB3dbVXrGLPUhWQSLmH7eNUkgMarGD62OaMzCNCwtEYPmCGqYtlA3eheIjZxsBhei6p+5EllWn8nxC3ZQvnBj/D55PtgKeM+0RhWWfQCBDzeI0DdaY/1vmiwXCnKjPKvvOBHvSBkwZCXtS5yJ204cW178r0X/bE7KqRS2hkCt27uDRQuZxyfaHmNKyEMQxvaKwtqJw2MDhsFuApJI2EeSFpeiul4ALVQnNvpwIDAQAB
    -----END PUBLIC KEY-----"""

    app_private_key_string = """-----BEGIN RSA PRIVATE KEY-----
    MIIEowIBAAKCAQEAtIhOD9M7bgYNAD/oRA8QjiCZSW9R1wVi6s1dzskH2nWvmimNuuSIC6zqPhp0XD/6vl57kBAApGtSCpyK60K/fwfu2dBOX8bSBn4gy+C+6cSMfvKKFAB3dbVXrGLPUhWQSLmH7eNUkgMarGD62OaMzCNCwtEYPmCGqYtlA3eheIjZxsBhei6p+5EllWn8nxC3ZQvnBj/D55PtgKeM+0RhWWfQCBDzeI0DdaY/1vmiwXCnKjPKvvOBHvSBkwZCXtS5yJ204cW178r0X/bE7KqRS2hkCt27uDRQuZxyfaHmNKyEMQxvaKwtqJw2MDhsFuApJI2EeSFpeiul4ALVQnNvpwIDAQABAoIBAB9qvRL58pSyDt8lP/lgGcRyHdruuXJO6Kjt9k4/I9O7uUR9yMFmddp6TAVkuy02oR8x+BTZBBOY7Z0VIwPQCN1FdyaGnq0CP5iLqI9yXCb4Ym7RLIBQmHluhoRkaaniQMq3JtWaQyRpz+GBuwW2EXiRBlQ66Rop2CV3MawJzJraAxH3jP4e1hrsCYI4ppHcXwwQ8F54n2ow1rJaBSJaI9HXIZ1m75gSy3oKuGuAV+vXuN74p9/U3W6txoREsmF+yT4nApCjsjOMqeYgX1vFxLu803Jh70YSV0wBUx7RbCEzAdGbUFDUK9LkdINkR+6/Kdpj/US0eB15zxDcE95sB1ECgYEA3692RrmS23uLh11ZyHujht+I0pT7F+FTvkiw42ByQJGMdt7FPvr0wiJ85aG/kN+kpBE3JVxV7Payrbv7WJvPIvsLzrzIzmHAoWZsruQpjiNswiKIlu7n6uHJ+PpoVITGptFzMHhQfVZkearARGz/zvxmB5pduaPwb61u7o3QZDkCgYEAzpzrt/79n15ILyBg/hlCee78y91Hrq1hUVUsKeCCqhALkz2HqMBAY1WrzMTSM4wa31M5JGuZk87wTFSrdPgrwO+jQZ76SCh/DqcnyGkh5WGLjdA9OUHX+6oQCsJmJgsMm0zaXUK5omFuF5yjeBDKXSE4zTCcBz5zfq8hBvMhMt8CgYBGHnq1MPcYVmImzNyYPCnG3cvGN21+zuOxgpfwrwshsn6VxL+QPpr7QFRmp42lnHW/+KWQ0KEe5zabv5HK9Qy5qnjJFeTczUfVUIZBTMS6CeDN+oVWyw1oU988bULHO9gJ8x5o005n++0DNsOOr5yBBh31xC4dQ4bbe0KLBWmOAQKBgQCr/BF3CqnhtCCQIfq66Rnd1+LUbDDUJXzBsA1gGoOJvmt0OB6piMbQKSsl+5whznk79tG1EGA5mmOKllxWtJHvO0sBP62EzTjeYKQL/f96KhV5iaK8+6Mm2OwbmLBg8Ieg6ntGcFmH4mQ7AWdNdWSN2y6mFtV6bjDDflIWr+GtrwKBgBxlirxrNlh5KE1TqbtgQpombetshcjbuXkchUeBRLpXxqGjigfo7Y/HY3PMGeDnbMgSeLo+G6TCBvameo0zj1ruJ5uohZeoOxpPQsnUTa03D/OPKEk70rLeMIG85l7nBqKWVAHArSIGrNf53H/x2aP5+FL0IgojeVV0VmkruROG
    -----END RSA PRIVATE KEY-----"""

    alipay = AliPay(
        appid="2016101000652508",
        app_notify_url=None,
        app_private_key_string=app_private_key_string,
        alipay_public_key_string=alipay_public_key_string,
        sign_type="RSA2"
    )

    order_string = alipay.api_alipay_trade_page_pay(
        out_trade_no=order_id,
        total_amount=str(money),
        subject="生鲜交易",
        return_url="http://127.0.0.1:8000/Buyer/pay_result/",
        notify_url="http://127.0.0.1:8000/Buyer/pay_result/"
    )

    return HttpResponseRedirect("https://openapi.alipaydev.com/gateway.do?" + order_string)
# Create your views here.


def pay_result(request):
    return render(request,"buyer/pay_result.html",locals())

