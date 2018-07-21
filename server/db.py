from flask import abort
from mongoengine.queryset import DoesNotExist, QuerySet
import mongoengine_goodjson as gj


class BaseQuerySet(QuerySet):
    """Mongoengine's queryset extended with handy extras."""

    def get_or_404(self, *args, **kwargs):
        """
        Get a document and raise a 404 Not Found error if it doesn't
        exist.
        """
        try:
            return self.get(*args, **kwargs)
        except (DoesNotExist):
            abort(404)

    def first_or_404(self):
        """Same as get_or_404, but uses .first, not .get."""
        obj = self.first()
        if obj is None:
            abort(404)

        return obj


class BaseDocument(gj.Document):
    meta = {'abstract': True, 'queryset_class': BaseQuerySet}
