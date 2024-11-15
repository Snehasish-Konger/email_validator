This is a microservice to verifiy emails.

### How to Test Locally

1. **Install Dependencies**:
   - Make sure you have Python installed on your machine.
   - Install the required libraries using pip:
     ```bash
     pip install Flask dnspython
     ```

2. **Run the Application**:
   - Save the code to a file named `email_verification_service.py`.
   - In your terminal or command prompt, navigate to the directory containing the file.
   - Run the application using:
     ```bash
     python email_verification_service.py
     ```
   - The server will start on `http://localhost:5002`.

3. **Test the Service**:
   - You can use tools like `curl`, Postman, or your web browser to test the API.
   - Example `curl` command to test an email address:
     ```bash
     curl -X POST http://localhost:5002/verify-email -H "Content-Type: application/json" -d '{"email": "test@example.com"}'
     ```
   - Alternatively, you can use Postman to send a POST request to `http://localhost:5000/verify-email` with a JSON body containing the email:
     ```json
     {
       "email": "test@example.com"
     }
     ```

### Notes:
- **Replace `'test@example.com'`** in the `verify_email_smtp` function with your actual email address or a valid sender email to avoid rejection during the SMTP handshake.
- **Debugging**: You can set `server.set_debuglevel(1)` to see detailed SMTP communication logs for debugging.
- **Privacy and Security**: Be mindful that some mail servers may block SMTP verification attempts to protect user privacy.
- **DNS Lookups**: Ensure that your local network allows outbound DNS queries.

By running this code locally, you can test various email addresses to see if they pass syntax checks, MX record checks, and SMTP deliverability verification.
