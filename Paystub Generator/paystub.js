const puppeteer = require("puppeteer");
const fs = require("fs");
const path = require("path");

// Contractor and company details
const EMPLOYEE_NAME = "Himanshu Oberoi";
const EMPLOYEE_ADDRESS = "C-489, 4th floor, Street no 11, Majlis park, Delhi 110033";
const POSITION = "Senior Software Engineer";
const COMPANY_NAME = "Cannect Inc.";
const COMPANY_ADDRESS = "81 Navy Wharf Court, Toronto, ON M5V 3S2, Canada";
const COMPANY_PHONE = "(416) 766-9000";
const PAY_METHOD = "Electronic Transfer";
const COMPANY_LOGO = "https://oscar-campaigns-uploads.s3.amazonaws.com/f1d26833-f783-4e6c-97c8-5be1e73195bc/Screenshot 2025-03-20 at 3.23.48 PM.png";
const ANNUAL_SALARY = 90000;
const PAY_PER_PERIOD = ANNUAL_SALARY / 26; // Bi-weekly pay
const PAY_PERIOD_DAYS = 14;
const OUTPUT_FOLDER = "paystubs";

// Deductions (all set to 0 for contractor)
const DEDUCTIONS = [
    "Canada Pension Plan",
    "Employment Insurance",
    "Federal Tax",
    "Provincial Tax",
    "Second Additional CPP Contribution"
];

// Ensure output folder exists
if (!fs.existsSync(OUTPUT_FOLDER)) {
    fs.mkdirSync(OUTPUT_FOLDER);
}

