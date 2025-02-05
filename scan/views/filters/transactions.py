from django.db.models import Q
from django_filters import FilterSet, NumberFilter

from java_wallet.models import IndirecIncoming, Transaction


class TxFilter(FilterSet):
    block = NumberFilter(field_name="block__height")
    a = NumberFilter(method="filter_by_account")

    class Meta:
        model = Transaction
        fields = ("block", "a")

    @staticmethod
    def filter_by_account(queryset, name, value):
        indirects = list(
            IndirecIncoming.objects.using("java_wallet")
            .values_list('transaction_id', flat=True)
            .filter(account_id=value)
        )
        return queryset.filter(Q(sender_id=value) | Q(recipient_id=value) | Q(id__in=indirects))
