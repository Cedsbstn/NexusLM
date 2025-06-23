
"""
This module provides core utility functions for performing customer service agent operations.

It includes functions for:
- Sending meeting invitation through email
- Updating HubSpot CRM with customer details
- Retrieving cart information for a customer
- Getting product recommendations based on customer needs
- Sending security instructions for compute engine types
- Sending security best practices to customers
- Logging customer interactions for better service
"""

import logging
import uuid
import smtplib
import googleapiclient
import hubspot
from config import Config
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google.adk.tools import ToolContext
from hubspot.contacts import SimplePublicObjectInput
from prompts import SECURITY_INSTRUCTIONS

configs = Config()
logger = logging.getLogger(__name__)


def send_meeting_invitation(sender_email, sender_password, receiver_email, subject, message):
    """
    Sends a link to the user's phone number to start a video session.

    Args:
        sender_email (str): The email address of the sender.
        sender_password (str): The password for the sender's email account.
        receiver_email (str): The email address of the receiver.
        subject (str): The subject of the email.
        message (str): The message body of the email.

    Returns:
        dict: A dictionary with the status and message.

    Example:
        >>> send_meeting_invitation(sender_email='example@gmail.com', sender_password='password', receiver_email='receiver@gmail.com', subject='Meeting Link', message='Join the meeting here.')
        {'status': 'success', 'message': 'Link sent to receiver@gmail.com'}
    """
    sender_email = configs.sender_email
    sender_password = configs.sender_password
    receiver_email = ToolContext.get_input(
        "Please enter the receiver's email address")
    subject = 'Meeting Invitation!'
    # Use first 8 chars of UUID for shorter link
    meeting_id = str(uuid.uuid4())[:8]
    meeting_link = f"https://meet.google.com/{meeting_id}"
    message = f'Hello there! This issue needs further investigation. Please join the meeting session using the link below.\n{meeting_link}'

    # Create a multipart message and set headers
    email_message = MIMEMultipart()
    email_message['From'] = sender_email
    email_message['To'] = receiver_email
    email_message['Subject'] = subject

    # Add body to the email
    email_message.attach(MIMEText(message, 'plain'))

    # Create SMTP session for sending the email
    smtp_server = smtplib.SMTP('smtp.gmail.com', 587)
    smtp_server.starttls()
    smtp_server.login(sender_email, sender_password)

    # Convert the multipart message to a string
    email_text = email_message.as_string()

    # Send the email
    smtp_server.sendmail(sender_email, receiver_email, email_text)
    smtp_server.quit()

    send_meeting_invitation(sender_email, sender_password,
                            receiver_email, subject, message)

    logger.info("Sending meeting invitation to %s", receiver_email)

    return {"status": "success", "message": f"Link sent to {receiver_email}"}


def update_hubspot_crm(customer_id: str, details: dict) -> dict:
    """
    Updates the HubSpot CRM with customer details through ADK web interface.

    Args:
        customer_id (str): The ID of the customer.
        details (str): A dictionary of details to update in HubSpot.

    Returns:
        dict: A dictionary with the status and message.

    Example:
        >>> update_hubspot_crm(customer_id='123', details={
            'appointment_date': '2024-07-25', 
            'appointment_time': '9-12',
            'items': 'G2 Standard Instance (2 vCPU), Persistent SSD Disk 500GB',
            })
        {'status': 'success', 'message': 'HubSpot record updated.'}
    """
    logger.info(
        "Updating HubSpot CRM for customer ID %s with details: %s",
        customer_id,
        details,
    )

    # Get input confirmation from ADK interface
    confirm = ToolContext.get_confirmation(
        f"Update HubSpot record for customer {customer_id} with following details?\n"
        f"{details}"
    )

    if not confirm:
        return {"status": "cancelled", "message": "Update cancelled by user"}

    # Initialize HubSpot client with API key

    try:
        hubspot_client = hubspot.Client.create(
            access_token=configs.hubspot_api_key)

        # Prepare properties to update
        properties = SimplePublicObjectInput(properties=details)

        # Update contact in HubSpot
        api_response = hubspot_client.crm.contacts.basic_api.update(
            contact_id=customer_id,
            simple_public_object_input=properties
        )

        ToolContext.log_info(f"HubSpot API response: {api_response}")

    except hubspot.ApiException as e:
        logger.error("HubSpot API error: %s", str(e))
        raise

    try:
        # Process details through ADK interface
        for key, value in details.items():
            ToolContext.log_info(f"Updating {key}: {value}")

        return {"status": "success", "message": "HubSpot record updated."}
    except Exception as e:
        logger.error("Failed to update HubSpot: %s", str(e))
        return {"status": "error", "message": f"Failed to update HubSpot: {str(e)}"}


