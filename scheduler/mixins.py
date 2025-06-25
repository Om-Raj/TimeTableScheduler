from django.shortcuts import get_object_or_404
from .organization.models import Organization

class OrganizationContextMixin:
    """
    A mixin that adds the organization to the context.
    """
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['organization'] = get_object_or_404(Organization, id=self.kwargs['org_id'])
        return context 