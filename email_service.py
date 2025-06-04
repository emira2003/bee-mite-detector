import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import datetime
import os
import sqlite3
import socket  # For timeout handling

class EmailService:
    def __init__(self):
        """Initialize the email service with SMTP settings"""
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        
        self.username = "ergimira22@gmail.com"
        self.password = "ugyoonebbuuuojdg"

        
        # Print debug info about credentials (without showing the actual values)
        print(f"Email service initialized. Username available: {'Yes' if self.username else 'No'}, "
              f"Password available: {'Yes' if self.password else 'No'}")
        
        # Hardcoded recipient email - CHANGE THIS TO YOUR EMAIL
        self.recipient = "ergimira25@gmail.com"
        
        # Timeout settings
        self.connect_timeout = 10  # seconds
        self.socket_timeout = 15  # seconds
        
    def send_session_summary(self, session_id, db_path):
        """Send a summary email for a specific session"""
        # Skip if credentials missing
        if not self.username or not self.password:
            print("Email not sent: Missing email credentials")
            print(f"Username available: {'Yes' if self.username else 'No'}, "
                  f"Password available: {'Yes' if self.password else 'No'}")
            return False
        
        # Print recipient for debugging
        print(f"Attempting to send email to: {self.recipient}")
        
        # Get session data
        session_data = self._get_session_data(session_id, db_path)
        if not session_data:
            print(f"Email not sent: Could not retrieve data for session {session_id}")
            return False
        
        # Format email content
        subject = f"Bee Colony Health Monitor - Session Summary #{session_id}"
        html_content = self._format_email_content(session_data)
        text_content = self._format_plain_text_content(session_data)
        
        # Send email
        try:
            print(f"Creating email message for session {session_id}...")
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.username
            msg['To'] = self.recipient
            
            # Attach parts
            part1 = MIMEText(text_content, 'plain')
            part2 = MIMEText(html_content, 'html')
            msg.attach(part1)
            msg.attach(part2)
            
            print(f"Connecting to SMTP server {self.smtp_server}:{self.smtp_port}...")
            
            # Set socket timeout
            socket.setdefaulttimeout(self.socket_timeout)
            
            # Connect to server and send
            server = smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=self.connect_timeout)
            server.set_debuglevel(1)  # Enable SMTP debugging
            
            print("Starting TLS...")
            server.starttls()
            
            print("Logging in...")
            server.login(self.username, self.password)
            
            print(f"Sending email from {self.username} to {self.recipient}...")
            server.sendmail(self.username, self.recipient, msg.as_string())
            
            print("Quitting SMTP server...")
            server.quit()
            
            print(f"Session summary email sent to {self.recipient}")
            return True
            
        except Exception as e:
            print(f"Failed to send email: {e}")
            print(f"Error type: {type(e).__name__}")
            # For certain errors, provide more specific debug info
            if isinstance(e, smtplib.SMTPAuthenticationError):
                print("Authentication failed. Check your username and password.")
            elif isinstance(e, socket.timeout):
                print(f"Connection timed out after {self.socket_timeout} seconds.")
            elif isinstance(e, ConnectionRefusedError):
                print(f"Connection refused. Check if the SMTP server is reachable.")
            return False
            
    def _get_session_data(self, session_id, db_path):
        """Retrieve session data from the database"""
        try:
            print(f"Retrieving session data for session {session_id} from {db_path}")
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get session info
            cursor.execute(
                'SELECT * FROM sessions WHERE session_id = ?',
                (session_id,)
            )
            session = cursor.fetchone()
            if not session:
                print(f"Session {session_id} not found in database")
                return None
                
            # Get metrics for this session
            cursor.execute(
                '''SELECT * FROM bee_metrics 
                WHERE session_id = ? 
                ORDER BY timestamp DESC''',
                (session_id,)
            )
            metrics = cursor.fetchall()
            print(f"Found {len(metrics)} metrics for session {session_id}")
            
            # Calculate summary statistics
            bee_counts = [m['unique_bee_count'] for m in metrics]
            varroa_counts = [m['unique_varroa_count'] for m in metrics]
            ratios = [m['infestation_ratio'] for m in metrics]
            
            # Calculate total unique bees and varroa for the entire session
            total_unique_bees = max(bee_counts) if bee_counts else 0
            total_unique_varroa = max(varroa_counts) if varroa_counts else 0
            
            # Calculate overall infestation ratio
            overall_ratio = total_unique_varroa / total_unique_bees if total_unique_bees > 0 else 0
            
            summary = {
                'session': dict(session),
                'metrics_count': len(metrics),
                # Keep traditional stats for backward compatibility
                'bee_stats': {
                    'max': max(bee_counts) if bee_counts else 0,
                    'min': min(bee_counts) if bee_counts else 0,
                    'avg': sum(bee_counts) / len(bee_counts) if bee_counts else 0
                },
                'varroa_stats': {
                    'max': max(varroa_counts) if varroa_counts else 0,
                    'min': min(varroa_counts) if varroa_counts else 0,
                    'avg': sum(varroa_counts) / len(varroa_counts) if varroa_counts else 0
                },
                'ratio_stats': {
                    'max': max(ratios) if ratios else 0,
                    'min': min(ratios) if ratios else 0,
                    'avg': sum(ratios) / len(ratios) if ratios else 0
                },
                # New simplified totals
                'total_unique_bees': total_unique_bees,
                'total_unique_varroa': total_unique_varroa,
                'overall_ratio': overall_ratio,
                'latest_metrics': [dict(m) for m in metrics[:10]]  # Include last 10 metrics
            }
            
            conn.close()
            return summary
            
        except Exception as e:
            print(f"Error retrieving session data: {e}")
            return None
    
    def _format_email_content(self, data):
        """Format the email content as HTML"""
        session = data['session']
        
        # Determine risk level based on overall infestation ratio
        overall_ratio = data['overall_ratio']
        if overall_ratio < 0.05:
            risk_level = "Low"
            risk_color = "#28a745"  # green
        elif overall_ratio < 0.10:
            risk_level = "Moderate"
            risk_color = "#ffc107"  # yellow
        elif overall_ratio < 0.15:
            risk_level = "High"
            risk_color = "#fd7e14"  # orange
        else:
            risk_level = "Critical"
            risk_color = "#dc3545"  # red
        
        # Format duration
        if session['end_time'] and session['start_time']:
            try:
                start = datetime.datetime.fromisoformat(session['start_time'])
                end = datetime.datetime.fromisoformat(session['end_time'])
                duration = end - start
                duration_str = str(duration).split('.')[0]  # Remove microseconds
            except ValueError:
                duration_str = "Unknown"
        else:
            duration_str = "Session not completed"
        
        # Create HTML content
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto; }}
                .header {{ background-color: #f8f9fa; padding: 20px; border-bottom: 4px solid #ffc107; margin-bottom: 20px; }}
                h1, h2, h3 {{ margin-top: 0; }}
                h1 {{ color: #212529; }}
                h2 {{ color: #495057; border-bottom: 1px solid #e9ecef; padding-bottom: 10px; margin-top: 30px; }}
                .summary-box {{ background-color: #f8f9fb; border-left: 4px solid {risk_color}; padding: 15px; margin-bottom: 20px; }}
                .summary-box h3 {{ margin-top: 0; color: {risk_color}; }}
                table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
                th, td {{ text-align: left; padding: 12px; }}
                th {{ background-color: #f8f9fa; }}
                tr:nth-child(even) {{ background-color: #f8f9fb; }}
                .risk-badge {{ display: inline-block; padding: 5px 10px; background-color: {risk_color}; color: white; border-radius: 4px; font-weight: bold; }}
                .footer {{ margin-top: 30px; padding-top: 15px; border-top: 1px solid #e9ecef; font-size: 0.9em; color: #6c757d; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🐝 Bee Colony Health Monitor</h1>
                <p>Session Summary Report</p>
            </div>
            
            <div class="summary-box">
                <h3>Session Overview</h3>
                <p>
                    <strong>Session ID:</strong> {session['session_id']}<br>
                    <strong>Source:</strong> {session['source']}<br>
                    <strong>Started:</strong> {session['start_time']}<br>
                    <strong>Ended:</strong> {session['end_time'] or 'Not completed'}<br>
                    <strong>Duration:</strong> {duration_str}<br>
                    <strong>Colony Health Status:</strong> <span class="risk-badge">{risk_level} Risk</span>
                </p>
            </div>
            
            <h2>Detection Summary</h2>
            <table>
                <tr>
                    <th>Metric</th>
                    <th>Value</th>
                </tr>
                <tr>
                    <td><strong>Total Bees Detected</strong></td>
                    <td>{data['total_unique_bees']}</td>
                </tr>
                <tr>
                    <td><strong>Total Varroa Mites Detected</strong></td>
                    <td>{data['total_unique_varroa']}</td>
                </tr>
                <tr>
                    <td><strong>Overall Infestation Ratio</strong></td>
                    <td>{data['overall_ratio']:.3f}</td>
                </tr>
            </table>
            
            <h2>Recent Metrics</h2>
            <table>
                <tr>
                    <th>Timestamp</th>
                    <th>Bees</th>
                    <th>Varroa</th>
                    <th>Ratio</th>
                </tr>
                """
        
        # Add the latest metrics to the table
        for metric in data['latest_metrics']:
            html += f"""
                <tr>
                    <td>{metric['timestamp']}</td>
                    <td>{metric['unique_bee_count']}</td>
                    <td>{metric['unique_varroa_count']}</td>
                    <td>{metric['infestation_ratio']:.3f}</td>
                </tr>
            """
            
        html += f"""
            </table>
            
            <div class="footer">
                <p>This is an automated report from the Bee Colony Health Monitor system. Total metrics collected: {data['metrics_count']}</p>
                <p>Notes: {session['notes'] or 'None'}</p>
            </div>
        </body>
        </html>
        """
        
        return html
        
    def _format_plain_text_content(self, data):
        """Format the email content as plain text"""
        session = data['session']
        
        # Determine risk level based on overall infestation ratio
        overall_ratio = data['overall_ratio']
        if overall_ratio < 0.05:
            risk_level = "Low"
        elif overall_ratio < 0.10:
            risk_level = "Moderate"
        elif overall_ratio < 0.15:
            risk_level = "High"
        else:
            risk_level = "Critical"
        
        # Format duration
        if session['end_time'] and session['start_time']:
            try:
                start = datetime.datetime.fromisoformat(session['start_time'])
                end = datetime.datetime.fromisoformat(session['end_time'])
                duration = end - start
                duration_str = str(duration).split('.')[0]  # Remove microseconds
            except ValueError:
                duration_str = "Unknown"
        else:
            duration_str = "Session not completed"
        
        # Create plain text content
        text = f"""
BEE COLONY HEALTH MONITOR
Session Summary Report

SESSION OVERVIEW
-----------------------
Session ID: {session['session_id']}
Source: {session['source']}
Started: {session['start_time']}
Ended: {session['end_time'] or 'Not completed'}
Duration: {duration_str}
Colony Health Status: {risk_level} Risk

DETECTION SUMMARY
-----------------------
Total Bees Detected: {data['total_unique_bees']}
Total Varroa Mites Detected: {data['total_unique_varroa']}
Overall Infestation Ratio: {data['overall_ratio']:.3f}

RECENT METRICS
-----------------------
"""
        
        # Add latest metrics
        for metric in data['latest_metrics']:
            text += f"  {metric['timestamp']} - Bees: {metric['unique_bee_count']}, Varroa: {metric['unique_varroa_count']}, Ratio: {metric['infestation_ratio']:.3f}\n"
        
        text += f"""
-----------------------
This is an automated report from the Bee Colony Health Monitor system.
Total metrics collected: {data['metrics_count']}
Notes: {session['notes'] or 'None'}
"""
        
        return text