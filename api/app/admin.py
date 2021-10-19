from django.contrib import admin
from django import forms

from .models import *


class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = User
        # exclude = ['groups', 'user_permissions', 'is_staff', 'is_active', 'last_login']
        fields = ['username', 'password1', 'password2', 'first_name', 'last_name', 'middle_name', 'position', 'user_access', 'email', 'phone_number', 'avatar', 'role', 'company', 'workpoint']

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserAdmin(admin.ModelAdmin):
    form = UserCreationForm
    list_filter = ('company', )


class NotificationCreationForm(forms.ModelForm):
    users = forms.ModelMultipleChoiceField(User.objects.all())
    companies = forms.ModelMultipleChoiceField(Company.objects.all())

    class Meta:
        model = Notification
        fields = ['text', 'type', 'is_read', 'material_order', 'user']

    def __init__(self, *args, **kwargs):
        super(NotificationCreationForm, self).__init__(*args, **kwargs)
        self.fields['companies'].required = False
        self.fields['users'].required = False

    def save_m2m(self):
        pass

    def save(self, commit=True):
        form_users = self.cleaned_data.get("users")
        form_companies = self.cleaned_data.get("companies")
        text = self.cleaned_data.get("text")
        type = self.cleaned_data.get("type")

        notification = None

        if len(form_users) > 0:
            for user in form_users:
                notification = Notification.objects.create(text=text, type=type, user=user)

        if len(form_companies) > 0:
            for company in form_companies:
                users = User.objects.filter(company=company)
                for user in users:
                    notification = Notification.objects.create(text=text, type=type, user=user)

        return notification or super().save()

        

class MassNotifications(admin.ModelAdmin):
    form = NotificationCreationForm



admin.site.register(User, UserAdmin)
admin.site.register(Company)
admin.site.register(UserRole)
admin.site.register(Page)
admin.site.register(SystemPost)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Material)
admin.site.register(MaterialOrder)
admin.site.register(Notification, MassNotifications)
admin.site.register(UserChangeQuery)
admin.site.register(Product)
admin.site.register(Consumable)
admin.site.register(Leg)
admin.site.register(Molding)
admin.site.register(Workpoint)
admin.site.register(OrderNumber)
admin.site.register(Specification)
admin.site.register(FabricSpecification)

