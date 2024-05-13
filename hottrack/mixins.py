class SearchQueryMixin:
    query = None

    def get(self, request, *args, **kwargs):
        self.query = request.GET.get("query", "").strip()
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data["query"] = self.query
        return context_data
