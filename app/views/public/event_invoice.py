from flask.ext.restplus import abort
from flask_admin import BaseView, expose
from flask import redirect, url_for, request, jsonify, make_response, flash
from xhtml2pdf import pisa
from cStringIO import StringIO
from app.settings import get_settings
import pycountry

from app.helpers.data import save_to_db
from app.helpers.invoicing import InvoicingManager
from app.helpers.payment import PayPalPaymentsManager

def create_pdf(pdf_data):
    pdf = StringIO()
    pisa.CreatePDF(StringIO(pdf_data.encode('utf-8')), pdf)
    return pdf

class EventInvoicingView(BaseView):
    @expose('/', methods=('GET',))
    def index(self):
        abort(404)
        return redirect("/")

    @expose('/<invoice_identifier>/', methods=('GET',))
    def view_invoice(self, invoice_identifier):
        invoice = InvoicingManager.get_invoice_by_identifier(invoice_identifier)
        if not invoice:
            abort(404)
        if invoice.status == 'completed':
            return redirect(url_for('event_invoicing.view_invoice_after_payment', invoice_identifier=invoice_identifier))

        stripe_publishable_key = get_settings()['stripe_publishable_key']
        if not stripe_publishable_key or stripe_publishable_key != "":
            stripe_publishable_key = "No Key Set"

        return self.render('/gentelella/guest/ticketing/invoice_pre_payment.html', invoice=invoice, event=invoice.event,
                           countries=list(pycountry.countries),
                           stripe_publishable_key=stripe_publishable_key)

    @expose('/<invoice_identifier>/view/', methods=('GET',))
    def view_invoice_after_payment(self, invoice_identifier):
        invoice = InvoicingManager.get_invoice_by_identifier(invoice_identifier)
        if not invoice or invoice.status != 'completed':
            abort(404)
        return self.render('/gentelella/guest/ticketing/invoice_post_payment.html', invoice=invoice, event=invoice.event)

    @expose('/<invoice_identifier>/view/pdf/', methods=('GET',))
    def view_invoice_after_payment_pdf(self, invoice_identifier):
        invoice = InvoicingManager.get_invoice_by_identifier(invoice_identifier)
        if not invoice or invoice.status != 'completed':
            abort(404)
        pdf = create_pdf(self.render('/gentelella/guest/ticketing/invoice_pdf.html',
                                     invoice=invoice, event=invoice.event))
        response = make_response(pdf.getvalue())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = \
            'inline; filename=%s.pdf' % invoice.get_invoice_number()
        return response

    @expose('/initiate/payment/', methods=('POST',))
    def initiate_invoice_payment(self):
        result = InvoicingManager.initiate_invoice_payment(request.form)
        if result:
            if request.form.get('pay_via_service', 'stripe') == 'stripe':
                return jsonify({
                    "status": "ok",
                    "email": result.user.email,
                    "action": "start_stripe" if result.status == 'initialized' else "show_completed"
                })
            else:
                return jsonify({
                    "status": "ok",
                    "email": result.user.email,
                    "action": "start_paypal",
                    "redirect_url": PayPalPaymentsManager.get_checkout_url(result)
                })
        else:
            return jsonify({
                "status": "error"
            })

    @expose('/charge/payment/', methods=('POST',))
    def charge_stripe_invoice_payment(self):
        status, result = InvoicingManager.charge_stripe_invoice_payment(request.form)
        if status:
            return jsonify({
                "status": "ok",
                "message": result.transaction_id
            })
        else:
            return jsonify({
                "status": "error",
                "message": result
            })

    @expose('/<invoice_identifier>/error/', methods=('GET', 'POST'))
    def show_transaction_error(self, invoice_identifier):
        invoice = InvoicingManager.get_invoice_by_identifier(invoice_identifier)
        return self.render('/gentelella/guest/ticketing/invoice_post_payment_error.html', invoice=invoice,
                           event=invoice.event)

    @expose('/<invoice_identifier>/paypal/<function>/', methods=('GET',))
    def paypal_callback(self, invoice_identifier, function):
        invoice = InvoicingManager.get_invoice_by_identifier(invoice_identifier)
        if not invoice or invoice.status == 'expired':
            abort(404)
        if function == 'cancel':
            invoice.status = 'cancelled'
            save_to_db(invoice)
            return redirect(url_for('event_detail.display_event_detail_home', identifier=invoice.event.identifier))
        elif function == 'success':
            status, result = InvoicingManager.charge_paypal_invoice_payment(invoice)
            if status:
                return redirect(url_for('.view_invoice', invoice_identifier=invoice_identifier))
            else:
                flash("An error occurred while processing your transaction. " + str(result), "danger")
                return redirect(url_for('.show_transaction_error', invoice_identifier=invoice_identifier))
        abort(404)
