from rest_framework import views
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response

from continuing_education.models.admission import Admission
from continuing_education.models.file import File


class FileUploadView(views.APIView):
    parser_classes = (FileUploadParser,)

    def put(self, request, format='pdf'):
        file_obj = request.data['file']
        admission = Admission.objects.get(pk=520)
        file = File(admission=admission, name="test", file=file_obj)
        file.save()
        return Response(data="File uploaded sucessfully", status=207)