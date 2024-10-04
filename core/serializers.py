from rest_framework import serializers


class AuditSerializerMixin(serializers.ModelSerializer):
    class Meta:
        abstract = True

    def create(self, validated_data):
        request = self.context.get('request', None)

        # Create a new Unit instance

        instance = self.Meta.model(**validated_data)

        # Call save() on the instance and pass the request
        instance.save(request=request)

        return instance

    def update(self, instance, validated_data):
        request = self.context.get('request', None)

        # Update the instance with the validated data
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Call save() on the instance and pass the request
        instance.save(request=request)

        return instance

    def delete(self, instance):
        request = self.context.get('request', None)

        instance.delete(request=request)

    def to_internal_value(self, data):
        # This will ensure that the `id` is passed through to the validated data
        category_id = data.get('id', None)

        # Call the default to_internal_value to handle normal validation
        validated_data = super().to_internal_value(data)

        # If there's an ID, include it in the validated data
        if category_id is not None:
            validated_data['id'] = category_id

        return validated_data