def retrieve_cart_information(customer_id: str) -> dict:
    """
    Args:
        customer_id (str): The ID of the customer.

    Returns:
        dict: A dictionary representing the cart contents.

    Example:
        >>> retrieve_cart_information(customer_id='123')
        {'items': [{'product_id': 'n2-standard-2', 'name': 'N2 Standard Instance (2 vCPU)', 'quantity': 1}, {'product_id': 'pd-ssd', 'name': 'Persistent SSD Disk 500GB', 'quantity': 1}], 'subtotal': 125.40}
    """
    logger.info("Accessing cart information for customer ID: %s", customer_id)

    try:
        # Initialize Google Cloud clients
        compute = googleapiclient.discovery.build('compute', 'v1')
        billing = googleapiclient.discovery.build('cloudbilling', 'v1')

        cart_items = []
        cart_subtotal = 0.0

        # Query customer's selected instances
        zone = ToolContext.get_input("Please enter the zone for resources")
        request = compute.instances().list(project=configs.GOOGLE_CLOUD_PROJECT, zone=zone)
        while request is not None:
            response = request.execute()
            for instance in response.get('items', []):
                if instance.get('labels', {}).get('customer_id') == customer_id:
                    machine_type = instance['machineType'].split('/')[-1]

                    # Get pricing using Cloud Billing API
                    price_request = billing.services().skus().list(
                        parent=f'services/6F81-5844-456A',  # Compute Engine service
                        filter=f'resource.name = {machine_type}'
                    ).execute()

                    # Calculate instance cost from pricing data
                    price_per_hour = float(
                        price_request['skus'][0]['pricingInfo'][0]['pricingExpression']['tieredRates'][0]['unitPrice']['nanos']) / 1e9
                    monthly_cost = price_per_hour * 730  # Average hours per month

                    cart_items.append({
                        'product_id': machine_type,
                        'name': instance['name'],
                        'quantity': 1,
                        'monthly_cost': monthly_cost
                    })
                    cart_subtotal += monthly_cost
                request = compute.instances().list_next(
                    previous_request=request, previous_response=response)

            # Query customer's selected disks
            request = compute.disks().list(project=configs.GOOGLE_CLOUD_PROJECT, zone=zone)
        while request is not None:
            response = request.execute()
            for disk in response.get('items', []):
                if disk.get('labels', {}).get('customer_id') == customer_id:
                    disk_type = disk['type'].split('/')[-1]
                    size_gb = int(disk['sizeGb'])

                    # Get disk pricing using Cloud Billing API
                    price_request = billing.services().skus().list(
                        parent='services/6F81-5844-456A',
                        filter=f'resource.name = {disk_type}'
                    ).execute()

                    # Calculate disk cost from pricing data
                    price_per_gb = float(
                        price_request['skus'][0]['pricingInfo'][0]['pricingExpression']['tieredRates'][0]['unitPrice']['nanos']) / 1e9
                    monthly_cost = price_per_gb * size_gb

                    cart_items.append({
                        'product_id': disk_type,
                        'name': f"{disk_type} {size_gb}GB",
                        'quantity': 1,
                        'monthly_cost': monthly_cost
                    })
                    cart_subtotal += monthly_cost
            request = compute.disks().list_next(
                previous_request=request, previous_response=response)

        return {
            "items": cart_items,
            "subtotal": cart_subtotal
        }

    except Exception as e:
        logger.error("Failed to access cart information: %s", str(e))
        raise


