from fastmcp import FastMCP

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
PROJECT_ROOT = Path(__file__).resolve().parent.parent


import json
import requests #requests is http library
from bs4 import BeautifulSoup
import sqlite3
import smtplib
import os
from email.mime.text import MIMEText
from dotenv import load_dotenv


load_dotenv()
mcp = FastMCP()

RAG_URL = "http://localhost:8000/rag"
DB_PATH = PROJECT_ROOT / "staff.db"
email_sent = False




# ============================================================
# External Patient Services RAG Tool
# ============================================================

@mcp.tool()
def external_patient_services_search(query:str)->str:
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


# ============================================================
# Staff Database Tool
# ============================================================

@mcp.tool()
def query_database(sql: str) -> str:
    """
    Query the hospital staff database for information about
    nurses, lab technicians, and doctors, including their
    departments, shifts, availability, rooms, experience,
    and leave status.
    """

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(sql)

    rows = cursor.fetchall()

    columns = [
        desc[0]
        for desc in cursor.description
    ]

    cursor.close()
    conn.close()

    if columns:
        results = [
            dict(zip(columns, row))
            for row in rows
        ]

        return json.dumps(
            results,
            indent=2
        )

    return json.dumps(
        rows,
        indent=2
    )



# ============================================================
# web search tool
# ============================================================
#explanations-7

@mcp.tool()
def web_search(query: str) -> str:
    """
    Query the outside web and for non related db information.
    """
   
    url = "https://html.duckduckgo.com/html/"

    response = requests.get(
        url,
        params={"q": query},
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=10
    )

    soup = BeautifulSoup(response.text, "html.parser")

    results = soup.select(".result__snippet")

    if results:
        return "\n".join(
            result.get_text(" ", strip=True)
            for result in results[:5]
        )

    return "No search results found"



#text cleaner tool
@mcp.tool()
def text_cleaner(text:str)->str:
    """
    validate and refine the output
    """
    return " ".join(text.split())


# ============================================================
# Appointment Booking Tool
# ============================================================

@mcp.tool()
def book_appointment(
    doctor: str,
    specialization: str,
    appointment_date: str,
    appointment_time: str
) -> str:

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    # --------------------------------------------------------
    # Check doctor availability
    # --------------------------------------------------------

    cursor.execute(
        """
        SELECT appointment_id
        FROM appointments
        WHERE doctor = ?
        AND appointment_date = ?
        AND appointment_time = ?
        AND status = 'booked'
        """,
        (
            doctor,
            appointment_date,
            appointment_time
        )
    )

    existing = cursor.fetchone()

    if existing:

        cursor.close()
        conn.close()

        return (
            "Appointment slot is already booked."
        )

    # --------------------------------------------------------
    # Book appointment
    # --------------------------------------------------------

    cursor.execute(
        """
        INSERT INTO appointments (
            doctor,
            specialization,
            appointment_date,
            appointment_time,
            status
        )
        VALUES (?, ?, ?, ?, 'booked')
        """,
        (
            doctor,
            specialization,
            appointment_date,
            appointment_time
        )
    )

    appointment_id = cursor.lastrowid

    conn.commit()

    cursor.close()
    conn.close()

    return (
        f"Appointment booked successfully. "
        f"Appointment ID: {appointment_id}. "
        f"Doctor: {doctor}. "
        f"Specialization: {specialization}. "
        f"Date: {appointment_date}. "
        f"Time: {appointment_time}."
    )


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


if __name__ == "__main__":
    mcp.run()
