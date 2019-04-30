from rest_framework import generics

from continuing_education.api.serializers.admissionPrez import AdmissionBasicSerializer, AdmissionDetailsSerializer
from continuing_education.models.admission import Admission


class AdmissionBasic(generics.ListAPIView):
    """
       Return a list of all the admission with optional filtering.
    """
    name = 'admission-basic'

    filter_fields = (
        'formation',
    )
    search_fields = (
        'formation',
    )
    ordering_fields = (
        'formation',
    )
    ordering = (
        'formation',
    )  # Default ordering

    serializer_class = AdmissionBasicSerializer

    def get_queryset(self):
        return Admission.admission_objects.all().select_related(
            'person_information',
            'formation'
        )


class AdmissionDetails(generics.RetrieveAPIView):
    """
       Return a list of all the admission with optional filtering.
    """
    name = 'admission-details'

    filter_fields = (
        'formation',
    )
    search_fields = (
        'formation',
    )
    ordering_fields = (
        'formation',
    )
    ordering = (
        'formation',
    )  # Default ordering

    serializer_class = AdmissionDetailsSerializer
    queryset = Admission.admission_objects.all()
    lookup_field = 'uuid'
