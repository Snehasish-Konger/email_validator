from flask import Flask, request, jsonify
import re
import dns.resolver
import smtplib
import socket

app = Flask(__name__)

def is_valid_email_syntax(email):
    """Check if the email has a valid syntax."""
    regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(regex, email) is not None

def has_mx_record(domain):
    """Check if the domain has an MX record."""
    try:
        mx_records = dns.resolver.resolve(domain, 'MX')
        return len(mx_records) > 0, mx_records[0].exchange.to_text()
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.Timeout, socket.error) as e:
        print(f"DNS lookup error for domain {domain}: {e}")
        return False, str(e)

def verify_email_smtp(email, mx_record):
    """Check if the email address is deliverable via SMTP."""
    try:
        # Establish an SMTP connection
        server = smtplib.SMTP(mx_record, timeout=10)
        server.set_debuglevel(0)  # Set to 1 for detailed SMTP messages if needed
        server.connect(mx_record)
        server.helo()  # Introduce ourselves
        server.mail('noreply@yourdomain.com')  # Use a valid domain for this interaction

        # Perform the recipient check
        code, message = server.rcpt(email)
        server.quit()
        
        # Consider 250 and 251 codes as successful responses
        if code in [250, 251]:
            return "deliverable", "Mailbox exists and is deliverable"
        else:
            return "undeliverable", f"SMTP response code: {code}, message: {message}"

    except (smtplib.SMTPConnectError, smtplib.SMTPServerDisconnected, smtplib.SMTPResponseException, socket.error) as e:
        print(f"SMTP verification error for {email}: {e}")
        return "error", str(e)

@app.route('/verify-email', methods=['POST'])
def verify_email():
    """Endpoint to verify an email address."""
    data = request.json
    email = data.get('email')
    response = {
        'email': email,
        'status': 'undeliverable',
        'details': {
            'syntax_valid': False,
            'mx_record_found': False,
            'mx_record': None,
            'smtp_status': None,
            'smtp_message': None,
        }
    }

    # Check if email is provided
    if not email:
        response['message'] = 'Email is required'
        return jsonify(response), 400

    # Step 1: Syntax validation
    response['details']['syntax_valid'] = is_valid_email_syntax(email)
    if not response['details']['syntax_valid']:
        response['message'] = 'Invalid email syntax'
        return jsonify(response)

    # Step 2: Domain/MX record check
    domain = email.split('@')[-1]
    mx_record_found, mx_record = has_mx_record(domain)
    response['details']['mx_record_found'] = mx_record_found
    response['details']['mx_record'] = mx_record

    if not mx_record_found:
        response['message'] = 'Domain does not have an MX record'
        return jsonify(response)

    # Step 3: SMTP verification
    smtp_status, smtp_message = verify_email_smtp(email, mx_record)
    response['details']['smtp_status'] = smtp_status
    response['details']['smtp_message'] = smtp_message

    # Set final status based on the SMTP check
    if smtp_status == "deliverable":
        response['status'] = 'valid'
        response['message'] = 'Email is valid and deliverable'
    elif smtp_status == "undeliverable":
        response['status'] = 'undeliverable'
        response['message'] = 'Mailbox does not exist or cannot be verified'
    else:
        response['status'] = 'error'
        response['message'] = 'An error occurred during SMTP verification'

    return jsonify(response)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
