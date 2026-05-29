from SfDocumentBuilder import SalesforceTopicGenerator as SfDocBuilder
from flask import Flask, render_template, request, send_file
import os


class DocGenerator:

    def executeDoc(self, prompt_type, topic, website_content, website_urls, upload_content):
        try:
            # FIX 1: Condition only checked `topic`, but UploadPrompt and WebsiteReference
            #         don't use topic — each type needs its own required field check
            if prompt_type == 'SalesforceTopic' and not topic:
                raise ValueError("Topic is required for SalesforceTopic.")
            elif prompt_type == 'UploadPrompt' and not upload_content:
                raise ValueError("Upload content is required for UploadPrompt.")
            elif prompt_type == 'WebsiteReference' and not website_content and not website_urls:
                raise ValueError("Website content or URL is required for WebsiteReference.")

            sf = SfDocBuilder('Salesforce_Notes.docx')
            return sf.processTopic(prompt_type, topic, website_content, website_urls, upload_content)

        except Exception as e:
            print(f"Error executing document generation: {e}")
            raise  # FIX 2: Re-raise so the Flask route catches it and returns a 500 properly


app = Flask(__name__)
dg = DocGenerator()


@app.route('/')
def index():
    return render_template('SfDocGenerator.html')


@app.route('/generate-sf-doc', methods=['POST'])
def run_script():
    #'promptType' doesn't match HTML name="prompt_type" — was returning None
    prompt_type = request.form.get('prompt_type')       # was 'promptType'
    topic       = request.form.get('topic')
    storage_path = request.form.get('storage_path')     # was 'storagePath'

    # These are correct — match the HTML hidden field names
    upload_content  = request.form.get('prompt_content')
    website_content = request.form.get('website_content')
    website_urls    = request.form.get('website_urls')

    print(f"prompt_type: {prompt_type}")
    print(f"topic: {topic}, storage_path: {storage_path}")
    print(f"upload_content: {upload_content}")
    print(f"website_content: {website_content}, website_urls: {website_urls}")

    #Guard against missing prompt_type entirely
    if not prompt_type:
        return "Prompt type is required.", 400

    #WebsiteReference validation was INVERTED —
    #         `(websiteContent and urlInput)` returns 400 when values ARE present.
    #         Should return 400 when BOTH are missing.
    if prompt_type == 'SalesforceTopic' and not topic:
        return "Topic is required.", 400
    elif prompt_type == 'UploadPrompt' and not upload_content:
        return "Prompt content is required.", 400
    elif prompt_type == 'WebsiteReference' and not website_content and not website_urls:
        return "Website content or URL is required.", 400

    print(f"Generating doc — type: {prompt_type} | topic: {topic} | "
          f"upload_content: {upload_content} | website_content: {website_content} | "
          f"website_urls: {website_urls}")

    try:
        if prompt_type == 'SalesforceTopic':
            dg.executeDoc(prompt_type, topic, None, None, None)
        elif prompt_type == 'UploadPrompt':
            #Was passing None for topic — fine, but upload_content var name
            #         was 'promptBox' before; now consistent with the rest of the code
            dg.executeDoc(prompt_type, None, None, None, upload_content)
        elif prompt_type == 'WebsiteReference':
            dg.executeDoc(prompt_type, None, website_content, website_urls, None)
        else:
            return f"Unknown prompt type: '{prompt_type}'.", 400
        
        # ✅ Send the file back as a download
        file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output", "Salesforce_Notes.docx")
        return send_file(file_path, as_attachment=True, download_name="Salesforce_Notes.docx")

        return "Document generation initiated successfully.", 200

    except Exception as e:
        return f"Error initiating document generation: {e}", 500


if __name__ == '__main__':
    #Old : commented to run in the local
    #app.run(debug=True)
    
    #New : to run in server
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)