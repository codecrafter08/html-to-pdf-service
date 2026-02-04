import os
import boto3
import pdfkit
from flask import Flask, request, jsonify
from urllib.parse import urlparse
from botocore.exceptions import NoCredentialsError, ClientError

app = Flask(__name__)

# Configure AWS credentials and region
s3_client = boto3.client(
    's3',
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION")
)

# Set path to wkhtmltopdf
#PDFKIT_CONFIG = pdfkit.configuration(wkhtmltopdf='/usr/local/bin/wkhtmltopdf')
PDFKIT_CONFIG = pdfkit.configuration(wkhtmltopdf='/usr/bin/wkhtmltopdf')

def generate_presigned_url(bucket_name, object_key):
    """Generate a pre-signed URL for S3 object."""
    try:
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name, 'Key': object_key}
        )
        return url
    except ClientError as e:
        return None


@app.route('/convert-html-to-pdf', methods=['POST'])
def convert_html_to_pdf():
    try:
        data = request.json
        s3_uri = data.get("s3_uri")

        if not s3_uri:
            return jsonify({"error": "s3_uri is required"}), 400
        parsed_uri = urlparse(s3_uri)
        bucket_name = parsed_uri.netloc
        object_key = parsed_uri.path.lstrip('/')
        file_name = os.path.basename(object_key)

        # Download HTML file from S3
        html_local_path = f"/tmp/{file_name}"
        pdf_local_path = html_local_path.replace(".html", ".pdf")
        pdf_s3_key = object_key.replace(".html", ".pdf")

        s3_client.download_file(bucket_name, object_key, html_local_path)

        options = {
                "page-size": "A2",  # Ensure A2 page size
                "margin-top": "10mm",
                "margin-bottom": "10mm",
                "margin-left": "10mm",
                "margin-right": "10mm",
                "encoding": "UTF-8",
                "enable-local-file-access": None,  # Required for local CSS
            }

        # Convert HTML to PDF
        pdfkit.from_file(html_local_path, pdf_local_path, options=options, configuration=PDFKIT_CONFIG)

        # Upload PDF back to S
        s3_client.upload_file(pdf_local_path, bucket_name, pdf_s3_key, ExtraArgs={
            'ContentType': 'application/pdf',  # Ensure correct MIME type
            'ACL': 'public-read'  # Make the file publicly accessible
            })

        # Construct new S3 URI
        # pdf_s3_uri = f"s3://{bucket_name}/{pdf_s3_key}"
        # pdf_url = generate_presigned_url(bucket_name, pdf_s3_key)
        pdf_url = f"https://{bucket_name}.s3.amazonaws.com/{pdf_s3_key}"

        return jsonify({"pdf_s3_url": pdf_url})

    except NoCredentialsError:
              return jsonify({"error": "AWS credentials not found"}), 500
    except ClientError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
                                                  
                                      