// Format currency (e.g., USD/CAD formatting)
const formatCurrency = (amount) => {
    return `$${amount.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
};

// Format date as YYYY-MM-DD for filenames
const formatDateForFilename = (date) => {
    return date.toISOString().split("T")[0];
};

// Format date as MM/DD/YYYY for display
const formatDate = (date) => {
    return date.toLocaleDateString("en-US", { month: "2-digit", day: "2-digit", year: "numeric" });
};

// Helper function: Count workdays (Mon-Fri) between two dates (inclusive)
const countWorkdays = (start, end) => {
    let count = 0;
    let current = new Date(start);
    while (current <= end) {
        const day = current.getDay();
        // Monday (1) through Friday (5)
        if (day >= 1 && day <= 5) {
            count++;
        }
        current.setDate(current.getDate() + 1);
    }
    return count;
};

// Generate pay stubs from Oct 28, 2021 to end of April 2025
const generatePayStubs = async () => {
    const browser = await puppeteer.launch();

    const startDate = new Date("2021-10-28"); // First pay date (Thursday)
    const endDateCandidate = new Date("2025-04-30"); // End of April 2025

    // Determine the last Thursday on or before endDateCandidate
    let endDate = new Date(endDateCandidate);
    while(endDate.getDay() !== 4) { // In JS, Thursday is 4
        endDate.setDate(endDate.getDate() - 1);
    }

    let payDate = new Date(startDate);
    let payPeriods = [];

    // Track YTD for each calendar year
    let currentYear = payDate.getFullYear();
    let currentYearYTD = 0;

    while (payDate <= endDate) {
        // Reset YTD when crossing into a new calendar year.
        if (payDate.getFullYear() !== currentYear) {
            currentYear = payDate.getFullYear();
            currentYearYTD = 0;
        }

        // Calculate the pay period start date.
        // Subtract (PAY_PERIOD_DAYS - 1) so the period spans exactly 14 calendar days.
        let periodStartDate = new Date(payDate.getTime() - (PAY_PERIOD_DAYS - 1) * 24 * 60 * 60 * 1000);

        // Total workdays in the pay period (should normally be 10)
        let totalWorkDays = countWorkdays(periodStartDate, payDate);

        // For YTD calculation, count only the workdays from January 1 of current year
        let startOfYear = new Date(currentYear, 0, 1);
        let effectiveStart = periodStartDate < startOfYear ? startOfYear : periodStartDate;
        let workdaysInCurrentYear = countWorkdays(effectiveStart, payDate);

        // Fraction of this period's pay that belongs to the current year
        let fractionInYear = totalWorkDays > 0 ? workdaysInCurrentYear / totalWorkDays : 0;

        // Add only the portion of the current pay period that falls in the current year.
        currentYearYTD += fractionInYear * PAY_PER_PERIOD;

        payPeriods.push({
            payPeriodStart: formatDate(periodStartDate),
            payPeriodEnd: formatDate(payDate),
            payDate: formatDate(payDate),
            YTD: currentYearYTD,
        });

        // Move to the next pay date (exactly 14 days later)
        payDate.setDate(payDate.getDate() + PAY_PERIOD_DAYS);
    }

    for (let i = 0; i < payPeriods.length; i++) {
        let { payPeriodStart, payPeriodEnd, payDate, YTD } = payPeriods[i];
        let formattedFilenameDate = formatDateForFilename(new Date(payDate));

        const htmlContent = `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pay Stub - ${payDate}</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Open+Sans:wght@300;400;600&display=swap');
        body { font-family: 'Open Sans', sans-serif; margin: 20px auto; padding: 20px; max-width: 800px; background-color: #f9faff; color: #333; }
        .container { background: #fff; padding: 20px; border-radius: 12px; box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1); }
        .header { text-align: right; margin-bottom: 20px; }
        .logo { width: 200px; height: auto; margin-bottom: 10px; }
        h2 { text-align: left; font-size: 22px; font-weight: 400; border-bottom: 3px solid #4a90e2; padding-bottom: 10px; color: #4a90e2; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 10px; text-align: left; font-size: 14px; }
        th { background-color: #e3efff; color: #333; font-weight: 400; text-transform: uppercase; letter-spacing: 0.5px; }
        td { border-bottom: 1px solid #ddd; vertical-align: top; }
        .right { text-align: right; }
        .footer { text-align: center; font-size: small; margin-top: 40px; color: #666; }
        .page-number { text-align: right; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <img src="${COMPANY_LOGO}" alt="Company Logo" class="logo">
            <h2>Statement of Earnings</h2>
        </div>
        <table>
            <colgroup>
                <col style="width: 32.5%;">
                <col style="width: 32.5%;">
                <col style="width: 35%;">
            </colgroup>
            <tr>
                <th>Employer</th>
                <th>Employee</th>
                <th>Pay Details</th>
            </tr>
            <tr>
                <td><b>${COMPANY_NAME}</b><br>${COMPANY_ADDRESS}<br>Phone: ${COMPANY_PHONE}</td>
                <td><b>${EMPLOYEE_NAME}</b><br>${EMPLOYEE_ADDRESS}</td>
                <td>
                    <b>Pay Period:</b> &nbsp;&nbsp;&nbsp;&nbsp;<br>${payPeriodStart} to ${payPeriodEnd}<br>
                    <b>Pay Date:</b> ${payDate}<br>
                    <b>Pay Total:</b> ${formatCurrency(PAY_PER_PERIOD)}<br>
                    <b>Paid By:</b> ${PAY_METHOD}
                </td>
            </tr>
        </table>
        <h3>Earnings</h3>
        <table>
            <tr>
                <th>Description</th>
                <th class="right">Amount</th>
                <th class="right">Year to Date</th>
            </tr>
            <tr>
                <td>Gross Income</td>
                <td class="right">${formatCurrency(PAY_PER_PERIOD)}</td>
                <td class="right">${formatCurrency(YTD)}</td>
            </tr>
        </table>
        <h3>Deductions</h3>
        <table>
            ${DEDUCTIONS.map(deduction => `<tr><td>${deduction}</td><td class="right">$0.00</td><td class="right">$0.00</td></tr>`).join('')}
        </table>
        <h3>Net Income</h3>
        <table>
            <tr>
                <th>Net Income</th>
                <th class="right">${formatCurrency(PAY_PER_PERIOD)}</th>
            </tr>
        </table>
        <div class="footer">
            <div>For any inquiries related to this document, please contact th@cannect.ca</div>
            <div class="page-number">Page 1 of 1</div>
        </div>
    </div>
</body>
</html>
        `;

        const page = await browser.newPage();
        await page.setContent(htmlContent, { waitUntil: "load" });

        const pdfPath = path.join(OUTPUT_FOLDER, `paystub-${formattedFilenameDate}.pdf`);
        await page.pdf({ path: pdfPath, format: "letter", printBackground: true });

        console.log(`Generated: ${pdfPath}`);
        await page.close();
    }

    await browser.close();
};

generatePayStubs().catch(console.error);
