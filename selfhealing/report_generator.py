import os

from datetime import datetime

 

# Report directory setup

OUTPUT_DIR = "output"

if not os.path.exists(OUTPUT_DIR):

    os.makedirs(OUTPUT_DIR)

 

def generate_html_report(report_data):

    """

    Generate an HTML report based on the collected data

    """

    run_id = report_data['run_id']

    start_time = report_data['start_time']

    end_time = report_data['end_time']

    duration = report_data['duration']

    total_elements = report_data['total_elements']

    updated_elements = report_data['updated_elements']

    error_elements = report_data['error_elements']

    updates = report_data['updates']

    errors = report_data['errors']

   

    # Calculate success rate

    success_rate = ((total_elements - error_elements) / total_elements * 100) if total_elements > 0 else 0

   

    html = f"""<!DOCTYPE html>

<html lang="en">

<head>

    <meta charset="UTF-8">

    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <title>SelfHeal Report - {start_time}</title>

    <style>

        body {{

            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;

            margin: 0;

            padding: 20px;

            color: #333;

            background-color: #f5f5f5;

        }}

        .container {{

            max-width: 1200px;

            margin: 0 auto;

            background-color: #fff;

            padding: 25px;

            border-radius: 8px;

            box-shadow: 0 2px 10px rgba(0,0,0,0.1);

        }}

        h1, h2 {{

            color: #2c3e50;

        }}

        .header {{

            border-bottom: 2px solid #eee;

            padding-bottom: 15px;

            margin-bottom: 20px;

        }}

        .summary {{

            display: flex;

            flex-wrap: wrap;

            gap: 15px;

            margin-bottom: 30px;

        }}

        .summary-card {{

            flex: 1;

            min-width: 200px;

            padding: 15px;

            border-radius: 8px;

            box-shadow: 0 2px 5px rgba(0,0,0,0.05);

            text-align: center;

        }}

        .card-title {{

            font-size: 14px;

            font-weight: 600;

            margin-bottom: 5px;

            color: #7f8c8d;

        }}

        .card-value {{

            font-size: 24px;

            font-weight: 700;

        }}

        .status-success {{

            background-color: #d5f5e3;

            color: #27ae60;

        }}

        .status-warning {{

            background-color: #fef9e7;

            color: #f1c40f;

        }}

        .status-error {{

            background-color: #fdedec;

            color: #e74c3c;

        }}

        .status-info {{

            background-color: #ebf5fb;

            color: #3498db;

        }}

        table {{

            width: 100%;

            border-collapse: collapse;

            margin: 20px 0;

        }}

        th, td {{

            padding: 12px 15px;

            text-align: left;

            border-bottom: 1px solid #eee;

        }}

        th {{

            background-color: #f8f9fa;

            font-weight: 600;

        }}

        tr:hover {{

            background-color: #f9f9f9;

        }}

        .changed {{

            background-color: #e8f4fc;

        }}

        .error {{

            background-color: #fdedec;

        }}

        .badge {{

            display: inline-block;

            padding: 3px 10px;

            border-radius: 12px;

            font-size: 12px;

            font-weight: 600;

        }}

        .badge-success {{

            background-color: #d5f5e3;

            color: #27ae60;

        }}

        .badge-error {{

            background-color: #fdedec;

            color: #e74c3c;

        }}

        footer {{

            margin-top: 30px;

            text-align: center;

            color: #7f8c8d;

            font-size: 14px;

        }}

        .xpath-cell {{

            font-family: monospace;

            max-width: 350px;

            overflow-x: auto;

            padding: 5px;

            background: #f8f8f8;

            border-radius: 3px;

        }}

    </style>

</head>

<body>

    <div class="container">

        <div class="header">

            <h1>SelfHeal Execution Report</h1>

            <p>Automated XPath verification and correction</p>

        </div>

       

        <h2>Run Summary</h2>

        <div class="summary">

            <div class="summary-card status-info">

                <div class="card-title">Run ID</div>

                <div class="card-value">{run_id[:8]}</div>

            </div>

            <div class="summary-card status-info">

                <div class="card-title">Start Time</div>

                <div class="card-value">{start_time}</div>

            </div>

            <div class="summary-card status-info">

                <div class="card-title">End Time</div>

                <div class="card-value">{end_time}</div>

            </div>

            <div class="summary-card status-info">

                <div class="card-title">Duration</div>

                <div class="card-value">{duration}</div>

            </div>

            <div class="summary-card status-info">

                <div class="card-title">Elements Checked</div>

                <div class="card-value">{total_elements}</div>

            </div>

            <div class="summary-card {'status-success' if updated_elements == 0 else 'status-warning'}">

                <div class="card-title">Elements Updated</div>

                <div class="card-value">{updated_elements}</div>

            </div>

            <div class="summary-card {'status-success' if error_elements == 0 else 'status-error'}">

                <div class="card-title">Errors</div>

                <div class="card-value">{error_elements}</div>

            </div>

            <div class="summary-card {'status-success' if success_rate > 95 else ('status-warning' if success_rate > 80 else 'status-error')}">

                <div class="card-title">Success Rate</div>

                <div class="card-value">{success_rate:.1f}%</div>

            </div>

        </div>

       

        <h2>Element Results</h2>

        <table>

            <thead>

                <tr>

                    <th>Variable Name</th>

                    <th>Status</th>

                    <th>Original XPath</th>

                    <th>New XPath</th>

                </tr>

            </thead>

            <tbody>

    """

   

    # Add rows for updated elements

    for update in updates:

        html += f"""

                <tr class="changed">

                    <td>{update['Variable_Name']}</td>

                    <td><span class="badge badge-success">Updated</span></td>

                    <td class="xpath-cell">{update['Old_XPath']}</td>

                    <td class="xpath-cell">{update['New_XPath']}</td>

                </tr>"""

   

    # Add rows for error elements

    for error in errors:

        html += f"""

                <tr class="error">

                    <td>{error['Variable_Name']}</td>

                    <td><span class="badge badge-error">Error</span></td>

                    <td class="xpath-cell">{error.get('XPath', 'N/A')}</td>

                    <td>{error.get('Error', 'Unknown Error')}</td>

                </tr>"""

   

    # Add rows for unchanged elements

    for element in report_data['unchanged_elements']:

        html += f"""

                <tr>

                    <td>{element}</td>

                    <td><span class="badge badge-success">No Change</span></td>

                    <td class="xpath-cell" colspan="2">{report_data['xpath_map'].get(element, 'N/A')}</td>

                </tr>"""

   

    html += """

            </tbody>

        </table>

       

        <footer>

            <p>Generated automatically by SelfHeal - &copy; 2025</p>

        </footer>

    </div>

</body>

</html>

    """

   

    return html

 

def save_report(html_content, filename):

    """

    Save the HTML report to a file in the output directory

   

    Args:

        html_content (str): HTML content to save

        filename (str): Name of the report file

   

    Returns:

        str: Full path to the saved report

    """

    # Ensure output directory exists

    if not os.path.exists(OUTPUT_DIR):

        os.makedirs(OUTPUT_DIR)

   

    # Full path for the report

    report_path = os.path.join(OUTPUT_DIR, filename)

   

    # Write the HTML content to the file

    with open(report_path, 'w', encoding='utf-8') as f:

        f.write(html_content)

   

    return report_path