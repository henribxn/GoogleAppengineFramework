import sys
sys.path.insert(0, 'lib')
from google.appengine.api import mail
from cloudstorage import open as gcs_open
from requests import post
from oauth2client.client import GoogleCredentials
from google.appengine.api import taskqueue
from googleapiclient.discovery import build
from secret import *


def start_compute_engine(instance_name):
    """
    Start a compute engine to process the data from the queue
    Args:
        instance_name: String, name of the instance
    """
    compute = build('compute', 'v1', credentials=GoogleCredentials.get_application_default())
    request = compute.instances().start(project=PROJECT_NAME, zone=PROJECT_ZONE, instance=instance_name)
    request.execute()


def add_msg_to_queue(json_message_to_queue):
    """
    Add a message to my pull queue
    Args:
        json_message_to_queue: Dict containing info to be sent to the worker
    Returns: Bool, True if it worked, False otherwise
    """
    queue_name = 'myqueue'
    q = taskqueue.Queue(queue_name)
    body = str(json_message_to_queue)
    try:
        q.add([taskqueue.Task(payload=body, method='PULL')])
        return True
    except:
        send_email(body="impossible to add message to GCS queue : " + queue_name)
        return False


def add_msg_to_sqs_amazon(json_message_to_queue):
    """
    Add a message to my Amazon queue
    Args:
        json_message_to_queue: Dict containing info to be sent to the worker
    Returns: Bool, True if it worked, False otherwise
    """
    url = AWS_QUEUE_URL
    url += "?Action=SendMessage&MessageBody="
    body = str(json_message_to_queue)
    url += body.replace(" ", "%20")
    try:
        post(url)
        return True
    except:
        send_email(body="impossible to add message to AWS queue    \n    " + url)
        return False


def save_file_to_bucket(file_name, content, bucket_folder_name):
    """
    Save a file to my google cloud bucket
    Args:
        file_name: String, name of the file
        content: Binary, file content
        bucket_folder_name: String, name of the folder
    Returns: String, URL of the created file if it worked, False otherwise
    """
    full_name = '/' + bucket_folder_name + '/' + file_name
    try:
        f = gcs_open(full_name, 'w')
        f.write(content)
        f.close()
        return full_name
    except:
        send_email(body="impossible to save file to bucket")
        return False


def get_file_from_bucket(file_name, bucket_folder_name):
    """
    Get a file from my google cloud bucket
    Args:
        file_name: String, name of the file
        bucket_folder_name: String, name of the folder
    Returns: file content if it worked, False otherwise
    """
    full_name = '/' + bucket_folder_name + '/' + file_name
    try:
        f = gcs_open(full_name, 'r')
        file_content = f.read()
        f.close()
        return file_content
    except:
        send_email(body="impossible to get file from bucket     \n     " + full_name)
        return False


def send_email(to=MY_HOTMAIL, body='Error in GAE', subject='Error in GAE', attachments=[]):
    """
    Send an email to my private email to report an error
    Args:
        to: String, email addess
        body: String, body or the email
        subject: String, subject of the email
        attachments: List of tuple (filename, filecontent)
    """
    message = mail.EmailMessage(sender=SERVICE_EMAIL)
    message.subject = subject
    message.to = to
    message.body = body
    if attachments:
        message.attachments = attachments
    try:
        # Some attachments format might not be supported
        message.send()
    except:
        del message.attachments
        message.send()

