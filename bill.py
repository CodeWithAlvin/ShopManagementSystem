import os
from InvoiceGenerator.api import Invoice, Item, Client, Provider, Creator
from InvoiceGenerator.pdf import SimpleInvoice

def genrate(store_name,name,phone,basket):
    # choosing English as the document language
    os.environ["INVOICE_LANG"] = "en"
    client = Client(name)
    provider = Provider(store_name)
    creator = Creator('Signature')
    # creating an invoice object
    invoice = Invoice(client, provider, creator)

    # adding items to bill
    for item,price,quantity in basket:
        invoice.add_item(Item(quantity, price, description=item))

    invoice.currency = "Rs."
    doc = SimpleInvoice(invoice)
    doc.gen(f"Bill/{name}{phone}.pdf", generate_qr_code=False) #you can put QR code by setting the #qr_code parameter to ‘True’

    print("Bill Genrated.")