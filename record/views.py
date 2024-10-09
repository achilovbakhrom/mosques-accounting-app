from rest_framework import permissions, viewsets
from rest_framework.exceptions import ValidationError, NotFound
from rest_framework_simplejwt.authentication import JWTAuthentication
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample

from core.models import Record, Place, Category
from core.pagination import CustomPagination
from record.serializers import RecordSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum
from django.db.models.functions import TruncDay, TruncWeek, TruncMonth
from collections import defaultdict
from datetime import datetime, timedelta
from django.utils.dateparse import parse_date

class RecordView(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    queryset = Record.objects.all()
    serializer_class = RecordSerializer
    pagination_class = CustomPagination
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        parameters=[
            OpenApiParameter(name='from', description='Date From YYYY-MM-DD', required=False, type=str),
            OpenApiParameter(name='to', description='Date To YYYY-MM-DD', required=False, type=str),
            OpenApiParameter(name='place_id', description='PlaceId', required=False, type=int),
        ],
        responses={200: RecordSerializer}
    )
    def list(self, request, *args, **kwargs):
        qp_place_id = request.query_params.get('place_id')
        user = request.user

        if qp_place_id is None and user.role != 'mosque_admin':
            raise ValidationError('Specify place id for not mosque admins')

        place_id = qp_place_id or user.place.id
        found = Place.objects.get(pk=place_id)

        if found is None:
            raise ValidationError('Provide a valid place id')

        ids = []

        ids.append(found.id)
        if found.parent is not None:
            ids.append(found.parent.id)
            if found.parent.parent is not None:
                ids.append(found.parent.parent.id)


        if user.place is not None and user.place.id not in ids:
            raise ValidationError('Place id does not belong to your area')

        records = Record.objects.filter(place_id=place_id)

        paginator = self.pagination_class()

        try:
            # Paginate the queryset
            page = paginator.paginate_queryset(records, request)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return paginator.get_paginated_response(serializer.data)
        except NotFound:
            # Handle the invalid page case, return an empty result set
            return Response(
                {
                    "count": records.count(),
                    "next": None,
                    "previous": None,
                    "results": []
                },
                status=200
            )

        serializer = self.get_serializer(page, many=True)
        return Response(serializer.data)

    def get_serializer_context(self):
        context = super(type(self), self).get_serializer_context()
        context['request'] = self.request
        return context

    def perform_destroy(self, instance):
        serializer = self.get_serializer(instance)
        serializer.delete(instance)


class RecordReportView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Get Expense Report",
        description="Retrieve the expense report grouped by categories and by the selected period (supports 'daily', 'weekly', or 'monthly'). Fill gaps with zero if no data exists for a particular period.",
        parameters=[
            OpenApiParameter(
                name='period',
                location=OpenApiParameter.PATH,
                description="The period for grouping the report ('daily', 'weekly', or 'monthly').",
                required=True,
                type=str,
                enum=['daily', 'weekly', 'monthly']
            ),
            OpenApiParameter(
                name='place_id',
                location=OpenApiParameter.QUERY,
                description="Place Id",
                type=int,
            ),
            OpenApiParameter(
                name='start',
                location=OpenApiParameter.QUERY,
                description="Start date for the report in 'YYYY-MM-DD' format.",
                required=True,
                type=str,
            ),
            OpenApiParameter(
                name='end',
                location=OpenApiParameter.QUERY,
                description="End date for the report in 'YYYY-MM-DD' format.",
                required=True,
                type=str,
            )
        ],
        responses={
            200: OpenApiExample(
                "Successful Response",
                value={
                    "periods": ["2024-09-01", "2024-09-02"],
                    "data": [
                        ["Food", 150.00, 200.00, 350.00],
                        ["Transport", 100.00, 150.00, 250.00],
                        ["Total", 250.00, 350.00, 600.00]
                    ]
                }
            ),
            400: OpenApiExample(
                "Invalid Period or Dates",
                value={"error": "Invalid period or dates."}
            )
        }
    )
    def get(self, request, period, *args, **kwargs):
        place_id = request.query_params.get('place_id')
        current_user = request.user
        if current_user.role != 'mosque_admin' and place_id is None:
            raise ValueError('Invalid place')
        elif current_user.role == 'mosque_admin':
            place_id = current_user.place_id

        start_date = request.query_params.get('start')
        end_date = request.query_params.get('end')

        if not start_date:
            start_date = datetime.now().strftime('%Y-%m-01')
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')

        start_date = parse_date(start_date)
        end_date = parse_date(end_date)

        if not start_date or not end_date or start_date > end_date:
            return Response({"error": "Invalid start or end date."}, status=400)

        # Choose the correct truncation method based on the period
        if period == 'daily':
            trunc_period = TruncDay('date')
            date_range = self._generate_date_range(start_date, end_date, 'daily')
            date_format = '%Y-%m-%d'
        elif period == 'weekly':
            trunc_period = TruncWeek('date')
            date_range = self._generate_date_range(start_date, end_date, 'weekly')
            date_format = '%Y-%W'
        elif period == 'monthly':
            trunc_period = TruncMonth('date')
            date_range = self._generate_date_range(start_date, end_date, 'monthly')
            date_format = '%Y-%m'
        else:
            return Response({"error": "Invalid period. Choose from 'daily', 'weekly', or 'monthly'."}, status=400)

        # Group by period and category
        expenses = Record.objects.filter(place_id=place_id).annotate(period=trunc_period).values('period',
                                                                                                 'category__name',
                                                                                                 'category__operation_type').annotate(
            total_amount=Sum('amount')).order_by('period')

        report_data = defaultdict(lambda: defaultdict(float))

        for expense in expenses:
            category = expense['category__name']
            period_label = expense['period'].strftime(date_format)

            # Adjust total_amount based on the category's operation_type (income or expense)
            if expense['category__operation_type'] == 'income':
                report_data[category][period_label] = expense['total_amount']
            else:
                report_data[category][period_label] = -expense['total_amount']

        table_data = []
        category_totals = defaultdict(float)
        column_totals = defaultdict(float)

        for category, period_data in report_data.items():
            row = [category]
            category_sum = 0
            for period_label in date_range:
                amount = period_data.get(period_label, 0)
                row.append(amount)
                category_sum += amount
                column_totals[period_label] += float(amount)
            row.append(category_sum)
            table_data.append(row)

        total_row = ['Жами']
        overall_total = 0
        for period_label in date_range:
            col_sum = column_totals[period_label]
            total_row.append(col_sum)
            overall_total += col_sum
        total_row.append(overall_total)
        table_data.append(total_row)

        response_data = {
            "periods": date_range,
            "data": table_data,
        }

        return Response(response_data)

    def _generate_date_range(self, start, end, period):
        current = start
        date_range = []

        if period == 'daily':
            while current <= end:
                date_range.append(current.strftime('%Y-%m-%d'))
                current += timedelta(days=1)
        elif period == 'weekly':
            while current <= end:
                date_range.append(current.strftime('%Y-%W'))
                current += timedelta(weeks=1)
        elif period == 'monthly':
            while current <= end:
                date_range.append(current.strftime('%Y-%m'))
                next_month = current.replace(day=28) + timedelta(days=4)
                current = next_month.replace(day=1)

        return date_range
