import http from 'k6/http';

export const options = {
    vus: 10,        // virtual users
    duration: '120s' // test duration
};

export default function () {

    const payload = JSON.stringify({
        message:
        "what is refund duration"
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