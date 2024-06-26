# hottrack/views.py

import datetime
from io import BytesIO
from typing import Literal

from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404

# from datetime import datetime

from django.conf import settings

from hottrack.models import Song
from django.db.models import Q
from django.views.generic import (
    DetailView,
    ListView,
    YearArchiveView,
    MonthArchiveView,
    DayArchiveView,
    TodayArchiveView,
    WeekArchiveView,
    ArchiveIndexView,
    DateDetailView,
)

from hottrack.utils.cover import make_cover_image
import pandas as pd

from .mixins import SearchQueryMixin


class IndexView(SearchQueryMixin, ListView):
    model = Song
    template_name = "hottrack/index.html"
    paginate_by = 10

    def get_queryset(self):
        qs = super().get_queryset()

        release_date = self.kwargs.get("release_date")
        if release_date:
            qs = qs.filter(release_date=release_date)

        if self.query:
            qs = qs.filter(
                Q(name__icontains=self.query)
                | Q(artist_name__icontains=self.query)
                | Q(album_name__icontains=self.query)
            )
        return qs


index = IndexView.as_view()

# def index(request: HttpRequest, release_date: datetime.date = None) -> HttpResponse:
#     query = request.GET.get("query", "").strip()

#     song_qs: QuerySet[Song] = Song.objects.all()

#     if release_date:
#         song_qs = song_qs.filter(release_date=release_date)

#     # melon_chart_url = "https://raw.githubusercontent.com/pyhub-kr/dump-data/main/melon/melon-20230910.json"
#     # json_string = urlopen(melon_chart_url).read().decode("utf-8")
#     # # 외부 필드명을 그대로 쓰기보다, 내부적으로 사용하는 필드명으로 변경하고, 필요한 메서드를 추가합니다.
#     # song_list = [Song.from_dict(song_dict) for song_dict in json.loads(json_string)]

#     if query:
#         song_qs = song_qs.filter(
#             Q(name__icontains=query)
#             | Q(artist_name__icontains=query)
#             | Q(album_name__icontains=query)
#         )
#         # song_list = [
#         #     song
#         #     for song in song_list
#         #     if query in song.name
#         #     or query in song.artist_name
#         #     or query in song.album_name
#         # ]
#     return render(
#         request=request,
#         template_name="hottrack/index.html",
#         context={
#             "song_list": song_qs,
#             "query": query,
#         },
#     )


class SongDetailView(DetailView):
    model = Song

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()

        melon_uid = self.kwargs.get("melon_uid")
        if melon_uid:
            return get_object_or_404(queryset, melon_uid=melon_uid)
        return super().get_object(queryset)


song_detail = SongDetailView.as_view()


def cover_png(request, pk):
    # 최대값 512, 기본값 256
    canvas_size = min(512, int(request.GET.get("size", 256)))

    song = get_object_or_404(Song, pk=pk)

    cover_image = make_cover_image(
        song.cover_url, song.artist_name, canvas_size=canvas_size
    )

    # param fp : filename (str), pathlib.Path object or file object
    # image.save("image.png")
    response = HttpResponse(content_type="image/png")
    cover_image.save(response, format="png")

    return response


def export(request, format: Literal["csv", "xlsx", "xls"]):
    song_qs = Song.objects.all()
    df = pd.DataFrame(data=song_qs.values())
    export_file = BytesIO()

    if format == "csv":
        content_type = "text/csv"
        filename = "hottrack.csv"
        df.to_csv(path_or_buf=export_file, index=False, encoding="utf-8-sig")
    elif (format == "xlsx") or (format == "xls"):
        content_type = "application/vnd.ms-excel"
        filename = {"xlsx": "hottrack.xlsx", "xls": "hottrack(97-2003v).xls"}.get(
            format, "hottrack.xlsx"
        )
        df.to_excel(excel_writer=export_file, index=False)
    else:
        return HttpResponseBadRequest(f"Invalid format : {format}")

    response = HttpResponse(content=export_file.getvalue(), content_type=content_type)
    response["Content-Disposition"] = 'attachment; filename="{}"'.format(filename)

    return response


class SongYearArchiveView(YearArchiveView):
    model = Song
    date_field = "release_date"  # 조회할 날짜 필드
    make_object_list = True


class SongMonthArchiveView(MonthArchiveView):
    model = Song
    date_field = "release_date"
    month_format = "%m"


class SongDayArchiveView(DayArchiveView):
    model = Song
    date_field = "release_date"
    month_format = "%m"


class SongTodayArchiveView(TodayArchiveView):
    model = Song
    date_field = "release_date"

    if settings.DEBUG:

        def get_dated_items(self):
            fake_today = self.request.GET.get("fake-today", "")
            try:
                year, month, day = map(int, fake_today.split("-", 3))
                return self._get_dated_items(datetime.date(year, month, day))
            except ValueError:
                # fake_today 파라미터가 없거나 날짜 형식이 잘못되었을 경우
                return super().get_dated_items()


class SongWeekArchiveView(WeekArchiveView):
    model = Song
    date_field = "release_date"

    week_format = "%W"


class SongArchiveIndexView(ArchiveIndexView):
    model = Song
    date_field = "release_date"
    paginate_by = 10

    # date_list_period = "year"  # 단위 : year (디폴트), month, day, week
    def get_date_list_period(self):
        # URL Captured Value에 date_list_period가 없으면, date_list_period 속성을 활용합니다.
        return self.kwargs.get("date_list_period", self.date_list_period)

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data["date_list_period"] = self.get_date_list_period()
        return context_data


class SongDateDetailView(DateDetailView):
    model = Song
    date_field = "release_date"
    month_format = "%m"
