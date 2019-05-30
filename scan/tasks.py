# TODO: scheduler :)
from django.db.models import Q

from java_wallet.models import Transaction
from scan.models import MultiOut
from scan.helpers import get_last_height
from burst.multiout import MultiOutPack


def group_list(lst, n):
    for i in range(0, len(lst), n):
        val = lst[i:i + n]
        if len(val) == n:
            yield tuple(val)


def aggregate_multiouts():
    print('Start')

    last_aggr_height = MultiOut.objects.order_by('-height').values_list(
        'height', flat=True).first()

    if last_aggr_height == get_last_height():
        return

    txs = Transaction.objects.using('java-wallet').filter(
        Q(type=0) & (Q(subtype=1) | Q(subtype=2))
    ).order_by('height')

    if last_aggr_height:
        txs = txs.filter(height__gt=last_aggr_height)

    for tx in txs.iterator():
        print('Aggregating height #', tx.height, "transaction #", tx.id)
        if tx.subtype == 1:
            data = MultiOutPack().unpack_multi_out(tx.attachment_bytes)
            for r, amount in group_list(data, 2):
                MultiOut.objects.create(
                    tx_id=tx.id,
                    height=tx.height,
                    sender_id=tx.sender_id,
                    recipient_id=r,
                    amount=amount,
                    tx_type=1
                )

        elif tx.subtype == 2:
            recipients = MultiOutPack().unpack_multi_out_same(tx.attachment_bytes)
            amount = tx.amount / len(recipients)
            for r in recipients:
                MultiOut.objects.create(
                    tx_id=tx.id,
                    height=tx.height,
                    sender_id=tx.sender_id,
                    recipient_id=r,
                    amount=amount,
                    tx_type=2
                )