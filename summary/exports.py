from models import (Campaign,
                    Event,
                    Result,
                    get_result_event_by_campaign)
import jinja2
from io import BytesIO
from xhtml2pdf import pisa
import os
# import pandas as pd

environment = jinja2.Environment()


input_dict = {'results': [{'email': 'a@b.c', 'open': True, 'click': True,
                                    'submit': False, 'report': False, 'os': 'windows', 'browser': 'chrome'}
                          ],
              'details': [
    {'firstname': 'john', 'lastname': 'carter', 'ip': '0.0.0.0', 'email': 'john.c@c.co', 'location': 'test,test,test',
        'browser': 'firefox', 'os': 'linux', 'send': '01/01/23', 'open': '02/02/23', 'click': '03/03/23', 'submit': '04/04/23'},
],
    'browers': [{'name': 'chrome', 'count': 10}, {'name': 'firefox', 'count': 5}],
    'oses': [{'name': 'windows', 'count': 10}, {'name': 'ubuntu', 'count': 5}],
    'ips': [{'name': '0.0.0.0', 'count': 10}, {'name': '127.0.0.1', 'count': 5}],
    'campaign': {'name': 'test', 'status': 'complete', 'create_at': '01/01/23', 'launch_date': '02/02/23', 'complete_date': '03/03/23'},
    'envelop_sender': 'es', 'base_url': 'ur', 're_url': 're', 'capture_cred': False, 'capture_pass': False,
    'targets': 10, 'opened': 5, 'clicked': 3, 'submitted': 1}


TEMPLATE_DIR = os.path.join(os.path.dirname(
    __file__), "export_templates/pdf.html")


def convert_html_to_pdf():
    output = BytesIO()
    temp = environment.get_template(TEMPLATE_DIR)
    rendered = temp.render(input_dict)
    # convert HTML to PDF
    pisa_status = pisa.CreatePDF(
        rendered,                # the HTML to convert
        dest=output)           # ByteIo handle to recieve result

    if pisa_status.err:
        raise Exception('cannot create pdf')
    # return bytes of pdf file
    return output.getvalue()


def export_pdf(campaign: Campaign):
    get_result_event_by_campaign(
        campaign_id=campaign.id, org_id=campaign.org_id)
