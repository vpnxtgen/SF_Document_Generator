from AIClient import AIClient as aiprocessor
from docx import Document
from docx.shared import Pt
import os


class SalesforceTopicGenerator:
    def __init__(self, fileName = 'Salesforce_Notes.docx'):
        print('Initializing SalesforceTopicGenerator')
        self.fileName = fileName
    
    def prompt(self, topic):
        print('Inside the prompt function')
        
        return f"""
                    Generate a comprehensive Salesforce technical guide for the topic: "{topic}".

                    The guide must be structured for both beginners and experts. 
                    Include: Key Concepts, Best Practices, Limitations, and a Code/Scenario Example.
                """
    
    
    def processTopic(self, topic):
        
        AIClient = aiprocessor('GEMENI_API_KEY')
        prompt = self.prompt(topic)
        print('Generated Prompt: ', prompt)
        
        try:
            response = AIClient.gemeniAiConnect(
                prompt=prompt
            )
            print('Gemini Response: ', response)
            
            if response:
                self.appendToSpecficPath(response)
        
        except Exception as e:
            print(f"Error processing topic '{topic}': {e}")
            
    
    def generateDocument(self,json_response, doc):
        
        if json_response is None:
            print("No response to generate document.")
            return
        
        try:
              if not doc:
                    print("Document object is not initialized.")
                    return
              
              # Add the topic as the title
              topic_para = doc.add_paragraph()
              topic_para.style = 'Title'
              topic_run = topic_para.add_run(json_response['topic'])
              topic_run.bold = True
              topic_run.font.size = Pt(18)
              
              # Add the summary
              doc.add_heading('Summary', level=1)
              summary_para = doc.add_paragraph(json_response['summary'], style='List Bullet')
              
              # Add sections
              for section in json_response['sections']:
                  doc.add_heading(section['heading'], level=2)
                  doc.add_paragraph(section['content'], style='List Bullet')
              
              # 4. Add Best Practices as a Bullet List
              doc.add_heading('Best Practices', level=3)
              for practice in json_response['best_practices']:
                  doc.add_paragraph(practice, style='List Bullet')
                  
              # 5. Add Limitations as a Bullet List               
              doc.add_heading('Limitations', level=3)
              for limitation in json_response['limitations']:
                  doc.add_paragraph(limitation, style='List Bullet')  
                  
              # 6. Add Example
              doc.add_heading('Example', level=4)
              
              doc.save(self.fileName)
              
              return 'Document generated successfully.'
            
    
        
        except Exception as e:
            print(f"Error loading document template: {e}")
            return
        
    def appendToSpecficPath(self, json_response):
        try:
            folder_path = r'D:/SF_Interview_Hub'
            
            if self.fileName:
                full_path = os.path.join(folder_path, self.fileName)
                
                #Check if the file exists before trying to append
                if not os.path.exists(folder_path):
                    os.makedirs(folder_path)
                
                # If the file doesn't exist, create a new one
                if os.path.isfile(full_path):
                    print(f"File '{full_path}' already exists. Appending to it.")
                    
                    doc = Document(full_path)
                    doc.add_paragraph("\n" + "="*30 + "\n") # Visual separator
                
                else :
                    print(f"File '{full_path}' does not exist. Creating a new document.")
                    doc = Document()
                    
                self.generateDocument(json_response,doc)  # Pass the actual response here
                    
                
            
            
        except Exception as e:
            print(f"Error appending to document: {e}")


          
sf = SalesforceTopicGenerator('Salesforce_Notes.docx') 
sf.processTopic("What is Salesforce and its key features?")