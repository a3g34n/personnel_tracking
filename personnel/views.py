from django.shortcuts import redirect
from django.contrib.auth import logout
from django.utils.timezone import now
from rest_framework.test import APIRequestFactory
from attendance.views import CheckoutView

def custom_logout(request):
    if request.user.is_authenticated:  # Ensure the user is logged in
        user_role = request.user.role  # Get the role before logging out

        if user_role == 'employee':
            # Trigger CheckoutView programmatically
            factory = APIRequestFactory()
            checkout_request = factory.post('/api/attendance/checkout/', {}, format='json')
            checkout_request.user = request.user  # Attach the logged-in user
            response = CheckoutView.as_view()(checkout_request)

            # Handle any errors returned by CheckoutView (optional)
            if response.status_code != 200:
                print(response.data.get('message', 'Failed to check out.'))  # Log the error or notify admin

        # Log the user out
        logout(request)

        # Redirect based on user role
        if user_role == 'employee':
            return redirect('employee-login')
        elif user_role == 'admin':
            return redirect('admin-login')

    # If the user is not authenticated, redirect to a generic login page
    return redirect('employee-login')
