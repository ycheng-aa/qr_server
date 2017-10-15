from rest_framework import serializers


class AuthedSerializer(serializers.ModelSerializer):

    def current_user(self):
        return self.context['request'].user

    def get_method(self):
        return self.context['request'].method
