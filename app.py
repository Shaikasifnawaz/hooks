from flask import Flask, request, make_response
import requests
import logging

app = Flask(__name__)
app.config['VERIFY_TOKEN'] = '5qP_HAuWf2NCqxcxD6zO4ahisNsuK4XMxh7011EoZ3M'
app.config['PAGE_ID'] = '416684941525815'  # Your Page ID
app.config['PAGE_ACCESS_TOKEN'] = 'EAAV8OmoO8TEBO4xblaP6pQY0xj3H6asNKgn6hXTs6dZAF3WLBaubHCQmoBAWPFaqcFDXpBvoIG6FHJ0oYdEumC9X7xVXZAhzA2ggoM0i43osqks8f2WZAj4jBmCV2s9wvLvnZB4gqEHwRs0KFKeSlX2ZASoZAMjSOZBilIEPwfBErJs9GXCb24AsePvbxOS7tVWBDHt7LrtaHHSwYBMkU7ZBhH0ZA1Ls2RzAKKQZDZD'  # Your Page Access Token

logging.basicConfig(level=logging.INFO)

@app.route('/webhook/messaging-webhook', methods=['GET', 'POST'])
def messagingWebhook():
    if request.method == 'GET':
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')

        if mode and token:
            if mode == 'subscribe' and token == app.config['VERIFY_TOKEN']:
                logging.info(f'Verification successful. Challenge: {challenge}')
                return make_response(challenge, 200)
            else:
                logging.warning('Verification failed: Invalid token')
                return make_response('Invalid verification token', 403)
        else:
            logging.warning('Verification failed: Missing parameters')
            return make_response('Missing parameters', 400)

    if request.method == 'POST':
        body = request.get_json()
        if not body:
            logging.error('Request body is empty or not valid JSON')
            return make_response('Invalid JSON', 400)

        entry = body.get('entry', [])
        if body.get('object') != 'instagram':
            logging.warning('Invalid object type')
            return make_response('Invalid object type', 404)

        try:
            for output in entry:
                messaging_events = output.get('messaging', [])
                for messaging_event in messaging_events:
                    sender_id = messaging_event.get('sender', {}).get('id')
                    message_text = messaging_event.get('message', {}).get('text')

                    if sender_id and message_text:
                        response = "this is a response"
                        sendCustomerAMessage(app.config['PAGE_ID'], response, app.config['PAGE_ACCESS_TOKEN'], sender_id)
                    else:
                        logging.warning('Missing sender ID or message text')
            
            logging.info('Event received and processed')
            return make_response('EVENT_RECEIVED', 200)
        except Exception as e:
            logging.error(f'Error processing request: {e}')
            return make_response('Internal Server Error', 500)

def sendCustomerAMessage(page_id, response, page_token, psid):
    new_response = response.replace("'", r"\'")
    url = f"https://graph.facebook.com/v14.0/{page_id}/messages"
    payload = {
        'recipient': {'id': psid},
        'message': {'text': new_response},
        'messaging_type': 'RESPONSE',
        'access_token': page_token
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        logging.info(f'Message sent to {psid}: {response.json()}')
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f'Error sending message: {e}')
        return None

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)
