from models import (get_campaign_result_by_id,
                    get_campaign_event_by_id)
import jinja2
from io import BytesIO
from xhtml2pdf import pisa
# import pandas as pd

environment = jinja2.Environment()

# Define Base Template
source_html = """
<html>
<head>
<style>

    @page {
        size: a4 portrait;
        @frame header_frame {           /* Static Frame */
            -pdf-frame-content: header_cover;
            left: 0pt; width: 595pt; top: 0pt; height: 70pt;
        }
        @frame content_frame {          /* Content Frame */
            left: 50pt; width: 512pt; top: 80pt; height: 682pt;
        }
        @frame footer_frame {           /* Another static Frame */
            -pdf-frame-content: footer_content;
            left: 0pt; width: 595pt; top: 772pt; height: 70pt;
        }
    }
    @page _event {
        size: a4 portrait;
        @frame header_frame {           /* Static Frame */
            -pdf-frame-content: header_event;
            left: 0pt; width: 595pt; top: 0pt; height: 70pt;
        }
        @frame content_frame {          /* Content Frame */
            left: 50pt; width: 512pt; top: 80pt; height: 682pt;
        }
        @frame footer_frame {           /* Another static Frame */
            -pdf-frame-content: footer_content;
            left: 0pt; width: 595pt; top: 772pt; height: 70pt;
        }
    }
    @page _detail {
        size: a4 portrait;
        @frame header_frame {           /* Static Frame */
            -pdf-frame-content: header_detail;
            left: 0pt; width: 595pt; top: 0pt; height: 70pt;
        }
        @frame content_frame {          /* Content Frame */
            left: 50pt; width: 512pt; top: 80pt; height: 682pt;
        }
        @frame footer_frame {           /* Another static Frame */
            -pdf-frame-content: footer_content;
            left: 0pt; width: 595pt; top: 772pt; height: 70pt;
        }
    }
    @page _stat {
        size: a4 portrait;
        @frame header_frame {           /* Static Frame */
            -pdf-frame-content: header_stat;
            left: 0pt; width: 595pt; top: 0pt; height: 70pt;
        }
        @frame content_frame {          /* Content Frame */
            left: 50pt; width: 512pt; top: 80pt; height: 682pt;
        }
        @frame footer_frame {           /* Another static Frame */
            -pdf-frame-content: footer_content;
            left: 0pt; width: 595pt; top: 772pt; height: 70pt;
        }
    }

    body{
        font-family:"Helvetica";
    }
    p{
        margin:0;
        font-size: 10pt;
    }
    h3{
        font-size: 12pt;
    }
</style>
</head>

<body>
    <!-- Content for Static Frame 'header_frame' -->
    <table  style="display: block; text-align:left; color:#ff5c00" id="header_cover">
        <tr style="height: 69pt">
            <td style="width:50pt"></td>
            <td style="color:#ff5c00;vertical-align:bottom; font-size:16pt"><h1><b>Executive Summary</b></h1></td>
        </tr>
        <tr style="height: 1pt">
            <td></td>
            <td><div style="clear: both; border-top: solid #ff5c00 1pt;">&nbsp;</div></td>
        </tr>
    </table>

    <table  style="display: block; text-align:left; color:#ff5c00" id="header_event">
        <tr style="height: 65pt">
            <td style="width:50pt"></td>
            <td style="color:#ff5c00;vertical-align:bottom; font-size:16pt"><h1><b>Summary of Events</b></h1></td>
        </tr>
        <tr style="height: 1pt">
            <td></td>
            <td><div style="clear: both; border-top: solid #ff5c00 1pt;">&nbsp;</div></td>
        </tr>
    </table>

    <table  style="display: block; text-align:left; color:#ff5c00" id="header_detail">
        <tr style="height: 65pt">
            <td style="width:50pt"></td>
            <td style="color:#ff5c00;vertical-align:bottom; font-size:16pt"><h1><b>Detailed Findings</b></h1></td>
        </tr>
        <tr style="height: 1pt">
            <td></td>
            <td><div style="clear: both; border-top: solid #ff5c00 1pt;">&nbsp;</div></td>
        </tr>
    </table>

    <table  style="display: block; text-align:left; color:#ff5c00" id="header_stat">
        <tr style="height: 65pt">
            <td style="width:50pt"></td>
            <td style="color:#ff5c00;vertical-align:bottom; font-size:16pt"><h1><b>Statistics</b></h1></td>
        </tr>
        <tr style="height: 1pt">
            <td></td>
            <td><div style="clear: both; border-top: solid #ff5c00 1pt;">&nbsp;</div></td>
        </tr>
    </table>

    <!-- Content for Static Frame 'footer_frame' -->
    <table  style="display: block; text-align:center" id="footer_content">
        <tr style="height: 70pt">
            <td style="background:#ff5c00; color:white;"><b>MeshPhish&copy; </b>Report - page <pdf:pagenumber> of <pdf:pagecount> </td>
        </tr>
    </table>

    <!-- HTML Content -->
    <br>
    <h3>Campaign Results For: {{campaign.name}}</h3>
    <p>Status: {{campaign.status}}</p>
    <p>Create: {{campaign.create_at}}</p>
    <p>Started: {{campaign.launch_date}}</p>
    <p>Completed: {{campaign.complete_date}}</p>
    <br>
    <h3>Campaign Details</h3>
    <p>From: {{envelop_sender}}</p>
    <p>Phish URL: {{base_url}}</p>
    <p>Redirect URL: {{re_url}}</p>
    <p>Attachment(s): None Used</p>
    <p>Captured Credentials: {{capture_cred}}</p>
    <p>Stored Passwords: {{capture_pass}}</p>
    <br> 
    <h3>High Level Results </h3>
    <p>Total Targets: {{targets}}</p>
    <br>
    <p>The following totals indicate how many targets participated in each event type: </p>
    <p>Individuals Who Opened Email: {{opened}}</p>
    <p>Individuals Who Clicked: {{clicked}}</p>
    <p>Individuals Who Submitted: {{submitted}}</p>
    <p>Individuals Who Reported: -</p>
    <br>

    <pdf:nextpage name="_event" />

    <br>
    <p>The following table summarizes who opened and clicked on emails sent in this campaign.</p>
    <br>

    <table  style="display: block; text-align:left; padding-left:2pt">
        <tr style="height: 40pt; vertical-align:center;  background-color:blue">
            <td style="width:20%;color:white;"><b>Email Address</b></td>
            <td style="width:13%;color:white;"><b>Open</b></td>
            <td style="width:13%;color:white;"><b>Click</b></td>
            <td style="width:13%;color:white;"><b>Submit</b></td>
            <td style="width:13%;color:white;"><b>Report</b></td>
            <td style="width:13%;color:white;"><b>OS</b></td>
            <td style="width:13%;color:white;"><b>Browser</b></td>
        </tr>
        {% for res in results %}
        <tr style="height: 40pt; vertical-align:center; background-color:{{loop.cycle('#efebe9','#c9c4c1')}}">
            <td style="width:20%;">{{res.email}}</td>
            <td style="width:13%;">{% if res.open %}Yes{% else %}No{% endif %}</td>
            <td style="width:13%;">{% if res.click %}Yes{% else %}No{% endif %}</td>
            <td style="width:13%;">{% if res.sunmit %}Yes{% else %}No{% endif %}</td>
            <td style="width:13%;">{% if res.report %}-{% else %}-{% endif %}</td>
            <td style="width:13%;">{% if res.os %}{{res.os}}{% else %}-{% endif %}</td>
            <td style="width:13%;">{% if res.browser %}{{res.browser}}{% else %}-{% endif %}</td>
        </tr>
        {% endfor %}
    </table>

    {% for target in details %}
    <pdf:nextpage name="_detail" />
    <h3>{{target.firstname}} {{target.lastname}}</h3>
    <p>Department: {{target.department}}</p>
    <p>Email: {{target.email}}</p>
    <p>Email send: {{target.send}}</p>

    {% if target.open %}
    <p>Email Previews</p>
    <table  style="display: block; text-align:left; padding-left:2pt">
        <tr style="height: 40pt; vertical-align:center;  background-color:blue">
            <td style="width:50%;color:white;"><b>Time</b></td>
            <td style="width:50%;color:white;"></td>
        </tr>
        <tr style="height: 40pt; vertical-align:center; background-color:#efebe9">
            <td style="width:50%;">{{target.open}}</td>
            <td style="width:50%;"></td>
        </tr>
    </table>
    {% endif %}

    {% if target.click %}
    <p>Email Link Clicked</p>
    <table  style="display: block; text-align:left; padding-left:2pt">
        <tr style="height: 40pt; vertical-align:center;  background-color:blue">
            <td style="width:20%;color:white;"><b>Time</b></td>
            <td style="width:20%;color:white;"><b>IP</b></td>
            <td style="width:20%;color:white;"><b>Location</b></td>
            <td style="width:20%;color:white;"><b>Browser</b></td>
            <td style="width:20%;color:white;"><b>Operating System</b></td>
        </tr>
        <tr style="height: 40pt; vertical-align:center; background-color:#efebe9">
            <td style="width:20%;">{{target.click}}</td>
            <td style="width:20%;">{{target.ip}}</td>
            <td style="width:20%;">{{target.location}}</td>
            <td style="width:20%;">{{target.browser}}</td>
            <td style="width:20%;">{{target.os}}</td>
        </tr>
    </table>
    {% endif %}

    {% if target.submit %}
    <p>Data Captured</p>
    <table  style="display: block; text-align:left; padding-left:2pt">
        <tr style="height: 40pt; vertical-align:center;  background-color:blue">
            <td style="width:16%;color:white;"><b>Time</b></td>
            <td style="width:16%;color:white;"><b>IP</b></td>
            <td style="width:16%;color:white;"><b>Location</b></td>
            <td style="width:16%;color:white;"><b>Browser</b></td>
            <td style="width:16%;color:white;"><b>Operating System</b></td>
            <td style="width:16%;color:white;"><b>Data Captured</b></td>
        </tr>
        <tr style="height: 40pt; vertical-align:center; background-color:#efebe9">
            <td style="width:16%;">{{target.click}}</td>
            <td style="width:16%;">{{target.ip}}</td>
            <td style="width:16%;">{{target.location}}</td>
            <td style="width:16%;">{{target.browser}}</td>
            <td style="width:16%;">{{target.os}}</td>
            <td style="width:16%;">{{target.payload}}</td>
        </tr>
    </table>
    {% endif %}
    {% endfor %}
    
    <pdf:nextpage name="_stat" />

    <h3>The following table shows the browsers seen:</h3>
    <table  style="display: block; text-align:left; padding-left:2pt">
        <tr style="height: 40pt; vertical-align:center;  background-color:blue">
            <td style="width:50%;color:white;"><b>Browser</b></td>
            <td style="width:50%;color:white;"><b>Seen</b></td>
        </tr>
        {% for browser in browers %}
        <tr style="height: 40pt; vertical-align:center; background-color:#efebe9">
            <td style="width:50%;">{{browser.name}}</td>
            <td style="width:50%;">{{browser.count}}</td>
        </tr>
        {% endfor %}
    </table>

    <br><br>

    <h3>The following table shows the operating systems seen:</h3>
    <table  style="display: block; text-align:left; padding-left:2pt">
        <tr style="height: 40pt; vertical-align:center;  background-color:blue">
            <td style="width:50%;color:white;"><b>Operating System</b></td>
            <td style="width:50%;color:white;"><b>Seen</b></td>
        </tr>
        {% for os in oses %}
        <tr style="height: 40pt; vertical-align:center; background-color:#efebe9">
            <td style="width:50%;">{{os.name}}</td>
            <td style="width:50%;">{{os.count}}</td>
        </tr>
        {% endfor %}
    </table>

    <br><br>

    <h3>The following table shows the IP addresses captured:</h3>
    <table  style="display: block; text-align:left; padding-left:2pt">
        <tr style="height: 40pt; vertical-align:center;  background-color:blue">
            <td style="width:50%;color:white;"><b>IP</b></td>
            <td style="width:50%;color:white;"><b>Seen</b></td>
        </tr>
        {% for ip in ips %}
        <tr style="height: 40pt; vertical-align:center; background-color:#efebe9">
            <td style="width:50%;">{{ip.name}}</td>
            <td style="width:50%;">{{ip.count}}</td>
        </tr>
        {% endfor %}
    </table>

</body>
</html>
"""

