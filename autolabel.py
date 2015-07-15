"""
gmail-auto-label start

automatically generates labels for use in gmail,
based on either sender address, or recipient address (use with catch all addresses)

@category   Utility
@version    $ID: 1.1.1, 2015-07-01 17:00:00 CST $;
@author     KMR
@licence    GNU GPL v.3
"""
import re
import os
import yaml
import logit
import gmailconnector

class autolabel:
    log = None

    def __init__(self):
        DIR = os.path.dirname(os.path.realpath(__file__))
        self.conf = yaml.safe_load(open("{}/autolabel.cfg".format(DIR)))
        self.log = logit.logit(self.conf)
        self.log.info('autolabel initialised')

    def run(self):
        self.log.info('autolabel::run called')
        con = gmailconnector.gmailconnector()

        labels = {}

        for label in con.get_labels():
            labels[label['name']] = label['id']

        if not labels:
            resp = 'No labels found.'
            self.log.warn(resp)
        else:
            self.log.info('{0} labels found.'.format(len(labels)))

            messages = con.get_inbox_messages()

            if not messages:
                resp = 'No messages found.'
                self.log.warn(resp)
            else:
                msg = 0
                bad = 0
                for message in messages:
                    try:
                        address = con.get_address(message['id'])
                        radd = re.search(r'(?<=<)(.+)(?=>)', address)
                        if radd:
                            address = radd.group(0)

                        label = re.sub(r'\.', '/', re.search(r'(.+)(?=@)', address).group(0))
                        if label not in labels:
                            print label
                            try:
                                con.add_label(label)
                                labels.append(label)
                            except:
                                bad += 1
                                pass

                        con.move_msg_to_label(message['id'], labels[label])
                        msg += 1
                    except:
                        bad += 1
                resp = "{0} of {2} messages processed; {1} errors;".format(msg, bad, len(messages))
                self.log.info(resp)


        self.log.info("run complete")
        return resp


