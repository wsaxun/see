import os, json
from django.conf import settings
from rest_framework.views import APIView
from django.http import StreamingHttpResponse

class RenderFile(object):

    def create_file(self, params, content):
        pk, sfx = params.get('pk'), params.get('sfx')
        file_name = '{}.{}'.format(pk, sfx)
        path = settings.MEDIA.get('sql_file_path')
        isExists = os.path.exists(path)
        if not isExists:
            os.makedirs(path)
        path = os.path.join(path, file_name)
        with open(path, 'w') as f:
            content_list = json.loads(content)
            length = len(content_list)
            if isinstance(content_list, list):
                for row in content_list:
                    f.write(str(row))
                    if content_list.index(row) < length - 1:
                        f.write('\n')
            else:
                f.write(content)
        return path, file_name

    def file_iterator(self, file_path, chunk_size=512):
        with open(file_path) as f:
            while True:
                c = f.read(chunk_size)
                if c:
                    yield c
                else:
                    break

class DownloadBaseView(RenderFile, APIView):

    def get_content(self):
        return None

    def get(self, request, *args, **kwargs):
        file_path, file_name = self.create_file(kwargs, self.get_content())
        response = StreamingHttpResponse(self.file_iterator(file_path))
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment;filename="{0}"'.format(file_name)
        return response