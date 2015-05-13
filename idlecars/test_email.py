from django.core.mail import EmailMessage

msg = EmailMessage(
  subject="Shipped!",
  from_email="support@idlecars.com",
  to=["jeff@idlecars.com", "jeremy@idlecars.com"]
)
msg.template_name = 'single_cta'
msg.merge_vars = {
    'jeff@idlecars.com': {'FNAME': "McFly"},
    'jeremy@idlecars.com': {'FNAME': "Jeremy"},
}
msg.send()
