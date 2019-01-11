from webapp.models import User

import hashlib

class MyBackend:
    def authenticate(request, username=None, password=None):
        # Check the username/password and return a user.
        try:
            user = User.objects.get(email=username)
        except User.DoesNotExist:
            return None
        hashed_password = hashlib.sha512(password.encode('utf-8') + user.salt.encode('utf-8')).hexdigest()
        if(hashed_password == user.password_hash):
            return user
        return None
        
    def get_user(user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None