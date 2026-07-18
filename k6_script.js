import http from "k6/http";

export const options = {
  vus: 100,
  duration: "60s",
};

// ------------------------------
// Multi-turn conversations
// Same session_id => Query Rewriter will trigger
// ------------------------------
const conversations = [
  {
    session_id: "R101",
    questions: [
      "What is the refund duration?",
      "Can it be extended?",
      "Who approves it?",
      "What documents are required?"
    ]
  },
  {
    session_id: "R102",
    questions: [
      "What is the password policy?",
      "Can I reuse my previous password?",
      "How often should it be changed?",
      "What happens if I forget it?"
    ]
  },
  {
    session_id: "R103",
    questions: [
      "What is Multi-Factor Authentication?",
      "Is it mandatory?",
      "Where should it be enabled?",
      "Can I disable it later?"
    ]
  },
  {
    session_id: "R104",
    questions: [
      "What is remote access policy?",
      "Who is allowed to access remotely?",
      "Can contractors use it?",
      "What VPN should be used?"
    ]
  },
  {
    session_id: "R105",
    questions: [
      "What is acceptable use policy?",
      "Can I use office laptop personally?",
      "Can I install my own software?",
      "What happens if I violate the policy?"
    ]
  },
  {
    session_id: "R106",
    questions: [
      "What are confidential documents?",
      "Can I share them externally?",
      "Who approves sharing?",
      "How should they be protected?"
    ]
  },
  {
    session_id: "R107",
    questions: [
      "What is the leave policy?",
      "How many casual leaves are allowed?",
      "Can unused leaves be carried forward?",
      "Who approves leave requests?"
    ]
  },
  {
    session_id: "R108",
    questions: [
      "What is the reimbursement policy?",
      "Which expenses are reimbursable?",
      "How do I submit bills?",
      "How long does reimbursement take?"
    ]
  },
  {
    session_id: "R109",
    questions: [
      "What is the travel policy?",
      "Who approves business travel?",
      "Can I book my own hotel?",
      "What expenses are covered?"
    ]
  },
  {
    session_id: "R110",
    questions: [
      "What is the resignation process?",
      "How much notice period is required?",
      "Can it be waived?",
      "When will I receive the final settlement?"
    ]
  }
];

export default function () {

  // Pick one conversation randomly
  const convo =
    conversations[Math.floor(Math.random() * conversations.length)];

  // Ask ALL questions sequentially using SAME session_id
  for (const question of convo.questions) {

    const payload = JSON.stringify({
      message: question,
      session_id: convo.session_id
    });

    http.post(
      "http://localhost:8001/chat",
      payload,
      {
        headers: {
          "Content-Type": "application/json"
        }
      }
    );
  }

}