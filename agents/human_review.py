from crewai import Agent


def human_review_agent():

    return Agent(

        role="Human Review Agent",

        goal="""
        Protect sensitive company information.
        """,

        backstory="""
        Before allowing access to confidential employee
        information such as salary, joining date,
        notice period, phone number, email, manager details 
        or other sensitive records, require OTP approval.

        Only after successful verification should
        the SQL tool be executed.
        """,

        verbose=True
    )