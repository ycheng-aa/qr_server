class GetContextMixin(object):
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
