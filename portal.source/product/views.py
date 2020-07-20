from django.shortcuts import render, redirect
from datetime import timedelta, date
from app.utils import AccessPermission
import json
import os
import requests
from django.core import serializers

from .forms import ProductForm, BatchForm
from .models import Product, Batch, Item
from django.core import signing


def product(request):
    return product_helper(request, 0, False)


def update_product(request, id):
    return product_helper(request, id, False)


def view_product(request, id):
    return product_helper(request, id, True)


def cancel_product(request, id):
    org_id = request.user.profile.org.id
    model = Product.objects.filter(status='ACTIVE', org_id=org_id)
    if id:
        obj = Product.objects.get(id=id)
        form = ProductForm(request.POST or None)

    str_redirect = 'product'
    str_render = "product/add_products.html"
    return cancel_helper(request, id, model, form, obj, str_redirect, str_render, org_id)


def product_helper(request, id, is_view):
    org_id = request.user.profile.org.id
    model = Product.objects.filter(status='ACTIVE', org_id=org_id)
    if id > 0:
        obj = Product.objects.get(id=id)
        form = ProductForm(request.POST or None, instance=obj)
        is_update = True
        if is_view:
            form.fields['pro_name'].widget.attrs['readonly'] = True
            form.fields['pro_price'].widget.attrs['readonly'] = True
            form.fields['exp_duration'].widget.attrs['readonly'] = True
            form.fields['status'].widget.attrs['readonly'] = True
            is_update = False
    else:
        form = ProductForm(request.POST or None)
        is_update = False
        obj = None

    str_redirect = 'product'
    str_render = "product/add_products.html"
    return helper(request, model, form, str_redirect, str_render, is_update, is_view, obj, org_id)


def helper(request, model, form, str_redirect, str_render, is_update, is_view, obj, org_id):
    if form.is_valid():
        form.save()
        return redirect(str_redirect)

    goto_div = False
    if is_update or is_view:
        goto_div = True

    context = {
        'form': form,
        'model': model,
        'is_update': is_update,
        'is_view': is_view,
        'obj': obj,
        'org_id': org_id,
        'goto_div': goto_div,
        'roles': AccessPermission(request.user.profile.group.role_permission),
    }
    return render(request, str_render, context)


def cancel_helper(request, id, model, form, obj, str_redirect, str_render, org_id):
    if id:
        obj.status = 'INACTIVE'
        obj.save()
        return redirect(str_redirect)

    context = {
        'model': model,
        'form': form,
        'org_id': org_id,
        'roles': AccessPermission(request.user.profile.group.role_permission),
    }
    return render(request, str_render, context)


def batch(request):
    org_id = request.user.profile.org.id
    model = Batch.objects.filter(status='ACTIVE', org_id=org_id)
    p_model = Product.objects.filter(status='ACTIVE', org_id=org_id, batch_id__isnull=True)
    form = BatchForm(request.POST or None)
    id=0
    str_redirect = 'batch'
    str_render = "product/add_batch.html"
    return batch_helper(request, id, model, p_model, form, str_redirect, str_render,
                        org_id, is_view=False)


def view_batch(request, id):
    org_id = request.user.profile.org.id
    model = Batch.objects.filter(status='ACTIVE', org_id=org_id)
    p_model = Product.objects.filter(status='ACTIVE', org_id=org_id, batch_id__isnull=True)
    obj = Batch.objects.get(id=id)
    form = BatchForm(request.POST or None, instance=obj)
    form.fields['batch_name'].widget.attrs['readonly'] = True
    form.fields['no_of_products'].widget.attrs['readonly'] = True
    form.fields['release_date'].widget.attrs['readonly'] = True
    str_redirect = 'batch'
    str_render = "product/add_batch.html"
    return batch_helper(request, id, model, p_model, form, str_redirect, str_render,
                        org_id, is_view=True)


