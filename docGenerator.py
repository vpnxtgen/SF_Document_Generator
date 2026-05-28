from SfDocumentBuilder  import SalesforceTopicGenerator as SfDocBuilder
from flask import Flask, render_template, request


class DocGenerator:
    
    def executeDoc(self, topic, StoragePath):
        
        try:
            if topic:
                sf = SfDocBuilder('Salesforce_Notes.docx') 
                sf.processTopic(topic)
            else :
                raise ValueError("StoragePath and topic are required to generate the document.")
        
        except Exception as e:
            print(f"Error executing document generation: {e}")
            

app = Flask(__name__)
dg = DocGenerator()


@app.route('/')
def index():
    return render_template('SfDocGenerator.html')

@app.route('/generate-sf-doc', methods=['POST'])
def run_script():
    topic = request.form.get('topic')
    storage_path = request.form.get('storagePath')
    promptType = request.form.get('promptType')    
    
    print(f"Received topic: {topic}, storage_path: {storage_path}")
    
    promptBox = request.form.get('prompt_content')
    
    print(f"Received prompt Box: {promptBox}")
    
    websiteContent = request.form.get('website_content')
    urlInput =  request.form.get('website_urls')
    
    print(f"Received prompt Box: {websiteContent}, urlInput: {urlInput}")
    
    if promptType == 'UploadPrompt' and  not topic :
        return "Topic and Storage Path are required.", 400
    elif promptType == 'WebsiteReference' and not promptBox :
        return "Prompt Box  is requried.", 400
    elif promptType == 'SalesforceTopic' and (websiteContent and urlInput):
        return "Website Content and URL Input is requried.",400
    else:
        print(f'selected option:{topic}, promptBox option: {promptBox}, websiteContent option {websiteContent}')
    
    try:
        dg.executeDoc(topic, storage_path)
        return "Document generation initiated successfully."
    except Exception as e:
        return f"Error initiating document generation: {e}", 500
    
if __name__ == '__main__':
    app.run(debug=True)