from wagtail.api.v2.views import PagesAPIViewSet \
    as DefaultPagesAPIViewSet
from wagtail.images.api.v2.views import ImagesAPIViewSet \
    as DefaultImagesAPIViewSet
from wagtail.documents.api.v2.views import DocumentsAPIViewSet \
    as DefaultDocumentsAPIViewSet
from wagtail.api.v2.router import WagtailAPIRouter


# Create the router. "wagtailapi" is the URL namespace
api_router = WagtailAPIRouter('wagtailapi')


class PagesAPIViewSet(DefaultPagesAPIViewSet):
    permission_classes = []


class ImagesAPIViewSet(DefaultImagesAPIViewSet):
    permission_classes = []


class DocumentsAPIViewSet(DefaultDocumentsAPIViewSet):
    permission_classes = []


# Add the three endpoints using the "register_endpoint" method.
# The first parameter is the name of the endpoint (such as pages, images). This
# is used in the URL of the endpoint
# The second parameter is the endpoint class that handles the requests
api_router.register_endpoint('pages', PagesAPIViewSet)
api_router.register_endpoint('images', ImagesAPIViewSet)
api_router.register_endpoint('documents', DocumentsAPIViewSet)
