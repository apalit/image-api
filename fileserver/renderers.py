from rest_framework import renderers


class BaseImageRenderer(renderers.BaseRenderer):
    media_type = None
    format = None
    charset = None
    render_style = 'binary'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        return data


class JPGRenderer(BaseImageRenderer):
    media_type = 'image/jpeg'
    format = 'jpg'


class PNGRenderer(BaseImageRenderer):
    media_type = 'image/png'
    format = 'png'
