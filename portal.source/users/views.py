from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import logout
from django.template import loader
from django.http import HttpResponse
from .models import Profile, Groups, RolePermission, Organization
from .forms import (OrgRegisterForm, UserRegisterForm, UserUpdateForm, ProfileUpdateForm,
                    GroupsForm, RolePermissionForm, OrgUpdateForm, OrgApprovalForm,
                    ProfileAddForm)
from app.utils import AccessPermission


def get_roles(request):
    if not request.user.is_superuser:
        roles = AccessPermission(request.user.profile.group.role_permission)
    else:
        roles = 'superuser'
    return roles


def login_request(request):
    if request.method == 'POST':
        form = AuthenticationForm(request=request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.profile.status == 'INACTIVE':
                    return redirect('org-registered')

                login(request, user)

                if user.profile.force_login:
                    save_org(user, user.profile.org)
                    return redirect('password_change')

                context = {
                    'roles': get_roles(request),
                }
                return render(request, 'app/main.html', context)
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    form = AuthenticationForm()
    return render(request=request,
                  template_name="users/login.html",
                  context={"form": form})


# Organization Onboard handler,
def org_registered(request):
    context = {}
    logout(request)
    template = loader.get_template('users/org_register.html')
    return HttpResponse(template.render(context, request))


def save_org(user_obj, org_obj):
    profile_obj = Profile.objects.get(user_id=user_obj.id)
    profile_obj.org_id = org_obj.id
    profile_obj.force_login = False
    profile_obj.save()


def org_approved(request):
    org = Organization.objects.all().order_by('-date_added')
    form = OrgApprovalForm(request.POST or None)
    str_render = 'users/org_approve.html'
    return org_helper(request, form, org, id, str_render)


def org_approve(request, id):
    if id > 0:
        obj = Profile.objects.get(org_id=id)
        org_id = obj.org.id
        form = OrgApprovalForm(org_id, request.POST or None, instance=obj)
        if request.method == 'POST':
            if form.is_valid():
                prof_obj = form.save()
                prof_obj.group = form.cleaned_data.get('group')
                prof_obj.status = 'ACTIVE'
                prof_obj.force_login = False
                prof_obj.save()
                org_obj = Organization.objects.get(id=prof_obj.org_id)
                org_obj.status = 'ACTIVE'
                org_obj.save()
                messages.success(request, 'The organization is activated')
                return redirect('org-approved')
    else:
        form = OrgApprovalForm(request.POST or None)

    org = Organization.objects.all().order_by('-date_added')
    str_render = 'users/org_approve.html'
    return org_helper(request, form, org, id, str_render)


def org_onboard(request):
    if request.method == 'POST':
        o_form = OrgRegisterForm(request.POST)
        u_form = UserRegisterForm(request.POST)

        if o_form.is_valid() and u_form.is_valid():
            user_obj = u_form.save()
            org_obj = o_form.save()

            save_org(user_obj, org_obj)
            messages.success(request, "The organization is activated")
            return redirect('org-registered')
    else:
        o_form = OrgRegisterForm(request.POST or None)
        u_form = UserRegisterForm(request.POST or None)

    context = {
        'o_form': o_form,
        'u_form': u_form
    }
    return render(request, 'users/organization_add.html', context)


def org_update(request):
    org_id = request.user.profile.org.id
    org_obj = Organization.objects.get(id=org_id)
    form = OrgUpdateForm(request.POST or None, instance=org_obj)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, 'The Organization details are updated')
            redirect('org-update')
    str_render = 'users/org_update.html'
    return org_helper(request, form, org_obj, org_id, str_render)


def org_helper(request, form, org, org_id, str_render):
    context = {
        'form': form,
        'model': org,
        'org_id': org_id,
        'roles': get_roles(request),
    }
    return render(request, str_render, context)


def profile_helper(request, u_form, p_form, org_id, is_update, str_render):
    model = User.objects.filter(profile__org=org_id)
    context = {
        'form': u_form,
        'model': model,
        'p_form': p_form,
        'org_id': org_id,
        'roles': get_roles(request),
        'is_update': is_update,
    }
    return render(request, str_render, context)


def register(request):
    org_id = request.user.profile.org.id
    org_obj = Organization.objects.get(id=org_id)
    form = UserRegisterForm(request.POST or None)
    p_form = ProfileAddForm(org_id, request.POST or None)
    if request.method == 'POST' and form.is_valid() and p_form.is_valid():
        user_obj = form.save()
        messages.success(request, f'New user {user_obj.username} is created')
        profile_obj = Profile.objects.get(user_id=user_obj.id)
        profile_obj.org_id = org_obj.id
        profile_obj.group = p_form.cleaned_data.get('group')
        profile_obj.status = 'ACTIVE'
        profile_obj.force_login = True
        profile_obj.save()
        redirect('register')
    str_render = 'users/users_add.html'
    return profile_helper(request, form, p_form, org_id, False, str_render)


