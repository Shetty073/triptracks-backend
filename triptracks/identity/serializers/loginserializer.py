from rest_framework import serializers
from django.contrib.auth import authenticate

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")

        if email and password:
            user = authenticate(email=email, password=password)

            if not user:
                raise serializers.ValidationError("Invalid credentials!")
        
        else:
            raise serializers.ValidationError("Username and password is mandatory")
        
        data["user"] = user

        return data
