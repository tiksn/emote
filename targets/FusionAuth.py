import logging
import re
import uuid
from typing import Dict, List

from fusionauth.fusionauth_client import FusionAuthClient
from knack.log import get_logger

from target import Persona, Origin

logger = get_logger(__name__)


def populate_target(api_key: str, origins: List[Origin], personas: Dict[uuid.UUID, List[Persona]]):
    client = FusionAuthClient(api_key, 'http://localhost:9011')

    group_names = ['Administrators']
    application_names = ['Fossa', 'Verdant', 'Yabby']
    administrator_role_name = 'administrator'
    main_key_id = uuid.UUID('a3aee1ec-c965-4ec8-97b2-c0245bc1c5ec')
    main_key_name = 'MainKey'

    create_or_update_key(client, main_key_id, main_key_name)

    for origin in origins:
        create_or_update_tenant(client, origin, main_key_id)

    for origin in origins:

        client.set_tenant_id(str(origin.ID))

        administrator_role_ids = []

        for application_name in application_names:
            application_id = uuid.uuid5(origin.ID, f"application-{application_name}")
            administrator_role_id = uuid.uuid5(application_id, f"role-{administrator_role_name}")
            administrator_role_ids.append(str(administrator_role_id))

            create_or_update_application(client, origin, application_id, application_name, administrator_role_id,
                                         administrator_role_name)

        for group_name in group_names:
            group_id = uuid.uuid5(origin.ID, f"group-{group_name}")

            create_or_update_group(client, group_id, group_name, administrator_role_ids)

    for origin_id, origin_personas in personas.items():

        origin = next(filter(lambda x: x.ID == origin_id, origins))
        email_domain_name = origin.Name.strip().lower().replace(' ', '-').replace('&', 'and') + '.com'

        client.set_tenant_id(str(origin_id))

        for persona in origin_personas:
            user_name = re.sub('\W+', '-', persona.FullName.strip().lower()).strip('-')
            email = f"{user_name}@{email_domain_name}"

            create_or_update_user(client, origin_id, user_name, email, persona)

            for application_name in application_names:
                application_id = uuid.uuid5(origin.ID, f"application-{application_name}")

                create_or_update_registration(client, origin.ID, persona.ID, application_id)

            for group_name in group_names:
                group_id = uuid.uuid5(origin.ID, f"group-{group_name}")

                create_or_update_members(client, group_id, persona)


def create_or_update_members(client: FusionAuthClient,
                             group_id: uuid.UUID,
                             persona: Persona):
    if persona.IsAdmin:
        members_request = {
            'members': {
                str(group_id): [
                    {
                        'userId': str(persona.ID)
                    },
                ]
            },
        }

        create_members_response = client.create_group_members(members_request)
        if create_members_response.was_successful():
            logging.info(create_members_response.success_response)
        else:
            logging.error(create_members_response.error_response)


def create_or_update_registration(client: FusionAuthClient,
                                  origin_id: uuid.UUID,
                                  user_id: uuid.UUID,
                                  application_id: uuid.UUID):
    roles = []
    registration_request = {
        'skipRegistrationVerification': True,
        'registration': {
            'tenantId': str(origin_id),
            'applicationId': str(application_id),
            'roles': roles,
        }
    }
    retrieve_registration_response = client.retrieve_registration(str(user_id), str(application_id))
    if retrieve_registration_response.was_successful():

        update_registration_response = client.update_registration(str(user_id), registration_request)
        if update_registration_response.was_successful():
            logging.info(update_registration_response.success_response)
        else:
            logging.error(update_registration_response.error_response)
    else:

        create_registration_response = client.register(registration_request, str(user_id))
        if create_registration_response.was_successful():
            logging.info(create_registration_response.success_response)
        else:
            logging.error(create_registration_response.error_response)


