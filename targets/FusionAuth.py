import logging
import re
from typing import Dict, List

from fusionauth.fusionauth_client import FusionAuthClient
from knack.log import get_logger

from target import Persona, Origin

logger = get_logger(__name__)


def populate_target(api_key: str, origins: List[Origin], personas: Dict[str, List[Persona]]):
    client = FusionAuthClient(api_key, 'http://localhost:9011')

    for origin in origins:

        tenant_request = {
            'tenant': {
                'name': origin.Name
            }
        }

        retrieve_tenant_response = client.retrieve_tenant(origin.ID)

        if retrieve_tenant_response.was_successful():

            update_tenant_response = client.update_tenant(origin.ID, tenant_request)
            if update_tenant_response.was_successful():
                logging.info(update_tenant_response.success_response)
            else:
                logging.error(update_tenant_response.error_response)

        else:

            create_tenant_response = client.create_tenant(tenant_request, origin.ID)
            if create_tenant_response.was_successful():
                logging.info(create_tenant_response.success_response)
            else:
                logging.error(create_tenant_response.error_response)

    for origin_id, origin_personas in personas.items():

        tenant_id = str(origin_id)

        origin = next(filter(lambda x: x.ID == origin_id, origins))
        email_domain_name = origin.Name.strip().lower().replace(' ', '-').replace('&', 'and') + '.com'

        client.set_tenant_id(tenant_id)

        for persona in origin_personas:
            user_name = re.sub('\W+', '-', persona.FullName.strip().lower()).strip('-')
            email = f"{user_name}@{email_domain_name}"

            user_id = str(persona.ID)

            user_request = {
                'sendSetPasswordEmail': False,
                'skipVerification': True,
                'user': {
                    'tenantId': tenant_id,
                    'username': user_name,
                    'email': email,
                    'password': 'Tiksn.com#1',
                    'firstName': persona.FirstName,
                    'lastName': persona.LastName,
                    'fullName': persona.FullName,
                    'imageUrl': persona.ProfilePictureUrl,
                }
            }

            retrieve_user_response = client.retrieve_user(user_id)
            if retrieve_user_response.was_successful():

                update_user_response = client.update_user(user_id, user_request)
                if update_user_response.was_successful():
                    logging.info(update_user_response.success_response)
                else:
                    logging.error(update_user_response.error_response)
            else:

                create_user_response = client.create_user(user_request, user_id)
                if create_user_response.was_successful():
                    logging.info(create_user_response.success_response)
                else:
                    logging.error(create_user_response.error_response)
