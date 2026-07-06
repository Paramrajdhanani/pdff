from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Profile, UserOTP
import random

# Profile Detail & Usage dashboard
@login_required
def profile_view(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    
    # Calculate percentage storage used
    storage_percentage = 0
    if profile.storage_limit > 0:
        storage_percentage = min(100, round((profile.storage_used / profile.storage_limit) * 100))
        
    friendly_used = f"{(profile.storage_used / (1024 * 1024)):.2f} MB"
    friendly_limit = f"{(profile.storage_limit / (1024 * 1024)):.2f} MB"

    if request.method == "POST":
        if "generate_key" in request.POST:
            profile.generate_api_key()
            messages.success(request, "API Token generated successfully! Engage portal operations.")
        elif "change_plan" in request.POST:
            tier = request.POST.get("plan_tier", "FREE")
            profile.plan_tier = tier
            # Adjust storage limits based on tier
            if tier == "PREMIUM":
                profile.storage_limit = 5368709120  # 5GB
            elif tier == "ENTERPRISE":
                profile.storage_limit = 53687091200 # 50GB
            else:
                profile.storage_limit = 524288000   # 500MB
            profile.save()
            messages.success(request, f"Identity upgraded to {tier} tier. Quotas refitted.")
        return redirect('accounts:profile')

    context = {
        'profile': profile,
        'storage_percentage': storage_percentage,
        'friendly_used': friendly_used,
        'friendly_limit': friendly_limit,
    }
    return render(request, 'profile.html', context)

# OTP code verification view
@login_required
def otp_verify_view(request):
    if request.method == "POST":
        code = request.POST.get("otp_code", "").strip()
        otps = UserOTP.objects.filter(user=request.user, otp_code=code, is_verified=False)
        if otps.exists():
            for o in otps:
                o.is_verified = True
                o.save()
            messages.success(request, "OTP Verification code verified successfully. Lock systems clear.")
            return redirect('converter:dashboard')
        else:
            messages.error(request, "Invalid OTP code configuration. Please verify credentials.")
            
    # Auto-generate mock OTP for user convenience when accessing view
    code = str(random.randint(100000, 999999))
    UserOTP.objects.create(user=request.user, otp_code=code)
    context = {
        'mock_otp': code
    }
    return render(request, 'otp_verify.html', context)

# User registration view
def signup_view(request):
    if request.user.is_authenticated:
        return redirect('converter:dashboard')
        
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        pwd = request.POST.get("password", "")
        confirm_pwd = request.POST.get("confirm_password", "")
        
        if not username or not email or not pwd:
            messages.error(request, "All fields are required to initialize identity.")
        elif pwd != confirm_pwd:
            messages.error(request, "Passwords mismatch. Verify secure inputs.")
        elif User.objects.filter(username=username).exists():
            messages.error(request, "Username is already linked to another grid identity.")
        elif User.objects.filter(email=email).exists():
            messages.error(request, "Email address is already linked to another grid identity.")
        else:
            user = User.objects.create_user(username=username, email=email, password=pwd)
            Profile.objects.create(user=user)
            login(request, user)
            messages.success(request, "Quantum identity successfully registered! Welcome to PDF Pro.")
            return redirect('accounts:otp_verify')
            
    return render(request, 'signup.html')

# User Login View
def login_view(request):
    if request.user.is_authenticated:
        return redirect('converter:dashboard')
        
    if request.method == "POST":
        email_username = request.POST.get("email", "").strip()
        pwd = request.POST.get("password", "")
        
        # Resolve username or email login
        user = None
        if "@" in email_username:
            try:
                candidate = User.objects.get(email=email_username)
                user = authenticate(username=candidate.username, password=pwd)
            except User.DoesNotExist:
                pass
        else:
            user = authenticate(username=email_username, password=pwd)
            
        if user is not None:
            login(request, user)
            messages.success(request, f"Identity validated. Welcome back, {user.username}!")
            next_page = request.GET.get('next')
            return redirect(next_page) if next_page else redirect('converter:dashboard')
        else:
            messages.error(request, "Authorization key mismatch. Please check your credentials.")
            
    return render(request, 'login.html')

# User Logout View
def logout_view(request):
    logout(request)
    messages.success(request, "Session closed. Connection terminated.")
    return redirect('core_landing')
