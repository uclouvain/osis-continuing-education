from rest_framework import serializers

from continuing_education.models.address import Address
from continuing_education.models.admission import Admission
from reference.models.country import Country


class AdmissionBasicSerializer(serializers.HyperlinkedModelSerializer):

    participant = serializers.SerializerMethodField()
    formation = serializers.CharField(source='formation.acronym')

    class Meta:
        model = Admission
        fields = (
            'uuid',
            'participant',
            'formation',
        )

    def get_participant(self, obj):
        return obj.person_information.person.first_name + " " + obj.person_information.person.last_name


class AddressSerializer(serializers.HyperlinkedModelSerializer):
    country = serializers.SlugRelatedField(
        slug_field='iso_code',
        queryset=Country.objects.all(),
    )

    class Meta:
        model = Address
        fields = (
            'postal_code',
            'city',
            'location',
            'country'
        )


class AdmissionDetailsSerializer(AdmissionBasicSerializer):

    address = AddressSerializer()
    birth_location = serializers.CharField(source='person_information.birth_location')
    birth_date = serializers.CharField(source='person_information.birth_date')

    class Meta:
        model = Admission
        fields = AdmissionBasicSerializer.Meta.fields + (
            'state',
            'phone_mobile',
            'high_school_diploma',
            'high_school_graduation_year',
            'address',
            'birth_location',
            'birth_date'
        )