def create_or_update_user(client: FusionAuthClient, origin_id: uuid.UUID, user_name: str, email: str, persona: Persona):
    user_request = {
        'sendSetPasswordEmail': False,
        'skipVerification': True,
        'user': {
            'tenantId': str(origin_id),
            'username': user_name,
            'email': email,
            'password': 'Tiksn.com#1',
            'firstName': persona.FirstName,
            'lastName': persona.LastName,
            'fullName': persona.FullName,
            'imageUrl': persona.ProfilePictureUrl,
        }
    }
    retrieve_user_response = client.retrieve_user(str(persona.ID))
    if retrieve_user_response.was_successful():

        update_user_response = client.update_user(str(persona.ID), user_request)
        if update_user_response.was_successful():
            logging.info(update_user_response.success_response)
        else:
            logging.error(update_user_response.error_response)
    else:

        create_user_response = client.create_user(user_request, str(persona.ID))
        if create_user_response.was_successful():
            logging.info(create_user_response.success_response)
        else:
            logging.error(create_user_response.error_response)


def create_or_update_group(client: FusionAuthClient, group_id: uuid.UUID, group_name: str,
                           administrator_role_ids: list[str]):
    group_request = {
        'group': {
            'name': group_name
        },
        'roleIds': administrator_role_ids,
    }
    retrieve_group_response = client.retrieve_group(group_id)
    if retrieve_group_response.was_successful():

        update_group_response = client.update_group(group_id, group_request)
        if update_group_response.was_successful():
            logging.info(update_group_response.success_response)
        else:
            logging.error(update_group_response.error_response)

    else:

        create_group_response = client.create_group(group_request, group_id)
        if create_group_response.was_successful():
            logging.info(create_group_response.success_response)
        else:
            logging.error(create_group_response.error_response)


def create_or_update_application(client: FusionAuthClient, origin: Origin,
                                 application_id: uuid.UUID,
                                 application_name: str,
                                 administrator_role_id: uuid.UUID,
                                 administrator_role_name: str):
    application_request = {
        'application': {
            'tenantId': str(origin.ID),
            'name': application_name,
            'roles': [
                {
                    'id': str(administrator_role_id),
                    'name': administrator_role_name,
                    'description': f"'{administrator_role_name}' for '{application_name}'",
                    'isSuperRole': True,
                }
            ],
            'oauthConfiguration': {
                'authorizedRedirectURLs': [
                    'http://127.0.0.1/sample-wpf-app',
                ],
                'generateRefreshTokens': True,
                'proofKeyForCodeExchangePolicy': 'Required',
                'enabledGrants': ['authorization_code', 'refresh_token'],
            },
        }
    }
    retrieve_application_response = client.retrieve_application(application_id)
    if retrieve_application_response.was_successful():

        update_application_response = client.update_application(application_id, application_request)
        if update_application_response.was_successful():
            logging.info(update_application_response.success_response)
        else:
            logging.error(update_application_response.error_response)

    else:

        create_application_response = client.create_application(application_request, application_id)
        if create_application_response.was_successful():
            logging.info(create_application_response.success_response)
        else:
            logging.error(create_application_response.error_response)


def create_or_update_tenant(client: FusionAuthClient,
                            origin: Origin,
                            key_id: uuid.UUID):
    tenant_request = {
        'tenant': {
            'name': origin.Name,
            'jwtConfiguration': {
                'accessTokenKeyId': str(key_id),
                'idTokenKeyId': str(key_id),
            }
        }
    }

    retrieve_tenant_response = client.retrieve_tenant(str(origin.ID))

    if retrieve_tenant_response.was_successful():

        update_tenant_response = client.update_tenant(str(origin.ID), tenant_request)
        if update_tenant_response.was_successful():
            logging.info(update_tenant_response.success_response)
        else:
            logging.error(update_tenant_response.error_response)

    else:

        create_tenant_response = client.create_tenant(tenant_request, str(origin.ID))
        if create_tenant_response.was_successful():
            logging.info(create_tenant_response.success_response)
        else:
            logging.error(create_tenant_response.error_response)


def create_or_update_key(client: FusionAuthClient,
                         key_id: uuid.UUID,
                         key_name: str):
    key_request = {
        'key': {
            'algorithm': 'RS256',
            'name': key_name,
            'length': 2048,
        }
    }
    retrieve_key_response = client.retrieve_key(str(key_id))
    if retrieve_key_response.was_successful():

        update_key_response = client.update_key(str(key_id), key_request)
        if update_key_response.was_successful():
            logging.info(update_key_response.success_response)
        else:
            logging.error(update_key_response.error_response)
    else:

        create_key_response = client.generate_key(key_request, str(key_id))
        if create_key_response.was_successful():
            logging.info(create_key_response.success_response)
        else:
            logging.error(create_key_response.error_response)
