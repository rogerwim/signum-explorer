from django.shortcuts import redirect, render
from django.views.decorators.cache import cache_page

from java_wallet.models import Block, Transaction
from scan.helpers.queries import get_unconfirmed_transactions
from scan.views.blocks import fill_data_block
from scan.views.transactions import fill_data_transaction


@cache_page(5)
def index(request):

    # redirect the old style accounts
    if 'account' in request.GET:
        return redirect('address/' + request.GET['account'])
    if 'action' in request.GET and request.GET['action'] == 'transaction' and 'id' in request.GET:
        return redirect('tx/' + request.GET['id'])

    txs = Transaction.objects.using("java_wallet").order_by("-height")[:5]

    for t in txs:
        fill_data_transaction(t, list_page=True)

    blocks = Block.objects.using("java_wallet").order_by("-height")[:5]

    for b in blocks:
        fill_data_block(b)

    context = {
        "txs": txs,
        "blocks": blocks,
        "txs_pending": get_unconfirmed_transactions()[:5],
    }

    return render(request, "home/index.html", context)
