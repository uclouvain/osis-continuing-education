from rest_framework import serializers

from continuing_education.models.address import Address
from continuing_education.models.admission import Admission


class AdmissionBasicSerializer(serializers.HyperlinkedModelSerializer):

    participant = serializers.SerializerMethodField()

    formation = serializers.SerializerMethodField()

    class Meta:
        model = Admission
        fields = (
            'uuid',
            'participant',
            'formation',
        )

    def get_participant(self, obj):
        return obj.person_information.person.first_name + " " + obj.person_information.person.last_name

    def get_formation(self, obj):
        return obj.formation.acronym


class AddressGetSerializer(serializers.HyperlinkedModelSerializer):

    zip_code = serializers.CharField(source='postal_code')

    class Meta:
        model = Address
        fields = (
            'zip_code',
            'city',
            'location',
        )


class AdmissionDetailsSerializer(AdmissionBasicSerializer):

    address = AddressGetSerializer()

    class Meta:
        model = Admission
        fields = AdmissionBasicSerializer.Meta.fields + (
            'state',
            'phone_mobile',
            'high_school_diploma',
            'high_school_graduation_year',
            'address'
        )

