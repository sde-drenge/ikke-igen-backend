from django.db.models import Q
from rest_framework import status
from rest_framework.response import Response
from settings.middleware.error_handling import CustomAPIView
from users.views import BasicPageination

from .models import Workplace
from .serializers import LightWorkplaceSerializer, WorkplaceSerializer


class SearchWorkPlacesView(CustomAPIView, BasicPageination):
    """
    <GET> returns paginatied list of workplaces
    ?search=<str>
    """

    serializer_class = LightWorkplaceSerializer
    authentication_classes = []
    permission_classes = []

    def get(self, request, *args, **kwargs):
        search = request.GET.get("search", "")

        workplaces = Workplace.objects.filter(
            Q(name__icontains=search, deletedAt__isnull=True)
            | Q(vat__icontains=search, deletedAt__isnull=True)
            | Q(website__icontains=search, deletedAt__isnull=True)
        )

        paginated = self.paginate(workplaces, request)
        return Response(data=paginated.data, status=status.HTTP_200_OK)


class CreateWorkPlaceView(CustomAPIView):
    """
    <POST> creates a new workplace
    """

    serializer_class = WorkplaceSerializer
    # authentication_classes = []
    # permission_classes = []

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)


class GetWorkplaceView(CustomAPIView):
    """
    <GET> returns a workplace by uuid
    """

    serializer_class = WorkplaceSerializer

    def get(self, request, *args, **kwargs):
        workplace_id = kwargs.get("workplaceUuid")
        workplace = Workplace.objects.get(uuid=workplace_id, deletedAt__isnull=True)
        serializer = self.serializer_class(workplace)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
