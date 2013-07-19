import mandrill


MANDRILL_API_KEY = "eW9iPysJRI-LBinyq_D_Hg"
FROM_EMAIL = "hello@appmoment.fr"
FROM_NAME = "Moment"

class Mail:


    def __init__(self):
        self.man = mandrill.Mandrill(MANDRILL_API_KEY)


    def send_template(self, subject, template_name, template_args, to_dests, global_vars = []):



        msg = {
            'from_email' : FROM_EMAIL,
            'from_name' : FROM_NAME,
            'subject' : subject,
            'to' : to_dests,
            'preserve_recipients' : False,
            'global_merge_vars' : global_vars
        }


        reponse = self.man.messages.send_template(template_name, template_args, msg)

        print reponse


    def send_template_with_from_name(self, subject, from_name, template_name, template_args, to_dests, global_vars = []):



        msg = {
            'from_email' : FROM_EMAIL,
            'from_name' : from_name,
            'subject' : subject,
            'to' : to_dests,
            'preserve_recipients' : False,
            'global_merge_vars' : global_vars
        }


        reponse = self.man.messages.send_template(template_name, template_args, msg)

        print reponse