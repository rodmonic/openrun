from rest_framework.renderers import BaseRenderer
from django.contrib.gis.geos import GEOSGeometry

from django.template import loader


class TemplateRenderer(BaseRenderer):

    template_name = None

    def render(self, data, accepted_media_type=None, renderer_context=None):

        svgpaths = []

        try:
            features = data['results']['features']
        except:
            features = [data]

        for feature in features:

            height = 1000
            width = 1000

            Geometry = GEOSGeometry(str(feature['geometry']))
            extent = Geometry.extent
            translate_x = extent[0] * -1
            translate_y = extent[1] * -1

            range_x = extent[2] - extent[0]
            range_y = extent[3] - extent[1]

            max_range = max(range_x, range_y)

            translate = 'translate(%s %s)' % ( translate_x, translate_y )
            scale = 'scale(%s)' % ( max(height, width) / max_range )

            for line in Geometry:
                tmpPath = 'M ' + str(line[0][0]) + ' ' + str(line[0][1])
                for point in line[1:]:
                    tmpPath += ' L ' + str(point[0]) + ' ' + str(point[1])
                svgpaths.append(tmpPath)

        template = loader.get_template(self.template_name)

        return template.render({
            'paths': svgpaths,
            'translate': translate,
            'scale': scale,
            'height': height,
            'width': width,
            })


class SVGRenderer(TemplateRenderer):

    media_type = 'image/svg+xml'
    format = 'svg'
    template_name = 'api/track.svg'
