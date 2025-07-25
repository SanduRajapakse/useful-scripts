import os
from datetime import datetime, timedelta
import pdfkit

# Constants
EMPLOYEE_NAME = "Himanshu Oberoi"
EMPLOYEE_ADDRESS = "C-489, 4th floor, Street no 11, Majlis park, Delhi 110033"
POSITION = "Senior Software Engineer"
COMPANY_NAME = "Cannect Inc."
COMPANY_ADDRESS = "81 Navy Wharf Court, Toronto, ON M5V 3S2, Canada"
COMPANY_PHONE = "(416) 766-9000"
PAY_METHOD = "Electronic Transfer"
ANNUAL_SALARY = 90000
PAY_PERIOD = 14  # Bi-weekly
PAY_PER_PERIOD = ANNUAL_SALARY / 26  # Bi-weekly salary
HOURS_WORKED = 80
VACATION_HOURS = 0.00  # Placeholder

# Generate pay dates (bi-weekly)
end_date = datetime(2025, 3, 20)
num_periods = 6  # Generate last 6 pay stubs
pay_dates = [end_date - timedelta(days=i * PAY_PERIOD) for i in range(num_periods)][::-1]

# Create paystubs directory
if not os.path.exists("paystubs"):
    os.makedirs("paystubs")

def generate_paystub(date, index, ytd_earnings):
    filename_html = f"paystubs/paystub_{date.strftime('%Y-%m-%d')}.html"
    filename_pdf = f"paystubs/paystub_{date.strftime('%Y-%m-%d')}.pdf"
    pay_period_start = (date - timedelta(days=13)).strftime('%m/%d/%Y')
    pay_period_end = date.strftime('%m/%d/%Y')

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Pay Stub - {date.strftime('%B %d, %Y')}</title>
        <style>
            body {{ font-family: 'Inter', sans-serif; background-color: #f9faff; color: #333; max-width: 800px; margin: 20px auto; padding: 20px; }}
            .container {{ background: #fff; padding: 20px; border-radius: 12px; box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1); }}
            h2 {{ text-align: center; font-size: 24px; color: #4a90e2; border-bottom: 3px solid #4a90e2; padding-bottom: 10px; }}
            table {{ width: 100%; border-collapse: collapse; background: #fff; }}
            th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background-color: #e3efff; color: #333; font-weight: 400; text-transform: uppercase; letter-spacing: 0.5px; }}
            .right {{ text-align: right; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>Statement of Earnings</h2>
            <table>
                <tr><th>Employer</th><th>Employee</th><th>Pay Details</th></tr>
                <tr>
                    <td><b>{COMPANY_NAME}</b><br>{COMPANY_ADDRESS}<br>Phone: {COMPANY_PHONE}</td>
                    <td><b>{EMPLOYEE_NAME}</b><br>{EMPLOYEE_ADDRESS}</td>
                    <td>
                        <b>Pay Period:</b> {pay_period_start} to {pay_period_end}<br>
                        <b>Pay Date:</b> {date.strftime('%m/%d/%Y')}<br>
                        <b>Pay Total:</b> ${PAY_PER_PERIOD:,.2f}<br>
                        <b>Paid By:</b> {PAY_METHOD}
                    </td>
                </tr>
            </table>
            <h3>Earnings</h3>
            <table>
                <tr><th>Description</th><th class="right">Amount</th><th class="right">Year to Date</th></tr>
                <tr><td>Gross Income</td><td class="right">${PAY_PER_PERIOD:,.2f}</td><td class="right">${ytd_earnings:,.2f}</td></tr>
                <tr><td>Regular Pay</td><td class="right">${PAY_PER_PERIOD:,.2f}</td><td class="right">${ytd_earnings:,.2f}</td></tr>
            </table>
            <h3>Additional Information</h3>
            <table>
                <tr><th>Regular Hours Worked</th><th class="right">{HOURS_WORKED:.2f}</th></tr>
                <tr><th>Available Vacation</th><th class="right">{VACATION_HOURS:.2f} hours</th></tr>
            </table>
        </div>
    </body>
    </html>
    """

    with open(filename_html, "w", encoding="utf-8") as file:
        file.write(html_content)

    # Convert HTML to PDF using wkhtmltopdf
    pdfkit.from_file(filename_html, filename_pdf)
    print(f"Generated: {filename_pdf}")

# Generate pay stubs
ytd_earnings = 0
for i, date in enumerate(pay_dates):
    ytd_earnings += PAY_PER_PERIOD
    generate_paystub(date, i, ytd_earnings)