def batch_helper(request, id, model, p_model, form, str_redirect, str_render, org_id, is_view):
    if form.is_valid():
        s_form = form.save()
        bat = Batch.objects.get(id=s_form.id)
        bat.batch_code = s_form.id

        prod_id = request.POST['prod_id']
        prod = Product.objects.get(id=prod_id)
        batch_id = s_form.id
        prod.batch_id = batch_id

        no_of_items = request.POST['no_of_products']
        added_date = str(date.today())
        # data = serializers.serialize('json', Item.objects.filter(org_id=org_id, product_id=prod_id,
        # status="INACTIVE")[:int(no_of_items)], fields=('date_added', 'product'))
        # values = Item.objects.filter(org_id=org_id, product_id=prod_id, status="INACTIVE")[:int(no_of_items)]
        # json_data = serializers.serialize('json', values, fields='date_added')
        # print(json_data)
        bat.exp_date = s_form.batch_date+timedelta(days=prod.exp_duration)
        prod.save()
        bat.save()

        # Generate UUID in Spring Boot Rest API
        url = os.environ.get("URL", 'http://localhost:3307/api/hashkey/add')
        url = "%s" % url
        body = {"exp_duration": "%s" % prod.exp_duration, "org_id": "%s" % org_id,
                "prod_id": "%s" % prod_id, "item_count": "%s" % no_of_items,
                "added_date": "%s" % added_date}
        response = requests.post(url, headers={'Content-Type': 'application/json'}, json=body)
        response_text = response.text
        if response.status_code == 200:
            print("HttpStatus.OK for Spring Boot")
            dic = json.loads(response_text)
            dic_keys = list(dic.keys())
            dic_keys.sort()

            # # Add UUID in Blockchain
            url = os.environ.get("URL", 'http://127.0.0.1:4010/records')
            url = "%s" % url
            for item_id in dic_keys:
                body = {"latitude": 44982734, "longitude": -93272107, "record_id": dic[item_id]}
                requests.post(url, headers={'Content-Type': 'application/json',
                                            'Authorization': 'eyJpYXQiOjE1MTA4NjM5NzksImV4cCI6MTUxMDg2NzU3OSwiYWxnIjoiSFMyNTYifQ.eyJpZCI6IjAyYTA2ZjM0NGM2MDc0ZTRiZDBjYThhMmFiZTQ1ZWU2ZWM5MmJmOWNkZDdiN2E2N2M4MDQzNTBiZmZmNGQ0YThjMCJ9.mM_uwZ1wrdag5PoCNThn_0gzZpsIhC_xSsa8xIFxggs'}, json=body)

            # Save UUID in Spring Boot Rest API DataBase
            url = os.environ.get("URL", 'http://localhost:3307/api/hashkey/save')
            url = "%s" % url
            body = {"exp_duration": "%s" % prod.exp_duration, "org_id": "%s" % org_id,
                    "prod_id": "%s" % prod_id,
                    "item_count": "%s" % no_of_items, "added_date": "%s" % added_date}
            response = requests.post(url, headers={'Content-Type': 'application/json'}, json=body)
            if response.status_code == 200:
                print("Successfully saved in Spring Boot Rest API service database")

                # Save UUID in Local DataBase
                for item_id in dic_keys:
                    item_form = Item(uuid=dic[item_id], status="ACTIVE", product_id=prod_id,
                                     org_id=org_id, item_id=item_id, batch_id=batch_id)
                    item_form.save()
                else:
                    print("Successfully saved in local MySQL database")
                    bat = Batch.objects.get(id=batch_id)
                    bat.prod_id_json = json.dumps(response.text)
                    bat.save()

        return redirect(str_redirect)
    context = {
        'model': model,
        'form': form,
        'item_id': id,
        'p_model': p_model,
        'org_id': org_id,
        'prod': Product.objects.filter(status='ACTIVE', org_id=org_id),
        'roles': AccessPermission(request.user.profile.group.role_permission),
        'is_view': is_view,
    }
    if is_view:
        context['prod_name'] = Product.objects.get(batch_id=id)
    return render(request, str_render, context)


def item(request, id):
    org_id = request.user.profile.org.id
    model = Item.objects.filter(org_id=org_id, batch_id=id)
    return item_helper(request, model, id)


def item_helper(request, model, id):
    bat = Batch.objects.get(id=id)
    context = {
        'model': model,
        'bat': bat,
        'prod': Product.objects.get(id=bat.prod_id),
        'roles': AccessPermission(request.user.profile.group.role_permission),
    }
    return render(request, "product/add_item.html", context)


def view_qr_code(request, id):
    org_id = request.user.profile.org.id
    model = Item.objects.filter(org_id=org_id, batch_id=id)
    bat = Batch.objects.get(id=id)
    prod = Product.objects.get(id=bat.prod_id)
    li = [{'item_id': mod.id, 'prod_name': prod.pro_name, 'uuid': mod.uuid, 'price': prod.pro_price,
           'expiry_duration': prod.exp_duration, 'created_date': str(mod.date_added)} for mod in model]

    context = {
        'bat': bat,
        'prod': prod,
        'roles': AccessPermission(request.user.profile.group.role_permission),
        'list': li,
    }
    return render(request, "product/view_qr_code.html", context)