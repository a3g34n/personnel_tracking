from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()

class EmployeeForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput,
        required=True,
        label="Password"
    )
    date_of_birth = forms.DateField(
        widget=forms.DateInput(
            attrs={
                'type': 'date',  # HTML5 tarih seçici
                'class': 'form-control',
            }
        ),
        required=False,
        label="Date of Birth"
    )
    class Meta:
        model = User
        fields = ['username', 'email', 'role', 'password', 'phone_number', 'date_of_birth']  # Şifreyi ekledik

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])  # Şifreyi hashleyerek sakla
        if commit:
            user.save()
        return user
