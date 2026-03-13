"""
Notification Utility for DMMMSU-SLUC Disaster Monitoring System
Handles Email and SMS notifications
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import os

# Configuration - In production, these should be environment variables
SMTP_SERVER = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.environ.get('SMTP_PORT', '587'))
SMTP_USERNAME = os.environ.get('SMTP_USERNAME', '')
SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD', '')
FROM_EMAIL = os.environ.get('FROM_EMAIL', 'noreply@dmmmsu.edu.ph')

# SMS Gateway configuration (using email-to-SMS gateways)
# Format: phone_number@gateway.com
SMS_GATEWAYS = {
    'globe': '@globetel.com.ph',
    'smart': '@smart.com.ph',
    'tm': '@tmobile.net.ph',
    'tnt': '@tnt.net.ph',
}

ADMIN_EMAILS = ['admin@dmmmsu.edu.ph']  # List of admin emails for notifications


def send_email_notification(incident, status_update=False):
    """
    Send email notification for incident
    
    Args:
        incident: Incident model object
        status_update: Boolean indicating if this is a status update notification
    """
    # Skip if SMTP not configured
    if not SMTP_USERNAME or not SMTP_PASSWORD:
        print("SMTP not configured. Email notification skipped.")
        return False
    
    try:
        if status_update:
            subject = f"Status Update: Incident {incident.incident_id} - {incident.status}"
            message = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <h2 style="color: #1e40af;">Incident Status Update</h2>
                <p>The status of the following incident has been updated:</p>
                <table style="border-collapse: collapse; width: 100%; max-width: 600px;">
                    <tr>
                        <td style="padding: 8px; border: 1px solid #ddd; font-weight: bold;">Incident ID:</td>
                        <td style="padding: 8px; border: 1px solid #ddd;">{incident.incident_id}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border: 1px solid #ddd; font-weight: bold;">New Status:</td>
                        <td style="padding: 8px; border: 1px solid #ddd; color: {get_status_color(incident.status)};">{incident.status}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border: 1px solid #ddd; font-weight: bold;">Location:</td>
                        <td style="padding: 8px; border: 1px solid #ddd;">{incident.location}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border: 1px solid #ddd; font-weight: bold;">Date:</td>
                        <td style="padding: 8px; border: 1px solid #ddd;">{incident.date.strftime('%B %d, %Y')}</td>
                    </tr>
                </table>
                <p style="margin-top: 20px;">
                    <a href="#" style="background-color: #1e40af; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">View Incident</a>
                </p>
                <hr style="margin-top: 30px; border: none; border-top: 1px solid #ddd;">
                <p style="font-size: 12px; color: #666;">
                    This is an automated message from the DMMMSU-SLUC Disaster/Emergency Incident Report Monitoring System.<br>
                    Please do not reply to this email.
                </p>
            </body>
            </html>
            """
        else:
            subject = f"New Incident Reported: {incident.incident_id}"
            message = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <h2 style="color: #dc2626;">New Incident Reported</h2>
                <p>A new incident has been submitted and requires your attention.</p>
                <table style="border-collapse: collapse; width: 100%; max-width: 600px;">
                    <tr>
                        <td style="padding: 8px; border: 1px solid #ddd; font-weight: bold;">Incident ID:</td>
                        <td style="padding: 8px; border: 1px solid #ddd;">{incident.incident_id}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border: 1px solid #ddd; font-weight: bold;">Status:</td>
                        <td style="padding: 8px; border: 1px solid #ddd; color: #dc2626;">Pending</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border: 1px solid #ddd; font-weight: bold;">Location:</td>
                        <td style="padding: 8px; border: 1px solid #ddd;">{incident.location}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border: 1px solid #ddd; font-weight: bold;">Cause:</td>
                        <td style="padding: 8px; border: 1px solid #ddd;">{incident.cause}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border: 1px solid #ddd; font-weight: bold;">Date:</td>
                        <td style="padding: 8px; border: 1px solid #ddd;">{incident.date.strftime('%B %d, %Y')}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border: 1px solid #ddd; font-weight: bold;">Reported By:</td>
                        <td style="padding: 8px; border: 1px solid #ddd;">{incident.reporter.full_name if incident.reporter else 'N/A'}</td>
                    </tr>
                </table>
                <p style="margin-top: 20px;">
                    <a href="#" style="background-color: #dc2626; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Review Incident</a>
                </p>
                <hr style="margin-top: 30px; border: none; border-top: 1px solid #ddd;">
                <p style="font-size: 12px; color: #666;">
                    This is an automated message from the DMMMSU-SLUC Disaster/Emergency Incident Report Monitoring System.<br>
                    Please do not reply to this email.
                </p>
            </body>
            </html>
            """
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = FROM_EMAIL
        msg['To'] = ', '.join(ADMIN_EMAILS)
        
        # Attach HTML content
        msg.attach(MIMEText(message, 'html'))
        
        # Send email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.sendmail(FROM_EMAIL, ADMIN_EMAILS, msg.as_string())
        
        print(f"Email notification sent successfully for incident {incident.incident_id}")
        return True
        
    except Exception as e:
        print(f"Failed to send email notification: {str(e)}")
        return False


def send_sms_notification(incident):
    """
    Send SMS notification for incident
    Note: This uses email-to-SMS gateway which requires knowing the carrier
    
    Args:
        incident: Incident model object
    """
    # SMS notification is simulated in this implementation
    # In production, you would integrate with an SMS gateway API
    
    print(f"SMS notification simulated for incident {incident.incident_id}")
    print(f"Message: New incident reported - {incident.incident_id} at {incident.location}")
    
    # Example implementation with email-to-SMS gateway:
    # carrier_gateway = SMS_GATEWAYS.get('globe')
    # sms_email = f"09123456789{carrier_gateway}"
    # send_email(to=sms_email, subject="", body=f"New incident: {incident.incident_id}")
    
    return True


def get_status_color(status):
    """Get hex color code for status"""
    colors = {
        'Pending': '#dc2626',
        'In Progress': '#d97706',
        'Solved': '#059669'
    }
    return colors.get(status, '#6b7280')


def send_password_reset_email(user, reset_token):
    """
    Send password reset email
    
    Args:
        user: User model object
        reset_token: Password reset token
    """
    if not SMTP_USERNAME or not SMTP_PASSWORD:
        print("SMTP not configured. Password reset email skipped.")
        return False
    
    try:
        subject = "Password Reset Request - DMMMSU-SLUC Disaster Monitoring System"
        message = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <h2 style="color: #1e40af;">Password Reset Request</h2>
            <p>Hello {user.first_name},</p>
            <p>We received a request to reset your password for the DMMMSU-SLUC Disaster/Emergency Incident Report Monitoring System.</p>
            <p>Click the link below to reset your password:</p>
            <p style="margin: 20px 0;">
                <a href="#" style="background-color: #1e40af; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Reset Password</a>
            </p>
            <p>Or copy and paste this token: <code>{reset_token}</code></p>
            <p style="color: #666; font-size: 12px;">This link will expire in 1 hour.</p>
            <p>If you did not request this reset, please ignore this email.</p>
            <hr style="margin-top: 30px; border: none; border-top: 1px solid #ddd;">
            <p style="font-size: 12px; color: #666;">
                This is an automated message from the DMMMSU-SLUC Disaster/Emergency Incident Report Monitoring System.<br>
                Please do not reply to this email.
            </p>
        </body>
        </html>
        """
        
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = FROM_EMAIL
        msg['To'] = user.email
        
        msg.attach(MIMEText(message, 'html'))
        
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.sendmail(FROM_EMAIL, [user.email], msg.as_string())
        
        print(f"Password reset email sent to {user.email}")
        return True
        
    except Exception as e:
        print(f"Failed to send password reset email: {str(e)}")
        return False
