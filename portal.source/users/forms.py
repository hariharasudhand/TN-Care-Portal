from django import forms
from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import UserCreationForm
from .models import Organization, Profile, RolePermission, Groups, MODULES, District, Zone, BMC
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column

class DistrictForm(forms.ModelForm):
    class Meta:
        model = District
        fields = ['district_name']


class ZoneForm(forms.ModelForm):
    class Meta:
        model = Zone
        fields = ['zone_name', 'district']

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

            if self.instance:
                self.fields['district'].queryset = District.objects.filter(status='ACTIVE')

class BMCForm(forms.ModelForm):
    class Meta:
        model = BMC
        fields = ['bmc_name', 'district', 'zone']

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

            if self.instance:
                self.fields['district'].queryset = District.objects.filter(status='ACTIVE')
                self.fields['zone'].queryset = Zone.objects.filter(status='ACTIVE')


class ChangePassForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']
        widgets = {'username': forms.HiddenInput(), }


class OrgRegisterForm(forms.ModelForm):
    class Meta:
        model = Organization
        fields = ['org_name']


class OrgApprovalForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['group', 'org']
        widgets = {'org': forms.HiddenInput(), }

    def __init__(self, orgId, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance:
            self.fields['group'].queryset = Groups.objects.filter(org=orgId).filter(status='ACTIVE')


class OrgUpdateForm(forms.ModelForm):
    class Meta:
        model = Organization
        fields = ['address', 'org_type']
        widgets = {'address': forms.Textarea(attrs={"rows":5, "cols":20}), }


class UserRegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']


class ProfileAddForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['district', 'zone', 'bmc', 'group']
    def __init__(self, orgId, *args, **kwargs):
        super(ProfileAddForm, self).__init__(*args, **kwargs)
        self.fields['zone'].queryset = Zone.objects.none()
        self.fields['bmc'].queryset = BMC.objects.none()
        # this block of code helps to dynamically select zone data based on district selection starts
        if 'district' in self.data:
            try:
                district_id = int(self.data.get('district'))
                self.fields['zone'].queryset = Zone.objects.filter(district_id=district_id).order_by('zone_name')
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['zone'].queryset = self.instance.district.district_id_set.order_by('zone_name')
        # this block of code helps to dynamically select zone data based on district selection ends
        # this block of code helps to dynamically select bmc data based on zone selection starts
        if 'zone' in self.data:
            try:
                zone_id = int(self.data.get('zone'))
                self.fields['bmc'].queryset = BMC.objects.filter(bmc_id=bmc_id).order_by('bmc_name')
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['bmc'].queryset = self.instance.zone.zone_id_set.order_by('bmc_name')
        # this block of code helps to dynamically select bmc data based on zone selection ends
        if self.instance:
            self.fields['group'].queryset = Groups.objects.filter(org=orgId).filter(status='ACTIVE')
            self.fields['district'].queryset = District.objects.filter(status='ACTIVE')


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['phone', 'photo']


class RolePermissionForm(forms.ModelForm):
    module = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,
                                          choices=MODULES)
    class Meta:
        model = RolePermission
        fields = ['role_name', 'module', 'create', 'view', 'update', 'delete', 'org']
        widgets = {'org': forms.HiddenInput(), }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.layout = Layout(
            'role_name',
            'module',
            Row(
                Column('create', css_class='form-group col-md-3 mb-0'),
                Column('view', css_class='form-group col-md-3 mb-0'),
                Column('update', css_class='form-group col-md-3 mb-0'),
                Column('delete', css_class='form-group col-md-3 mb-0'),
                css_class='form-row'
            ),
            Submit('submit', 'Save', css_class='btn btn-success col-md-offset-5')
        )


class GroupsForm(forms.ModelForm):

    class Meta:
        model = Groups
        fields = ['group_name', 'role_permission', 'org']
        widgets = {'org': forms.HiddenInput(), }

    def __init__(self, orgId, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance:
            self.fields['role_permission'].queryset = RolePermission.objects.filter(org=orgId).filter(status='ACTIVE')

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('group_name', css_class='form-group col-md-6 mb-0'),
                Column('role_permission', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Submit('submit', 'Save', css_class='btn btn-success col-md-offset-5')
        )
