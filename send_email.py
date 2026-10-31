import mailtrap

token="9b0725c6b6e37bcfbf1de3b137e96909"#auth app 


def email(to,subject,message):
    mail=mailtrap.Mail(
        sender=mailtrap.Address(email="hello@demomailtrap.co",name="FLASK_API"),
        to=[mailtrap.Address(email=to)],
        subject=subject,
        text=message,
        category="mailtrap integration test"
    )
    client = mailtrap.MailtrapClient(token=token)
    response= client.send(mail)

    print("this is mailtrap------------")
    print(response)


#email("agustinolarry07@gmail.com","Testing API","test one two one two")