# 🚀 Quick Start - Test Your OTP Password Reset

## Ready to Test? Follow These Steps:

### ✅ Step 1: Start Your Server
```bash
cd "C:\Users\SCATTER ONLY\Multibliz POS System"
python manage.py runserver
```

### ✅ Step 2: Open Your Browser
Navigate to: **http://localhost:8000/accounts/login/**

### ✅ Step 3: Click "Forgot Password"
Click the "Forgot your password?" link at the bottom of the login form

### ✅ Step 4: Enter Your Username or Email
Example: Type your username or the email associated with your account

### ✅ Step 5: Check Your Email 📧
You should receive an email with a 6-digit OTP code like:
```
Subject: Password Reset OTP - Multibliz POS

Hello username,

You requested to reset your password. Your OTP code is:

123456

This code is valid for 10 minutes.
```

### ✅ Step 6: Enter the OTP Code
Copy the 6-digit code and paste it into the verification page

### ✅ Step 7: Set New Password
Create a new password (minimum 8 characters)

### ✅ Step 8: Login with New Password! 🎉
You should be redirected to login page with a success message

---

## 🧪 Alternative: Test with Django Shell

If you want to see the OTP generation without going through the full flow:

```bash
python manage.py shell
```

```python
# Import required modules
from accounts.models import PasswordResetOTP, User

# Get a user (replace 'admin' with your username)
user = User.objects.get(username='admin')

# Create OTP
otp = PasswordResetOTP.create_for_user(user)

# Print the OTP code
print(f"OTP Code for {user.username}: {otp.code}")
print(f"Valid for 10 minutes")
print(f"Expires at: {otp.created_at}")

# Check if it's valid
print(f"Is valid? {otp.is_valid()}")
print(f"Is expired? {otp.is_expired()}")
```

---

## 🔧 Quick Troubleshooting

### Email Not Arriving?
1. **Check spam folder** - Gmail might filter it
2. **Verify email in database:**
   ```bash
   python manage.py shell
   ```
   ```python
   from accounts.models import User
   user = User.objects.get(username='your_username')
   print(user.email)  # Should show an email address
   ```

3. **Check Django logs** - Look for any error messages in the terminal

### OTP Not Working?
```python
# Check recent OTPs in database
from accounts.models import PasswordResetOTP
otps = PasswordResetOTP.objects.all().order_by('-created_at')[:5]
for otp in otps:
    print(f"{otp.user.username}: {otp.code} - Valid: {otp.is_valid()}")
```

### Need to Manually Reset Password?
```bash
python manage.py changepassword your_username
```

---

## 📱 Testing SMS (Optional)

### Prerequisites:
1. You have Twilio credentials in `settings.py`
2. User has phone number in their profile

### Test SMS Flow:
1. Add phone number to your user profile:
   ```python
   from accounts.models import User
   user = User.objects.get(username='your_username')
   user.phone = '+1234567890'  # Your phone number
   user.save()
   ```

2. Request password reset again
3. Check both email AND phone for OTP

---

## 🎯 URLs Reference

| Page | URL |
|------|-----|
| Login | http://localhost:8000/accounts/login/ |
| Forgot Password | http://localhost:8000/accounts/forgot-password/ |
| Verify OTP | http://localhost:8000/accounts/verify-otp/ |
| Reset Password | http://localhost:8000/accounts/reset-password/ |
| Admin Panel | http://localhost:8000/admin/ |

---

## ✅ Success Checklist

- [ ] Django server running
- [ ] Can access login page
- [ ] "Forgot Password" link works
- [ ] Can enter username/email
- [ ] Receive OTP email
- [ ] Can verify OTP code
- [ ] Can set new password
- [ ] Can login with new password

---

## 🆘 Need Help?

### Check These Files:
- `OTP_PASSWORD_RESET_GUIDE.md` - Full documentation
- `SETTINGS_CONFIGURATION.py` - Settings reference
- `IMPLEMENTATION_COMPLETE.md` - What was changed

### Common Issues:
1. **"Session expired"** → Clear browser cookies and try again
2. **"OTP expired"** → Request a new OTP (10-minute limit)
3. **"Invalid OTP"** → Check if you typed all 6 digits correctly
4. **"User not found"** → Verify the username/email exists in database

---

## 🎉 You're All Set!

The OTP password reset system is working and ready to use.

**Email delivery is already configured and working!**

SMS is optional - you can add Twilio credentials later if needed.

---

**Happy Testing! 🚀**
