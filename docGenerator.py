from SfDocumentBuilder  import SalesforceTopicGenerator as SfDocBuilder
from flask import Flask, render_template, request


class DocGenerator:
    
    def executeDoc(self, topic, StoragePath):
        
        try:
            if topic:
                topic = SfDocBuilder('Salesforce_Notes.docx') 
                topic.processTopic(topic)
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
    
    print(f"Received topic: {topic}, storage_path: {storage_path}")
    
    
    if not topic :
        return "Topic and Storage Path are required.", 400
    
    try:
        dg.executeDoc(topic, storage_path)
        return "Document generation initiated successfully."
    except Exception as e:
        return f"Error initiating document generation: {e}", 500
    
if __name__ == '__main__':
    app.run(debug=True)