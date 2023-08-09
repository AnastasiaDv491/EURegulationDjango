"""
    Utility functions for models
"""
from datetime import timedelta
from itertools import chain
import uuid
from django.db import models
from django.db.models import Q
from django.db.models.query import QuerySet

# Abstract models
class TimeStampedModel(models.Model):
    """An abstract base class model that provides self-updating
       created and modified fields.

    Args:
        models (django.db.models.Model): standard django model template
    """
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        app_label = 'db'


def get_short_uuid():
    return uuid.uuid4().hex

class Uid(models.Model):
    uid = models.CharField(max_length=32, null=True, default=get_short_uuid, unique=True, db_index=True, editable=False)

    class Meta:
        abstract = True


class BaseHistoryRequestQueryset(QuerySet):
    """
    This manager keeps track of requests for data
    - asset_field should be set
    - unique_field should be set if asset_field is a FK
    """

    def _get_requests(self, start_date, end_date, assets, **kwargs):
        # Get all requests we made, for all assets we asked, within this interval
        requests = self.filter(**kwargs, **{f'{self.asset_field}__in': assets}).filter(
            Q(start_date__gte=start_date, start_date__lte=end_date) |
            Q(end_date__gte=start_date, end_date__lte=end_date) |
            Q(start_date__lt=start_date, end_date__gt=end_date)).order_by('start_date')
        if self.unique_field:  # If this is set, this means asset_field is a foreign key
            return requests.select_related(self.asset_field) #prefetch_related
        return requests

    def _get_instr_key(self, instr):
        # If unique_field is not set, the key is just the assets that is passed, since this is a string then
        return instr if not self.unique_field else getattr(instr, self.unique_field)

    def get_all_missing_intervals_per_asset(self, start_date, end_date, assets, **kwargs):
        """
        Returns a dict with as key the assets id and as value a list of missing ranges (range = tuple)
        If assets had no missing range, it is not included in the dict
        """
        requests = self._get_requests(start_date, end_date, assets, **kwargs)

        # Create a dictionary with for every asset a list of requests we made
        # These requests are already sorted by start_date, so we don't need to sort anymore
        asset_dict = {self._get_instr_key(asset): [] for asset in assets}
        for request in requests:
            instr = getattr(request, self.asset_field)
            asset_dict[self._get_instr_key(instr)].append((request.start_date, request.end_date))

        # Now we can find the missing intervals
        missing_dict = dict()
        for key, ranges in asset_dict.items():
            missing = []
            # Check every range with the next range in the ranges we found
            # The first range should be compared to the day before the start_date
            # and the last range to the day after the end_date
            for range_a, range_b in zip(chain([(None, start_date - timedelta(days=1))], ranges),
                                        chain(ranges, [(end_date + timedelta(days=1), None)])):
                # If our end_date of the range is more than 1 day before the start_date of our next range
                if range_a[1] < range_b[0] - timedelta(days=1):
                    missing.append((range_a[1] + timedelta(days=1), range_b[0] - timedelta(days=1)))
            if missing:
                missing_dict[key] = missing
        return missing_dict

    def get_missing_interval_per_asset(self, start_date, end_date, assets, **kwargs):
        """
        Returns a dict with as key the asset id and as value one tuple which encompasses all missing ranges
        """
        missing = self.get_all_missing_intervals_per_asset(start_date, end_date, assets, **kwargs)
        return {key: (values[0][0], values[-1][1]) for key, values in missing.items()}

    def get_one_missing_interval_for_all_assets(self, start_date, end_date, assets, **kwargs):
        """
        Returns one tuple with a start- and end-date which encompasses all missing updates for all assets
        Returns None if no missing data
        """
        intervals = self.get_missing_interval_per_asset(start_date, end_date, assets, **kwargs)
        if not intervals:
            return None
        return min(r[0] for r in intervals.values()), max(r[1] for r in intervals.values())

    def update_request_table(self, start_date, end_date, assets, **kwargs):
        """
        Updates the request table and fixes sharding to improve speed for future calls
        """
        requests = self._get_requests(start_date, end_date, assets, **kwargs)

        # A dictionary with as key the asset_code and value an array of tuples (start_date, end_date)
        request_dict = dict()
        for request in requests:
            request_dict.setdefault(self._get_instr_key(getattr(request, self.asset_field)), []).append(
                (request.start_date, request.end_date))

        new_requests = []
        for instr in assets:
            # Get the existing requests in this range
            array = request_dict.get(self._get_instr_key(instr))
            r = self.model(**kwargs, **{f'{self.asset_field}': instr})
            if not array:  # If there are not existing requests
                r.start_date = start_date
                r.end_date = end_date
            else:
                # If the start_date of the first existing request is before our start_date, we take that start_date
                r.start_date = array[0][0] if array[0][0] < start_date else start_date
                # If the end_date of the last existing request is after our end_date, we take that end_date
                r.end_date = array[-1][1] if array[-1][1] > end_date else end_date
            new_requests.append(r)

        requests.delete()  # We remove all old requests, this way we don't have any sharding
        self.bulk_create(new_requests)