temp = environment.from_string(source_html)
input_dict = {'results': [{'email': 'a@b.c', 'open': True, 'click': True,
                                    'submit': False, 'report': False, 'os': 'windows', 'browser': 'chrome'},
                          {'email': 'a@b.c', 'open': True, 'click': True,
                           'submit': False, 'report': False, 'os': 'windows', 'browser': 'chrome'},
                          {'email': 'a@b.c', 'open': True, 'click': True,
                           'submit': False, 'report': False, 'os': 'windows', 'browser': 'chrome'},
                          {'email': 'a@b.c', 'open': True, 'click': True,
                           'submit': False, 'report': False, 'os': 'windows', 'browser': 'chrome'},
                          {'email': 'a@b.c', 'open': True, 'click': True,
                           'submit': False, 'report': False, 'os': 'windows', 'browser': 'chrome'},
                          {'email': 'a@b.c', 'open': True, 'click': True,
                           'submit': False, 'report': False, 'os': 'windows', 'browser': 'chrome'},
                          {'email': 'a@b.c', 'open': True, 'click': True,
                           'submit': False, 'report': False, 'os': 'windows', 'browser': 'chrome'},
                          {'email': 'a@b.c', 'open': True, 'click': True,
                           'submit': False, 'report': False, 'os': 'windows', 'browser': 'chrome'},
                          {'email': 'a@b.c', 'open': True, 'click': True,
                           'submit': False, 'report': False, 'os': 'windows', 'browser': 'chrome'},
                          {'email': 'a@b.c', 'open': True, 'click': True,
                           'submit': False, 'report': False, 'os': 'windows', 'browser': 'chrome'},
                          {'email': 'a@b.c', 'open': True, 'click': True,
                           'submit': False, 'report': False, 'os': 'windows', 'browser': 'chrome'},
                          {'email': 'a@b.c', 'open': True, 'click': True,
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
rendered = temp.render(input_dict)


def convert_html_to_pdf(source_html, output: BytesIO):
    temp.render(input_dict)
    # convert HTML to PDF
    pisa_status = pisa.CreatePDF(
        rendered,                # the HTML to convert
        dest=output)           # ByteIo handle to recieve result

    # return bytes of pdf file
    return output.getvalue()
