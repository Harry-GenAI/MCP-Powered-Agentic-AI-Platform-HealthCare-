from fastmcp import FastMCP
from rag.rag import retrieve_context
import json
import requests
import sqlite3
import smtplib
import os
from email.mime.text import MIMEText
from dotenv import load_dotenv


load_dotenv()
mcp = FastMCP()

RAG_URL = "http://localhost:8000/rag"
DB_PATH = "employees.db"
email_sent = False



#internal knowledge rag tool
@mcp.tool()
def employee_knowledge_search(query:str)->str:
    """
    Search the company's internal employee knowledge base 
    such as HR, travel, and remote work policies.
    """
    context, _, _, _ = retrieve_context(query)

    return f"Context:{context}"



#external knowledge rag tool
@mcp.tool()
def customer_knowledge_search(query:str)->str:
    """
    Search the customer-facing knowledge base including 
    refund, purchase, warranty, and shipping policies.
    """
    try:
        response = requests.post(
        url=RAG_URL,
        json={"query":query},
        )

        data = response.json()

        context = data.get("context", "")
        sources = data.get("sources", "")

        if not context:
            return "No context found in company knowledge."
        
        return f"Context:{context}\n Sources:{sources}"
    
    except Exception as e:
        return f"search_documents error: {e}"


#sql db tool
@mcp.tool()
def query_database(sql:str)->str:
    """
    query the sql db of employees
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute(sql)
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    cursor.close()
    conn.close()

    if columns:
        results = [dict(zip(columns, row)) for row in rows]
        return json.dumps(results, indent=2)
    
    results = json.dumps(rows, indent=2)

    return results


#email send tool
@mcp.tool()
def send_email(to:str, subject:str, body:str)->str:
    """
    Send an email using gmail SMTP.
    
    Inputs:
    -to : receiver email
    -subject : mail subject
    -body : main content
    """

    global email_sent

    if email_sent:
        return "Email already sent once. Skipping duplicate send."

    try:
        #mail credentials
        sender_email=os.getenv("mail_username")
        app_password=os.getenv("app_password")
        
        #construct MIME email msg
        msg = MIMEText(body)
        msg["Subject"]=subject
        msg["To"]=to
        msg["From"]=sender_email
        
        #launch server, start, send mail, quit server
        server = smtplib.SMTP("smtp.gmail.com", 587) #(host , port)
        server.starttls()
        server.login(sender_email, app_password)
        server.send_message(msg)
        server.quit()

        email_sent = True
        return "Email sent successfully."
    
    except Exception as e:
        return f"Email failed:{e}"



#web search tool
@mcp.tool()
def web_search(query:str)->str:
    """
    perform a websearch using duckduckgo engine
    returns summarized content
    """
    
    try:
        url = "https://api.duckduckgo.com/"
        params = {
            "q":query,
            "format":"json"

        }
        
        results = requests.get(url, params=params)#refer explanation #1
        results = results.json()

        if results.get("Abstract"):
            return results["Abstract"]
        
        elif results.get("RelatedTopics"):
            topic_results = results.get("RelatedTopics", [])[:3]
            return  "\n".join([r.get("Text", "") for r in topic_results if "Text" in r])
        
        return "No related information found"
    
    except Exception as e:
        return f"error:{e}"


#text cleaner tool
@mcp.tool()
def text_cleaner(text:str)->str:
    """
    validate and refine the output
    """
    return " ".join(text.split())


if __name__ == "__main__":
    mcp.run()
