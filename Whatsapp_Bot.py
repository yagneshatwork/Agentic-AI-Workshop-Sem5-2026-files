from flask import Flask , request
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv
from langchain_groq import ChatGroq
load_dotenv()

app = Flask(__name__)

@app.route('/',methods=['GET'])
def test():
    return "Tested OK....THANK YOU"

llm = ChatGroq(model='openai/gpt-oss-120b', temperature=0)

@app.route('/webhook',methods=['POST'])
def webhook():
    incoming_msg = request.values.get('Body','').lower()

    output = llm.invoke(incoming_msg).content
    
    #output = incoming_msg[:2]+incoming_msg[-2:] #llm code
    resp = MessagingResponse()
    msg = resp.message()
    msg.body(output)
    return str(resp)

if __name__ == '__main__':
    app.run(port=4000)