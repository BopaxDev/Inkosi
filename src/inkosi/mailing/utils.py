def html_generator(
    template_name: str,
    **kwargs,
) -> str | None:
    download_email_template(
        template_name,
    )

    template_source = get_email_template_source()
    if not path.exists(template_source):
        raise TemplateSourceNotFound

    template_loader = jinja2.FileSystemLoader(
        searchpath=get_email_template_source(),
    )
    template_env = jinja2.Environment(
        loader=template_loader,
    )
    template = template_env.get_template(
        template_name,
    )
    return template.render(
        **kwargs,
    )


def mail_sender(
    receiver: list[str] | str,
    subject: str,
    plainText,
    htmlText,
):
    if not isinstance(
        receiver,
        (
            str,
            list,
        ),
    ):
        raise MailSenderWrongParameters

    smtp_server = get_email_smtp_server()
    smtp_port = get_email_smtp_port()
    email_sender = get_email_sender()
    email_sender_full_name = get_email_sender_fullname()
    email_password = get_email_password()

    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = formataddr((email_sender_full_name, email_sender))

    if plainText is not None:
        message.attach(
            MIMEText(
                plainText,
                "plain",
            ),
        )
    elif htmlText is not None:
        message.attach(
            MIMEText(
                htmlText,
                "html",
            ),
        )
    else:
        raise MailSenderNoMIMETypeSpecified

    context = ssl.create_default_context()

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls(context=context)
        server.login(email_sender, email_password)

        if isinstance(receiver, str):
            if "To" in message:
                message.replace_header("To", receiver)
            else:
                message["To"] = receiver

            result = send(server, email_sender, receiver, message.as_string())
            if result.get("result", -2) == 0:
                INFO_LOG(
                    f"Email to {receiver} from {email_sender} correctly sent",
                    _LOG_SOURCE,
                )
        elif isinstance(receiver, list):
            for recipient in receiver:
                if "To" in message:
                    message.replace_header("To", recipient)
                else:
                    message["To"] = recipient

                result = send(
                    server,
                    email_sender,
                    recipient,
                    message.as_string(),
                )
                status_code = result.get("result", -2)
                match status_code:
                    case 0:
                        INFO_LOG(
                            f"Email to {recipient} from {email_sender} correctly sent",
                            _LOG_SOURCE,
                        )
                    case -1:
                        pass
                    case _:
                        ERROR_LOG(
                            "No status code has been returned from send() -"
                            f" Receiver: {recipient}",
                            _LOG_SOURCE,
                        )

                time.sleep(get_email_time_sleep())
    except Exception as error:
        raise UnableToSendEmail(error)
    else:
        server.quit()


def send(
    server: smtplib.SMTP,
    sender: str,
    receiver: str,
    message: str,
) -> dict:
    result = {}

    try:
        server.sendmail(
            sender,
            receiver,
            message,
        )
        result["result"] = 0
        result["detail"] = f"Email correctly sent to {receiver} from {sender}"

        INFO_LOG(
            f"Sent an E-mail Address to {receiver} from {sender}",
            _LOG_SOURCE,
            remote_log=True,
        )
    except Exception as error:
        result["result"] = -1
        result["detail"] = error

        ERROR_LOG(
            f"Unable to send e-mail to the address {receiver} from {message}: {error}",
            _LOG_SOURCE,
            remote_log=True,
        )

    return result