def get_product_recommendations(customer_id: str) -> dict:
    """Provides Compute Engine product recommendations based on customer needs.

    Args:
        customer_id: Customer ID for personalized recommendations.

    Returns:
        A dictionary of recommended Compute Engine products.
    """
    logger.info(
        "Getting Compute Engine recommendations for customer %s",
        customer_id,
    )

    try:
        # Get customer needs through ADK interface
        workload_type = ToolContext.get_input(
            "What type of workload? (web-server/data-processing)")

        vcpu_count = ToolContext.get_input(
            "How many vCPUs needed? (enter number)")

        memory_needed = ToolContext.get_input(
            "How much memory needed in GB? (enter number)")

        # Initialize Google Cloud Compute Engine client
        compute = googleapiclient.discovery.build('compute', 'v1')

        # Get available machine types in the specified zone
        zone = ToolContext.get_input(
            "Please enter the zone for recommendations")
        machine_types_request = compute.machineTypes().list(
            project=configs.GOOGLE_CLOUD_PROJECT,
            zone=zone
        )

        machine_types = machine_types_request.execute()

        recommendations = {"recommendations": []}

        if workload_type.lower() == "web-server":
            # For web servers, recommend balanced instances matching specs
            for machine in machine_types.get('items', []):
                if ('n2-standard' in machine['name'] and
                    machine['guestCpus'] <= int(vcpu_count) * 1.5 and
                        machine['memoryMb']/1024 <= float(memory_needed) * 1.5):
                    recommendations["recommendations"].append({
                        "product_id": machine['name'],
                        "name": f"{machine['name']} Instance",
                        "description": f"General-purpose instance with {machine['guestCpus']} vCPUs and {machine['memoryMb']/1024}GB memory",
                        "specs": {
                            "cpus": machine['guestCpus'],
                            "memory_gb": machine['memoryMb']/1024
                        }
                    })

        elif workload_type.lower() == "data-processing":
            # For data processing, recommend compute-optimized instances
            for machine in machine_types.get('items', []):
                if ('c2-standard' in machine['name'] and
                    machine['guestCpus'] >= int(vcpu_count) and
                        machine['memoryMb']/1024 >= float(memory_needed)):
                    recommendations["recommendations"].append({
                        "product_id": machine['name'],
                        "name": f"{machine['name']} Instance",
                        "description": f"Compute-optimized instance with {machine['guestCpus']} vCPUs and {machine['memoryMb']/1024}GB memory",
                        "specs": {
                            "cpus": machine['guestCpus'],
                            "memory_gb": machine['memoryMb']/1024
                        }
                    })

        # Add storage recommendations based on workload
        disk_types_request = compute.diskTypes().list(
            project=configs.GOOGLE_CLOUD_PROJECT,
            zone=zone
        )
        disk_types = disk_types_request.execute()

        storage_needed = ToolContext.get_input(
            "How much storage needed in GB? (enter number)")

        for disk in disk_types.get('items', []):
            if ('pd-ssd' in disk['name'] and workload_type.lower() == "data-processing") or \
               ('pd-standard' in disk['name'] and workload_type.lower() == "web-server"):
                recommendations["recommendations"].append({
                    "product_id": disk['name'],
                    "name": "Persistent Disk",
                    "description": f"Storage optimized for {workload_type}",
                    "specs": {
                        "type": "SSD" if "ssd" in disk['name'] else "Standard",
                        "size_gb": storage_needed
                    }
                })

        return recommendations

    except Exception as e:
        logger.error("Failed to get recommendations: %s", str(e))
        raise


def send_security_instructions(customer_id: str, delivery_method: str = 'email') -> dict:
    """Sends security best practices for specific compute engine type.

    Args:
        customer_id: The ID of the customer.
        delivery_method: 'email' (default) or 'sms'.

    Returns:
        A dictionary indicating the status.

    Example:
        >>> send_security_instructions(customer_id='123')
        {'status': 'success', 'message': 'Security instructions for N2 instance sent via email.'}
    """
    logger.info(
        "Sending security instructions to customer: %s via %s",
        customer_id,
        delivery_method
    )

    # Get compute engine type through ADK interface
    compute_type = ToolContext.get_input(
        "What type of compute engine? (n2-standard/c2-standard)")

    # Get instructions from prompts config
    try:

        base_instructions = SECURITY_INSTRUCTIONS['base']
        specific_instructions = SECURITY_INSTRUCTIONS.get(
            compute_type.lower(), [])

        instructions = base_instructions + specific_instructions
        message = f"Security Best Practices for {compute_type}:\n" + "\n".join(
            instructions)

    except (ImportError, KeyError) as e:
        logger.error("Failed to load security instructions: %s", str(e))
        return {"status": "error", "message": "Failed to load security configuration"}

    # Mock sending instructions
    return {
        "status": "success",
        "message": f"Security instructions for {compute_type} sent via {delivery_method}."
    }
