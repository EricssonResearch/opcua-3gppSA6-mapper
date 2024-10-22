import requests
import json

pathOfTheProxyDirectory = "/home/bundab/Work/Ericsson/EricssonWork_02/Open-source_version_01" #"PathOfTheProxyDirectory"

def register():
    url = "http://capifcore:8080/register"
    headers = {"Content-Type": "application/json"}

    with open(f"{pathOfTheProxyDirectory}/Proxy/CommandsForCAPIF/JsonFiles/"
              "Register.json", "r") as f:
        json_data = json.load(f)

    data = json_data

    entity_id = None

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()

        entity_id = response.json()['id']
        print(f"User registered successfully. ID: {entity_id}")

    except requests.exceptions.RequestException as e:
        print(f"Error registering user: {e}")

    return entity_id


def get_auth():
    url = "http://capifcore:8080/getauth"
    headers = {"Content-Type": "application/json"}
    access_token = None

    with open(f"{pathOfTheProxyDirectory}/Proxy/CommandsForCAPIF/JsonFiles/"
              "GetAuth.json", "r") as f:
        json_data = json.load(f)

    data = json_data

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()

        access_token = response.json()['access_token']
        print(f"Access token obtained: {access_token}")

    except requests.exceptions.RequestException as e:
        print(f"Error fetching access token: {e}")

    return access_token


def sign_csr(id_param):
    url = "http://capifcore:8080/sign-csr"
    authorization_header = "Bearer " + str(id_param)
    content_type_header = "application/json"

    with open(f"{pathOfTheProxyDirectory}/Proxy/CommandsForCAPIF/JsonFiles/"
              "SignCsr.json", "r") as f:
        json_data = json.load(f)

    data = json_data

    headers = {
        "Authorization": authorization_header,
        "Content-Type": content_type_header
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()

        certificate = response.json()['certificate']
        with open(f"{pathOfTheProxyDirectory}/Proxy/CommandsForCAPIF/CertificatesAndKeys/"
                  "exposer.crt", "w") as f:
            f.write(certificate)

        print("Certificate saved to exposer.crt")
    except requests.exceptions.RequestException as e:
        print(f"Error signing CSR: {e}")


def published_apis(id_param, access_token_param):
    url = "https://capifcore/published-apis/v1/" + str(id_param) + "/service-apis"
    cert_path = (f"{pathOfTheProxyDirectory}/Proxy/CommandsForCAPIF/CertificatesAndKeys/"
                 "exposer.crt")
    key_path = (f"{pathOfTheProxyDirectory}/Proxy/CommandsForCAPIF/CertificatesAndKeys/"
                "exposer.key")
    ca_cert_path = (f"{pathOfTheProxyDirectory}/Proxy/CommandsForCAPIF/CertificatesAndKeys/"
                    "ca.crt")

    access_token = access_token_param

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }

    with open(f"{pathOfTheProxyDirectory}/Proxy/CommandsForCAPIF/JsonFiles/"
              "PublishedApis.json", "r") as f:
        json_data = json.load(f)

    data = json_data

    try:
        response = requests.post(url, headers=headers, json=data, cert=(cert_path, key_path), verify=ca_cert_path)
        response.raise_for_status()

        print("Service API registered successfully.")

    except requests.exceptions.RequestException as e:
        print(f"Error registering service API: {e}")


def all_commands():
    entity_id = register()
    access_token = get_auth()
    sign_csr(id_param=entity_id)
    published_apis(id_param=entity_id, access_token_param=access_token)
