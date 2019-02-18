from continuing_education.models.address import Address


def update_address(self, instance, validated_data, address_field):
    if address_field in validated_data:
        address_data = validated_data.pop(address_field)
        address, created = Address.objects.update_or_create(**address_data)
        setattr(instance, address_field, address)