def profile_update(request, id):
    org_id = request.user.profile.org.id
    if id:
        u_obj = User.objects.get(id=id)
        p_obj = Profile.objects.get(user_id=id)
        u_form = UserRegisterForm(request.POST or None, instance=u_obj)
        p_form = ProfileAddForm(org_id, request.POST or None, request.FILES, instance=p_obj)

        if request.method == 'POST' and u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            username = u_form.cleaned_data.get('username')
            messages.success(request, f' {username} profile is updated')
        str_render = 'users/users_add.html'
        return profile_helper(request, u_form, p_form, org_id, True, str_render)


def profile(request):
    u_form = UserUpdateForm(request.POST, instance=request.user)
    if request.method == 'POST':
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Your profile is updated')
            return redirect('profile')
    else:
        p_form = ProfileUpdateForm(instance=request.user.profile)

    str_render = 'users/profile.html'
    return profile_helper(request, u_form, p_form, None, True, str_render)


def profile_delete(request, id):
    org_id = request.user.profile.org.id
    if id:
        p_obj = Profile.objects.get(user_id=id)
        p_obj.status = 'INACTIVE'
        p_obj.save()

    u_form = UserRegisterForm(request.POST or None)
    p_form = ProfileAddForm(org_id, request.POST or None)
    str_render = 'users/users_add.html'
    return profile_helper(request, u_form, p_form, org_id, False, str_render)


def roles_add(request):
    return roles_helper(request, 0)


def roles_update(request, id):
    return roles_helper(request, id)


def roles_helper(request, id):
    org_id = request.user.profile.org.id
    model = RolePermission.objects.filter(status='ACTIVE').filter(org=org_id)
    if id > 0:
        obj = RolePermission.objects.get(id=id)
        form = RolePermissionForm(request.POST or None, instance=obj)
        is_update = True
    else:
        form = RolePermissionForm(request.POST or None)
        is_update = False
        obj = None

    str_redirect = 'roles'
    str_render = 'users/roles.html'
    str_msg = 'Roles'
    return helper(request, model, form, str_redirect, str_render, str_msg, is_update, obj)


def roles_cancel(request, id):
    model = RolePermission.objects.filter(status='ACTIVE').filter(org=request.user.profile.org.id)
    form = RolePermissionForm(request.POST or None)
    if id:
        obj = RolePermission.objects.get(id=id)

    str_render = "users/roles.html"
    return cancel_helper(request, id, model, form, obj, str_render)


def group_add(request):
    return groups_helper(request, 0)


def group_update(request, id):
    return groups_helper(request, id)


def groups_cancel(request, id):
    model = Groups.objects.filter(status='ACTIVE').filter(org=request.user.profile.org.id)
    form = Groups(request.POST or None)
    if id:
        obj = Groups.objects.get(id=id)

    str_render = "app/main.html"
    # str_render = "users/groups.html"
    return cancel_helper(request, id, model, form, obj, str_render)


def groups_helper(request, id):
    org_id = request.user.profile.org.id
    model = Groups.objects.filter(status='ACTIVE').filter(org=org_id)
    if id > 0:
        obj = Groups.objects.get(id=id)
        form = GroupsForm(org_id, request.POST or None, instance=obj)
        is_update = True
    else:
        form = GroupsForm(org_id, request.POST or None)
        is_update = False
        obj = None

    str_redirect = 'groups'
    str_render = 'users/groups.html'
    str_msg = 'Groups'
    return helper(request, model, form, str_redirect, str_render, str_msg, is_update, obj)


def helper(request, model, form, str_redirect, str_render, str_msg, is_update, obj):
    org_id = request.user.profile.org.id
    if form.is_valid():
        form.save()
        messages.success(request, f'{str_msg} data is updated')
        return redirect(str_redirect)
    context = {
        'form': form,
        'model': model,
        'is_update': is_update,
        'obj': obj,
        'org_id': org_id,
        'roles': get_roles(request),
    }
    return render(request, str_render, context)


def cancel_helper(request, id, model, form, obj, str_render):
    if id:
        obj.status = 'INACTIVE'
        obj.save()
    context = {
        'model': model,
        'form': form,
        'roles': get_roles(request),
    }
    template = loader.get_template(str_render)
    return HttpResponse(template.render(context, request))
